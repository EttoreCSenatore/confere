# Registro interno de incidentes de segurança (art. 10 da Res. CD/ANPD nº 15/2024)

Guardar por **5 anos**, inclusive os não notificados. Cada instância mantém o seu. O projeto em si nunca teve instância com dados reais de usuários; nenhum incidente a registrar.

| ID | Data/hora do incidente | Data/hora da ciência | Descrição e causa | Dados/titulares afetados | Avaliação (art. 5º) | Comunicação ANPD / titulares | Medidas | Guardar até |
|---|---|---|---|---|---|---|---|---|
| (nenhum) | | | | | | | | |

## Achado interno que quase virou incidente (não afetou usuários)

- **2026-11-17, durante o M1.1**: o log INFO da biblioteca `httpx` imprimia a URL completa de cada chamada à fonte, inclusive o CNPJ consultado. Descoberto por teste automático **antes de existir qualquer instância**; corrigido (log silenciado) e coberto por teste. Mantido aqui como lição: novos componentes de rede devem passar pelo mesmo teste de log.
