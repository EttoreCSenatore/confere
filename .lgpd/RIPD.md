# RIPD preventivo (art. 38) — Confere (v1, rascunho ⏸ checkpoint)

Não há tratamento de alto risco evidente (sem dado sensível, sem menores como público, sem decisão automatizada com efeito jurídico). O relatório é **preventivo** por causa do indício de "pontuação".

| # | Risco | Prob. | Impacto | Mitigação | Residual |
|---|---|---|---|---|---|
| R1 | Pontuação de risco prejudicar empresário individual/MEI injustamente | Média | Médio | Texto "indício, não prova"; regras explicadas; sem lista negra; sem decisão automatizada | Baixo |
| R2 | Reidentificação/exposição de sócios | Baixa | Médio | Nomes omitidos; só agregados | Baixo |
| R3 | Vazamento de consultas | Baixa | Médio | Nada é gravado; log sem IP/CNPJ | Muito baixo |
| R4 | Abuso do serviço (varredura em massa de CNPJs) | Média | Médio | Limite de taxa; sem exportação em massa de dados pessoais | Baixo |
| R5 | Indisponibilidade/erro da BrasilAPI levar a conclusão errada | Média | Baixo | Erro explícito; nunca "sem risco" por falta de dado | Baixo |

**Compromisso**: sem perfilamento, sem histórico por pessoa usuária, sem publicidade, sem venda de dados. Se isso mudar, refazer este RIPD.
