"""Dados abertos: bancos, participantes do Pix, municípios (IBGE), NCM e corretoras (CVM).

De onde vêm as listas, nesta ordem:
1. **Cópia local** (`confere/snapshots/*.json.gz`, atualizada toda semana), se tiver até `snapshot_max_dias` dias:
   nenhuma chamada de rede, então não depende da BrasilAPI e nada sai do servidor;
2. **BrasilAPI**, se a cópia estiver velha ou não existir;
3. a cópia **velha**, marcada `desatualizado`, se a BrasilAPI falhar.

A busca roda aqui, na memória: o texto digitado nunca é repassado a ninguém. Só ficam os campos úteis
(minimização): das corretoras saem e-mail, telefone e endereço, e a cópia no repositório já nasce assim."""

import asyncio
import csv
import gzip
import io
import json
import unicodedata
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date
from importlib import resources
from pathlib import Path
from typing import Any

from confere import cnpj as cnpj_mod
from confere.brasilapi import BrasilApi, FonteIndisponivel
from confere.cache import CacheTTL

Linha = dict[str, Any]
Registro = tuple[Linha, str]  # (linha, texto de busca já normalizado)

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
# Em cópia local: os cinco conjuntos mais as UFs (usadas nos filtros).
ARQUIVOS = (*CONJUNTOS, "ufs")
DIR_PADRAO: Path | None = None  # os testes apontam para uma pasta vazia


def plano(texto: object) -> str:
    """Minúsculas e sem acento, para busca tolerante (cafe acha Café)."""
    sem = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in sem if not unicodedata.combining(c)).casefold()


def texto_busca(linha: Linha) -> str:
    """Texto pesquisável de uma linha: todos os valores, e também sem `.`, `/`, `-` (NCM 0901 acha 09.01)."""
    partes: list[str] = []
    for v in linha.values():
        if v is None or isinstance(v, bool):
            continue
        t = plano(v)
        partes.append(t)
        sem_pontuacao = t.replace(".", "").replace("/", "").replace("-", "")
        if sem_pontuacao != t:
            partes.append(sem_pontuacao)
    return " ".join(partes)


def _s(valor: object) -> str | None:
    texto = str(valor).strip() if valor not in (None, "") else ""
    return texto or None


# --- da resposta da fonte para linhas mínimas -------------------------------------------------------------------


def _banco(x: dict, ispbs_pix: set[str]) -> Linha:
    code = x.get("code")
    return {
        "codigo_compe": code if isinstance(code, int) else None,
        "ispb": _s(x.get("ispb")),
        "nome": _s(x.get("name")),
        "nome_completo": _s(x.get("fullName")),
        "participa_pix": _s(x.get("ispb")) in ispbs_pix,
    }


def _pix(x: dict) -> Linha:
    return {
        "ispb": _s(x.get("ispb")),
        "nome": _s(x.get("nome")),
        "modalidade": _s(x.get("modalidade_participacao")),
        "tipo_participacao": _s(x.get("tipo_participacao")),
    }


def _municipio(x: dict, uf: str) -> Linha:
    return {"codigo_ibge": _s(x.get("codigo_ibge")), "nome": _s(x.get("nome")), "uf": uf}


def _ncm(x: dict) -> Linha:
    return {
        "codigo": _s(x.get("codigo")),
        "descricao": _s(x.get("descricao")),
        "data_inicio": _s(x.get("data_inicio")),
        "data_fim": _s(x.get("data_fim")),
    }


def _corretora(x: dict) -> Linha:
    numero = cnpj_mod.normalizar(str(x.get("cnpj") or ""))
    return {
        "cnpj": cnpj_mod.formatar(numero) if len(numero) == 14 else None,
        "nome_social": _s(x.get("nome_social")),
        "nome_comercial": _s(x.get("nome_comercial")),
        "status": _s(x.get("status")),
        "uf": _s(x.get("uf")),
        "municipio": _s(x.get("municipio")),
        "codigo_cvm": _s(x.get("codigo_cvm")),
        "data_registro": _s(x.get("data_registro")),
    }


def _uf(x: dict) -> Linha:
    return {
        "sigla": _s(x.get("sigla")),
        "nome": _s(x.get("nome")),
        "regiao": _s((x.get("regiao") or {}).get("nome")),
        "capital": _s(x.get("capital")),
    }


# --- cópia local -------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Copia:
    gerado_em: date
    itens: Any  # lista de linhas (municípios: dict UF -> lista)


class Snapshots:
    """Lê as cópias locais (`*.json.gz`). Pasta ausente ou arquivo faltando = sem cópia (usa a fonte)."""

    def __init__(self, diretorio: Path | None = None) -> None:
        self._dir = diretorio or DIR_PADRAO
        self._cache: dict[str, Copia | None] = {}

    def _arquivo(self, nome: str):
        if self._dir is not None:
            return self._dir / f"{nome}.json.gz"
        return resources.files("confere") / "snapshots" / f"{nome}.json.gz"

    def obter(self, nome: str) -> Copia | None:
        if nome not in self._cache:
            try:
                bruto = json.loads(gzip.decompress(self._arquivo(nome).read_bytes()))
                self._cache[nome] = Copia(
                    date.fromisoformat(bruto["gerado_em"]), bruto.get("itens", bruto.get("por_uf"))
                )
            except (OSError, ValueError, KeyError, TypeError):
                self._cache[nome] = None
        return self._cache[nome]


