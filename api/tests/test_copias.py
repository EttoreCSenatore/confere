import gzip
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from confere import dados as mod
from confere.app import criar_app
from confere.brasilapi import FonteIndisponivel
from confere.config import Config
from confere.dados import ARQUIVOS, COLUNAS, Snapshots, gravar_copia, texto_busca
from tests.conftest import HOJE, FonteFalsa

REAIS = Path(mod.__file__).parent / "snapshots"

LINHAS_BANCOS = [
    {
        "codigo_compe": 1,
        "ispb": "00000000",
        "nome": "BANCO DA COPIA",
        "nome_completo": "Banco da Cópia S.A.",
        "participa_pix": True,
    }
]
LINHAS_PIX = [
    {
        "ispb": "00000000",
        "nome": "BANCO DA COPIA",
        "modalidade": "Provedor de Conta Transacional",
        "tipo_participacao": "Direta",
    }
]


def pasta(tmp_path, dias_atras=1):
    """Cria cópias locais de mentira, geradas `dias_atras` dias antes de HOJE."""
    gerado = HOJE - timedelta(days=dias_atras)
    gravar_copia(tmp_path, "bancos", LINHAS_BANCOS, gerado)
    gravar_copia(tmp_path, "pix", LINHAS_PIX, gerado)
    gravar_copia(
        tmp_path, "ufs", [{"sigla": "SP", "nome": "São Paulo", "regiao": "Sudeste", "capital": "São Paulo"}], gerado
    )
    return tmp_path


def app(tmp_path, fonte, dias_atras=1, **cfg):
    return TestClient(
        criar_app(Config(**cfg), fonte=fonte, hoje=lambda: HOJE, snapshots=Snapshots(pasta(tmp_path, dias_atras)))
    )


def test_copia_recente_nao_usa_a_rede(tmp_path):
    fonte = FonteFalsa()
    with app(tmp_path, fonte) as c:
        r = c.get("/v1/dados/bancos").json()
        assert r["origem"] == "copia" and r["atualizado_em"] == (HOJE - timedelta(days=1)).isoformat()
        assert r["desatualizado"] is False and r["itens"][0]["nome"] == "BANCO DA COPIA"
        ufs = c.get("/v1/dados/ufs").json()
        assert ufs["atualizado_em"] == r["atualizado_em"] and ufs["itens"][0]["sigla"] == "SP"
    assert fonte.chamadas_listas == 0 and fonte.chamadas == 0


def test_pode_pagar_tambem_usa_a_copia(tmp_path):
    fonte = FonteFalsa(resposta=None)
    from tests.conftest import BRUTO_PJ

    fonte.resposta = dict(BRUTO_PJ)
    with app(tmp_path, fonte) as c:
        r = c.post("/v1/pagamento/check", json={"cnpj": "00000000000191", "ispb": "00000000"}).json()
    assert r["instituicao"]["nome"] == "BANCO DA COPIA" and r["instituicao"]["participa_pix"] is True
    assert fonte.chamadas_listas == 0  # só a consulta do CNPJ foi à rede


def test_copia_velha_busca_na_fonte(tmp_path):
    fonte = FonteFalsa()
    with app(tmp_path, fonte, dias_atras=30) as c:
        r = c.get("/v1/dados/bancos").json()
    assert r["origem"] == "fonte" and r["atualizado_em"] == HOJE.isoformat() and r["desatualizado"] is False
    assert fonte.chamadas_listas >= 1 and r["total"] == 3  # os dados simulados da fonte


def test_fonte_fora_do_ar_cai_na_copia_velha_e_avisa(tmp_path):
    fonte = FonteFalsa(erro=FonteIndisponivel("x"))
    with app(tmp_path, fonte, dias_atras=30) as c:
        r = c.get("/v1/dados/bancos").json()
        csv = c.get("/v1/dados/bancos", params={"formato": "csv"})
    assert r["origem"] == "copia" and r["desatualizado"] is True and r["itens"][0]["nome"] == "BANCO DA COPIA"
    assert csv.status_code == 200 and csv.headers["x-confere-dados-de"] == (HOJE - timedelta(days=30)).isoformat()


def test_max_dias_zero_ignora_as_copias(tmp_path):
    fonte = FonteFalsa()
    with app(tmp_path, fonte, snapshot_max_dias=0) as c:
        assert c.get("/v1/dados/bancos").json()["origem"] == "fonte"


