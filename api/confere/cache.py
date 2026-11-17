"""Cache em memória com validade curta. Nada é gravado em disco; reiniciar o processo esvazia tudo."""

import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any


class CacheTTL:
    def __init__(self, ttl: float, max_itens: int = 1000, relogio: Callable[[], float] = time.monotonic) -> None:
        self._ttl = ttl
        self._max = max_itens
        self._relogio = relogio
        self._dados: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def obter(self, chave: str) -> Any | None:
        item = self._dados.get(chave)
        if item is None:
            return None
        if item[0] <= self._relogio():
            del self._dados[chave]
            return None
        return item[1]

    def guardar(self, chave: str, valor: Any) -> None:
        if self._ttl <= 0:
            return
        self._dados[chave] = (self._relogio() + self._ttl, valor)
        self._dados.move_to_end(chave)
        while len(self._dados) > self._max:
            self._dados.popitem(last=False)

    def __len__(self) -> int:
        return len(self._dados)
