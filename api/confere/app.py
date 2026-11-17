"""Aplicação FastAPI. Regras de privacidade: nada é gravado, o log não tem IP nem CNPJ, só identificadores
validados vão para a BrasilAPI."""

import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from confere import __version__
from confere import cnpj as cnpj_mod
from confere.brasilapi import BrasilApi, FonteIndisponivel, NaoEncontrado
from confere.cache import CacheTTL
from confere.config import Config, carregar
from confere.empresa import Empresa, reduzir
from confere.instituicoes import COMPE, ISPB, Diretorio, Instituicao
from confere.limite import LimiteTaxa
from confere.risco import IDIOMAS, Sinal, avaliar

acesso = logging.getLogger("confere.acesso")


def _silenciar_logs_com_url() -> None:
    """httpx/httpcore registram a URL completa de cada chamada (com o CNPJ) em INFO/DEBUG: só avisos e erros."""
    for nome in ("httpx", "httpcore"):
        logging.getLogger(nome).setLevel(logging.WARNING)


AVISO = {
    "pt-BR": "Indícios a partir de dados públicos; não é prova de fraude nem análise de crédito. "
    "Ausência de sinais não significa que seja seguro.",
    "en": "Indications from public data; not proof of fraud nor a credit analysis. "
    "No signals does not mean it is safe.",
}


class ErroApi(Exception):
    def __init__(self, status: int, codigo: str, mensagem: str, cabecalhos: dict[str, str] | None = None) -> None:
        self.status, self.codigo, self.mensagem, self.cabecalhos = status, codigo, mensagem, cabecalhos or {}


class Fonte(BaseModel):
    nome: str = "BrasilAPI"
    url: str = "https://brasilapi.com.br/"


class Erro(BaseModel):
    codigo: str
    mensagem: str


class PedidoPagamento(BaseModel):
    """Corpo do POST: dados sensíveis ao contexto vão no corpo (não na URL), que proxies costumam registrar."""

    model_config = ConfigDict(extra="forbid")
    cnpj: str = Field(max_length=32, description="CNPJ de quem vai receber (com ou sem pontuação)")
    ispb: str | None = Field(None, max_length=16, description="ISPB (8 dígitos) da instituição de quem recebe")
    banco: str | None = Field(None, max_length=8, description="Código COMPE (1 a 3 dígitos); alternativa ao ISPB")
    lang: str = Field("pt-BR", max_length=8, description="pt-BR ou en")


_ERROS = {
    404: {"model": Erro, "description": "CNPJ não encontrado na fonte pública"},
    422: {"model": Erro, "description": "CNPJ inválido (formato ou dígitos verificadores)"},
    429: {"model": Erro, "description": "Limite de consultas por minuto excedido (veja Retry-After)"},
    502: {"model": Erro, "description": "A BrasilAPI não respondeu"},
}

LIMITES_PIX = {
    "pt-BR": "Só confirmamos que a instituição existe e participa do Pix. Não verificamos o titular da chave "
    "nem a conta de destino.",
    "en": "We only confirm that the institution exists and takes part in Pix. We do not verify the key holder "
    "or the destination account.",
}


class RespostaCnpj(BaseModel):
    cnpj: str
    consultado_em: datetime
    nivel: str
    pontuacao: int
    sinais: list[Sinal]
    empresa: Empresa
    aviso: str
    fonte: Fonte


class RespostaPagamento(RespostaCnpj):
    instituicao: Instituicao | None
    limites: str


def _origem(request: Request, confiar_proxy: bool) -> str:
    if confiar_proxy:
        encaminhado = request.headers.get("x-forwarded-for", "")
        if encaminhado:
            return encaminhado.split(",")[-1].strip()  # valor acrescentado pelo nosso proxy
    return request.client.host if request.client else "desconhecida"


