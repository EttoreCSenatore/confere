# Confere

[English](README.en.md) · **Português**

**Confira antes de pagar.** Aplicativo web, API e CLI que cruzam dados públicos da [BrasilAPI](https://brasilapi.com.br/) (CNPJ, bancos, participantes do Pix) e mostram sinais de alerta **explicados**, sem guardar suas consultas.

📖 Documentação: https://ettorecsenatore.github.io/confere/ (português e inglês)

> Estado: **M0 a M4.1: API, interface web, explorador, CLI e docs**. Veja o [roadmap](https://ettorecsenatore.github.io/confere/docs/roadmap).

## Princípios

- **Privacidade por padrão (LGPD)**: sem conta, sem histórico, sem IP em log. Artefatos em [`.lgpd/`](.lgpd/STATUS.md) (minutas, pendentes de revisão jurídica).
- **Explicável**: cada indício mostra a regra que o gerou. É dica, não prova de fraude.
- **Software livre**: código AGPL-3.0-or-later ([LICENSE](LICENSE)); documentação CC BY-SA 4.0 ([LICENSE-DOCS.md](LICENSE-DOCS.md)).

## Desenvolvimento

```bash
cd api && python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]' && python -m confere   # API
cd web && npm ci && npm run dev                                                                   # interface
cd website && npm ci && npm start                                                                  # docs
```

Veja a página [Desenvolvimento](https://ettorecsenatore.github.io/confere/docs/tecnico/desenvolvimento). Vulnerabilidades: [SECURITY.md](SECURITY.md).
