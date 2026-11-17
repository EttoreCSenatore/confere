---
id: pode-pagar
title: Pode pagar?
---

# Pode pagar? (CNPJ + banco + Pix)

## Como usar

Na aba **Pode pagar?**, informe o CNPJ de quem recebe e a instituição dele, por **ISPB** (8 dígitos) ou pelo **código do banco** (1 a 3 dígitos). O app confere a empresa e confirma se a instituição existe e participa do Pix.

![Resultado de uma instituição que participa do Pix](/img/screenshots/app-pode-pagar.png)

## Quando há alerta

Se a instituição não consta nas listas do Banco Central, ou existe mas não participa do Pix, o nível sobe para **Indícios altos** e o motivo aparece nos sinais. Os sinais da empresa e os da instituição se somam.

![Resultado com instituição não encontrada](/img/screenshots/app-pode-pagar-alto.png)

## O que isso não faz

O Confere **não verifica o titular da chave Pix** nem a conta de destino: a BrasilAPI não oferece isso. Esse limite aparece sempre no resultado. Os dados vão no corpo de um `POST`, e não na URL.