def test_sem_copia_e_sem_fonte_da_502(tmp_path):
    with app(tmp_path, FonteFalsa(erro=FonteIndisponivel("x"))) as c:
        assert c.get("/v1/dados/ncm").status_code == 502  # ncm não tem cópia nesta pasta


def test_gravar_copia_e_deterministico(tmp_path):
    assert gravar_copia(tmp_path, "bancos", LINHAS_BANCOS, date(2026, 1, 1)) is True
    antes = (tmp_path / "bancos.json.gz").read_bytes()
    assert gravar_copia(tmp_path, "bancos", LINHAS_BANCOS, date(2026, 6, 6)) is False  # só a data mudou
    assert (tmp_path / "bancos.json.gz").read_bytes() == antes
    assert gravar_copia(tmp_path, "bancos", [], date(2026, 6, 6)) is True


def test_copias_ilegiveis_viram_ausentes(tmp_path):
    (tmp_path / "ncm.json.gz").write_bytes(b"isto nao e gzip")
    (tmp_path / "pix.json.gz").write_bytes(gzip.compress(b'{"sem": "itens"}'))
    s = Snapshots(tmp_path)
    assert s.obter("ncm") is None and s.obter("pix") is None and s.obter("bancos") is None


def test_texto_busca():
    t = texto_busca({"codigo": "09.01", "nome": "Café", "ok": True, "x": None, "cnpj": "11.222.333/0001-81"})
    assert "0901" in t and "cafe" in t and "11222333000181" in t and "true" not in t


# --- as cópias de verdade, no repositório -------------------------------------------------------------------------


@pytest.mark.parametrize("nome", ARQUIVOS)
def test_copias_reais_existem_e_tem_tamanho_razoavel(nome):
    arq = REAIS / f"{nome}.json.gz"
    assert arq.exists() and arq.stat().st_size < 1_000_000
    bruto = json.loads(gzip.decompress(arq.read_bytes()))
    gerado = date.fromisoformat(bruto["gerado_em"])
    assert date(2026, 1, 1) <= gerado <= date.today() + timedelta(days=1) and bruto["fonte"] == "BrasilAPI"


def test_copias_reais_tem_o_volume_esperado_e_so_os_campos_minimos():
    s = Snapshots(REAIS)
    minimos = {"bancos": 300, "pix": 500, "ncm": 10_000, "corretoras": 100, "ufs": 27}
    for nome, minimo in minimos.items():
        itens = s.obter(nome).itens
        assert len(itens) >= minimo, nome
        if nome in COLUNAS:
            assert all(set(i) == set(COLUNAS[nome]) for i in itens), f"{nome}: campos fora do esperado"
    por_uf = s.obter("municipios").itens
    assert set(por_uf) == set(mod.UFS) and sum(len(v) for v in por_uf.values()) >= 5_000
    assert all(set(m) == set(COLUNAS["municipios"]) for v in por_uf.values() for m in v)


def test_copias_reais_nao_tem_contato_nem_endereco():
    for nome in ARQUIVOS:
        texto = gzip.decompress((REAIS / f"{nome}.json.gz").read_bytes()).decode().lower()
        assert "@" not in texto, f"{nome}: parece haver e-mail"
        for campo in ("telefone", "email", "logradouro", "cep", "qsa", "valor_patrimonio_liquido", "ddd_telefone_1"):
            # confere o NOME do campo (um município pode se chamar "Logradouro")
            assert f'"{campo}":' not in texto, f"{nome}: campo {campo}"


def test_copias_reais_alimentam_a_api_sem_rede():
    fonte = FonteFalsa(erro=FonteIndisponivel("sem rede"))
    cfg = Config(snapshot_max_dias=10_000)  # idade da cópia não importa neste teste
    with TestClient(criar_app(cfg, fonte=fonte, hoje=lambda: date.today(), snapshots=Snapshots(REAIS))) as c:
        assert c.get("/v1/dados/bancos", params={"q": "brasil"}).json()["total"] >= 1
        assert c.get("/v1/dados/municipios", params={"uf": "SP", "q": "campinas"}).json()["total"] == 1
        assert c.get("/v1/dados/ncm", params={"q": "0901"}).json()["total"] >= 1
        assert c.get("/v1/dados/ufs").json()["itens"][0]["sigla"] == "AC"
    assert fonte.chamadas_listas == 0
