import json
from datetime import date

import httpx
import pytest
from fastapi.testclient import TestClient

from confere.app import criar_app
from confere.brasilapi import BrasilApi
from confere.config import Config

HOJE = date(2026, 11, 17)
CNPJ_OK = "00000000000191"  # Banco do Brasil (público)

BRUTO_PJ = {
    "cnpj": CNPJ_OK,
    "razao_social": "BANCO EXEMPLO S.A.",
    "nome_fantasia": "BANCO EXEMPLO",
    "descricao_situacao_cadastral": "ATIVA",
    "data_situacao_cadastral": "2005-11-03",
    "situacao_especial": "",
    "data_inicio_atividade": "1966-08-01",
    "codigo_natureza_juridica": 2038,
    "natureza_juridica": "Sociedade de Economia Mista",
    "porte": "DEMAIS",
    "capital_social": 120000000000,
    "opcao_pelo_simples": False,
    "opcao_pelo_mei": False,
    "cnae_fiscal": 6422100,
    "cnae_fiscal_descricao": "Bancos múltiplos, com carteira comercial",
    "municipio": "BRASILIA",
    "uf": "DF",
    "cep": "70040912",
    "logradouro": "SAUN QUADRA 5",
    "email": "contato@exemplo.test",
    "ddd_telefone_1": "6134939002",
    "qsa": [
        {"nome_socio": "FULANO DE TAL SEGREDO", "qualificacao_socio": "Diretor", "cnpj_cpf_do_socio": "***550179**"},
        {"nome_socio": "BELTRANA SIGILOSA", "qualificacao_socio": "Presidente", "cnpj_cpf_do_socio": "***842999**"},
    ],
}


BANCOS = [
    {
        "ispb": "00000000",
        "name": "BCO DO BRASIL S.A.",
        "code": 1,
        "fullName": "Banco do Brasil S.A.",
        "logo_url": "https://cdn.jsdelivr.net/x.svg",
        "headquarters_address": {"street": "SAUN"},
    },
    {"ispb": "11111111", "name": "BANCO SEM PIX S.A.", "code": 999},
    {"ispb": "22222222", "name": "BANCO SEM CODIGO", "code": None},
]
PIX = [
    {
        "ispb": "00000000",
        "nome": "BCO DO BRASIL S.A.",
        "nome_reduzido": "BB",
        "modalidade_participacao": "Provedor de Conta Transacional",
        "tipo_participacao": "Direta",
        "inicio_operacao": None,
    },
    {
        "ispb": "33333333",
        "nome": "FINTECH IP S.A.",
        "nome_reduzido": "FINTECH",
        "modalidade_participacao": "Provedor de Conta Transacional",
        "tipo_participacao": "Indireta",
        "inicio_operacao": None,
    },
]


UFS_FALSAS = [
    {"id": 35, "sigla": "SP", "nome": "São Paulo", "regiao": {"nome": "Sudeste"}, "capital": "São Paulo"},
    {"id": 33, "sigla": "RJ", "nome": "Rio de Janeiro", "regiao": {"nome": "Sudeste"}, "capital": "Rio de Janeiro"},
]
MUNICIPIOS_FALSOS = {
    "SP": [
        {"nome": "SÃO PAULO", "codigo_ibge": "3550308"},
        {"nome": "CAMPINAS", "codigo_ibge": "3509502"},
        {"nome": "=CMD()", "codigo_ibge": "1"},
    ]
}
NCM_FALSO = [
    {
        "codigo": "09.01",
        "descricao": "Café, mesmo torrado ou descafeinado",
        "data_inicio": "2022-04-01",
        "data_fim": "9999-12-31",
    },
    {"codigo": "0901.11.10", "descricao": "- - - Café em grão", "data_inicio": "2022-04-01", "data_fim": "9999-12-31"},
    {"codigo": "01", "descricao": "Animais vivos.", "data_inicio": "2022-04-01", "data_fim": "9999-12-31"},
]
CORRETORAS_FALSAS = [
    {
        "cnpj": "11222333000181",
        "nome_social": "ALFA CORRETORA S.A.",
        "nome_comercial": "ALFA",
        "status": "EM FUNCIONAMENTO NORMAL",
        "email": "contato@alfa.test",
        "telefone": "1199999999",
        "cep": "01000000",
        "logradouro": "RUA SECRETA 1",
        "uf": "SP",
        "municipio": "SAO PAULO",
        "codigo_cvm": "123",
        "data_registro": "1990-01-01",
        "valor_patrimonio_liquido": "1.0",
    },
    {
        "cnpj": "00000000000191",
        "nome_social": "BETA DTVM LTDA",
        "nome_comercial": None,
        "status": "CANCELADA",
        "email": "beta@beta.test",
        "telefone": "2188888888",
        "uf": "RJ",
        "municipio": "RIO DE JANEIRO",
        "codigo_cvm": "456",
        "data_registro": "2001-02-03",
    },
]


class FonteFalsa:
    """Substitui a BrasilAPI nos testes: conta chamadas e devolve o que for configurado."""

    def __init__(self, resposta=None, erro=None, bancos=None, pix=None):
        self.resposta, self.erro, self.chamadas = resposta, erro, 0
        self._bancos, self._pix, self.chamadas_listas = (
            (BANCOS if bancos is None else bancos),
            (PIX if pix is None else pix),
            0,
        )

    async def bancos(self):
        self.chamadas_listas += 1
        if self.erro:
            raise self.erro
        return self._bancos

    async def participantes_pix(self):
        self.chamadas_listas += 1
        if self.erro:
            raise self.erro
        return self._pix

    async def _lista(self, dados):
        self.chamadas_listas += 1
        if self.erro:
            raise self.erro
        return dados

    async def ufs(self):
        return await self._lista(UFS_FALSAS)

    async def municipios(self, uf):
        return await self._lista(MUNICIPIOS_FALSOS.get(uf, []))

    async def ncm(self):
        return await self._lista(NCM_FALSO)

    async def corretoras(self):
        return await self._lista(CORRETORAS_FALSAS)

    async def cnpj(self, cnpj):
        self.chamadas += 1
        if self.erro:
            raise self.erro
        return self.resposta

    async def fechar(self):
        pass


@pytest.fixture
def fonte():
    return FonteFalsa(resposta=dict(BRUTO_PJ))


@pytest.fixture
def cliente(fonte):
    app = criar_app(Config(), fonte=fonte, hoje=lambda: HOJE)
    with TestClient(app) as c:
        yield c


def transporte(handler):
    return httpx.MockTransport(handler)


def json_resp(dados, status=200):
    return httpx.Response(status, content=json.dumps(dados))


__all__ = ["BRUTO_PJ", "CNPJ_OK", "HOJE", "BrasilApi", "FonteFalsa", "json_resp", "transporte"]
