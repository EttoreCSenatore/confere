---
id: desenvolvimento
title: Development
---

# Development

## Workflow

1. One step per branch, with a pull request.
2. CI must pass (documentation, API, audit).
3. Squash-merge; documentation in Portuguese and English updated in the same PR.

## Documentation

```bash
cd website
npm ci
npm start          # pt-BR at http://localhost:3000/confere/
npm run build      # builds pt-BR and English
python3 ../scripts/checar-traducao.py
```

CI fails if an English page is missing or has a different structure (headings, code blocks, images) from the Portuguese version.

## API

```bash
cd api && . .venv/bin/activate
ruff check . && ruff format --check .
pytest
```

## CLI

```bash
cd cli && python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
ruff check . && pytest
confere --help
```

## Web

```bash
cd web
npm ci
npm run dev        # http://localhost:5173 (proxies /v1 to the API at 127.0.0.1:8000)
npm test && npm run build
npm run screenshots -- ../website/static/img/screenshots   # with `npx vite preview --port 4173` running
```

## Dependency licenses

```bash
python3 scripts/auditar-licencas.py --npm website
python3 scripts/auditar-licencas.py --npm web
python3 scripts/auditar-licencas.py --python    # with the API venv active
python3 scripts/auditar-licencas.py --python --pyproject cli/pyproject.toml   # with the CLI venv
```

Only licenses compatible with AGPL-3.0-or-later are accepted.
