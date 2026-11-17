# Política de Privacidade do Confere — v1.1

> **Estado**: minuta revisada por IA em 2026-11-17 (ver `../revisao-conformidade.md`). **Não é aconselhamento jurídico** e não passou por advogado(a). Cada instância preenche os campos entre colchetes com a sua `instancia.md` (modelo em `../instancia-modelo.md`) antes de publicar.

**Quem é o controlador.** O Confere é software livre. Quem hospeda uma instância é o controlador dos dados tratados nela. Nesta instância: **[NOME COMPLETO OU RAZÃO SOCIAL]**, **[CPF/CNPJ]**, **[ENDEREÇO]**. Canal de privacidade: **[E-MAIL DEDICADO]**. **[Encarregado: NOME, ou: controlador de pequeno porte dispensado de indicar encarregado, com canal de comunicação, nos termos da Res. CD/ANPD nº 2/2022]**.

**O que fazemos e por quê (finalidade e base legal).** Você informa um CNPJ, banco ou outro identificador e mostramos dados públicos e indícios explicados, obtidos da BrasilAPI, para ajudar a **prevenir fraudes e conferir quem vai receber um pagamento**. Base legal: **legítimo interesse** (art. 7º, IX) e tratamento de dados de **acesso público** (art. 7º, §§ 3º e 4º, LGPD). Não é prova de fraude nem análise de crédito.

**Que dados tratamos.** O identificador que você digita (CNPJ, ISPB, código de banco ou texto de busca); dados públicos de empresas (alguns são de pessoa física: empresário individual e MEI, por isso mostramos menos); seu endereço IP, **por até 60 segundos, só em memória e sem guardar o valor original**, para limitar abusos. O que você digita na busca do explorador é filtrado na memória do nosso servidor e **não é enviado à BrasilAPI**.

**O que NÃO fazemos.** Não pedimos conta, não gravamos o que você consulta, não registramos seu IP nem o CNPJ nos logs, não usamos cookies de rastreamento, anúncios, perfis ou histórico e não vendemos dados. O navegador guarda só o seu idioma preferido.

**Por quanto tempo.** Respostas públicas ficam em memória por até 10 minutos (listas de dados abertos, até 24 horas) e somem ao reiniciar. Os logs guardam só método, rota genérica, status e tempo, sem dado pessoal, com rotação limitada. **[Se esta instância for obrigada a guardar registros de acesso (Marco Civil da Internet, art. 15), descreva aqui: o quê, por quanto tempo (6 meses), com acesso restrito e sem outro uso.]**

**Com quem compartilhamos.** Enviamos à BrasilAPI **só o identificador consultado** (nunca o seu IP). A BrasilAPI é a fonte dos dados e usa a infraestrutura de terceiros (por exemplo, Cloudflare e Vercel), que pode processar fora do Brasil; por isso só enviamos identificadores públicos. A hospedagem desta instância é **[PROVEDOR, PAÍS]** e atua como operadora. Não há outros destinatários.

**Seus direitos (art. 18 da LGPD).** Você pode pedir confirmação do tratamento, acesso, correção, anonimização, bloqueio ou eliminação, portabilidade, informação sobre compartilhamento e revogação, e **se opor** a tratamento feito com base em legítimo interesse (art. 18, § 2º). O canal é gratuito. Respondemos em formato simplificado de imediato e com declaração completa em até **[15 dias; 30 dias para controlador de pequeno porte, conforme a Res. CD/ANPD nº 2/2022]**. Se você é empresário individual ou MEI e quer se opor ao tratamento do seu CNPJ, escreva para o canal acima. Como não guardamos dados por consulta, em geral a resposta é que não há o que apagar.

**Decisões e o "indício" (art. 20).** O Confere **não toma decisões sobre pessoas**: ele mostra indícios com a regra de cada um ("Por quê?"). Não use o resultado como único critério para negar serviço, crédito ou contrato a alguém, nem para discriminar. Se você acha que um indício está errado ou foi usado contra você, escreva para o canal acima e peça revisão.

**Segurança.** Conexão cifrada (HTTPS), validação de entrada, destinos restritos, sem banco de dados, contêiner sem privilégio, política de segurança de conteúdo e verificações automáticas. Incidentes seguem o runbook em `incidents/runbook.md` e a Res. CD/ANPD nº 15/2024.

**Transferência internacional.** Ver "Com quem compartilhamos". **[Se a hospedagem for fora do Brasil, indique o país e o mecanismo (adequação ou cláusulas-padrão).]**

**Crianças e adolescentes.** O serviço é uma ferramenta empresarial, sem conta, e não é direcionado a menores.

**Mudanças.** Esta política é versionada no repositório (`.lgpd/policies/`). Mudanças relevantes são anunciadas na página de privacidade.