def criar_app(
    config: Config | None = None,
    fonte: BrasilApi | None = None,
    hoje: Callable[[], date] = date.today,
) -> FastAPI:
    config = config or carregar()
    _silenciar_logs_com_url()
    cache = CacheTTL(config.cache_ttl)
    limite = LimiteTaxa(maximo=config.limite_por_minuto)
    api_fonte = fonte or BrasilApi(timeout=config.timeout_fonte)
    diretorio = Diretorio(api_fonte, CacheTTL(config.cache_ttl_diretorio, max_itens=4))

    @asynccontextmanager
    async def ciclo(_: FastAPI):
        yield
        await api_fonte.fechar()

    app = FastAPI(
        title="Confere API",
        version=__version__,
        summary="Conferência de empresas com dados públicos da BrasilAPI.",
        description="Indícios explicados, sem guardar consultas. Não é prova de fraude. Código: AGPL-3.0-or-later.",
        docs_url="/docs" if config.docs else None,
        redoc_url=None,
        lifespan=ciclo,
    )
    if config.cors_origens:
        app.add_middleware(CORSMiddleware, allow_origins=list(config.cors_origens), allow_methods=["GET"])

    @app.middleware("http")
    async def seguranca_e_log(request: Request, call_next):
        inicio = time.perf_counter()
        resposta = await call_next(request)
        rota = request.scope.get("route")
        modelo = getattr(rota, "path", "-")  # modelo da rota (/v1/cnpj/{cnpj}/check), nunca o valor
        resposta.headers["Cache-Control"] = "no-store"
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["Referrer-Policy"] = "no-referrer"
        if not (config.docs and request.url.path == "/docs"):  # Swagger (só dev) precisa de scripts da CDN
            resposta.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        acesso.info(
            "%s %s %d %.0fms", request.method, modelo, resposta.status_code, (time.perf_counter() - inicio) * 1000
        )
        return resposta

    @app.exception_handler(ErroApi)
    async def tratar_erro(_: Request, exc: ErroApi):
        return JSONResponse(
            {"codigo": exc.codigo, "mensagem": exc.mensagem}, status_code=exc.status, headers=exc.cabecalhos
        )

    @app.get("/healthz", include_in_schema=False)
    async def saude():
        return {"status": "ok"}

    def _limitar(request: Request) -> None:
        espera = limite.verificar(_origem(request, config.confiar_proxy))
        if espera is not None:
            raise ErroApi(
                429,
                "limite_excedido",
                "Muitas consultas; tente de novo em instantes.",
                {"Retry-After": str(int(espera) + 1)},
            )

    async def _empresa(numero: str) -> Empresa:
        if not cnpj_mod.valido(numero):
            raise ErroApi(422, "cnpj_invalido", "CNPJ inválido (formato ou dígitos verificadores).")
        empresa = cache.obter(numero)
        if empresa is None:
            try:
                empresa = reduzir(numero, await api_fonte.cnpj(numero))
            except NaoEncontrado:
                raise ErroApi(404, "nao_encontrado", "CNPJ não encontrado na fonte pública.") from None
            except FonteIndisponivel:
                raise ErroApi(502, "fonte_indisponivel", "A BrasilAPI não respondeu. Nada foi concluído.") from None
            cache.guardar(numero, empresa)
        return empresa

    @app.get("/v1/cnpj/{cnpj}/check", response_model=RespostaCnpj, summary="Confere um CNPJ", responses=_ERROS)
    async def conferir_cnpj(
        request: Request,
        cnpj: str,
        lang: str = Query("pt-BR", description="Idioma das mensagens: pt-BR ou en"),
    ) -> RespostaCnpj:
        _limitar(request)
        idioma = lang if lang in IDIOMAS else "pt-BR"
        empresa = await _empresa(cnpj_mod.normalizar(cnpj))
        av = avaliar(empresa, hoje(), idioma)
        return RespostaCnpj(
            cnpj=cnpj_mod.formatar(empresa.cnpj),
            consultado_em=datetime.now(UTC),
            nivel=av.nivel,
            pontuacao=av.pontuacao,
            sinais=av.sinais,
            empresa=empresa,
            aviso=AVISO[idioma],
            fonte=Fonte(),
        )

    @app.post(
        "/v1/pagamento/check",
        response_model=RespostaPagamento,
        summary="Pode pagar? Confere o CNPJ e a instituição (Pix)",
        responses=_ERROS,
    )
    async def conferir_pagamento(request: Request, pedido: PedidoPagamento) -> RespostaPagamento:
        _limitar(request)
        idioma = pedido.lang if pedido.lang in IDIOMAS else "pt-BR"
        ispb, banco = (pedido.ispb or "").strip(), (pedido.banco or "").strip()
        if bool(ispb) == bool(banco) or (ispb and not ISPB.match(ispb)) or (banco and not COMPE.match(banco)):
            raise ErroApi(422, "instituicao_invalida", "Informe só o ISPB (8 dígitos) ou só o código do banco (1 a 3).")
        empresa = await _empresa(cnpj_mod.normalizar(pedido.cnpj))
        try:
            instituicao = await diretorio.buscar(ispb=ispb or None, codigo=int(banco) if banco else None)
        except FonteIndisponivel:
            raise ErroApi(502, "fonte_indisponivel", "A BrasilAPI não respondeu. Nada foi concluído.") from None
        av = avaliar(empresa, hoje(), idioma, instituicao)
        return RespostaPagamento(
            cnpj=cnpj_mod.formatar(empresa.cnpj),
            consultado_em=datetime.now(UTC),
            nivel=av.nivel,
            pontuacao=av.pontuacao,
            sinais=av.sinais,
            empresa=empresa,
            aviso=AVISO[idioma],
            fonte=Fonte(),
            instituicao=instituicao,
            limites=LIMITES_PIX[idioma],
        )

    return app
