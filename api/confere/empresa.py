"""Reduz a resposta da BrasilAPI ao mínimo necessário (minimização, LGPD art. 6º, III).

Nomes de sócios nunca saem daqui. Para empresário individual e MEI, o nome empresarial costuma ser o nome
da pessoa seguido do CPF: é omitido, junto com CEP, logradouro e contatos."""

from datetime import date

from pydantic import BaseModel

NATUREZA_EMPRESARIO_INDIVIDUAL = 2135


class Cnae(BaseModel):
    codigo: int | None
    descricao: str | None


class Empresa(BaseModel):
    cnpj: str
    individual: bool
    razao_social: str | None
    nome_fantasia: str | None
    situacao: str
    data_situacao: date | None
    situacao_especial: str
    data_abertura: date | None
    natureza_codigo: int | None
    natureza_juridica: str | None
    porte: str | None
    capital_social: float | None
    optante_simples: bool | None
    mei: bool | None
    cnae_principal: Cnae
    municipio: str | None
    uf: str | None
    contato_publico: bool
    socios_total: int
    socios_qualificacoes: list[str]


def _data(valor: object) -> date | None:
    try:
        return date.fromisoformat(str(valor)) if valor else None
    except ValueError:
        return None


def _texto(valor: object) -> str | None:
    texto = str(valor).strip() if valor not in (None, "") else ""
    return texto or None


def reduzir(cnpj: str, bruto: dict) -> Empresa:
    codigo = bruto.get("codigo_natureza_juridica")
    mei = bruto.get("opcao_pelo_mei")
    individual = codigo == NATUREZA_EMPRESARIO_INDIVIDUAL or mei is True
    qsa = bruto.get("qsa") or []
    qualificacoes = sorted({q for s in qsa if (q := _texto(s.get("qualificacao_socio")))})
    capital = bruto.get("capital_social")
    return Empresa(
        cnpj=cnpj,
        individual=individual,
        razao_social=None if individual else _texto(bruto.get("razao_social")),
        nome_fantasia=None if individual else _texto(bruto.get("nome_fantasia")),
        situacao=(_texto(bruto.get("descricao_situacao_cadastral")) or "DESCONHECIDA").upper(),
        data_situacao=_data(bruto.get("data_situacao_cadastral")),
        situacao_especial=_texto(bruto.get("situacao_especial")) or "",
        data_abertura=_data(bruto.get("data_inicio_atividade")),
        natureza_codigo=codigo if isinstance(codigo, int) else None,
        natureza_juridica=_texto(bruto.get("natureza_juridica")),
        porte=_texto(bruto.get("porte")),
        capital_social=None if individual or not isinstance(capital, int | float) else float(capital),
        optante_simples=bruto.get("opcao_pelo_simples"),
        mei=mei,
        cnae_principal=Cnae(
            codigo=bruto.get("cnae_fiscal") if isinstance(bruto.get("cnae_fiscal"), int) else None,
            descricao=_texto(bruto.get("cnae_fiscal_descricao")),
        ),
        municipio=_texto(bruto.get("municipio")),
        uf=_texto(bruto.get("uf")),
        contato_publico=bool(_texto(bruto.get("email")) or _texto(bruto.get("ddd_telefone_1"))),
        socios_total=len(qsa),
        socios_qualificacoes=qualificacoes,
    )
