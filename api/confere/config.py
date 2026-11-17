"""Configuração por variáveis de ambiente (prefixo CONFERE_). Nenhum segredo é necessário."""

import os
from collections.abc import Mapping
from dataclasses import dataclass


def _bool(valor: str | None) -> bool:
    return (valor or "").strip().lower() in {"1", "true", "sim", "yes"}


@dataclass(frozen=True)
class Config:
    docs: bool = False  # /docs (Swagger) carrega scripts de CDN: só em desenvolvimento
    cors_origens: tuple[str, ...] = ()  # por padrão, nenhuma origem externa
    confiar_proxy: bool = False  # usar X-Forwarded-For (último valor) atrás de UM proxy de confiança
    limite_por_minuto: int = 30
    cache_ttl: float = 600.0  # segundos; só memória
    cache_ttl_dados: float = 86400.0  # conjuntos de dados abertos (IBGE, NCM, CVM): mudam pouco
    snapshot_max_dias: int = 14  # cópia local mais nova que isso é usada sem rede; 0 desliga as cópias
    timeout_fonte: float = 8.0


def carregar(env: Mapping[str, str] | None = None) -> Config:
    env = os.environ if env is None else env
    origens = tuple(o.strip() for o in env.get("CONFERE_CORS_ORIGENS", "").split(",") if o.strip())
    return Config(
        docs=_bool(env.get("CONFERE_DOCS")),
        cors_origens=origens,
        confiar_proxy=_bool(env.get("CONFERE_CONFIAR_PROXY")),
        limite_por_minuto=int(env.get("CONFERE_LIMITE_POR_MINUTO", "30")),
        cache_ttl=float(env.get("CONFERE_CACHE_TTL", "600")),
        cache_ttl_dados=float(env.get("CONFERE_CACHE_TTL_DADOS", "86400")),
        snapshot_max_dias=int(env.get("CONFERE_SNAPSHOT_MAX_DIAS", "14")),
        timeout_fonte=float(env.get("CONFERE_TIMEOUT_FONTE", "8")),
    )
