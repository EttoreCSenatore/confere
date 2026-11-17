"""Cliente da BrasilAPI. Único destino de rede do projeto: o endereço-base é fixo e só identificadores
já validados entram na URL; o IP e qualquer dado da pessoa usuária nunca são repassados."""

import re

import httpx

BASE = "https://brasilapi.com.br/api"
_ID = re.compile(r"^[0-9A-Z]{14}$")


class NaoEncontrado(Exception):
    """A fonte não conhece o identificador."""


class FonteIndisponivel(Exception):
    """Fonte fora do ar, lenta ou com resposta inválida."""


class BrasilApi:
    def __init__(
        self, *, base: str = BASE, timeout: float = 8.0, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base,
            timeout=timeout,
            transport=transport,
            follow_redirects=False,
            headers={"User-Agent": "confere/0.1 (+https://github.com/EttoreCSenatore/confere)"},
        )

    async def fechar(self) -> None:
        await self._http.aclose()

    async def _obter(self, caminho: str) -> dict:
        ultimo: Exception | None = None
        for _ in range(2):  # uma nova tentativa só para falhas de rede e 5xx
            try:
                resp = await self._http.get(caminho)
            except httpx.HTTPError as exc:
                ultimo = exc
                continue
            if resp.status_code in (400, 404):
                raise NaoEncontrado(caminho)
            if resp.status_code >= 500:
                ultimo = FonteIndisponivel(f"status {resp.status_code}")
                continue
            if resp.status_code != 200:
                raise FonteIndisponivel(f"status {resp.status_code}")
            try:
                dados = resp.json()
            except ValueError as exc:
                raise FonteIndisponivel("resposta inválida") from exc
            if not isinstance(dados, dict):
                raise FonteIndisponivel("resposta inválida")
            return dados
        raise FonteIndisponivel(type(ultimo).__name__) from ultimo

    async def cnpj(self, cnpj: str) -> dict:
        if not _ID.match(cnpj):  # defesa em profundidade: nunca montar URL com texto livre
            raise ValueError("CNPJ não normalizado")
        return await self._obter(f"/cnpj/v1/{cnpj}")
