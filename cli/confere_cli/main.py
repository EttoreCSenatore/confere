"""Interface de linha de comando. Sem estado: não lê nem grava configuração, histórico ou cache."""

import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated

import httpx
import typer

from confere_cli import __version__
from confere_cli.client import Cliente, ErroCli
from confere_cli.saida import NIVEIS, tabela, texto_resposta
from confere_cli.textos import t

_TRANSPORT: httpx.BaseTransport | None = None  # trocado nos testes

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help="Confere: confira empresas (CNPJ), bancos e participantes do Pix com dados públicos da BrasilAPI. "
    "Indícios, não prova de fraude. / Check companies, banks and Pix participants with public data.",
)


class Conjunto(str, Enum):
    bancos = "bancos"
    pix = "pix"
    municipios = "municipios"
    ncm = "ncm"
    corretoras = "corretoras"


class Nivel(str, Enum):
    atencao = "atencao"
    alto = "alto"


def _lang_padrao() -> str:
    return "pt-BR" if os.environ.get("LANG", "pt").lower().startswith("pt") else "en"


def _versao(ligado: bool) -> None:
    if ligado:
        typer.echo(f"confere {__version__}")
        raise typer.Exit()


@app.callback()
def principal(
    ctx: typer.Context,
    api: Annotated[
        str, typer.Option("--api", envvar="CONFERE_API_URL", help="URL da API (https, ou http em localhost)")
    ] = "http://127.0.0.1:8000",
    lang: Annotated[str, typer.Option("--lang", envvar="CONFERE_LANG", help="Idioma: pt-BR ou en")] = "",
    versao: Annotated[bool, typer.Option("--version", callback=_versao, is_eager=True, help="Mostra a versão")] = False,
) -> None:
    idioma = lang if lang in ("pt-BR", "en") else _lang_padrao()
    ctx.obj = {"api": api, "lang": idioma}


def _cliente(ctx: typer.Context) -> Cliente:
    return Cliente(ctx.obj["api"], ctx.obj["lang"], transport=_TRANSPORT)


def _falhar(ctx: typer.Context, e: ErroCli) -> None:
    typer.echo(e.mensagem, err=True)
    raise typer.Exit(e.saida)


def _ler(valor: str, lang: str) -> str:
    """`-` lê o valor da entrada padrão: assim ele não fica no histórico do shell."""
    if valor != "-":
        return valor
    linha = sys.stdin.readline(65).strip()
    if not linha:
        raise ErroCli(t(lang, "err.stdin"))
    return linha


def _mostrar(ctx: typer.Context, r: dict, como_json: bool, falhar_se: Nivel | None) -> None:
    if como_json:
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        typer.echo(texto_resposta(r, ctx.obj["lang"]))
    if falhar_se is not None and NIVEIS[r["nivel"]] >= NIVEIS[falhar_se.value]:
        raise typer.Exit(3)


@app.command(help="Confere um CNPJ. Use `-` para ler da entrada padrão (não fica no histórico do shell).")
def cnpj(
    ctx: typer.Context,
    numero: Annotated[str, typer.Argument(help="CNPJ, com ou sem pontuação, ou - para a entrada padrão")],
    como_json: Annotated[bool, typer.Option("--json", help="Saída em JSON")] = False,
    falhar_se: Annotated[
        Nivel | None, typer.Option("--falhar-se", help="Sai com código 3 se o nível for igual ou pior")
    ] = None,
) -> None:
    try:
        r = _cliente(ctx).cnpj(_ler(numero, ctx.obj["lang"]))
    except ErroCli as e:
        _falhar(ctx, e)
    _mostrar(ctx, r, como_json, falhar_se)


@app.command(
    help="Pode pagar? Confere o CNPJ e a instituição (ISPB ou código do banco). Não verifica o titular da chave Pix."
)
def pagar(
    ctx: typer.Context,
    numero: Annotated[str, typer.Argument(help="CNPJ de quem vai receber, ou - para a entrada padrão")],
    ispb: Annotated[str | None, typer.Option("--ispb", help="ISPB (8 dígitos)")] = None,
    banco: Annotated[str | None, typer.Option("--banco", help="Código do banco, COMPE (1 a 3 dígitos)")] = None,
    como_json: Annotated[bool, typer.Option("--json", help="Saída em JSON")] = False,
    falhar_se: Annotated[
        Nivel | None, typer.Option("--falhar-se", help="Sai com código 3 se o nível for igual ou pior")
    ] = None,
) -> None:
    try:
        if bool(ispb) == bool(banco):
            raise ErroCli(t(ctx.obj["lang"], "err.inst_xor"))
        r = _cliente(ctx).pagar(_ler(numero, ctx.obj["lang"]), ispb=ispb, banco=banco)
    except ErroCli as e:
        _falhar(ctx, e)
    _mostrar(ctx, r, como_json, falhar_se)


@app.command(help="Explora dados abertos: bancos, pix, municipios (exige --uf), ncm, corretoras.")
def dados(
    ctx: typer.Context,
    conjunto: Annotated[Conjunto, typer.Argument(help="Conjunto de dados")],
    q: Annotated[str, typer.Option("--q", help="Busca (todas as palavras; sem acento/maiúscula)")] = "",
    uf: Annotated[str, typer.Option("--uf", help="UF (obrigatória em municipios)")] = "",
    status: Annotated[str, typer.Option("--status", help="Situação (corretoras)")] = "",
    limite: Annotated[int, typer.Option("--limite", min=1, max=200)] = 50,
    offset: Annotated[int, typer.Option("--offset", min=0)] = 0,
    csv: Annotated[bool, typer.Option("--csv", help="Baixa todas as linhas do filtro em CSV")] = False,
    saida: Annotated[Path | None, typer.Option("--saida", "-o", help="Arquivo do CSV (padrão: saída padrão)")] = None,
    forcar: Annotated[bool, typer.Option("--forcar", help="Sobrescreve o arquivo de saída")] = False,
    como_json: Annotated[bool, typer.Option("--json", help="Saída em JSON")] = False,
) -> None:
    filtros: dict[str, str | int] = {k: v for k, v in {"q": q, "uf": uf, "status": status}.items() if v}
    lang = ctx.obj["lang"]
    try:
        cli = _cliente(ctx)
        if csv:
            conteudo = cli.dados_csv(conjunto.value, filtros)
            if saida is None:
                sys.stdout.buffer.write(conteudo)
                return
            try:
                with open(saida, "wb" if forcar else "xb") as f:
                    f.write(conteudo)
            except FileExistsError:
                raise ErroCli(t(lang, "err.exists", p=saida)) from None
            typer.echo(t(lang, "saved", p=saida), err=True)
            return
        r = cli.dados(conjunto.value, {**filtros, "limite": limite, "offset": offset})
    except ErroCli as e:
        _falhar(ctx, e)
    if como_json:
        typer.echo(json.dumps(r, ensure_ascii=False, indent=2))
        return
    typer.echo(tabela(r["colunas"], r["itens"]))
    typer.echo(t(lang, "results", n=r["total"], m=len(r["itens"])), err=True)
    if r.get("atualizado_em"):
        typer.echo(t(lang, "stale" if r.get("desatualizado") else "asof", data=r["atualizado_em"]), err=True)


@app.command(help="Lista as UFs.")
def ufs(ctx: typer.Context) -> None:
    try:
        r = _cliente(ctx).ufs()
    except ErroCli as e:
        _falhar(ctx, e)
    typer.echo(tabela(["sigla", "nome", "regiao", "capital"], r["itens"]))


if __name__ == "__main__":
    app()
