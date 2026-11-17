# Pendências (priorizadas)

| ID | Pendência | Quem | Prioridade |
|---|---|---|---|
| T1 | Criar **e-mail dedicado de privacidade** (não usar o pessoal) e rótulo `privacidade` nas issues | Mantenedor | Alta (antes de publicar) |
| T2 | Escolher hospedagem/região; avaliar transferência internacional (Res. CD/ANPD 19/2024, 32/2026) | Mantenedor | Alta (M4) |
| T3 | Hospedagem da BrasilAPI conferida pelos cabeçalhos (Cloudflare/Vercel, função nos EUA): mitigado por só enviar identificadores públicos. Termos de uso e limites ainda a ler | Mantenedor | Baixa |
| T4 | ~~Revisão jurídica~~ **Decisão do mantenedor (2026-11-17): sem revisão por advogado(a)**. Feita revisão assistida por IA: `revisao-conformidade.md`. Não é aconselhamento jurídico; conferir resoluções da ANPD no texto oficial | — | Fechada (com ressalva) |
| T5 | ~~Confirmar ECA Digital~~ Avaliado na revisão por IA: não aplicável; reavaliar se surgir conta ou público infantil | — | Fechada (com ressalva) |
| T6 | Decidir se nomes de sócios entram em algum modo opt-in (hoje omitidos) | Mantenedor | Média |
| T7 | ~~Runbook de incidente~~ **Resolvido (M4.3)**: `incidents/` (runbook, registro, exercício no papel); falta o exercício cronometrado com pessoas, por instância | — | Fechada |
| T8 | Teste de invasão/revisão de segurança independente | Terceiro | Média (M4) |
| T9 | Empresário individual/MEI: nome omitido pode reduzir a utilidade; reavaliar com o uso real | Mantenedor | Baixa |
| T10 | ~~`/docs` (Swagger) usa CDN~~ **Resolvido (M4.2)**: desligado em produção (compose não define `CONFERE_DOCS`; `smoke.sh` confere) | — | Fechada |
| T11 | ~~`CONFERE_CONFIAR_PROXY` exige um proxy~~ **Resolvido (M4.2)**: Caddy sobrescreve `X-Forwarded-For`; `smoke.sh` prova que um valor falso não burla o limite | — | Fechada |
| T12 | ~~CSP como cabeçalho~~ **Resolvido (M4.2)**: Caddyfile envia CSP (com `frame-ancestors 'none'`) e serve o SPA com fallback | — | Fechada |
| T13 | ~~Proxy sem query string em log~~ **Resolvido (M4.2)**: Caddy sem log de acesso e logs de erro sem IP/URI/cabeçalhos; `smoke.sh` confere os logs | — | Fechada |
| T14 | A fonte (CVM via BrasilAPI) tem nomes com acentos trocados (ex.: "T-TULOS"); apenas documentado, não corrigimos o dado público | — | Baixa |
| T15 | Marco Civil, art. 15: instância operada por PJ com atividade econômica organizada deve guardar registros de acesso por 6 meses, o que colide com "sem IP em log"; decidir por instância | Mantenedor da instância | Média (por instância) |
| T16 | Preencher `instancia-modelo.md` (controlador, endereço, e-mail, hospedagem) e a política v1.1 antes de anunciar uma instância pública | Mantenedor | Alta (antes de anunciar) |
