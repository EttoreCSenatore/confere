import logging

import pytest
from fastapi.testclient import TestClient

from confere.app import criar_app
from confere.brasilapi import FonteIndisponivel
from confere.config import Config
from confere.dados import filtrar, para_csv, plano
from tests.conftest import HOJE, FonteFalsa


def itens(r):
    assert r.status_code == 200, r.text
    return r.json()["itens"]


def test_plano_tira_acento_e_caixa():
    assert plano("São PAULO") == "sao paulo" and plano("Café") == "cafe"


def test_bancos_busca_por_nome_codigo_e_ispb(cliente):
    todos = cliente.get("/v1/dados/bancos").json()
    assert todos["total"] == 3 and todos["colunas"][0] == "codigo_compe"
    # ordenação: com código primeiro, sem código por último
    assert [b["codigo_compe"] for b in todos["itens"]] == [1, 999, None]
    assert [b["ispb"] for b in itens(cliente.get("/v1/dados/bancos", params={"q": "brasil"}))] == ["00000000"]
    assert [b["ispb"] for b in itens(cliente.get("/v1/dados/bancos", params={"q": "999"}))] == ["11111111"]
    assert [b["ispb"] for b in itens(cliente.get("/v1/dados/bancos", params={"q": "22222222"}))] == ["22222222"]
    bb = todos["itens"][0]
    assert bb["participa_pix"] is True and todos["itens"][1]["participa_pix"] is False
    assert "logo" not in str(todos) and "headquarters" not in str(todos)


def test_pix_lista_participantes(cliente):
    r = cliente.get("/v1/dados/pix", params={"q": "fintech"})
    assert [p["ispb"] for p in itens(r)] == ["33333333"]


def test_municipios_exigem_uf(cliente):
    r = cliente.get("/v1/dados/municipios")
    assert r.status_code == 422 and r.json()["codigo"] == "filtro_invalido"
    assert cliente.get("/v1/dados/municipios", params={"uf": "XX"}).json()["codigo"] == "filtro_invalido"
    nomes = [m["nome"] for m in itens(cliente.get("/v1/dados/municipios", params={"uf": "sp", "q": "sao"}))]
    assert nomes == ["SÃO PAULO"]  # uf em minúsculas é aceita; busca ignora acento


def test_ncm_busca_com_e_sem_pontos_e_por_palavras(cliente):
    assert [n["codigo"] for n in itens(cliente.get("/v1/dados/ncm", params={"q": "0901"}))] == ["09.01", "0901.11.10"]
    assert [n["codigo"] for n in itens(cliente.get("/v1/dados/ncm", params={"q": "café grão"}))] == ["0901.11.10"]
    assert itens(cliente.get("/v1/dados/ncm", params={"q": "inexistente"})) == []


def test_corretoras_minimiza_filtra_e_formata(cliente):
    r = cliente.get("/v1/dados/corretoras")
    assert r.status_code == 200
    for proibido in ("contato@alfa", "beta@beta", "1199999999", "RUA SECRETA", "01000000", "patrimonio"):
        assert proibido not in r.text
    assert r.json()["itens"][0]["cnpj"] == "11.222.333/0001-81"
    assert [c["uf"] for c in itens(cliente.get("/v1/dados/corretoras", params={"uf": "RJ"}))] == ["RJ"]
    assert [c["codigo_cvm"] for c in itens(cliente.get("/v1/dados/corretoras", params={"status": "cancelada"}))] == [
        "456"
    ]
    assert [c["codigo_cvm"] for c in itens(cliente.get("/v1/dados/corretoras", params={"q": "11222333000181"}))] == [
        "123"
    ]


def test_filtros_que_nao_valem_para_o_conjunto(cliente):
    assert cliente.get("/v1/dados/ncm", params={"uf": "SP"}).json()["codigo"] == "filtro_invalido"
    assert cliente.get("/v1/dados/bancos", params={"status": "x"}).json()["codigo"] == "filtro_invalido"
    assert cliente.get("/v1/dados/inexistente").json()["codigo"] == "conjunto_desconhecido"


def test_paginacao_e_limites(cliente):
    r = cliente.get("/v1/dados/bancos", params={"limite": 2, "offset": 1}).json()
    assert r["total"] == 3 and len(r["itens"]) == 2 and r["offset"] == 1 and r["limite"] == 2
    assert itens(cliente.get("/v1/dados/bancos", params={"offset": 99})) == []
    for ruim in ({"limite": 0}, {"limite": 201}, {"offset": -1}, {"q": "x" * 81}, {"formato": "xml"}):
        r = cliente.get("/v1/dados/bancos", params=ruim)
        assert r.status_code == 422 and r.json()["codigo"] == "requisicao_invalida"


