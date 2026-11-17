---
id: experimente
title: Try it
---

# Try Confere

You can test everything on your computer in a few minutes, with no account and no Docker.

## Start the app

You need Python 3.13+ and Node 24+. From the repository root:

```bash
./scripts/dev.sh
```

The script creates the environment, starts the API (port 8000) and the app (port 5173) and prints the addresses. `Ctrl+C` stops both.

![Output of scripts/dev.sh](/img/screenshots/experimente-dev-en.png)

## What to try in the app

Open `http://127.0.0.1:5173`. Suggestions:

- **Check**: CNPJ `00.000.000/0001-91` (a public bank) should give "No signs". Try a CNPJ with a wrong digit and see the error message.
- **Safe to pay?**: use the same CNPJ with ISPB `00000000` (takes part in Pix) and then with `12345678` (does not exist: the level rises).
- **Explore**: search `cafe` in NCM, pick SP in Municipalities and download the CSV.
- **Language and theme**: switch to English and try your system's dark theme.

![Result of a lookup in the app](/img/screenshots/app-resultado-atencao-en.png)

## Try the command line

With the app running, in another terminal:

```bash
pip install -e cli
confere cnpj 00000000000191
confere pagar 00000000000191 --ispb 12345678 --falhar-se alto; echo $?
```

![CLI example](/img/screenshots/cli-pagar-alto-en.png)

## Try it like production (Docker)

To see HTTPS, the security headers and `smoke.sh`, see the [Deployment](../tecnico/implantacao.md) page. For local tests use `CONFERE_DOMAIN=localhost` and unprivileged ports.

## Found a problem?

Open a GitHub issue (with no personal data) or, for a vulnerability, use the private report described in `SECURITY.md`.
