import logging

import pytest
from fastapi.testclient import TestClient

from confere.app import criar_app
from confere.brasilapi import FonteIndisponivel
from confere.config import Config
from confere.empresa import reduzir
from confere.risco import avaliar
from tests.conftest import BRUTO_PJ, CNPJ_OK, HOJE, FonteFalsa

URL = "/v1/pagamento/check"


def post(c, **corpo):
    return c.post(URL, json={"cnpj": CNPJ_OK, **corpo})


def test_participante_do_pix_por_ispb(cliente):
    r = post(cliente, ispb="00000000")
    assert r.status_code == 200
    d = r.json()
    assert d["nivel"] == "sem_indicios" and d["sinais"] == []
    assert d["instituicao"] == {
        "ispb": "00000000",
        "nome": "BCO DO BRASIL S.A.",
        "codigo_compe": 1,
        "participa_pix": True,
        "modalidade_pix": "Provedor de Conta Transacional",
        "tipo_participacao": "Direta",
    }
    assert "Não verificamos o titular" in d["limites"]
    for descartado in ("logo", "jsdelivr", "SAUN", "headquarters"):
        assert descartado not in r.text


def test_por_codigo_compe_com_zeros(cliente):
    assert post(cliente, banco="001").json()["instituicao"]["ispb"] == "00000000"


def test_participante_so_no_pix_sem_codigo(cliente):
    d = post(cliente, ispb="33333333").json()
    assert d["instituicao"]["participa_pix"] and d["instituicao"]["codigo_compe"] is None and d["sinais"] == []


def test_banco_existe_mas_nao_participa(cliente):
    d = post(cliente, banco="999").json()
    assert [s["codigo"] for s in d["sinais"]] == ["NAO_PARTICIPA_PIX"]
    assert d["nivel"] == "atencao" and d["instituicao"]["participa_pix"] is False


def test_instituicao_desconhecida_e_alto(cliente):
    d = post(cliente, ispb="99999999").json()
    assert d["instituicao"] is None and d["nivel"] == "alto"
    assert [s["codigo"] for s in d["sinais"]] == ["INSTITUICAO_NAO_ENCONTRADA"]


def test_sinais_da_empresa_somam_com_os_da_instituicao(fonte):
    fonte.resposta = {**BRUTO_PJ, "descricao_situacao_cadastral": "BAIXADA"}
    with TestClient(criar_app(Config(), fonte=fonte, hoje=lambda: HOJE)) as c:
        d = post(c, ispb="99999999", lang="en").json()
    assert [s["codigo"] for s in d["sinais"]] == ["SITUACAO_NAO_ATIVA", "INSTITUICAO_NAO_ENCONTRADA"]
    assert d["pontuacao"] == 100 and d["nivel"] == "alto" and "not in the Central Bank" in d["sinais"][1]["mensagem"]


@pytest.mark.parametrize(
    "corpo",
    [{}, {"ispb": "00000000", "banco": "1"}, {"ispb": "123"}, {"banco": "1234"}, {"banco": "abc"}, {"ispb": "../x"}],
)
def test_instituicao_invalida_422(cliente, fonte, corpo):
    r = post(cliente, **corpo)
    assert r.status_code == 422 and r.json()["codigo"] == "instituicao_invalida" and fonte.chamadas == 0


def test_cnpj_invalido_422_e_campo_extra_rejeitado(cliente):
    r = cliente.post(URL, json={"cnpj": "123", "ispb": "00000000"})
    assert r.status_code == 422 and r.json()["codigo"] == "cnpj_invalido"
    assert cliente.post(URL, json={"cnpj": CNPJ_OK, "ispb": "00000000", "x": 1}).status_code == 422
    assert cliente.post(URL, json={"cnpj": "1" * 40, "ispb": "00000000"}).status_code == 422


def test_listas_vem_do_cache(cliente, fonte):
    post(cliente, ispb="00000000")
    post(cliente, banco="1")
    assert fonte.chamadas_listas == 2  # bancos + pix, uma vez só


def test_fonte_fora_do_ar_nao_inventa(fonte):
    class Parcial(FonteFalsa):
        async def bancos(self):
            raise FonteIndisponivel("x")

    app = criar_app(Config(), fonte=Parcial(resposta=dict(BRUTO_PJ)), hoje=lambda: HOJE)
    with TestClient(app) as c:
        r = post(c, ispb="00000000")
    assert r.status_code == 502 and r.json()["codigo"] == "fonte_indisponivel"


def test_limite_compartilhado_com_cnpj(fonte):
    app = criar_app(Config(limite_por_minuto=2), fonte=fonte, hoje=lambda: HOJE)
    with TestClient(app) as c:
        assert c.get(f"/v1/cnpj/{CNPJ_OK}/check").status_code == 200
        assert post(c, ispb="00000000").status_code == 200
        assert post(c, ispb="00000000").status_code == 429


def test_log_sem_ispb_nem_cnpj(cliente, caplog):
    with caplog.at_level(logging.DEBUG):
        post(cliente, ispb="00000000")
        post(cliente, ispb="99999999")
    log = "\n".join(r.getMessage() for r in caplog.records)
    for proibido in (CNPJ_OK, "00000000", "99999999", "testclient"):
        assert proibido not in log
    assert "POST /v1/pagamento/check 200" in log


def test_avaliar_sem_instituicao_nao_acrescenta_sinais():
    e = reduzir(CNPJ_OK, BRUTO_PJ)
    assert avaliar(e, HOJE).sinais == []
