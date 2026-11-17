---
id: interface
title: Idioma, tema e celular
---

# Idioma, tema e celular

## Idioma

O seletor no topo troca entre **português** e **inglês**. A escolha também vai à API, que devolve as mensagens dos sinais no mesmo idioma. É a **única** coisa que o app guarda no navegador.

![Resultado em inglês](/img/screenshots/app-resultado-empresa-en.png)

## Tema claro e escuro

O app segue o tema do sistema, com contraste suficiente nos dois.

![Resultado no tema escuro](/img/screenshots/app-escuro.png)

## No celular

O layout se adapta a telas estreitas: o menu fica numa linha própria e os dados empilham.

![Resultado no celular](/img/screenshots/app-celular.png)

## Outras páginas

**Explorar** (explorador de dados abertos, chega no M3):

![Página Explorar](/img/screenshots/app-explorar.png)

**API e CLI** (exemplos de uso da API; a CLI chega no M4):

![Página API e CLI](/img/screenshots/app-api.png)

**Privacidade** (resumo em linguagem simples da política):

![Página Privacidade](/img/screenshots/app-privacidade.png)

## Acessibilidade e privacidade no navegador

Há link para pular ao conteúdo, foco visível, rótulos em todos os campos, resultado anunciado a leitores de tela e foco movido para o título do resultado. Os campos usam `autocomplete="off"`, a consulta nunca vai para a URL e a página envia `Referrer-Policy: no-referrer`. O build inclui uma política de segurança de conteúdo (CSP) que só permite recursos do próprio site: sem CDN, sem fontes externas.
