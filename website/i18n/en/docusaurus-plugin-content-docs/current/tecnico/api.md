---
id: api
title: API (M1.1)
---

# CNPJ check API

The API alone owns the rules: validation, warning signs, cache and rate limiting. The web app (M2) and the CLI (M4) just call it.

## Run locally

```bash
cd api
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
CONFERE_DOCS=true python -m confere      # http://127.0.0.1:8000/docs
```

`/docs` (Swagger) loads scripts from a CDN, so it is **only enabled with `CONFERE_DOCS=true`**, for development.

![Interactive API documentation (Swagger)](/img/screenshots/api-docs.png)

## Check a CNPJ

```bash
curl 'http://127.0.0.1:8000/v1/cnpj/00000000000191/check?lang=en'
```

Send letters and digits only (no `/`). The **alphanumeric** CNPJ format, in force since July 2026, is accepted.

![Response of a CNPJ check](/img/screenshots/api-conferir-cnpj.png)

### What comes back

| Field | Meaning |
|---|---|
| `nivel` | `sem_indicios` (no signs), `atencao` (attention) or `alto` (high); never "safe" |
| `pontuacao` | Sum of the signal weights, 0 to 100 |
| `sinais[]` | Each warning sign: `codigo`, `gravidade`, `peso`, `mensagem` and the `regra` that produced it |
| `empresa` | **Minimized** public data: status, age, activity, size, city/state, number and qualification of partners |
| `aviso` | Reminder that it is an indication, not proof |

## Warning-sign rules

| Code | Severity | Weight | Rule |
|---|---|---|---|
| `SITUACAO_NAO_ATIVA` | high | 60 | Registration status other than ATIVA |
| `EMPRESA_RECEM_ABERTA` | high | 40 | Activity started less than 30 days ago |
| `EMPRESA_NOVA` | attention | 25 | Between 30 and 179 days |
| `SITUACAO_ESPECIAL` | attention | 20 | Special-status field filled |
| `DADOS_INCOMPLETOS` | attention | 15 | Activity start date missing |
| `SEM_CONTATO_PUBLICO` | attention | 10 | No e-mail or phone in the registry |
| `QUADRO_SOCIETARIO_VAZIO` | attention | 10 | Private legal entity with no partners listed |
| `EMPRESARIO_INDIVIDUAL` | info | 0 | Sole proprietor or MEI: name and address omitted |

Levels: `alto` from 50 points, `atencao` from 15, otherwise `sem_indicios`.

## Errors

| Status | `codigo` | When |
|---|---|---|
| 404 | `nao_encontrado` | The source does not know the CNPJ |
| 422 | `cnpj_invalido` | Wrong format or check digits (the source is not even called) |
| 429 | `limite_excedido` | More than 30 lookups per minute (`Retry-After` header) |
| 502 | `fonte_indisponivel` | BrasilAPI did not answer; nothing is made up |

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `CONFERE_DOCS` | `false` | Enables `/docs` (development only) |
| `CONFERE_CORS_ORIGENS` | empty | Allowed origins, comma-separated |
| `CONFERE_CONFIAR_PROXY` | `false` | Use the last `X-Forwarded-For` value (behind **one** proxy of yours) |
| `CONFERE_LIMITE_POR_MINUTO` | `30` | Lookups per origin |
| `CONFERE_CACHE_TTL` | `600` | Cache lifetime in seconds (0 disables) |
