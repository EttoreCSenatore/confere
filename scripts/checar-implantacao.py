#!/usr/bin/env python3
"""Confere a configuração de implantação contra regressões de privacidade e segurança (só biblioteca padrão).

Falha se o Caddyfile voltar a registrar acessos/IP/URL, se faltar CSP ou limite de corpo, ou se o Compose perder o
endurecimento (somente leitura, sem capacidades, API sem porta publicada, Swagger ligado, logs sem rotação).
Complementa o `deploy/smoke.sh`, que testa uma implantação de verdade."""

import re
import sys
from pathlib import Path

DEPLOY = Path(__file__).resolve().parent.parent / "deploy"
problemas: list[str] = []


def exige(cond: bool, msg: str) -> None:
    if not cond:
        problemas.append(msg)


def bloco_global(caddy: str) -> str:
    """Primeiro bloco `{ ... }` do Caddyfile (opções globais)."""
    inicio = caddy.index("{")
    nivel = 0
    for i, c in enumerate(caddy[inicio:], inicio):
        nivel += c == "{"
        nivel -= c == "}"
        if nivel == 0:
            return caddy[inicio : i + 1]
    raise ValueError("Caddyfile sem fechamento de bloco global")


def main() -> int:
    caddy = (DEPLOY / "Caddyfile").read_text(encoding="utf-8")
    sem_comentarios = "\n".join(re.sub(r"#.*", "", l) for l in caddy.splitlines())
    globais = bloco_global(sem_comentarios)
    resto = sem_comentarios.replace(globais, "", 1)

    exige(not re.search(r"^\s*log\b", resto, flags=re.M), "Caddyfile: há diretiva `log` no site (registraria acessos, IP e URL)")
    for campo in ("request>remote_ip", "request>client_ip", "request>uri", "request>headers"):
        exige(re.search(rf"{re.escape(campo)}\s+delete", globais) is not None, f"Caddyfile: o log global não apaga {campo}")
    exige("level WARN" in globais, "Caddyfile: o log global deve ser só WARN")
    exige("admin off" in globais, "Caddyfile: a API de administração do Caddy deve estar desligada")
    exige("default-src 'none'" in resto and "frame-ancestors 'none'" in resto, "Caddyfile: CSP restritiva (com frame-ancestors) ausente")
    exige("Strict-Transport-Security" in resto, "Caddyfile: HSTS ausente")
    exige("Referrer-Policy no-referrer" in resto, "Caddyfile: Referrer-Policy no-referrer ausente")
    exige(re.search(r"max_size\s+\d+KB", resto) is not None, "Caddyfile: limite de corpo (request_body max_size) ausente")
    exige("-Server" in resto, "Caddyfile: o cabeçalho Server deveria ser removido")

    compose = (DEPLOY / "docker-compose.yml").read_text(encoding="utf-8")
    servicos = re.split(r"\n  (?=(?:api|web):\n)", compose)
    exige(len(servicos) >= 3, "Compose: serviços api e web não encontrados")
    for nome, trecho in zip(("api", "web"), servicos[1:3], strict=False):
        exige("read_only: true" in trecho, f"Compose: {nome} deve ser somente leitura")
        exige("cap_drop: [ALL]" in trecho, f"Compose: {nome} deve largar todas as capacidades")
        exige("no-new-privileges:true" in trecho, f"Compose: {nome} deve usar no-new-privileges")
        exige("max-size" in trecho and "max-file" in trecho, f"Compose: {nome} precisa de rotação de log limitada")
    api = servicos[1] if len(servicos) > 1 else ""
    exige("ports:" not in api, "Compose: a API não pode publicar portas")
    exige("CONFERE_DOCS" not in re.sub(r"#.*", "", api), "Compose: CONFERE_DOCS não pode ser definido (Swagger usa CDN)")
    exige('CONFERE_CONFIAR_PROXY: "true"' in api, "Compose: a API deve confiar no proxy (X-Forwarded-For)")

    for nome in ("Dockerfile.api", "Dockerfile.web"):
        texto = (DEPLOY / nome).read_text(encoding="utf-8")
        exige("USER 10001:10001" in texto, f"{nome}: deve rodar como usuário sem privilégio")
    exige("pip uninstall -y pip setuptools" in (DEPLOY / "Dockerfile.api").read_text(encoding="utf-8"), "Dockerfile.api: pip/setuptools devem sair da imagem final")

    if problemas:
        print("\n".join(f"- {p}" for p in problemas), file=sys.stderr)
        return 1
    print("ok: Caddyfile, Compose e Dockerfiles seguem as regras de privacidade e segurança")
    return 0


if __name__ == "__main__":
    sys.exit(main())
