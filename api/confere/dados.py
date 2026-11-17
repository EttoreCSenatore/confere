"""Explorador de dados abertos: bancos, participantes do Pix, municípios (IBGE), NCM e corretoras (CVM).

As listas são buscadas inteiras na BrasilAPI e filtradas aqui, na memória: o texto que a pessoa digita nunca é
repassado à fonte. Só ficam os campos úteis (minimização): das corretoras saem e-mail, telefone e endereço."""

import asyncio
import csv
import io
import unicodedata
from collections.abc import Awaitable, Callable
from typing import Any

from confere import cnpj as cnpj_mod
from confere.brasilapi import BrasilApi
from confere.cache import CacheTTL

Registro = tuple[dict[str, Any], str]  # (linha, texto de busca já normalizado)

COLUNAS: dict[str, list[str]] = {
    "bancos": ["codigo_compe", "ispb", "nome", "nome_completo", "participa_pix"],
    "pix": ["ispb", "nome", "modalidade", "tipo_participacao"],
    "municipios": ["codigo_ibge", "nome", "uf"],
    "ncm": ["codigo", "descricao", "data_inicio", "data_fim"],
    "corretoras": ["cnpj", "nome_social", "nome_comercial", "status", "uf", "municipio", "codigo_cvm", "data_registro"],
}
CONJUNTOS = tuple(COLUNAS)
UFS = frozenset(
    [
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    ]
)


def plano(texto: object) -> str:
    """Minúsculas e sem acento, para busca tolerante (cafe acha Café)."""
    sem = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in sem if not unicodedata.combining(c)).casefold()


def _s(valor: object) -> str | None:
    texto = str(valor).strip() if valor not in (None, "") else ""
    return texto or None


def _busca(*partes: object) -> str:
    return " ".join(plano(p) for p in partes if p not in (None, ""))


def _banco(x: dict, pix: dict[str, dict]) -> Registro:
    code = x.get("code") if isinstance(x.get("code"), int) else None
    linha = {
        "codigo_compe": code,
        "ispb": _s(x.get("ispb")),
        "nome": _s(x.get("name")),
        "nome_completo": _s(x.get("fullName")),
        "participa_pix": str(x.get("ispb")) in pix,
    }
    return linha, _busca(code, linha["ispb"], linha["nome"], linha["nome_completo"])


def _pix(x: dict) -> Registro:
    linha = {
        "ispb": _s(x.get("ispb")),
        "nome": _s(x.get("nome")),
        "modalidade": _s(x.get("modalidade_participacao")),
        "tipo_participacao": _s(x.get("tipo_participacao")),
    }
    return linha, _busca(linha["ispb"], linha["nome"], x.get("nome_reduzido"), linha["modalidade"])


def _municipio(x: dict, uf: str) -> Registro:
    linha = {"codigo_ibge": _s(x.get("codigo_ibge")), "nome": _s(x.get("nome")), "uf": uf}
    return linha, _busca(linha["codigo_ibge"], linha["nome"])


def _ncm(x: dict) -> Registro:
    codigo = _s(x.get("codigo"))
    linha = {
        "codigo": codigo,
        "descricao": _s(x.get("descricao")),
        "data_inicio": _s(x.get("data_inicio")),
        "data_fim": _s(x.get("data_fim")),
    }
    return linha, _busca(codigo, (codigo or "").replace(".", ""), linha["descricao"])


def _corretora(x: dict) -> Registro:
    numero = cnpj_mod.normalizar(str(x.get("cnpj") or ""))
    linha = {
        "cnpj": cnpj_mod.formatar(numero) if len(numero) == 14 else None,
        "nome_social": _s(x.get("nome_social")),
        "nome_comercial": _s(x.get("nome_comercial")),
        "status": _s(x.get("status")),
        "uf": _s(x.get("uf")),
        "municipio": _s(x.get("municipio")),
        "codigo_cvm": _s(x.get("codigo_cvm")),
        "data_registro": _s(x.get("data_registro")),
    }
    return linha, _busca(numero, linha["nome_social"], linha["nome_comercial"], linha["codigo_cvm"], linha["municipio"])


