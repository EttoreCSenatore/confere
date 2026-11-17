---
id: roadmap
title: Roadmap
sidebar_position: 3
---

# Roadmap

Cada etapa vira um pull request, revisado e integrado antes da próxima. Documentação (pt-BR e inglês) e artefatos de LGPD são atualizados a cada etapa.

| Etapa | Entrega | Estado |
|---|---|---|
| **M0** | Fundação: repositório, licença, documentação bilíngue no GitHub Pages, CI, artefatos de LGPD (mapa de dados, bases legais, ROPA, RIPD, política) | Em andamento |
| **M1.1** | API: validação de CNPJ, cliente BrasilAPI, motor de risco explicável, cache em memória, limite de taxa | Planejado |
| **M1.2** | API: "pode pagar?" (CNPJ + banco + participante do Pix) | Planejado |
| **M2** | Interface web bilíngue (Conferir, Explorar, API/CLI) | Planejado |
| **M3** | Explorador de dados abertos (bancos, municípios, NCM, corretoras) com CSV | Planejado |
| **M4** | CLI publicável, implantação (Docker, usuário sem privilégio), CI de segurança e revisão final | Planejado |

## Fora do escopo

- Guardar histórico de consultas ou criar contas de usuário.
- Verificar o titular de uma chave Pix: só a existência e a participação da instituição.
- Qualquer nota de crédito ou "lista suja" própria.
