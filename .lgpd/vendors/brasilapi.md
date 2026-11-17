# Fornecedor: BrasilAPI (v1, rascunho)

- Papel: **fonte de dados públicos**; recebe apenas CNPJ/ISPB/código e o IP do **servidor** do Confere (nunca da pessoa usuária). Projeto aberto e gratuito, sem contrato.
- Não há DPA possível com um serviço gratuito sem contrato; o risco é mitigado enviando só identificadores públicos.
- Verificado em 2026-11-17 pelos cabeçalhos de resposta: atrás de **Cloudflare** e **Vercel** (`x-vercel-id: gru1::sfo1`: borda em São Paulo, função em São Francisco). Logo, o identificador consultado **pode ser processado nos EUA**. Mitigação: só CNPJ/ISPB/código públicos, nunca IP nem texto livre; a busca do explorador roda localmente. Risco baixo; alternativa futura: espelhar as listas públicas.
- **Reduzido em M5**: as listas de bancos, Pix, municípios, NCM e corretoras vêm de cópia local semanal; a BrasilAPI só recebe, em tempo real, o CNPJ da consulta de empresa (que não dá para copiar) e as listas quando a cópia está velha.
- A conferir (T3, em aberto): termos de uso e limites da BrasilAPI.
