# Estado da conformidade LGPD — Confere

Última atualização: 2026-11-17 (M5: cópia local semanal dos dados abertos, menos dependência da BrasilAPI; M4.3: revisão de conformidade assistida por IA em `revisao-conformidade.md`, política v1.1, runbook de incidente, ficha da instância; sem revisão por advogado(a), por decisão do mantenedor) (M4.2: implantação com Docker/Caddy, logs sem identificadores verificados por `smoke.sh`, T10-T13 fechadas; M4.1: CLI sem estado; M3: explorador de dados abertos, busca só na memória, corretoras minimizadas; M2: interface web sem terceiros, CSP e testes de privacidade; M1.2: "pode pagar?" implementado; M1.1: API do CNPJ; controles de log, minimização, limite e cache cobertos por testes). Pipeline: **A (greenfield)**, skills de [goul4rt/lgpd-skills](https://github.com/goul4rt/lgpd-skills). **Não é aconselhamento jurídico**. Por decisão do mantenedor **não haverá revisão por advogado(a)**: os artefatos foram revisados por IA (`revisao-conformidade.md`); quem hospeda uma instância responde por ela e deve conferir as resoluções da ANPD no texto oficial.

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
| `legal-basis.md` (inclui LIA) | v1, revisado por IA |
| `encarregado.md` | Rascunho v1 (canal ATPP) |
| `ROPA.md` | Rascunho v1, ⏸ checkpoint |
| `RIPD.md` | Rascunho v1 preventivo, ⏸ checkpoint |
| `retention.md` | Rascunho v1 |
| `policies/privacy-policy-v1.md` | v1.1, preencher campos da instância (`instancia-modelo.md`) antes de publicar |
| `vendors/brasilapi.md` | Rascunho v1 |
| `eca-digital.md` | Avaliação v1 |
| `gaps.md` | Pendências priorizadas |
| `incidents/` | Runbook, registro e exercício no papel (M4.3) |
| `revisao-conformidade.md` | Revisão por IA (M4.3) com achados R1-R10 |
| `instancia-modelo.md` | Ficha que cada instância preenche |

## Regra do repositório

Todo PR que passe a tratar um dado pessoal novo atualiza `data-map.md`, `ROPA.md` e `gaps.md`.
