import logging

import pytest
from fastapi.testclient import TestClient

from confere.app import criar_app
from confere.brasilapi import FonteIndisponivel, NaoEncontrado
from confere.config import Config
from tests.conftest import CNPJ_OK, HOJE, FonteFalsa


def test_conferir_ok_e_privacidade(cliente):
    r = cliente.get(f"/v1/cnpj/{CNPJ_OK}/check")
    assert r.status_code == 200
    d = r.json()
    assert d["cnpj"] == "00.000.000/0001-91" and d["nivel"] == "sem_indicios" and d["sinais"] == []
    assert d["fonte"]["nome"] == "BrasilAPI" and "não é prova" in d["aviso"]
    e = d["empresa"]
    assert e["socios_total"] == 2 and e["socios_qualificacoes"] == ["Diretor", "Presidente"]
    corpo = r.text
    for proibido in ("FULANO", "BELTRANA", "***", "70040912", "SAUN", "contato@exemplo"):
        assert proibido not in corpo


def test_formatado_e_ingles(cliente):
    r = cliente.get("/v1/cnpj/00.000.000-0001-91/check", params={"lang": "en"})
    assert r.status_code == 200 and "not proof" in r.json()["aviso"]


def test_invalido_422_sem_chamar_fonte(cliente, fonte):
    r = cliente.get("/v1/cnpj/00000000000192/check")
    assert r.status_code == 422 and r.json()["codigo"] == "cnpj_invalido" and fonte.chamadas == 0


@pytest.mark.parametrize(
    ("erro", "status", "codigo"),
    [(NaoEncontrado("x"), 404, "nao_encontrado"), (FonteIndisponivel("x"), 502, "fonte_indisponivel")],
)
def test_erros_da_fonte(erro, status, codigo):
    app = criar_app(Config(), fonte=FonteFalsa(erro=erro), hoje=lambda: HOJE)
    with TestClient(app) as c:
        r = c.get(f"/v1/cnpj/{CNPJ_OK}/check")
    assert r.status_code == status and r.json()["codigo"] == codigo


def test_cache_evita_segunda_chamada(cliente, fonte):
    cliente.get(f"/v1/cnpj/{CNPJ_OK}/check")
    cliente.get(f"/v1/cnpj/{CNPJ_OK}/check")
    assert fonte.chamadas == 1


def test_limite_429_com_retry_after(fonte):
    app = criar_app(Config(limite_por_minuto=2), fonte=fonte, hoje=lambda: HOJE)
    with TestClient(app) as c:
        assert [c.get(f"/v1/cnpj/{CNPJ_OK}/check").status_code for _ in range(3)] == [200, 200, 429]
        r = c.get(f"/v1/cnpj/{CNPJ_OK}/check")
        assert r.json()["codigo"] == "limite_excedido" and int(r.headers["retry-after"]) >= 1


def test_proxy_confiavel_usa_ultimo_valor(fonte):
    app = criar_app(Config(limite_por_minuto=1, confiar_proxy=True), fonte=fonte, hoje=lambda: HOJE)
    with TestClient(app) as c:
        h1 = {"X-Forwarded-For": "9.9.9.9, 1.1.1.1"}  # o falso à esquerda não conta
        h2 = {"X-Forwarded-For": "8.8.8.8, 2.2.2.2"}
        assert c.get(f"/v1/cnpj/{CNPJ_OK}/check", headers=h1).status_code == 200
        assert c.get(f"/v1/cnpj/{CNPJ_OK}/check", headers=h2).status_code == 200
        assert c.get(f"/v1/cnpj/{CNPJ_OK}/check", headers={"X-Forwarded-For": "7.7.7.7, 1.1.1.1"}).status_code == 429


def test_cabecalhos_de_seguranca(cliente):
    r = cliente.get(f"/v1/cnpj/{CNPJ_OK}/check")
    assert r.headers["cache-control"] == "no-store" and r.headers["x-content-type-options"] == "nosniff"
    assert (
        r.headers["referrer-policy"] == "no-referrer" and "default-src 'none'" in r.headers["content-security-policy"]
    )


def test_docs_desligado_por_padrao_e_sem_cors(cliente):
    assert cliente.get("/docs").status_code == 404
    r = cliente.get(f"/v1/cnpj/{CNPJ_OK}/check", headers={"Origin": "https://outro.test"})
    assert "access-control-allow-origin" not in r.headers


def test_log_nao_tem_ip_nem_cnpj(cliente, caplog):
    with caplog.at_level(logging.DEBUG):
        cliente.get(f"/v1/cnpj/{CNPJ_OK}/check", headers={"User-Agent": "segredo-ua"})
        cliente.get("/v1/cnpj/00000000000192/check")
    log = "\n".join(r.getMessage() for r in caplog.records)
    assert "confere.acesso" in {r.name for r in caplog.records}
    for proibido in (CNPJ_OK, "00000000000192", "testclient", "127.0.0.1", "segredo-ua", "0001-91"):
        assert proibido not in log
    assert "/v1/cnpj/{cnpj}/check" in log


def test_chamada_real_a_fonte_nao_loga_o_cnpj(caplog):
    """O cliente httpx de produção (aqui com transporte simulado) não pode registrar a URL com o CNPJ."""
    from confere.brasilapi import BrasilApi
    from tests.conftest import BRUTO_PJ, json_resp, transporte

    app = criar_app(Config(), fonte=BrasilApi(transport=transporte(lambda r: json_resp(BRUTO_PJ))), hoje=lambda: HOJE)
    with caplog.at_level(logging.DEBUG), TestClient(app) as c:
        assert c.get(f"/v1/cnpj/{CNPJ_OK}/check").status_code == 200
    assert CNPJ_OK not in "\n".join(r.getMessage() for r in caplog.records)


def test_docs_ligado_so_por_configuracao_e_sem_csp_restritiva(fonte):
    app = criar_app(Config(docs=True), fonte=fonte, hoje=lambda: HOJE)
    with TestClient(app) as c:
        r = c.get("/docs")
        assert r.status_code == 200 and "content-security-policy" not in r.headers
        assert "default-src" in c.get(f"/v1/cnpj/{CNPJ_OK}/check").headers["content-security-policy"]