def gravar_copia(diretorio: Path, nome: str, itens: Any, gerado_em: date) -> bool:
    """Grava a cópia de forma determinística (mesmo conteúdo = mesmos bytes). Devolve False se nada mudou."""
    chave = "por_uf" if nome == "municipios" else "itens"
    destino = diretorio / f"{nome}.json.gz"
    anterior = Snapshots(diretorio).obter(nome)
    if anterior is not None and anterior.itens == itens:
        return False  # só a data mudou: não gera diferença à toa
    corpo = json.dumps(
        {"gerado_em": gerado_em.isoformat(), "fonte": "BrasilAPI", chave: itens},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    destino.write_bytes(gzip.compress(corpo, compresslevel=9, mtime=0))
    return True


# --- fonte + cópia -----------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Lista:
    registros: list[Registro]
    origem: str  # "copia" ou "fonte"
    data: date  # da cópia, ou do dia em que foi baixado
    desatualizado: bool = False


def _registros(linhas: list[Linha]) -> list[Registro]:
    return [(linha, texto_busca(linha)) for linha in linhas]


class Dados:
    def __init__(
        self,
        fonte: BrasilApi,
        cache: CacheTTL,
        snapshots: Snapshots | None = None,
        max_dias: int = 14,
        hoje: Callable[[], date] = date.today,
    ) -> None:
        self._fonte = fonte
        self._cache = cache
        self._snapshots = snapshots if snapshots is not None else Snapshots()
        self._max_dias = max_dias
        self._hoje = hoje
        self._travas: dict[str, asyncio.Lock] = {}  # uma por lista: evita baixar 3 MB duas vezes em pedidos simultâneos

    # download da fonte -> linhas (também usado pelo script que atualiza as cópias)
    async def baixar(self, nome: str, uf: str | None = None) -> list[Linha]:
        f = self._fonte
        if nome == "bancos":
            ispbs = {linha["ispb"] for linha, _ in (await self._lista("pix")).registros}  # mesma regra de cópia/fonte
            return [_banco(x, ispbs) for x in await f.bancos() if isinstance(x, dict)]
        if nome == "pix":
            return [_pix(x) for x in await f.participantes_pix() if isinstance(x, dict)]
        if nome == "municipios":
            assert uf
            return [_municipio(x, uf) for x in await f.municipios(uf) if isinstance(x, dict)]
        if nome == "ncm":
            return [_ncm(x) for x in await f.ncm() if isinstance(x, dict)]
        if nome == "corretoras":
            return [_corretora(x) for x in await f.corretoras() if isinstance(x, dict)]
        if nome == "ufs":
            return [_uf(x) for x in await f.ufs() if isinstance(x, dict)]
        raise KeyError(nome)

    def _da_copia(self, nome: str, uf: str | None) -> tuple[list[Linha], date] | None:
        copia = self._snapshots.obter(nome)
        if copia is None:
            return None
        itens = copia.itens.get(uf) if nome == "municipios" and isinstance(copia.itens, dict) else copia.itens
        return (itens, copia.gerado_em) if isinstance(itens, list) else None

    async def _lista(self, nome: str, uf: str | None = None) -> Lista:
        chave = f"{nome}:{uf or ''}"
        pronto = self._cache.obter(chave)
        if pronto is not None:
            return pronto
        copia = self._da_copia(nome, uf) if self._max_dias > 0 else None
        if copia is not None and (self._hoje() - copia[1]).days <= self._max_dias:
            lista = Lista(_registros(copia[0]), "copia", copia[1])
        else:
            async with self._travas.setdefault(chave, asyncio.Lock()):
                pronto = self._cache.obter(chave)
                if pronto is not None:
                    return pronto
                try:
                    lista = Lista(_registros(await self.baixar(nome, uf)), "fonte", self._hoje())
                except FonteIndisponivel:
                    if copia is None:
                        raise
                    lista = Lista(_registros(copia[0]), "copia", copia[1], desatualizado=True)
        self._cache.guardar(chave, lista)
        return lista

    async def ufs(self) -> Lista:
        return await self._lista("ufs")

    async def registros(self, conjunto: str, uf: str | None = None) -> Lista:
        if conjunto not in CONJUNTOS:
            raise KeyError(conjunto)
        if conjunto == "municipios":
            assert uf
        return await self._lista(conjunto, uf if conjunto == "municipios" else None)


def filtrar(registros: list[Registro], q: str) -> list[Linha]:
    """Todas as palavras de `q` precisam aparecer (E), sem diferença de maiúsculas e acentos."""
    palavras = plano(q).split()
    return [linha for linha, texto in registros if all(p in texto for p in palavras)]


def ordenar(conjunto: str, linhas: list[Linha]) -> list[Linha]:
    chave = {
        "bancos": lambda r: (r["codigo_compe"] is None, r["codigo_compe"] or 0, r["nome"] or ""),
        "pix": lambda r: (plano(r["nome"] or ""), r["ispb"] or ""),
        "municipios": lambda r: plano(r["nome"] or ""),
        "ncm": lambda r: r["codigo"] or "",
        "corretoras": lambda r: plano(r["nome_social"] or ""),
        "ufs": lambda r: r["sigla"] or "",
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


def para_csv(conjunto: str, linhas: list[Linha]) -> bytes:
    saida = io.StringIO()
    escritor = csv.writer(saida, lineterminator="\r\n")
    colunas = COLUNAS[conjunto]
    escritor.writerow(colunas)
    for linha in linhas:
        escritor.writerow([_celula(linha.get(c)) for c in colunas])
    return b"\xef\xbb\xbf" + saida.getvalue().encode("utf-8")  # BOM: o Excel brasileiro abre acentos certos


Montar = Callable[[dict], Any]
Baixar = Callable[[], Awaitable[list]]
