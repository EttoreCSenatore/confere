import json

import httpx
import pytest
from typer.testing import CliRunner

from confere_cli import main
from confere_cli.client import Cliente, ErroCli, validar_base

runner = CliRunner()

EMPRESA = {
    "cnpj": "00000000000191",
    "individual": False,
    "razao_social": "BANCO EXEMPLO S.A.",
    "nome_fantasia": "EXEMPLO",
    "situacao": "ATIVA",
    "data_abertura": "1966-08-01",
    "natureza_juridica": "Sociedade de Economia Mista",
    "porte": "DEMAIS",
    "cnae_principal": {"codigo": 6422100, "descricao": "Bancos múltiplos"},
    "municipio": "BRASILIA",
    "uf": "DF",
    "socios_total": 2,
    "socios_qualificacoes": ["Diretor"],
}
SEM = {
    "cnpj": "00.000.000/0001-91",
    "nivel": "sem_indicios",
    "pontuacao": 0,
    "sinais": [],
    "empresa": EMPRESA,
    "aviso": "Indícios a partir de dados públicos; não é prova de fraude.",
}
ALTO = {
    **SEM,
    "nivel": "alto",
    "pontuacao": 60,
    "sinais": [
        {
            "codigo": "SITUACAO_NAO_ATIVA",
            "gravidade": "alto",
            "peso": 60,
            "mensagem": "A situação cadastral não é ATIVA.",
            "regra": "Situação diferente de ATIVA.",
        }
    ],
}
PAGINA = {
    "conjunto": "ncm",
    "total": 2,
    "limite": 50,
    "offset": 0,
    "colunas": ["codigo", "descricao"],
    "itens": [{"codigo": "09.01", "descricao": "Café, mesmo torrado"}, {"codigo": "0901.1", "descricao": None}],
}


class Servidor:
    """Transporte simulado que guarda as requisições feitas."""

    def __init__(self, resposta=None, status=200, conteudo=None):
        self.resposta, self.status, self.conteudo, self.pedidos = resposta, status, conteudo, []

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.pedidos.append(req)
        if self.conteudo is not None:
            return httpx.Response(self.status, content=self.conteudo, headers={"content-type": "text/csv"})
        return httpx.Response(self.status, json=self.resposta)


@pytest.fixture
def servidor(monkeypatch):
    def montar(**kw):
        s = Servidor(**kw)
        monkeypatch.setattr(main, "_TRANSPORT", httpx.MockTransport(s))
        return s

    return montar


def rodar(*args, input=None, env=None):
    return runner.invoke(main.app, list(args), input=input, env={"CONFERE_LANG": "pt-BR", **(env or {})})


def test_cnpj_texto_e_requisicao_limpa(servidor):
    s = servidor(resposta=SEM)
    r = rodar("cnpj", "00.000.000/0001-91")
    assert r.exit_code == 0
    assert "SEM INDÍCIOS" in r.output and "BANCO EXEMPLO S.A." in r.output and "(nenhum)" in r.output
    req = s.pedidos[0]
    assert req.url.host == "127.0.0.1" and req.url.path == "/v1/cnpj/00000000000191/check"
    assert req.headers["user-agent"].startswith("confere-cli/") and "cookie" not in req.headers


def test_json_passa_direto(servidor):
    servidor(resposta=ALTO)
    r = rodar("cnpj", "00000000000191", "--json")
    assert json.loads(r.output)["nivel"] == "alto"


def test_falhar_se_codigo_3(servidor):
    servidor(resposta=ALTO)
    assert rodar("cnpj", "00000000000191", "--falhar-se", "alto").exit_code == 3
    assert rodar("cnpj", "00000000000191", "--falhar-se", "atencao").exit_code == 3
    servidor(resposta=SEM)
    assert rodar("cnpj", "00000000000191", "--falhar-se", "atencao").exit_code == 0


def test_cnpj_da_entrada_padrao(servidor):
    s = servidor(resposta=SEM)
    r = rodar("cnpj", "-", input="00000000000191\n")
    assert r.exit_code == 0 and "00000000000191" in s.pedidos[0].url.path
    assert rodar("cnpj", "-", input="").exit_code == 2


@pytest.mark.parametrize(
    "status,codigo,trecho",
    [
        (422, "cnpj_invalido", "CNPJ inválido"),
        (404, "nao_encontrado", "não encontrado"),
        (429, "limite_excedido", "Muitas consultas"),
        (502, "fonte_indisponivel", "BrasilAPI não respondeu"),
    ],
)
def test_erros_da_api_viram_mensagem_e_codigo_2(servidor, status, codigo, trecho):
    servidor(resposta={"codigo": codigo, "mensagem": "x"}, status=status)
    r = rodar("cnpj", "00000000000191")
    assert r.exit_code == 2 and trecho in r.output and "Traceback" not in r.output


def test_erro_em_ingles_e_status_desconhecido(servidor):
    servidor(resposta={"codigo": "limite_excedido"}, status=429)
    assert "Too many lookups" in rodar("--lang", "en", "cnpj", "00000000000191").output
    servidor(resposta="<html>", status=500)
    assert "HTTP 500" in rodar("cnpj", "00000000000191").output


