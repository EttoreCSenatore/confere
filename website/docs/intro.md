---
id: intro
title: Visão geral
slug: /intro
sidebar_position: 1
---

# Confere

**Confere** é um aplicativo web, uma API e uma ferramenta de linha de comando (CLI) para **conferir antes de pagar**: ele cruza dados públicos de empresas (CNPJ), bancos e participantes do Pix, e mostra sinais de alerta **explicados**.

Tudo vem da [BrasilAPI](https://brasilapi.com.br/), um serviço gratuito e aberto. O Confere não substitui uma análise de crédito nem prova fraude: é uma **dica baseada em dados públicos**.

![Página inicial do site do Confere](/img/screenshots/site-inicio.png)

## O que ele faz

| Recurso | Para quê |
|---|---|
| **Checagem de CNPJ** | Situação cadastral, idade da empresa, atividade (CNAE), porte e sinais de alerta. |
| **Pode pagar?** | Confirma que o banco ou a instituição existe e participa do Pix, e cruza com o CNPJ de quem recebe. |
| **Explorador de dados abertos** | Bancos, municípios, NCM e corretoras com busca, filtros e exportação CSV. |
| **CLI e API** | Os mesmos recursos para automatizar a conferência (`confere cnpj ...`). |

## Princípios

- **Privacidade por padrão**: sem conta, sem histórico das suas consultas e sem IP em log. Veja [Segurança e LGPD](tecnico/seguranca-e-lgpd.md).
- **Explicável**: cada sinal de risco mostra a regra que o gerou.
- **Software livre**: código sob AGPL-3.0-or-later, documentação sob CC BY-SA 4.0. Veja [Licença](licenca.md).
- **Bilíngue**: documentação em português e inglês.

## Estado atual

Fundação pronta (M0) e **API de conferência de CNPJ** no ar em desenvolvimento (M1.1). Veja a [API](tecnico/api.md) e o [roadmap](roadmap.md).
