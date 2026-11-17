# Revisão de conformidade (LGPD) — Confere

**Data**: 2026-11-17 · **Quem revisou**: Claude (IA), no papel de "revisor jurídico simulado", seguindo as skills de [goul4rt/lgpd-skills](https://github.com/goul4rt/lgpd-skills) · **Decisão do mantenedor**: não haverá revisão por advogado(a).

> **Limite honesto**: esta é uma revisão assistida por IA. **Não é aconselhamento jurídico** e não substitui um profissional. Ela confere os artefatos `.lgpd/` contra o código e os testes reais e contra os dispositivos citados. As resoluções da ANPD (2/2022, 15/2024, 18/2024, 19/2024, 32/2026) **não estão** em `ctresb/leis`: foram citadas como constam nas skills e devem ser conferidas no texto oficial antes de qualquer afirmação pública. Quem hospeda uma instância é o controlador dela e responde por ela.

## 1. Resumo

| Área | Resultado |
|---|---|
| Bases legais e LIA | Coerentes com o que o código faz; um ponto de atenção (MEI/EI) tratado por minimização |
| Princípios do art. 6º | Atendidos, cada um com evidência no código ou nos testes (tabela 2) |
| Transparência (art. 9º) | **Lacunas corrigidas** nesta revisão: identificação do controlador por instância, prazos, art. 18 e art. 20 |
| Direitos do titular (art. 18) | Fluxo definido; não há o que apagar por consulta; oposição de MEI/EI analisada caso a caso |
| Segurança (arts. 46-49) | Controles verificados por teste automático (log, CSP, limite de taxa, contêiner) |
| Incidentes (art. 48) | Lacuna **corrigida**: runbook, registro e exercício em `incidents/` |
| Transferência internacional | Achado novo: a fonte (BrasilAPI) roda atrás de Cloudflare/Vercel, com função em região dos EUA; mitigado por só enviar identificadores públicos |
| Marco Civil (art. 15) | Achado novo: obrigação de guardar logs de acesso pode colidir com "sem IP em log" para instância operada por PJ com fins econômicos |
| ECA Digital | Não aplicável (ferramenta empresarial, sem conta, sem público infantil) |

## 2. Princípios (art. 6º) e evidências

| Princípio | Evidência |
|---|---|
| Finalidade, adequação | Só conferência de fornecedor/pagamento; nenhum outro uso (sem perfil, histórico, anúncio): `data-map.md`, RIPD |
| Necessidade (minimização) | Nomes de sócios nunca saem (`empresa.py`, testes); MEI/EI sem nome/endereço; corretoras sem e-mail/telefone/endereço (`dados.py`, testes); listas sem logotipo |
| Livre acesso | Resultado mostra a regra e o peso de cada sinal ("Por quê?"); política em `/privacidade` |
| Qualidade | Dados repassados como a fonte publica; erro de origem documentado (T14); nunca "sem risco" por falta de dado (502 em vez de adivinhar) |
| Transparência | Avisos na tela, na API e na CLI: "indício, não prova"; limite do Pix ("não verificamos o titular da chave") |
| Segurança | M4.2: contêiner sem privilégio, CSP, HSTS, limite de corpo, Trivy, gitleaks, SBOM; testes de privacidade de log |
| Prevenção | Sem banco, sem conta: reduz o dano de um vazamento; `smoke.sh` confere os logs |
| Não discriminação | Sem lista negra, sem decisão automatizada, texto contra uso como critério único (política v1.1); RIPD R1 |
| Responsabilização | Este conjunto de artefatos, testes, CI e histórico em PRs |

## 3. Achados e correções

| # | Achado | Dispositivo | Gravidade | Situação |
|---|---|---|---|---|
| R1 | A minuta de política não identificava o controlador nem trazia os prazos e o art. 18 de forma expressa | Art. 9º, III, VI | Média | **Corrigido**: política v1.1 + `instancia-modelo.md` (campos que cada instância preenche) |
| R2 | `encarregado.md` dava 15 dias para qualquer resposta; no regime ATPP a declaração completa pode levar 30 dias (a conferir na resolução) | Art. 19; Res. 2/2022 | Baixa | **Corrigido** (texto ajustado, marcado "a conferir") |
| R3 | Não havia runbook de incidente (T7) | Art. 48; Res. 15/2024 | Média | **Corrigido**: `incidents/runbook.md`, `log.md`, exercício |
| R4 | A retenção de log dizia "7 dias" mas o Docker mantém log sem limite por padrão | Art. 6º, III; 16 | Média | **Corrigido**: rotação limitada no Compose; texto da retenção ajustado para o que existe (log só com método/rota/status/tempo, sem dado pessoal) |
| R5 | A política não dizia como pedir revisão do "indício" | Art. 20 | Baixa | **Corrigido**: parágrafo na v1.1 (o resultado não é decisão automatizada sobre a pessoa; há canal para contestar) |
| R6 | A BrasilAPI está atrás de Cloudflare e Vercel, com função em região dos EUA (cabeçalho `x-vercel-id` mostra `gru1::sfo1`): o CNPJ consultado pode ser processado fora do Brasil | Arts. 33-36; Res. 19/2024 | Média | **Mitigado e documentado** em `vendors/brasilapi.md`: só vai o identificador público; nunca IP nem texto livre; alternativa futura: espelhar a base. Segue como T3 |
| R7 | Marco Civil da Internet, art. 15: provedor de aplicações **constituído como pessoa jurídica, com atividade econômica organizada**, deve guardar registros de acesso por 6 meses. A regra "sem IP em log" pode colidir | Lei 12.965/2014, art. 15 | Média | **Aberto (T15)**: vale só para instâncias de PJ com fins econômicos; a instância pública pessoal/sem fins lucrativos não se enquadra; o deploy documenta a escolha por instância |
| R8 | Dados de MEI/EI são dados pessoais; o tratamento de "dados de acesso público" não dispensa finalidade e boa-fé | Art. 7º, §§ 3º-4º | Baixa | Já mitigado por minimização, LIA e canal de oposição |
| R9 | Local de cada instância (hospedagem) define operador e transferência | Art. 39 | Média | **Aberto (T2)**: decisão do mantenedor quando for hospedar |
| R10 | O e-mail dedicado de privacidade ainda não existe | Art. 41, §2º; Res. 2/2022 art. 11 | Média | **Aberto (T1)**: decisão do mantenedor |

## 4. O que a revisão NÃO cobre

- Validade jurídica dos enquadramentos (ATPP, legítimo interesse para dados de acesso público, ECA Digital): são interpretações razoáveis, não pareceres.
- Texto oficial das resoluções da ANPD e do Marco Civil: conferir na fonte.
- Contratos com o provedor de hospedagem (operador) e a conformidade da própria BrasilAPI.
- Teste de invasão por terceiro: não realizado (verificações automáticas e revisão de código foram feitas, ver `docs` → Segurança).

## 4b. Revisão de segurança do código (feita junto)

| Risco | Verificação |
|---|---|
| Execução de código / injeção | Busca no código por `eval`, `exec`, `subprocess`, `shell=True`, `pickle`, `innerHTML`, `dangerouslySetInnerHTML`: nenhuma ocorrência |
| SSRF e URL montada com texto livre | Cliente da BrasilAPI com endereço-base fixo; só CNPJ normalizado (`^[0-9A-Z]{14}$`) e UF (`^[A-Z]{2}$`) entram na URL; a busca nunca vai à fonte; testes cobrem |
| XSS / clickjacking | React escapa tudo; CSP `default-src 'none'` com `frame-ancestors 'none'` no proxy |
| CSRF | Sem cookies nem sessão; CORS fechado por padrão |
| Negação de serviço | Limite de taxa por origem, corpo de até 16 KB, tempos limite, listas em cache com trava de download único |
| Vazamento em log / erro | Testes automáticos de log; erros de validação não ecoam o valor enviado |
| Injeção de fórmula em CSV | Prefixo `'` em células que começam com `=`, `+`, `-`, `@`; testes |
| Cadeia de suprimentos | `pip-audit`, `npm audit` (com exceção documentada), licenças, SBOM, Trivy, gitleaks, Dependabot |
| Configuração de implantação | `scripts/checar-implantacao.py` (falha em regressão, testado) e `deploy/smoke.sh` |

Não foi feito teste de invasão por terceiro.

## 5. Pendências que dependem de uma pessoa

1. **T1** criar o e-mail dedicado de privacidade (e usá-lo em `CONFERE_ACME_EMAIL` e na política).
2. **T2/T16** escolher a hospedagem e preencher `instancia-modelo.md` antes de anunciar uma instância pública.
3. **T15** decidir, por instância, sobre o art. 15 do Marco Civil.
