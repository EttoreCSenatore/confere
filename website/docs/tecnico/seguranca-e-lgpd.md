---
id: seguranca-e-lgpd
title: Segurança e LGPD
---

# Segurança e LGPD

O Confere trata **dados públicos**, mas alguns deles são **dados pessoais** (por exemplo, nome e endereço de um empresário individual ou MEI, e o quadro de sócios). A [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2018/lei/l13709.htm) vale mesmo para dados de acesso público (art. 7º, §§ 3º e 4º). O projeto segue as skills de [goul4rt/lgpd-skills](https://github.com/goul4rt/lgpd-skills); os artefatos ficam em `.lgpd/`.

## Privacidade por padrão

> Implementado na API (M1.1) e coberto por testes automáticos, inclusive um que falha se o log contiver IP ou CNPJ.

| Medida | Como |
|---|---|
| Sem conta e sem histórico | Nenhuma consulta é gravada em banco. |
| Sem IP em log | O log de acesso não registra IP, URL com CNPJ nem cabeçalhos. |
| Limite de taxa em memória | O contador por IP vive só em memória e some em 1 minuto. |
| Minimização | Nomes de sócios não são devolvidos; só quantidade e qualificação. |
| Logs sem URL | A biblioteca HTTP também é silenciada: ela registraria a URL com o CNPJ. |
| Cópia local dos dados abertos | As listas públicas vêm de uma cópia no repositório, sem contato nem endereço de corretoras: o explorador não precisa chamar a BrasilAPI. |
| Busca fora da fonte | No explorador, o texto buscado é filtrado na memória e nunca vai à BrasilAPI. |
| Cache curto | Respostas públicas ficam só em memória, com validade curta. |

## Segurança

- Entrada validada (CNPJ com dígitos verificadores) e **lista de permissão** de destinos: só a BrasilAPI é chamada.
- Tempo limite e novas tentativas controladas; se a BrasilAPI cair, o erro é claro e nada é inventado.
- Contêiner sem privilégio, dependências e segredos verificados na CI.
- Cabeçalhos de segurança e CORS restritivo.

## Limites

O Confere mostra **indícios** a partir de dados públicos, não prova fraude. Por decisão do mantenedor **não há revisão por advogado(a)**: os artefatos `.lgpd/` foram revisados por IA. Nada aqui é aconselhamento jurídico, e as resoluções da ANPD devem ser conferidas no texto oficial.

## Revisão de conformidade

A revisão (`.lgpd/revisao-conformidade.md`) confere cada artefato contra o código e os testes. Ela achou e corrigiu lacunas: identificação do controlador por instância, prazos e artigos 18 e 20 na política, runbook de incidente, rotação limitada de logs e um teste que impede o proxy de voltar a registrar IP e URL. Ficaram em aberto o e-mail dedicado de privacidade, a hospedagem e o artigo 15 do Marco Civil (por instância).

![Artefatos de conformidade em .lgpd](/img/screenshots/lgpd-artefatos.png)

## Quem é o controlador

O projeto é software livre. **Quem hospeda uma instância é o controlador** dos dados tratados nela. A instância pública de demonstração é operada pelo mantenedor do projeto.
