# Runbook de incidente de segurança — Confere (v1)

Base: LGPD art. 48 e Res. CD/ANPD nº 15/2024 (conferir no texto oficial). Aplica-se a **cada instância com dados reais de usuários**; quem hospeda é o controlador e assina as comunicações. Esta é uma minuta produzida com IA, não aconselhamento jurídico.

## O que pode dar errado no Confere (e o que está em jogo)

O Confere **não guarda** consultas, contas nem histórico. O dano potencial é menor, mas existe:

| Cenário | Dados em risco | Gravidade típica |
|---|---|---|
| C1. Regressão que volta a gravar IP/CNPJ/busca em log (proxy, API ou plataforma) | Quem consultou o quê | Média |
| C2. Servidor/contêiner comprometido | Tráfego em memória por até 10 min; IPs (HMAC) por 60 s; acesso ao proxy | Média |
| C3. Dependência ou imagem comprometida (cadeia de suprimentos) | Idem C2, mais execução de código | Alta |
| C4. Abuso: varredura em massa de CNPJs/MEI por terceiros | Dados públicos de MEI/EI já minimizados | Baixa |
| C5. Falha da BrasilAPI ou dado público errado exibido como certo | Indício incorreto sobre uma empresa | Baixa |

## Fases

1. **T+0 — ciência.** Registre data/hora **com fuso** de quando soube que dados pessoais foram afetados (marco dos prazos). Abra uma entrada em `log.md`.
2. **T+0 a T+4 h — conter e preservar.**
   - C1: reverta a mudança; rode `deploy/smoke.sh` (confere os logs); apague/rode a rotação dos logs afetados **depois** de copiar as evidências.
   - C2/C3: derrube o contêiner (`docker compose down`), troque a imagem por uma versão anterior conhecida, gire o certificado se o volume `caddy_data` pode ter vazado. Preserve `docker compose logs` e o `docker save` das imagens antes de reconstruir.
   - Não há banco nem sessões para revogar.
3. **T+4 h a T+24 h — escopo e triagem.** Responda: o que vazou, de quantas pessoas, por quanto tempo? Os dados estavam em memória, em log ou só em trânsito? Havia dado de criança, financeiro, de autenticação ou em larga escala? Aplique o critério **cumulativo** do art. 5º da Res. 15/2024 (risco/dano relevante **e** pelo menos uma das categorias). Registre a decisão e o motivo, **mesmo se não for notificável**.
4. **Prazo de comunicação.** Se notificável: ANPD e titulares em **3 dias úteis** da ciência (**6 dias úteis** no regime ATPP elegível, salvo risco à integridade física/moral ou à segurança pública), conforme a resolução. Use o canal oficial da ANPD. Conteúdo mínimo: natureza do incidente, dados e titulares afetados, medidas técnicas, riscos, o que foi feito, contato.
5. **Aos titulares.** Como o Confere não identifica quem consultou, a divulgação será **pública** (página do projeto e da instância) por no mínimo 3 meses, com linguagem simples, quando não for possível avisar individualmente.
6. **Pós-incidente.** Causa raiz, correção com teste que falha antes e passa depois, atualização de `ROPA.md`, `RIPD.md`, `data-map.md` e `gaps.md`, complemento da comunicação (até 20 dias úteis; 40 em ATPP) quando couber.
7. **Registro por 5 anos** em `log.md`, **inclusive incidentes não notificados** (art. 10 da Res. 15/2024).

## Quem faz o quê

| Papel | Quem |
|---|---|
| Responsável pela instância (controlador) | Mantenedor da instância |
| Detecção e contenção técnica | Operação da instância (pode ser a mesma pessoa) |
| Comunicação à ANPD e aos titulares | Controlador |
| Contato do hospedeiro (operador) | Definido na ficha da instância |

## Contatos e canais

Preencha na ficha da instância (`instancia-modelo.md`): e-mail dedicado de privacidade e contato do hospedeiro. Relato de vulnerabilidade por terceiros: `SECURITY.md`.

## Exercício (tabletop)

Mínimo anual. O primeiro, em `tabletop-2026-11-17.md`, foi feito **no papel por IA**: serve de roteiro; um exercício cronometrado com pessoas ainda precisa ser feito pelo responsável da instância.
