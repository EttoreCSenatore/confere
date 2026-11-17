import httpx
import pytest

from confere.brasilapi import BrasilApi, FonteIndisponivel, NaoEncontrado
from tests.conftest import CNPJ_OK, json_resp, transporte


async def chamar(handler, cnpj=CNPJ_OK):
    api = BrasilApi(transport=transporte(handler))
    try:
        return await api.cnpj(cnpj)
    finally:
        await api.fechar()


@pytest.mark.anyio
async def test_sucesso_e_url_fixa():
    vistos = []

    def h(req):
        vistos.append(req)
        return json_resp({"cnpj": CNPJ_OK})

    assert await chamar(h) == {"cnpj": CNPJ_OK}
    assert str(vistos[0].url) == f"https://brasilapi.com.br/api/cnpj/v1/{CNPJ_OK}"
    assert set(vistos[0].headers) >= {"user-agent"} and "x-forwarded-for" not in vistos[0].headers


@pytest.mark.anyio
@pytest.mark.parametrize("status", [400, 404])
async def test_nao_encontrado(status):
    with pytest.raises(NaoEncontrado):
        await chamar(lambda r: json_resp({}, status))


@pytest.mark.anyio
async def test_5xx_tenta_de_novo_uma_vez():
    n = {"v": 0}

    def h(req):
        n["v"] += 1
        return json_resp({"cnpj": CNPJ_OK}) if n["v"] == 2 else json_resp({}, 503)

    assert (await chamar(h))["cnpj"] == CNPJ_OK and n["v"] == 2


@pytest.mark.anyio
async def test_falha_persistente_e_indisponivel():
    n = {"v": 0}

    def h(req):
        n["v"] += 1
        raise httpx.ConnectTimeout("x")

    with pytest.raises(FonteIndisponivel):
        await chamar(h)
    assert n["v"] == 2


@pytest.mark.anyio
@pytest.mark.parametrize("status", [429, 302, 403])
async def test_outros_status_sao_indisponivel(status):
    with pytest.raises(FonteIndisponivel):
        await chamar(lambda r: json_resp({}, status))


@pytest.mark.anyio
async def test_json_invalido_ou_lista():
    with pytest.raises(FonteIndisponivel):
        await chamar(lambda r: httpx.Response(200, content=b"<html>"))
    with pytest.raises(FonteIndisponivel):
        await chamar(lambda r: json_resp([1, 2]))


@pytest.mark.anyio
@pytest.mark.parametrize("ruim", ["../../x", "0000000000019", "00000000000191/../a", "00.000.000/0001-91", "abc"])
async def test_nunca_monta_url_com_texto_livre(ruim):
    chamadas = []
    with pytest.raises(ValueError):
        await chamar(lambda r: chamadas.append(r) or json_resp({}), ruim)
    assert chamadas == []
