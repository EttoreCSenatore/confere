---
id: conferir-empresa
title: Check a company
---

# Check a company (CNPJ)

## How to use

Open the **Company (CNPJ)** tab, type the payee's CNPJ (with or without punctuation; the alphanumeric CNPJ works too) and click **Check**. The app only checks the format; digit validation and all rules live in the API.

![Home screen with the CNPJ form](/img/screenshots/app-conferir-en.png)

## Reading the result

The top shows the **level** (`No signs in public data`, `Attention` or `High signs`), with an icon and text, never colour alone, and the 0 to 100 score. Below come the signs and the company's public data. "No signs" does **not** mean "safe".

![Result for a company with no signs](/img/screenshots/app-resultado-empresa-en.png)

## Signs and the "Why?" button

Each sign has a message and a **Why?** that opens the exact rule and weight. There is no opaque model: the rules are on the [API](../tecnico/api.md) page.

![Result with attention signs and one rule open](/img/screenshots/app-resultado-atencao-en.png)

## Sole proprietors and MEI

When the CNPJ identifies a person, the app **omits name and address** and says so. Partner names are never shown, only their number and qualification.

![Result for an MEI, with the name omitted](/img/screenshots/app-resultado-mei-en.png)

## When something goes wrong

Errors appear in plain language: invalid CNPJ, not found, too many lookups in a row, or source down. In the last case nothing is made up.

![Invalid CNPJ message](/img/screenshots/app-erro-en.png)
