# Confere

**English** · [Português](README.md)

**Check before you pay.** A web app, API and CLI that cross-reference public data from [BrasilAPI](https://brasilapi.com.br/) (CNPJ, banks, Pix participants) and show **explained** warning signs, without storing your lookups.

📖 Documentation: https://ettorecsenatore.github.io/confere/en/ (Portuguese and English)

> Status: **M0 to M3: API, web interface, explorer and docs**. See the [roadmap](https://ettorecsenatore.github.io/confere/en/docs/roadmap).

## Principles

- **Privacy by default (LGPD)**: no account, no history, no IP in logs. Artifacts in [`.lgpd/`](.lgpd/STATUS.md) (Portuguese drafts, pending legal review).
- **Explainable**: every signal shows the rule behind it. A hint, not proof of fraud.
- **Free software**: code AGPL-3.0-or-later ([LICENSE](LICENSE)); documentation CC BY-SA 4.0 ([LICENSE-DOCS.md](LICENSE-DOCS.md)).

## Development

```bash
cd api && python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]' && python -m confere   # API
cd web && npm ci && npm run dev                                                                   # interface
cd website && npm ci && npm start                                                                  # docs
```

See the [Development](https://ettorecsenatore.github.io/confere/en/docs/tecnico/desenvolvimento) page. Vulnerabilities: [SECURITY.md](SECURITY.md).
