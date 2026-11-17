"""Motor de indícios. Regras simples, públicas e explicáveis: cada sinal traz código, peso, texto e a regra
que o gerou. Não há modelo opaco, lista negra nem decisão automatizada: o resultado é uma dica, não prova.

Ausência de sinais NÃO significa "seguro": só que os dados públicos não mostram indícios."""

from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel

from confere.empresa import Empresa

# código -> (gravidade, peso, {idioma: (mensagem, regra)})
_CATALOGO: dict[str, tuple[str, int, dict[str, tuple[str, str]]]] = {
    "SITUACAO_NAO_ATIVA": (
        "alto",
        60,
        {
            "pt-BR": ("A situação cadastral não é ATIVA.", "Situação cadastral diferente de ATIVA na Receita Federal."),
            "en": (
                "The registration status is not ACTIVE.",
                "Registration status other than ATIVA at Receita Federal.",
            ),
        },
    ),
    "EMPRESA_RECEM_ABERTA": (
        "alto",
        40,
        {
            "pt-BR": ("Empresa aberta há menos de 30 dias.", "Data de início de atividade com menos de 30 dias."),
            "en": ("Company opened less than 30 days ago.", "Activity start date less than 30 days ago."),
        },
    ),
    "EMPRESA_NOVA": (
        "atencao",
        25,
        {
            "pt-BR": ("Empresa aberta há menos de 6 meses.", "Início de atividade entre 30 e 179 dias atrás."),
            "en": ("Company opened less than 6 months ago.", "Activity start between 30 and 179 days ago."),
        },
    ),
    "SITUACAO_ESPECIAL": (
        "atencao",
        20,
        {
            "pt-BR": ("Há uma situação especial registrada.", "Campo de situação especial preenchido no cadastro."),
            "en": ("A special status is on record.", "Special-status field filled in the registry."),
        },
    ),
    "DADOS_INCOMPLETOS": (
        "atencao",
        15,
        {
            "pt-BR": ("Faltam dados básicos no cadastro.", "Data de início de atividade ausente na resposta."),
            "en": ("Basic registry data is missing.", "Activity start date missing in the response."),
        },
    ),
    "SEM_CONTATO_PUBLICO": (
        "atencao",
        10,
        {
            "pt-BR": ("Sem e-mail nem telefone públicos no cadastro.", "Nenhum e-mail ou telefone no cadastro."),
            "en": ("No public e-mail or phone in the registry.", "No e-mail or phone in the registry."),
        },
    ),
    "QUADRO_SOCIETARIO_VAZIO": (
        "atencao",
        10,
        {
            "pt-BR": ("Quadro de sócios vazio.", "Pessoa jurídica privada sem sócios ou administradores listados."),
            "en": ("Empty list of partners.", "Private legal entity with no partners or administrators listed."),
        },
    ),
    "EMPRESARIO_INDIVIDUAL": (
        "info",
        0,
        {
            "pt-BR": (
                "Empresário individual ou MEI: o CNPJ identifica uma pessoa. Nome e endereço foram omitidos.",
                "Natureza jurídica 2135 ou opção pelo MEI. Só mostramos o necessário (LGPD).",
            ),
            "en": (
                "Sole proprietor or MEI: the CNPJ identifies a person. Name and address were omitted.",
                "Legal nature 2135 or MEI option. We only show what is needed (LGPD).",
            ),
        },
    ),
}

IDIOMAS = ("pt-BR", "en")
LIMIAR_ATENCAO = 15
LIMIAR_ALTO = 50


class Sinal(BaseModel):
    codigo: str
    gravidade: str
    peso: int
    mensagem: str
    regra: str


@dataclass(frozen=True)
class Avaliacao:
    sinais: list[Sinal]
    pontuacao: int
    nivel: str  # sem_indicios | atencao | alto


def _sinal(codigo: str, idioma: str) -> Sinal:
    gravidade, peso, textos = _CATALOGO[codigo]
    mensagem, regra = textos.get(idioma, textos["pt-BR"])
    return Sinal(codigo=codigo, gravidade=gravidade, peso=peso, mensagem=mensagem, regra=regra)


def codigos(e: Empresa, hoje: date) -> list[str]:
    """Códigos dos sinais aplicáveis. Função pura: o mesmo cadastro e a mesma data dão o mesmo resultado."""
    achados: list[str] = []
    if e.situacao != "ATIVA":
        achados.append("SITUACAO_NAO_ATIVA")
    if e.data_abertura is None:
        achados.append("DADOS_INCOMPLETOS")
    else:
        idade = (hoje - e.data_abertura).days
        if 0 <= idade < 30:
            achados.append("EMPRESA_RECEM_ABERTA")
        elif 30 <= idade < 180:
            achados.append("EMPRESA_NOVA")
    if e.situacao_especial:
        achados.append("SITUACAO_ESPECIAL")
    if not e.contato_publico:
        achados.append("SEM_CONTATO_PUBLICO")
    publica = e.natureza_codigo is not None and 1000 <= e.natureza_codigo < 2000
    if not e.individual and not publica and e.socios_total == 0:
        achados.append("QUADRO_SOCIETARIO_VAZIO")
    if e.individual:
        achados.append("EMPRESARIO_INDIVIDUAL")
    return achados


def avaliar(e: Empresa, hoje: date, idioma: str = "pt-BR") -> Avaliacao:
    sinais = [_sinal(c, idioma) for c in codigos(e, hoje)]
    sinais.sort(key=lambda s: -s.peso)
    pontuacao = min(100, sum(s.peso for s in sinais))
    nivel = "alto" if pontuacao >= LIMIAR_ALTO else "atencao" if pontuacao >= LIMIAR_ATENCAO else "sem_indicios"
    return Avaliacao(sinais=sinais, pontuacao=pontuacao, nivel=nivel)
