"""Diretório de instituições: cruza a lista de bancos (código COMPE e ISPB) com os participantes do Pix.

Só guarda o necessário (ISPB, nome, código, modalidade, tipo); logotipos e endereços da fonte são descartados,
inclusive porque o logotipo vem de uma CDN de terceiros."""

import re

from pydantic import BaseModel

from confere.brasilapi import BrasilApi
from confere.cache import CacheTTL

ISPB = re.compile(r"^[0-9]{8}$")
COMPE = re.compile(r"^[0-9]{1,3}$")


class Instituicao(BaseModel):
    ispb: str
    nome: str
    codigo_compe: int | None
    participa_pix: bool
    modalidade_pix: str | None
    tipo_participacao: str | None


class Diretorio:
    def __init__(self, fonte: BrasilApi, cache: CacheTTL) -> None:
        self._fonte = fonte
        self._cache = cache

    async def _listas(self) -> tuple[list, list]:
        bancos = self._cache.obter("bancos")
        if bancos is None:
            bancos = await self._fonte.bancos()
            self._cache.guardar("bancos", bancos)
        pix = self._cache.obter("pix")
        if pix is None:
            pix = await self._fonte.participantes_pix()
            self._cache.guardar("pix", pix)
        return bancos, pix

    async def buscar(self, *, ispb: str | None = None, codigo: int | None = None) -> Instituicao | None:
        """Procura por ISPB ou por código COMPE. None se nenhuma das listas conhece a instituição."""
        bancos, pix = await self._listas()
        banco = next(
            (b for b in bancos if isinstance(b, dict) and (b.get("ispb") == ispb if ispb else b.get("code") == codigo)),
            None,
        )
        ispb = ispb or (banco or {}).get("ispb")
        participante = next((p for p in pix if isinstance(p, dict) and p.get("ispb") == ispb), None) if ispb else None
        if banco is None and participante is None:
            return None
        code = (banco or {}).get("code")
        nome = (participante or {}).get("nome") or (banco or {}).get("name") or ""
        return Instituicao(
            ispb=str(ispb),
            nome=str(nome),
            codigo_compe=code if isinstance(code, int) else None,
            participa_pix=participante is not None,
            modalidade_pix=(participante or {}).get("modalidade_participacao"),
            tipo_participacao=(participante or {}).get("tipo_participacao"),
        )
