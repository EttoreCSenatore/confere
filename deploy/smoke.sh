#!/usr/bin/env bash
# Verifica uma implantação do Confere: saúde, SPA, cabeçalhos de segurança, API e PRIVACIDADE dos logs.
# Uso: BASE=https://confere.exemplo.org ./smoke.sh          (local: CONFERE_SMOKE_LOCAL=1 BASE=https://localhost:18443 ...)
set -u
BASE="${BASE:-https://localhost}"
CURL=(curl -sS --max-time 30)
[ "${CONFERE_SMOKE_LOCAL:-0}" = 1 ] && CURL+=(-k)   # CA interna do Caddy só em teste local
falhas=0
ok()   { printf '  ok   %s\n' "$1"; }
erro() { printf '  FAIL %s\n' "$1"; falhas=$((falhas + 1)); }
checa() { if eval "$2"; then ok "$1"; else erro "$1"; fi; }

echo "Confere smoke em $BASE"
H=$("${CURL[@]}" -D - -o /tmp/smoke-index.html "$BASE/")
checa "página inicial responde 200" '[[ "$H" == *"200"* ]] && grep -q "id=\"root\"" /tmp/smoke-index.html'
checa "fallback do SPA (/explorar) responde 200 com HTML" '[ "$("${CURL[@]}" -o /dev/null -w "%{http_code}" "$BASE/explorar")" = 200 ]'
hl=$(printf '%s' "$H" | tr 'A-Z' 'a-z')
checa "CSP restritiva no site" '[[ "$hl" == *"content-security-policy: default-src '"'"'none'"'"'"* ]]'
checa "HSTS" '[[ "$hl" == *"strict-transport-security"* ]]'
checa "nosniff" '[[ "$hl" == *"x-content-type-options: nosniff"* ]]'
checa "referrer-policy no-referrer" '[[ "$hl" == *"referrer-policy: no-referrer"* ]]'
checa "sem cabeçalho Server" '[[ "$hl" != *$'"'"'\nserver:'"'"'* ]]'
checa "/healthz" '[ "$("${CURL[@]}" "$BASE/healthz")" = "{\"status\":\"ok\"}" ]'
checa "Swagger desligado (/docs não mostra swagger)" '! "${CURL[@]}" "$BASE/docs" | grep -qi swagger'
checa "CNPJ inválido dá 422" '[ "$("${CURL[@]}" -o /dev/null -w "%{http_code}" "$BASE/v1/cnpj/00000000000192/check")" = 422 ]'
checa "CNPJ de teste (rede) dá 200" '[ "$("${CURL[@]}" -o /dev/null -w "%{http_code}" "$BASE/v1/cnpj/00000000000191/check")" = 200 ]'
checa "pode pagar (POST) dá 200" '[ "$("${CURL[@]}" -o /dev/null -w "%{http_code}" -X POST -H "content-type: application/json" -d "{\"cnpj\":\"00000000000191\",\"ispb\":\"00000000\"}" "$BASE/v1/pagamento/check")" = 200 ]'
checa "explorador com busca dá 200" '[ "$("${CURL[@]}" -o /dev/null -w "%{http_code}" "$BASE/v1/dados/ncm?q=busca-secreta-smoke")" = 200 ]'
checa "corpo grande é recusado (413)" '[ "$(head -c 20000 /dev/zero | tr "\0" a | "${CURL[@]}" -o /dev/null -w "%{http_code}" -X POST -H "content-type: application/json" --data-binary @- "$BASE/v1/pagamento/check")" = 413 ]'

# Um X-Forwarded-For falso a cada pedido NÃO pode burlar o limite de taxa (o proxy o sobrescreve): deve aparecer 429.
# (O limite é de 30 por minuto por origem; aguarde 1 minuto para rodar o smoke de novo.)
n429=0
for i in $(seq 1 45); do
  c=$("${CURL[@]}" -o /dev/null -w "%{http_code}" -H "X-Forwarded-For: 10.9.$((i % 250)).$((i % 200))" "$BASE/v1/dados/ufs")
  [ "$c" = 429 ] && n429=$((n429 + 1))
done
checa "X-Forwarded-For falso não burla o limite de taxa ($n429 respostas 429)" '[ "$n429" -ge 1 ]'

if [ -f docker-compose.yml ] && docker compose ps >/dev/null 2>&1; then
  sleep 1
  logs=$(docker compose logs --no-color 2>&1)
  checa "logs sem o CNPJ consultado"      '! grep -q "00000000000191" <<<"$logs"'
  checa "logs sem o termo buscado"        '! grep -q "busca-secreta-smoke" <<<"$logs"'
  checa "logs sem campos de IP/URL de cliente" '! grep -Eq "\"remote_ip\"|\"client_ip\"|\"uri\"|/v1/cnpj/[0-9A-Za-z]{14}" <<<"$logs"'
else
  echo "  (sem docker compose neste diretório: verificação dos logs pulada)"
fi
echo
[ "$falhas" -eq 0 ] && echo "TUDO CERTO" || { echo "$falhas falha(s)"; exit 1; }
