from datetime import date, timedelta

from confere.empresa import reduzir
from confere.risco import avaliar, codigos
from tests.conftest import BRUTO_PJ, CNPJ_OK, HOJE


def empresa(**mudancas):
    bruto = {**BRUTO_PJ, **mudancas}
    return reduzir(CNPJ_OK, bruto)


def test_empresa_antiga_ativa_sem_indicios():
    av = avaliar(empresa(), HOJE)
    assert av.sinais == [] and av.pontuacao == 0 and av.nivel == "sem_indicios"


def test_situacao_nao_ativa_e_alto():
    av = avaliar(empresa(descricao_situacao_cadastral="BAIXADA"), HOJE)
    assert [s.codigo for s in av.sinais] == ["SITUACAO_NAO_ATIVA"]
    assert av.nivel == "alto"


def test_idade_limites():
    def com_idade(dias):
        return codigos(empresa(data_inicio_atividade=(HOJE - timedelta(days=dias)).isoformat()), HOJE)

    assert com_idade(29) == ["EMPRESA_RECEM_ABERTA"]
    assert com_idade(30) == ["EMPRESA_NOVA"]
    assert com_idade(179) == ["EMPRESA_NOVA"]
    assert com_idade(180) == []


def test_data_ausente_e_futura():
    assert "DADOS_INCOMPLETOS" in codigos(empresa(data_inicio_atividade=None), HOJE)
    assert codigos(empresa(data_inicio_atividade=(HOJE + timedelta(days=5)).isoformat()), HOJE) == []


def test_pontuacao_soma_e_nivel_atencao():
    av = avaliar(empresa(data_inicio_atividade=(HOJE - timedelta(days=60)).isoformat(), situacao_especial="X"), HOJE)
    assert av.pontuacao == 45 and av.nivel == "atencao"


def test_contato_e_qsa():
    c = codigos(empresa(email=None, ddd_telefone_1=None, qsa=[]), HOJE)
    assert "SEM_CONTATO_PUBLICO" in c and "QUADRO_SOCIETARIO_VAZIO" in c


def test_administracao_publica_sem_qsa_nao_alerta():
    assert "QUADRO_SOCIETARIO_VAZIO" not in codigos(empresa(qsa=[], codigo_natureza_juridica=1015), HOJE)


def test_mei_minimiza_e_informa():
    e = empresa(codigo_natureza_juridica=2135, opcao_pelo_mei=True, razao_social="JOAO DA SILVA 12345678901", qsa=[])
    assert e.individual and e.razao_social is None and e.nome_fantasia is None and e.capital_social is None
    av = avaliar(e, HOJE, "en")
    assert [s.codigo for s in av.sinais] == ["EMPRESARIO_INDIVIDUAL"]
    assert av.sinais[0].mensagem.startswith("Sole proprietor")
    assert av.nivel == "sem_indicios"


def test_idioma_desconhecido_cai_no_portugues():
    av = avaliar(empresa(descricao_situacao_cadastral="INAPTA"), HOJE, "fr")
    assert av.sinais[0].mensagem.startswith("A situação")


def test_reducao_nao_carrega_nomes_de_socios():
    e = empresa()
    texto = e.model_dump_json()
    assert "FULANO" not in texto and "BELTRANA" not in texto and "***" not in texto
    assert e.socios_total == 2 and e.socios_qualificacoes == ["Diretor", "Presidente"]
    assert date.fromisoformat("1966-08-01") == e.data_abertura
