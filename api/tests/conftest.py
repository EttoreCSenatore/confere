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


class FonteFalsa:
    """Substitui a BrasilAPI nos testes: conta chamadas e devolve o que for configurado."""

    def __init__(self, resposta=None, erro=None):
        self.resposta, self.erro, self.chamadas = resposta, erro, 0

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
