---
id: seguranca-e-lgpd
title: Security and LGPD
---

# Security and LGPD

Confere processes **public data**, but some of it is **personal data** (for example the name and address of a sole proprietor or MEI, and the list of partners). The [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2018/lei/l13709.htm) (Brazil's data protection law) applies even to publicly accessible data (art. 7, §§ 3 and 4). The project follows the skills from [goul4rt/lgpd-skills](https://github.com/goul4rt/lgpd-skills); the artifacts live in `.lgpd/`.

## Privacy by default

> Implemented in the API (M1.1) and covered by automated tests, including one that fails if the log contains an IP or a CNPJ.

| Measure | How |
|---|---|
| No account and no history | No lookup is written to a database. |
| No IP in logs | The access log does not record IP, URLs containing a CNPJ or headers. |
| In-memory rate limit | The per-IP counter lives only in memory and disappears after 1 minute. |
| Minimization | Partner names are not returned; only count and qualification. |
| No URLs in logs | The HTTP library is silenced too: it would log the URL with the CNPJ. |
| Search stays off the source | In the explorer, the searched text is filtered in memory and never sent to BrasilAPI. |
| Short cache | Public responses are kept in memory only, with a short expiry. |

## Security

- Validated input (CNPJ with check digits) and a destination **allowlist**: only BrasilAPI is called.
- Timeout and controlled retries; if BrasilAPI is down, the error is clear and nothing is made up.
- Unprivileged container, dependencies and secrets scanned in CI.
- Security headers and restrictive CORS.

## Limits

Confere shows **indications** from public data, not proof of fraud. The `.lgpd/` artifacts are **drafts**: they need review by a lawyer before a public instance is announced. This documentation is not legal advice.

## Who is the controller

The project is free software. **Whoever hosts an instance is the controller** of the data processed on it. The public demo instance is operated by the project maintainer.