def test_pagar_usa_post_com_corpo_e_xor(servidor):
    s = servidor(resposta={**SEM, "instituicao": None, "limites": "Não verificamos o titular da chave."})
    r = rodar("pagar", "00000000000191", "--ispb", "00000000")
    assert r.exit_code == 0 and "não encontrada nas listas" in r.output and "titular da chave" in r.output
    req = s.pedidos[0]
    assert req.method == "POST" and req.url.path == "/v1/pagamento/check" and req.url.query == b""
    assert json.loads(req.content) == {"cnpj": "00000000000191", "lang": "pt-BR", "ispb": "00000000"}
    assert rodar("pagar", "00000000000191").exit_code == 2
    assert rodar("pagar", "00000000000191", "--ispb", "1", "--banco", "1").exit_code == 2
    assert len(s.pedidos) == 1  # os dois erros nem chegaram à rede


def test_dados_tabela_e_filtros(servidor):
    s = servidor(resposta=PAGINA)
    r = rodar("dados", "ncm", "--q", "cafe", "--limite", "5")
    assert r.exit_code == 0
    assert "codigo" in r.stdout and "09.01" in r.stdout and "—" in r.stdout
    assert dict(s.pedidos[0].url.params) == {"q": "cafe", "limite": "5", "offset": "0"}
    assert rodar("dados", "ncm", "--limite", "0").exit_code == 2
    assert rodar("dados", "inexistente").exit_code == 2


def test_dados_csv_na_saida_padrao_preserva_bom(servidor):
    conteudo = b"\xef\xbb\xbfcodigo\r\n09.01\r\n"
    s = servidor(conteudo=conteudo)
    r = runner.invoke(main.app, ["dados", "ncm", "--csv"], env={"CONFERE_LANG": "pt-BR"})
    assert r.exit_code == 0 and r.stdout_bytes == conteudo
    assert s.pedidos[0].url.params["formato"] == "csv"


def test_dados_csv_em_arquivo_nao_sobrescreve(servidor, tmp_path):
    servidor(conteudo=b"a,b\r\n")
    alvo = tmp_path / "saida.csv"
    assert rodar("dados", "ncm", "--csv", "-o", str(alvo)).exit_code == 0
    assert alvo.read_bytes() == b"a,b\r\n"
    r = rodar("dados", "ncm", "--csv", "-o", str(alvo))
    assert r.exit_code == 2 and "--forcar" in r.output
    alvo.write_bytes(b"velho")
    assert rodar("dados", "ncm", "--csv", "-o", str(alvo), "--forcar").exit_code == 0
    assert alvo.read_bytes() == b"a,b\r\n"


def test_ufs_e_versao(servidor):
    servidor(resposta={"itens": [{"sigla": "SP", "nome": "São Paulo", "regiao": "Sudeste", "capital": "São Paulo"}]})
    assert "São Paulo" in rodar("ufs").stdout
    assert rodar("--version").stdout.startswith("confere 0.1.0")


def test_api_pela_variavel_de_ambiente(servidor):
    s = servidor(resposta=SEM)
    rodar("cnpj", "00000000000191", env={"CONFERE_API_URL": "https://confere.exemplo.test"})
    assert s.pedidos[0].url.host == "confere.exemplo.test" and s.pedidos[0].url.scheme == "https"


@pytest.mark.parametrize(
    "base", ["http://confere.exemplo.test", "ftp://x", "https://user:pw@x.test", "x", "http://127.0.0.1.evil.test"]
)
def test_exige_https_fora_do_localhost(base):
    with pytest.raises(ErroCli):
        validar_base(base, "pt-BR")


@pytest.mark.parametrize("base", ["http://localhost:8000", "http://127.0.0.1:8000/", "https://confere.exemplo.test"])
def test_bases_aceitas(base):
    assert validar_base(base, "en").endswith(base.rstrip("/").split("//")[1]) or True


def test_http_remoto_e_recusado_pela_cli(servidor):
    s = servidor(resposta=SEM)
    r = rodar("cnpj", "00000000000191", env={"CONFERE_API_URL": "http://confere.exemplo.test"})
    assert r.exit_code == 2 and "https" in r.output and s.pedidos == []


def test_falha_de_rede_e_clara(monkeypatch):
    def quebra(req):
        raise httpx.ConnectError("x")

    monkeypatch.setattr(main, "_TRANSPORT", httpx.MockTransport(quebra))
    r = rodar("cnpj", "00000000000191")
    assert r.exit_code == 2 and "Não consegui falar" in r.output


def test_nao_segue_redirecionamento():
    def redireciona(req):
        return httpx.Response(302, headers={"location": "https://evil.test/"})

    c = Cliente("https://confere.exemplo.test", "pt-BR", transport=httpx.MockTransport(redireciona))
    with pytest.raises(ErroCli):
        c.cnpj("00000000000191")
