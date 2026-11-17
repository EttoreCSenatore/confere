"""`python -m confere`: sobe a API em 127.0.0.1:8000 sem log de acesso do servidor (que registraria IP e URL)."""

import logging
import os

import uvicorn


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    uvicorn.run(
        "confere.app:criar_app",
        factory=True,
        host=os.environ.get("CONFERE_HOST", "127.0.0.1"),
        port=int(os.environ.get("CONFERE_PORTA", "8000")),
        access_log=False,  # o log do uvicorn tem IP e caminho completo (com o CNPJ)
        server_header=False,
    )


if __name__ == "__main__":
    main()
