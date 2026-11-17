# Mapa de dados — Confere (v1, rascunho)

Nada é gravado em banco. Os dados existem só em memória durante a requisição e no cache curto (`retention.md`).

## Atividades de tratamento

| ID | Atividade | Dados | Titulares | Origem | Destino |
|---|---|---|---|---|---|
| A001 | Checagem de CNPJ | CNPJ digitado; resposta pública da BrasilAPI: razão social/nome, endereço, situação, CNAE, porte, data de abertura, **quadro de sócios (QSA)** | Empresários individuais e MEI (o CNPJ identifica a pessoa); sócios e administradores (terceiros) | Pessoa usuária → API → BrasilAPI | Resposta à pessoa usuária |
| A002 | "Pode pagar?" | CNPJ, código do banco/ISPB, dados do participante do Pix | Os mesmos de A001 | Idem | Idem |
| A003 | Explorador de dados abertos | Bancos, municípios, NCM, corretoras (CVM), dados de pessoas jurídicas | Pouco ou nenhum dado pessoal (contatos de PJ) | BrasilAPI | Resposta, CSV |
| A004 | Operação e segurança | **Endereço IP** da requisição (limite de taxa), erros técnicos sem identificadores | Pessoas usuárias | Rede | Só memória (60 s) |

## A002 (implementado no M1.2)

`POST /v1/pagamento/check` recebe CNPJ + ISPB/código no **corpo** (não na URL, que proxies registram). As listas públicas de bancos e de participantes do Pix (sem dado pessoal) ficam em cache de memória por 1 h; só ISPB, nome, código, modalidade e tipo são mantidos (logotipo/endereço descartados; o logotipo vem de CDN de terceiros). O log não tem ISPB nem CNPJ (teste automático). Não verifica o titular da chave Pix.

## A003 (implementado no M3)

`GET /v1/dados/{conjunto}` (bancos, pix, municípios, NCM, corretoras): as listas inteiras são baixadas da BrasilAPI e filtradas **na memória**; o texto da busca (`q`) nunca vai à fonte. Cache de 24 h, só memória. **Corretoras**: e-mail, telefone, CEP, logradouro e patrimônio líquido são descartados; ficam CNPJ, razão social/nome comercial, situação, UF/município, código CVM e data de registro (dados de pessoa jurídica). CSV com proteção contra injeção de fórmula e sem dado pessoal. Erros de validação não repetem o valor enviado. A busca viaja na query string (GET): **o proxy de produção não pode registrar query string** (T13).

## Minimização aplicada

- **QSA**: nomes dos sócios **não** são devolvidos; só quantidade, qualificação e faixa de tempo de entrada. [DECISÃO do projeto; ver T6]
- CNPJ de pessoa natural (natureza jurídica 213-5 e MEI): resposta marcada como "empresário individual" e com menos campos de endereço.
- Log de acesso sem IP, sem caminho com CNPJ, sem cabeçalhos (só método, modelo da rota, status, latência). Os logs da biblioteca HTTP (`httpx`/`httpcore`) são rebaixados para aviso, pois registrariam a URL com o CNPJ; teste automático cobre isso.
- **Implementado no M1.1** (`api/confere/empresa.py`, `risco.py`, `limite.py`, `cache.py`). O IP do limite de taxa vira HMAC com sal aleatório por processo; nada em disco.

## Cookies, SDKs e terceiros

| Item | Situação |
|---|---|
| Cookies / armazenamento local | Só a preferência de idioma (`localStorage`, chave `confere.idioma`); nenhum cookie. Teste automático garante que CNPJ/ISPB não são guardados nem vão para a URL |
| Analytics, publicidade, fontes de CDN | Nenhum (ativos próprios; fontes do sistema). O build injeta CSP `default-src 'none'` + só `'self'`; `Referrer-Policy: no-referrer`; campos com `autocomplete="off"` |
| Terceiros | BrasilAPI (recebe só CNPJ/ISPB/código, nunca o IP da pessoa usuária); hospedagem (a definir, T2) |
