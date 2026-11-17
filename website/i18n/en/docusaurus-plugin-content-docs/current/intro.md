---
id: intro
title: Overview
slug: /intro
sidebar_position: 1
---

# Confere

**Confere** ("it checks") is a web app, an API and a command-line tool (CLI) to **check before you pay**: it cross-references public data on companies (CNPJ), banks and Pix participants, and shows **explained** warning signs.

All data comes from [BrasilAPI](https://brasilapi.com.br/), a free and open service. Confere is not a credit analysis and does not prove fraud: it is a **hint based on public data**.

![Confere site home page](/img/screenshots/site-inicio-en.png)

## What it does

| Feature | Purpose |
|---|---|
| **CNPJ check** | Registration status, company age, activity (CNAE), size and warning signs. |
| **Safe to pay?** | Confirms that the bank or institution exists and takes part in Pix, and cross-checks it with the payee's CNPJ. |
| **Open-data explorer** | Banks, municipalities, NCM codes and brokers with search, filters and CSV export. |
| **CLI and API** | The same features to automate your checks (`confere cnpj ...`). |

## Principles

- **Privacy by default**: no account, no history of your lookups and no IP in logs. See [Security and LGPD](tecnico/seguranca-e-lgpd.md).
- **Explainable**: every risk signal shows the rule that produced it.
- **Free software**: code under AGPL-3.0-or-later, documentation under CC BY-SA 4.0. See [License](licenca.md).
- **Bilingual**: documentation in Portuguese and English.

## Current status

Foundation (M0), the **check API** (CNPJ and "safe to pay?", M1) the bilingual **web interface** (M2) and the **open-data explorer** (M3) the **CLI** (M4.1) and the Docker + Caddy **deployment** (M4.2) are done. See the [features](funcionalidades/conferir-empresa.md), the [API](tecnico/api.md) and the [roadmap](roadmap.md).
