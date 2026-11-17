"""Limite de requisições por origem, só em memória. A chave é um HMAC do IP com um sal aleatório gerado a cada
início do processo: o IP em si não fica guardado e nada sobrevive a um reinício."""

import hashlib
import hmac
import secrets
import time
from collections import deque
from collections.abc import Callable


class LimiteTaxa:
    def __init__(
        self,
        maximo: int = 30,
        janela: float = 60.0,
        max_chaves: int = 10_000,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        self._maximo = maximo
        self._janela = janela
        self._max_chaves = max_chaves
        self._relogio = relogio
        self._sal = secrets.token_bytes(16)
        self._tentativas: dict[bytes, deque[float]] = {}

    def _chave(self, origem: str) -> bytes:
        return hmac.new(self._sal, origem.encode(), hashlib.sha256).digest()

    def verificar(self, origem: str) -> float | None:
        """Devolve None se pode seguir, ou os segundos até poder tentar de novo."""
        agora = self._relogio()
        chave = self._chave(origem)
        fila = self._tentativas.setdefault(chave, deque())
        while fila and agora - fila[0] >= self._janela:
            fila.popleft()
        if len(fila) >= self._maximo:
            return max(1.0, self._janela - (agora - fila[0]))
        fila.append(agora)
        if len(self._tentativas) > self._max_chaves:
            self._podar(agora)
        return None

    def _podar(self, agora: float) -> None:
        for k in [k for k, f in self._tentativas.items() if not f or agora - f[-1] >= self._janela]:
            del self._tentativas[k]
        while len(self._tentativas) > self._max_chaves:
            del self._tentativas[next(iter(self._tentativas))]
