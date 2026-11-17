# Retenção (v1, rascunho)

| Dado | Onde | Prazo |
|---|---|---|
| Resposta pública da BrasilAPI | Cache em memória do processo | 10 min (TTL); some ao reiniciar |
| IP (limite de taxa) | Memória | 60 s |
| Log de acesso | Sem IP, sem CNPJ, sem cabeçalhos | 7 dias (só método, rota genérica, status, latência) |
| Backups | Não há; nada é persistido | n/a |
