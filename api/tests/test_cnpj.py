import pytest

from confere import cnpj


@pytest.mark.parametrize("c", ["00000000000191", "00.000.000/0001-91", "11222333000181", "11.222.333/0001-81"])
def test_validos(c):
    assert cnpj.valido(c)


@pytest.mark.parametrize(
    "c",
    [
        "",
        "123",
        "00000000000192",
        "11111111111111",
        "0000000000019",
        "000000000001911",
        "ABCDEFGHIJKLMN",
        "00000000000A91",
    ],
)
def test_invalidos(c):
    assert not cnpj.valido(c)


def test_alfanumerico_dv_calculado():
    base = "12ABC34501DE"
    d1 = cnpj._digito(base)
    d2 = cnpj._digito(base + str(d1))
    assert cnpj.valido(f"{base}{d1}{d2}")
    assert not cnpj.valido(f"{base}{(d1 + 1) % 10}{d2}")
    assert cnpj.valido(f"{base.lower()}{d1}{d2}")  # minúsculas são normalizadas


def test_formatar():
    assert cnpj.formatar("00000000000191") == "00.000.000/0001-91"
