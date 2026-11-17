---
id: explorar
title: Explore open data
---

# Explore open data

## Choose the dataset

The **Explore** tab brings together five public datasets: **Banks** (Central Bank, with an indication of who takes part in Pix), **Pix participants**, **Municipalities** (IBGE), **NCM codes** (goods classification) and **Brokers (CVM)**.

![List of banks](/img/screenshots/app-explorar-en.png)

## Search and filter

Type in the search box: **all words** must appear, regardless of accents or case (`cafe` finds "Café"). In NCM, `0901` finds `09.01`. **Municipalities** require a state; **Brokers** accept state and status as filters.

![Municipalities of a state](/img/screenshots/app-explorar-municipios-en.png)

![NCM search](/img/screenshots/app-explorar-ncm-en.png)

## From a row to the check

On brokers, **Check CNPJ** opens the check with the CNPJ already filled in. On banks and Pix participants, **Safe to pay?** opens the right tab with the ISPB. The value travels through the router memory, not the URL.

![CVM brokers](/img/screenshots/app-explorar-corretoras-en.png)

## Download CSV

**Download CSV** exports **every row of the current filter** (not just the page). The file is UTF-8 with a BOM, so Excel opens accents correctly. Cells starting with `=`, `+`, `-` or `@` get a leading apostrophe so no spreadsheet runs them as a formula (formula injection).

## Limits and privacy

- The search runs in the **server memory**: the typed text is never sent to BrasilAPI. The lists are cached for 24 hours.
- For brokers, **e-mail, phone and address are not shown**: only identification and status data.
- Data is shown as the sources publish it, including upstream mistakes (for example swapped accents in some CVM names).