class Dados:
    def __init__(self, fonte: BrasilApi, cache: CacheTTL) -> None:
        self._fonte = fonte
        self._cache = cache
        self._trava = asyncio.Lock()  # evita baixar 3 MB duas vezes quando chegam dois pedidos juntos

    async def _carregar(self, chave: str, baixar: Callable[[], Awaitable[list]], montar: Callable[[dict], Any]) -> list:
        itens = self._cache.obter(chave)
        if itens is None:
            async with self._trava:
                itens = self._cache.obter(chave)
                if itens is None:
                    itens = [montar(x) for x in await baixar() if isinstance(x, dict)]
                    self._cache.guardar(chave, itens)
        return itens

    async def ufs(self) -> list[dict]:
        def montar(x: dict) -> dict:
            return {
                "sigla": _s(x.get("sigla")),
                "nome": _s(x.get("nome")),
                "regiao": _s((x.get("regiao") or {}).get("nome")),
                "capital": _s(x.get("capital")),
            }

        return await self._carregar("ufs", self._fonte.ufs, montar)

    async def _pix_por_ispb(self) -> dict[str, dict]:
        lista = await self._carregar("pix_bruto", self._fonte.participantes_pix, lambda x: x)
        return {str(p.get("ispb")): p for p in lista}

    async def registros(self, conjunto: str, uf: str | None = None) -> list[Registro]:
        if conjunto == "bancos":
            pix = await self._pix_por_ispb()
            return await self._carregar("bancos", self._fonte.bancos, lambda x: _banco(x, pix))
        if conjunto == "pix":
            return await self._carregar("pix", self._fonte.participantes_pix, _pix)
        if conjunto == "municipios":
            assert uf
            return await self._carregar(f"mun:{uf}", lambda: self._fonte.municipios(uf), lambda x: _municipio(x, uf))
        if conjunto == "ncm":
            return await self._carregar("ncm", self._fonte.ncm, _ncm)
        if conjunto == "corretoras":
            return await self._carregar("corretoras", self._fonte.corretoras, _corretora)
        raise KeyError(conjunto)


def filtrar(registros: list[Registro], q: str) -> list[dict]:
    """Todas as palavras de `q` precisam aparecer (E), sem diferença de maiúsculas e acentos."""
    palavras = plano(q).split()
    return [linha for linha, texto in registros if all(p in texto for p in palavras)]


def ordenar(conjunto: str, linhas: list[dict]) -> list[dict]:
    chave = {
        "bancos": lambda r: (r["codigo_compe"] is None, r["codigo_compe"] or 0, r["nome"] or ""),
        "pix": lambda r: (plano(r["nome"] or ""), r["ispb"] or ""),
        "municipios": lambda r: plano(r["nome"] or ""),
        "ncm": lambda r: r["codigo"] or "",
        "corretoras": lambda r: plano(r["nome_social"] or ""),
    }[conjunto]
    return sorted(linhas, key=chave)


_PERIGOSOS = ("=", "+", "-", "@", "\t", "\r")


def _celula(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    texto = str(valor)
    # Planilhas executam células que começam com = + - @ (injeção de fórmula): prefixo ' (recomendação OWASP).
    return "'" + texto if texto.startswith(_PERIGOSOS) else texto


def para_csv(conjunto: str, linhas: list[dict]) -> bytes:
    saida = io.StringIO()
    escritor = csv.writer(saida, lineterminator="\r\n")
    colunas = COLUNAS[conjunto]
    escritor.writerow(colunas)
    for linha in linhas:
        escritor.writerow([_celula(linha.get(c)) for c in colunas])
    return b"\xef\xbb\xbf" + saida.getvalue().encode("utf-8")  # BOM: o Excel brasileiro abre acentos certos
