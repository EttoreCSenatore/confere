"""Validação de CNPJ, inclusive o formato alfanumérico (vigente desde julho de 2026)."""

import re

_PESOS = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_FORMATO = re.compile(r"^[0-9A-Z]{12}[0-9]{2}$")


def normalizar(valor: str) -> str:
    """Tira pontos, barra, hífen e espaços e põe em maiúsculas."""
    return re.sub(r"[.\-/\s]", "", valor).upper()


def _digito(base: str) -> int:
    soma = sum((ord(c) - 48) * p for c, p in zip(base, _PESOS[-len(base) :], strict=True))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def valido(valor: str) -> bool:
    """Confere formato e dígitos verificadores. Não consulta nada: só aritmética."""
    c = normalizar(valor)
    if not _FORMATO.match(c) or len(set(c)) == 1:
        return False
    d1 = _digito(c[:12])
    d2 = _digito(c[:12] + str(d1))
    return c[12:] == f"{d1}{d2}"


def formatar(valor: str) -> str:
    c = normalizar(valor)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
