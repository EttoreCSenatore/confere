"""Instituições financeiras: cruza os bancos (código COMPE e ISPB) com os participantes do Pix.

Usa as mesmas listas do explorador (`dados.py`), então vale a mesma regra: cópia local recente, senão a fonte.
Só guarda o necessário (ISPB, nome, código, modalidade, tipo); logotipos e endereços são descartados, inclusive
porque o logotipo da fonte vem de uma CDN de terceiros."""

import re

from pydantic import BaseModel

from confere.dados import Dados

ISPB = re.compile(r"^[0-9]{8}$")
COMPE = re.compile(r"^[0-9]{1,3}$")


class Instituicao(BaseModel):
    ispb: str
    nome: str
    codigo_compe: int | None
    participa_pix: bool
    modalidade_pix: str | None
    tipo_participacao: str | None


async def buscar_instituicao(dados: Dados, *, ispb: str | None = None, codigo: int | None = None) -> Instituicao | None:
    """Procura por ISPB ou por código COMPE. None se nenhuma das listas conhece a instituição."""
    bancos = (await dados.registros("bancos")).registros
    pix = (await dados.registros("pix")).registros
    banco = next((b for b, _ in bancos if (b["ispb"] == ispb if ispb else b["codigo_compe"] == codigo)), None)
    ispb = ispb or (banco or {}).get("ispb")
    participante = next((p for p, _ in pix if p["ispb"] == ispb), None) if ispb else None
    if banco is None and participante is None:
        return None
    return Instituicao(
        ispb=str(ispb),
        nome=str((participante or {}).get("nome") or (banco or {}).get("nome") or ""),
        codigo_compe=(banco or {}).get("codigo_compe"),
        participa_pix=participante is not None,
        modalidade_pix=(participante or {}).get("modalidade"),
        tipo_participacao=(participante or {}).get("tipo_participacao"),
    )
