---
id: cli
title: Command line (CLI)
---

# Command line (CLI)

The CLI is a **thin client of the API**: it has no rules of its own and keeps no configuration, history or cache. Everything the web app does is here.

## Install and configure

```bash
pipx install ./cli                       # from the repository root
export CONFERE_API_URL=https://YOUR-SERVER    # default: http://127.0.0.1:8000
export CONFERE_LANG=en                   # or pt-BR; default: the system language
```

For safety, the CLI **only accepts `https`** (and `http` only on `localhost`), does not follow redirects and sends no cookies.

## Check a CNPJ

`confere cnpj` shows the level, the signs with the rule behind each one, and the company's public data.

![Output of confere cnpj](/img/screenshots/cli-cnpj-en.png)

To keep the CNPJ **out of your shell history**, pass `-` and send it on standard input:

![CNPJ read from standard input](/img/screenshots/cli-stdin-en.png)

## Safe to pay?

`confere pagar` checks the CNPJ and the institution (`--ispb` or `--banco`, only one). It does not verify the Pix key holder.

![Output of confere pagar](/img/screenshots/cli-pagar-en.png)

An unknown institution raises the level and the reason is explained:

![Institution not found](/img/screenshots/cli-pagar-alto-en.png)

## Use in scripts

`--json` prints the API response. `--falhar-se atencao|alto` exits with **code 3** when the level is equal or worse, useful in automation. Errors exit with code 2 and a plain message.

![Exit code with --falhar-se](/img/screenshots/cli-falhar-en.png)

## Explore open data

`confere dados` lists `bancos`, `pix`, `municipios` (requires `--uf`), `ncm` and `corretoras`, with `--q`, `--limite` and `--offset`.

![NCM search](/img/screenshots/cli-dados-ncm-en.png)

![Bank search](/img/screenshots/cli-dados-bancos-en.png)

With `--csv` the CLI downloads **every row of the filter** (UTF-8 with BOM, protected against formula injection). Without `-o`, the CSV goes to standard output; with `-o`, the CLI **will not overwrite** files without `--forcar`:

```bash
confere dados corretoras --uf SP --csv -o corretoras.csv
```

## Errors

API errors become clear messages in your language, with no technical traces.

![Invalid CNPJ message](/img/screenshots/cli-erro-en.png)
