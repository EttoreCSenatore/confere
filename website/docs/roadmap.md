---
id: roadmap
title: Roadmap
sidebar_position: 3
---

# Roadmap

Cada etapa vira um pull request, revisado e integrado antes da próxima. Documentação (pt-BR e inglês) e artefatos de LGPD são atualizados a cada etapa.

| Etapa | Entrega | Estado |
|---|---|---|
| **M0** | Fundação: repositório, licença, documentação bilíngue no GitHub Pages, CI, artefatos de LGPD (mapa de dados, bases legais, ROPA, RIPD, política) | Concluído |
| **M1.1** | API: validação de CNPJ, cliente BrasilAPI, motor de risco explicável, cache em memória, limite de taxa | Concluído (ver [API](tecnico/api.md)) |
| **M1.2** | API: "pode pagar?" (CNPJ + banco + participante do Pix) | Concluído (ver [API](tecnico/api.md)) |
| **M2** | Interface web bilíngue (Conferir, Explorar, API/CLI) | Concluído (ver [Funcionalidades](funcionalidades/conferir-empresa.md)) |
| **M3** | Explorador de dados abertos (bancos, municípios, NCM, corretoras) com CSV | Concluído (ver [Explorar](funcionalidades/explorar.md)) |
| **M4.1** | CLI (cliente fino da API; ver [CLI](funcionalidades/cli.md)) | Concluído |
| **M4.2** | Implantação (Docker, usuário sem privilégio, proxy com CSP), CI de segurança (ver [Implantação](tecnico/implantacao.md)) | Concluído |
| **M4.3** | Revisão final de conformidade (LGPD, por IA, sem advogado) e de segurança | Concluído |

## Fora do escopo

- Guardar histórico de consultas ou criar contas de usuário.
- Verificar o titular de uma chave Pix: só a existência e a participação da instituição.
- Qualquer nota de crédito ou "lista suja" própria.
