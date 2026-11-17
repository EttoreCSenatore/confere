# ROPA — Registro de operações (art. 37) — v1, rascunho ⏸ checkpoint

Controlador: mantenedor da instância (instância de demonstração: projeto Confere). Canal: ver `encarregado.md`.

| ID | Finalidade | Dados | Base legal | Compartilhamento | Retenção | Segurança |
|---|---|---|---|---|---|---|
| A001 | Checar CNPJ | CNPJ, dados cadastrais públicos | Legítimo interesse; art. 7º §§ 3º-4º | BrasilAPI (só CNPJ) | Cache de memória, TTL 10 min | TLS, validação, lista de destinos, QSA minimizado |
| A002 | "Pode pagar?" | CNPJ, ISPB/banco | Idem | BrasilAPI | Idem | Idem |
| A003 | Explorar dados abertos | Dados de PJ e tabelas públicas | Idem | BrasilAPI | Cache de memória | Idem |
| A004 | Limite de taxa e segurança | IP | Legítimo interesse | Nenhum | 60 s em memória | Sem log de IP |

Operador/terceiros: BrasilAPI (fonte, ver `vendors/brasilapi.md`) e hospedagem (T2). Transferência internacional: a definir (T2).
