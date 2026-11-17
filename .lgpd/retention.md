# Retenção (v1, rascunho)

| Dado | Onde | Prazo |
|---|---|---|
| Resposta pública da BrasilAPI | Cache em memória do processo | 10 min (TTL); some ao reiniciar |
| IP (limite de taxa) | Memória | 60 s |
| Log da API e do proxy | Só método, rota genérica, status, latência (sem IP, CNPJ, busca ou cabeçalhos); Caddy sem log de acesso e com erros sem IP/URI | Rotação limitada do Docker (até 5 × 10 MB por contêiner); não há prazo em dias |
| Registro de acesso do Marco Civil (art. 15) | **Não existe por padrão.** Só em instância operada por PJ com atividade econômica organizada, por decisão dessa instância (`instancia-modelo.md`) | 6 meses, acesso restrito |
| Backups | Não há; nada é persistido | n/a |
