---
id: conferir-empresa
title: Conferir uma empresa
---

# Conferir uma empresa (CNPJ)

## Como usar

Abra a aba **Empresa (CNPJ)**, digite o CNPJ de quem vai receber (com ou sem pontuação; o CNPJ alfanumérico também vale) e clique em **Conferir**. O app só confere o formato; a validação dos dígitos e todas as regras ficam na API.

![Tela inicial com o formulário de CNPJ](/img/screenshots/app-conferir.png)

## Lendo o resultado

O topo mostra o **nível** (`Sem indícios nos dados públicos`, `Atenção` ou `Indícios altos`), com ícone e texto, nunca só cor, e a pontuação de 0 a 100. Abaixo vêm os sinais e os dados públicos da empresa. "Sem indícios" **não** quer dizer "seguro".

![Resultado de uma empresa sem sinais](/img/screenshots/app-resultado-empresa.png)

## Sinais e o botão "Por quê?"

Cada sinal tem uma mensagem e um **Por quê?** que abre a regra exata e o peso. Não há modelo opaco: as regras estão na página [API](../tecnico/api.md).

![Resultado com sinais de atenção e uma regra aberta](/img/screenshots/app-resultado-atencao.png)

## Empresário individual e MEI

Quando o CNPJ identifica uma pessoa, o app **omite nome e endereço** e avisa. Nomes de sócios nunca são exibidos, só a quantidade e a qualificação.

![Resultado de um MEI, com nome omitido](/img/screenshots/app-resultado-mei.png)

## Quando dá erro

Os erros aparecem em linguagem simples: CNPJ inválido, não encontrado, muitas consultas seguidas ou fonte fora do ar. Nesse último caso nada é inventado.

![Mensagem de CNPJ inválido](/img/screenshots/app-erro.png)
