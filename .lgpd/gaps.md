# Pendências (priorizadas)

| ID | Pendência | Quem | Prioridade |
|---|---|---|---|
| T1 | Criar **e-mail dedicado de privacidade** (não usar o pessoal) e rótulo `privacidade` nas issues | Mantenedor | Alta (antes de publicar) |
| T2 | Escolher hospedagem/região; avaliar transferência internacional (Res. CD/ANPD 19/2024, 32/2026) | Mantenedor | Alta (M4) |
| T3 | Conferir termos e hospedagem da BrasilAPI | Claude/Mantenedor | Média |
| T4 | **Revisão jurídica** de LIA, política, ROPA, RIPD, enquadramento ATPP | Advogado(a) | Alta (antes de anunciar instância pública) |
| T5 | Confirmar não aplicabilidade do ECA Digital | Advogado(a) | Média |
| T6 | Decidir se nomes de sócios entram em algum modo opt-in (hoje omitidos) | Mantenedor + advogado(a) | Média |
| T7 | Runbook de incidente (mesmo sem dado guardado) e simulação | Claude/Mantenedor | Média (M4) |
| T8 | Teste de invasão/revisão de segurança independente | Terceiro | Média (M4) |
| T9 | Empresário individual/MEI: nome omitido pode reduzir a utilidade; reavaliar com advogado(a) | Mantenedor | Baixa |
| T10 | ~~`/docs` (Swagger) usa CDN~~ **Resolvido (M4.2)**: desligado em produção (compose não define `CONFERE_DOCS`; `smoke.sh` confere) | — | Fechada |
| T11 | ~~`CONFERE_CONFIAR_PROXY` exige um proxy~~ **Resolvido (M4.2)**: Caddy sobrescreve `X-Forwarded-For`; `smoke.sh` prova que um valor falso não burla o limite | — | Fechada |
| T12 | ~~CSP como cabeçalho~~ **Resolvido (M4.2)**: Caddyfile envia CSP (com `frame-ancestors 'none'`) e serve o SPA com fallback | — | Fechada |
| T13 | ~~Proxy sem query string em log~~ **Resolvido (M4.2)**: Caddy sem log de acesso e logs de erro sem IP/URI/cabeçalhos; `smoke.sh` confere os logs | — | Fechada |
| T14 | A fonte (CVM via BrasilAPI) tem nomes com acentos trocados (ex.: "T-TULOS"); apenas documentado, não corrigimos o dado público | — | Baixa |
