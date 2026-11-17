---
id: roadmap
title: Roadmap
sidebar_position: 3
---

# Roadmap

Each step becomes a pull request, reviewed and merged before the next one. Documentation (pt-BR and English) and LGPD artifacts are updated at every step.

| Step | Deliverable | Status |
|---|---|---|
| **M0** | Foundation: repository, license, bilingual documentation on GitHub Pages, CI, LGPD artifacts (data map, legal bases, ROPA, DPIA, policy) | Done |
| **M1.1** | API: CNPJ validation, BrasilAPI client, explainable risk engine, in-memory cache, rate limiting | Done (see [API](tecnico/api.md)) |
| **M1.2** | API: "safe to pay?" (CNPJ + bank + Pix participant) | Done (see [API](tecnico/api.md)) |
| **M2** | Bilingual web interface (Check, Explore, API/CLI) | Done (see [Features](funcionalidades/conferir-empresa.md)) |
| **M3** | Open-data explorer (banks, municipalities, NCM, brokers) with CSV | Done (see [Explore](funcionalidades/explorar.md)) |
| **M4.1** | CLI (thin API client; see [CLI](funcionalidades/cli.md)) | Done |
| **M4.2** | Deployment (Docker, unprivileged user, proxy with CSP), security CI (see [Deployment](tecnico/implantacao.md)) | Done |
| **M4.3** | Final compliance (LGPD, AI-assisted, no lawyer) and security review | Done |

## Out of scope

- Keeping a lookup history or creating user accounts.
- Verifying the holder of a Pix key: only the existence and Pix participation of the institution.
- Any own credit score or "blacklist".