def test_erro_de_validacao_nao_ecoa_o_valor_enviado(cliente):
    segredo = "x" * 81 + "SEGREDO"
    r = cliente.get("/v1/dados/bancos", params={"q": segredo})
    assert "SEGREDO" not in r.text and r.json()["campos"] == ["q"]
    r = cliente.post("/v1/pagamento/check", json={"cnpj": "1" * 40, "ispb": "00000000"})
    assert "1111111111" not in r.text and r.json()["codigo"] == "requisicao_invalida"


def test_csv_com_bom_cabecalho_e_sem_injecao_de_formula(cliente):
    r = cliente.get("/v1/dados/municipios", params={"uf": "SP", "formato": "csv"})
    assert r.status_code == 200 and r.headers["content-type"] == "text/csv; charset=utf-8"
    assert r.headers["content-disposition"] == 'attachment; filename="confere-municipios.csv"'
    assert r.content.startswith(b"\xef\xbb\xbf")
    linhas = r.content.decode("utf-8-sig").split("\r\n")
    assert linhas[0] == "codigo_ibge,nome,uf"
    assert "3550308,SÃO PAULO,SP" in linhas
    assert "1,'=CMD(),SP" in linhas  # célula que começa com "=" ganha apóstrofo
    ncm = cliente.get("/v1/dados/ncm", params={"formato": "csv", "q": "grão"}).content.decode("utf-8-sig")
    assert "'- - - Café em grão" in ncm  # "-" também é prefixo perigoso


def test_csv_exporta_tudo_do_filtro_sem_paginar(cliente):
    r = cliente.get("/v1/dados/bancos", params={"formato": "csv", "limite": 1})
    assert len(r.content.decode("utf-8-sig").strip().split("\r\n")) == 4  # cabeçalho + 3


def test_booleano_no_csv():
    assert b"true" in para_csv(
        "bancos", [{"codigo_compe": 1, "ispb": "0", "nome": "x", "nome_completo": "y", "participa_pix": True}]
    )


def test_filtrar_exige_todas_as_palavras():
    regs = [({"a": 1}, "cafe em grao"), ({"a": 2}, "cafe torrado")]
    assert filtrar(regs, "cafe grao") == [{"a": 1}]
    assert len(filtrar(regs, "")) == 2


def test_listas_vem_do_cache_e_ufs(cliente, fonte):
    for _ in range(3):
        cliente.get("/v1/dados/ncm", params={"q": "cafe"})
    assert fonte.chamadas_listas == 1
    ufs = cliente.get("/v1/dados/ufs").json()["itens"]
    assert [u["sigla"] for u in ufs] == ["RJ", "SP"]  # ordenadas por sigla
    assert ufs[1] == {"sigla": "SP", "nome": "São Paulo", "regiao": "Sudeste", "capital": "São Paulo"}
    cliente.get("/v1/dados/municipios", params={"uf": "SP"})
    cliente.get("/v1/dados/municipios", params={"uf": "SP", "q": "a"})
    assert fonte.chamadas_listas == 3  # ncm, ufs, municipios SP (uma vez cada)


def test_fonte_fora_do_ar_da_502(fonte):
    app = criar_app(Config(), fonte=FonteFalsa(erro=FonteIndisponivel("x")), hoje=lambda: HOJE)
    with TestClient(app) as c:
        r = c.get("/v1/dados/ncm")
    assert r.status_code == 502 and r.json()["codigo"] == "fonte_indisponivel"


def test_limite_de_taxa_vale_para_dados(fonte):
    app = criar_app(Config(limite_por_minuto=2), fonte=fonte, hoje=lambda: HOJE)
    with TestClient(app) as c:
        assert [c.get("/v1/dados/bancos").status_code for _ in range(3)] == [200, 200, 429]


def test_log_nao_registra_a_busca(cliente, caplog):
    with caplog.at_level(logging.DEBUG):
        cliente.get("/v1/dados/corretoras", params={"q": "busca-secreta-123", "uf": "SP"})
    log = "\n".join(r.getMessage() for r in caplog.records)
    assert "busca-secreta-123" not in log and "/v1/dados/{conjunto}" in log


@pytest.mark.anyio
async def test_downloads_simultaneos_baixam_uma_vez():
    import asyncio

    from confere.cache import CacheTTL
    from confere.dados import Dados

    class Lenta(FonteFalsa):
        async def ncm(self):
            await asyncio.sleep(0.05)
            return await super().ncm()

    fonte = Lenta()
    d = Dados(fonte, CacheTTL(60))
    await asyncio.gather(*(d.registros("ncm") for _ in range(5)))
    assert fonte.chamadas_listas == 1
