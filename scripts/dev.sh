#!/usr/bin/env bash
# Sobe a API (porta 8000) e o app web (porta 5173) para você testar o Confere no seu computador.
# Precisa de Python 3.13+ e Node 24+. Ctrl+C encerra os dois. / Starts the API and the web app for local testing.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d api/.venv ] || python3 -m venv api/.venv
# shellcheck disable=SC1091
. api/.venv/bin/activate
pip install -q -e api
[ -d web/node_modules ] || (cd web && npm ci --silent)

CONFERE_PORTA="${CONFERE_PORTA:-8000}" python -m confere &
API=$!
(cd web && npm run dev -- --host 127.0.0.1 --port "${WEB_PORTA:-5173}") &
WEB=$!
trap 'kill "$API" "$WEB" 2>/dev/null || true' EXIT INT TERM

sleep 4
echo
echo "  App web:  http://127.0.0.1:${WEB_PORTA:-5173}"
echo "  API:      http://127.0.0.1:${CONFERE_PORTA:-8000}/healthz"
echo "  CLI:      pip install -e cli  &&  confere cnpj 00000000000191"
echo "  (Ctrl+C para encerrar)"
wait
