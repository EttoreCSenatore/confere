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

## Dependency licenses

```bash
python3 scripts/auditar-licencas.py --npm website
```

Only licenses compatible with AGPL-3.0-or-later are accepted.
