"""Cliente HTTP da API do Confere. Só fala com a URL configurada, exige https (exceto em localhost), não segue
redirecionamentos, não guarda cookies e não envia nada além do necessário."""

import re
from urllib.parse import quote, urlparse

import httpx

from confere_cli import __version__
from confere_cli.textos import T, t


def normalizar(numero: str) -> str:
    """Tira pontos, barra, hífen e espaços (a barra quebraria o caminho da URL). A validação é só da API."""
    return re.sub(r"[.\-/\s]", "", numero).upper()


LOCAIS = {"localhost", "127.0.0.1", "::1"}


class ErroCli(Exception):
    def __init__(self, mensagem: str, saida: int = 2) -> None:
        super().__init__(mensagem)
        self.mensagem, self.saida = mensagem, saida


def validar_base(base: str, lang: str) -> str:
    u = urlparse(base)
    if u.scheme not in ("http", "https") or not u.hostname or u.username or u.password:
        raise ErroCli(t(lang, "err.https", base=base))
    if u.scheme == "http" and u.hostname not in LOCAIS:
        raise ErroCli(t(lang, "err.https", base=base))
    return base.rstrip("/")


class Cliente:
    def __init__(
        self, base: str, lang: str, *, transport: httpx.BaseTransport | None = None, timeout: float = 30.0
    ) -> None:
        self.base = validar_base(base, lang)
        self.lang = lang
        self._http = httpx.Client(
            base_url=self.base,
            timeout=timeout,
            transport=transport,
            follow_redirects=False,
            headers={"User-Agent": f"confere-cli/{__version__}", "Accept-Language": lang},
        )

    def _chamar(self, metodo: str, caminho: str, **kw) -> httpx.Response:
        try:
            resp = self._http.request(metodo, caminho, **kw)
        except httpx.HTTPError:
            raise ErroCli(t(self.lang, "err.rede", base=self.base)) from None
        if resp.status_code >= 400:
            codigo = "desconhecido"
            try:
                codigo = str(resp.json().get("codigo", codigo))
            except (ValueError, AttributeError):
                pass
            chave = f"err.{codigo}"
            if chave not in T[self.lang]:
                raise ErroCli(t(self.lang, "err.desconhecido", status=resp.status_code))
            raise ErroCli(t(self.lang, chave, status=resp.status_code, base=self.base))
        return resp

    def _json(self, resp: httpx.Response) -> dict:
        try:
            dados = resp.json()
        except ValueError:
            raise ErroCli(t(self.lang, "err.invalid_answer")) from None
        if not isinstance(dados, dict):
            raise ErroCli(t(self.lang, "err.invalid_answer"))
        return dados

    def cnpj(self, numero: str) -> dict:
        resp = self._chamar("GET", f"/v1/cnpj/{quote(normalizar(numero), safe='')}/check", params={"lang": self.lang})
        return self._json(resp)

    def pagar(self, cnpj: str, *, ispb: str | None, banco: str | None) -> dict:
        corpo: dict[str, str] = {"cnpj": normalizar(cnpj), "lang": self.lang}
        if ispb:
            corpo["ispb"] = ispb
        if banco:
            corpo["banco"] = banco
        return self._json(self._chamar("POST", "/v1/pagamento/check", json=corpo))

    def dados(self, conjunto: str, params: dict[str, str | int]) -> dict:
        return self._json(self._chamar("GET", f"/v1/dados/{quote(conjunto, safe='')}", params=params))

    def dados_csv(self, conjunto: str, params: dict[str, str | int]) -> bytes:
        return self._chamar("GET", f"/v1/dados/{quote(conjunto, safe='')}", params={**params, "formato": "csv"}).content

    def ufs(self) -> dict:
        return self._json(self._chamar("GET", "/v1/dados/ufs"))
