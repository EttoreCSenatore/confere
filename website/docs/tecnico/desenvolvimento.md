---
id: desenvolvimento
title: Desenvolvimento
---

# Desenvolvimento

## Fluxo de trabalho

1. Uma etapa por branch, com pull request.
2. A CI precisa passar (documentação, API, auditoria).
3. Integração por *squash*; documentação em português e inglês atualizada no mesmo PR.

## Documentação

```bash
cd website
npm ci
npm start          # pt-BR em http://localhost:3000/confere/
npm run build      # gera pt-BR e inglês
python3 ../scripts/checar-traducao.py
```

A CI falha se uma página em inglês faltar ou tiver estrutura diferente (títulos, blocos de código, imagens) da versão em português.

## API

```bash
cd api && . .venv/bin/activate
ruff check . && ruff format --check .
pytest
```

## Licenças das dependências

```bash
python3 scripts/auditar-licencas.py --npm website
python3 scripts/auditar-licencas.py --python    # com o venv da API ativo
```

Só licenças compatíveis com a AGPL-3.0-or-later são aceitas.
