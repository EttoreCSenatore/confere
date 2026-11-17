---
id: pode-pagar
title: Safe to pay?
---

# Safe to pay? (CNPJ + bank + Pix)

## How to use

On the **Safe to pay?** tab, enter the payee's CNPJ and their institution, by **ISPB** (8 digits) or by **bank code** (1 to 3 digits). The app checks the company and confirms whether the institution exists and takes part in Pix.

![Result for an institution that takes part in Pix](/img/screenshots/app-pode-pagar-en.png)

## When there is a warning

If the institution is not in the Central Bank lists, or exists but does not take part in Pix, the level rises to **High signs** and the reason shows in the signs. Company signs and institution signs add up.

![Result with institution not found](/img/screenshots/app-pode-pagar-alto-en.png)

## What this does not do

Confere does **not verify the Pix key holder** or the destination account: BrasilAPI does not offer that. This limit is always shown in the result. The data goes in the body of a `POST`, not in the URL.
