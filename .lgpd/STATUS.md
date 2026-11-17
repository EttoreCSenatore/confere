# Estado da conformidade LGPD — Confere

Última atualização: 2026-11-17 (M4.1: CLI sem estado; M3: explorador de dados abertos, busca só na memória, corretoras minimizadas; M2: interface web sem terceiros, CSP e testes de privacidade; M1.2: "pode pagar?" implementado; M1.1: API do CNPJ; controles de log, minimização, limite e cache cobertos por testes). Pipeline: **A (greenfield)**, skills de [goul4rt/lgpd-skills](https://github.com/goul4rt/lgpd-skills). **Não é aconselhamento jurídico**; todas as minutas aguardam revisão de advogado(a).

## Enquadramento

| Pergunta | Resposta | Observação |
|---|---|---|
| Cenário | A, projeto novo, privacidade desde o desenho | |
| Papel do projeto | Software livre. **Quem hospeda uma instância é o controlador** dela; a instância pública de demonstração é operada pelo mantenedor | [A CONFIRMAR] |
| Porte | Provável **ATPP** (Res. CD/ANPD nº 2/2022: inclui pessoa natural e entidade sem fins lucrativos), sem tratamento de alto risco | [A CONFIRMAR]; se virar alto risco, deixa de valer |
| ECA Digital (Lei 15.211/2025) | Em princípio **não aplicável**: ferramenta empresarial, sem conta, não direcionada a menores (`eca-digital.md`) | [A CONFIRMAR] |
| Dados sensíveis | Nenhum | |

## Artefatos

| Arquivo | Situação |
|---|---|
| `data-map.md` | Rascunho v1 |
| `legal-basis.md` (inclui LIA) | Rascunho v1, ⏸ revisão jurídica |
| `encarregado.md` | Rascunho v1 (canal ATPP) |
| `ROPA.md` | Rascunho v1, ⏸ checkpoint |
| `RIPD.md` | Rascunho v1 preventivo, ⏸ checkpoint |
| `retention.md` | Rascunho v1 |
| `policies/privacy-policy-v1.md` | Minuta, ⏸ checkpoint; publicar só após revisão |
| `vendors/brasilapi.md` | Rascunho v1 |
| `eca-digital.md` | Avaliação v1 |
| `gaps.md` | Pendências priorizadas |
| `incidents/` | Runbook preparatório em M4 |

## Regra do repositório

Todo PR que passe a tratar um dado pessoal novo atualiza `data-map.md`, `ROPA.md` e `gaps.md`.
