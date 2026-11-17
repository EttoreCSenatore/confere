# Mapa de dados — Confere (v1, rascunho)

Nada é gravado em banco. Os dados existem só em memória durante a requisição e no cache curto (`retention.md`).

## Atividades de tratamento

| ID | Atividade | Dados | Titulares | Origem | Destino |
|---|---|---|---|---|---|
| A001 | Checagem de CNPJ | CNPJ digitado; resposta pública da BrasilAPI: razão social/nome, endereço, situação, CNAE, porte, data de abertura, **quadro de sócios (QSA)** | Empresários individuais e MEI (o CNPJ identifica a pessoa); sócios e administradores (terceiros) | Pessoa usuária → API → BrasilAPI | Resposta à pessoa usuária |
| A002 | "Pode pagar?" | CNPJ, código do banco/ISPB, dados do participante do Pix | Os mesmos de A001 | Idem | Idem |
| A003 | Explorador de dados abertos | Bancos, municípios, NCM, corretoras (CVM), dados de pessoas jurídicas | Pouco ou nenhum dado pessoal (contatos de PJ) | BrasilAPI | Resposta, CSV |
| A004 | Operação e segurança | **Endereço IP** da requisição (limite de taxa), erros técnicos sem identificadores | Pessoas usuárias | Rede | Só memória (60 s) |

## Minimização aplicada

- **QSA**: nomes dos sócios **não** são devolvidos; só quantidade, qualificação e faixa de tempo de entrada. [DECISÃO do projeto; ver T6]
- CNPJ de pessoa natural (natureza jurídica 213-5 e MEI): resposta marcada como "empresário individual" e com menos campos de endereço.
- Log de acesso sem IP, sem caminho com CNPJ, sem cabeçalhos (só método, modelo da rota, status, latência). Os logs da biblioteca HTTP (`httpx`/`httpcore`) são rebaixados para aviso, pois registrariam a URL com o CNPJ; teste automático cobre isso.
- **Implementado no M1.1** (`api/confere/empresa.py`, `risco.py`, `limite.py`, `cache.py`). O IP do limite de taxa vira HMAC com sal aleatório por processo; nada em disco.

## Cookies, SDKs e terceiros

| Item | Situação |
|---|---|
| Cookies / armazenamento local | Nenhum além de preferência de idioma/tema no navegador (sem dado pessoal) |
| Analytics, publicidade, fontes de CDN | Nenhum (ativos próprios) |
| Terceiros | BrasilAPI (recebe só CNPJ/ISPB/código, nunca o IP da pessoa usuária); hospedagem (a definir, T2) |
