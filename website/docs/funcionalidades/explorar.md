---
id: explorar
title: Explorar dados abertos
---

# Explorar dados abertos

## Escolher o conjunto

A aba **Explorar** reúne cinco conjuntos públicos: **Bancos** (Banco Central, com a indicação de quem participa do Pix), **Participantes do Pix**, **Municípios** (IBGE), **NCM** (classificação de mercadorias) e **Corretoras (CVM)**.

![Lista de bancos](/img/screenshots/app-explorar.png)

## Buscar e filtrar

Digite na busca: **todas as palavras** precisam aparecer, sem diferença de acentos ou maiúsculas (`cafe` acha "Café"). No NCM, `0901` acha `09.01`. **Municípios** pedem uma UF; **Corretoras** aceitam UF e situação como filtros.

![Municípios de uma UF](/img/screenshots/app-explorar-municipios.png)

![Busca no NCM](/img/screenshots/app-explorar-ncm.png)

## De uma linha para a conferência

Nas corretoras, **Conferir CNPJ** abre a conferência já com o CNPJ preenchido. Em bancos e participantes do Pix, **Pode pagar?** abre a aba certa com o ISPB. O valor vai pela memória do roteador, não pela URL.

![Corretoras da CVM](/img/screenshots/app-explorar-corretoras.png)

## Baixar CSV

**Baixar CSV** exporta **todas as linhas do filtro** atual (não só a página). O arquivo é UTF-8 com BOM, para o Excel abrir os acentos certos. Células que começam com `=`, `+`, `-` ou `@` ganham um apóstrofo na frente, para que nenhuma planilha as execute como fórmula (injeção de fórmula).

## Limites e privacidade

- A busca roda na **memória do servidor**: o texto digitado nunca é enviado à BrasilAPI. As listas ficam em cache por 24 horas.
- Das corretoras, **e-mail, telefone e endereço não são exibidos**: só dados de identificação e situação.
- Os dados são mostrados como as fontes publicam, inclusive erros de origem (por exemplo, acentos trocados em alguns nomes da CVM).
