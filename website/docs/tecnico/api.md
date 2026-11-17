---
id: api
title: API
---

# API de conferência

A API é a única dona das regras: validação, indícios, cache e limite de taxa. A web (M2) e a CLI (M4) só a chamam.

## Rodar localmente

```bash
cd api
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
CONFERE_DOCS=true python -m confere      # http://127.0.0.1:8000/docs
```

O `/docs` (Swagger) carrega scripts de uma CDN e por isso **só liga com `CONFERE_DOCS=true`**, em desenvolvimento.

![Documentação interativa da API (Swagger)](/img/screenshots/api-docs.png)

## Conferir um CNPJ

```bash
curl 'http://127.0.0.1:8000/v1/cnpj/00000000000191/check?lang=pt-BR'
```

Envie só letras e números (sem `/`). O formato **alfanumérico** do CNPJ, vigente desde julho de 2026, é aceito.

![Resposta da conferência de um CNPJ](/img/screenshots/api-conferir-cnpj.png)

## Pode pagar? (CNPJ + banco + Pix)

```bash
curl -X POST http://127.0.0.1:8000/v1/pagamento/check \
  -H 'content-type: application/json' \
  -d '{"cnpj": "00000000000191", "ispb": "00000000"}'
```

Use `POST` de propósito: os dados vão no corpo, que proxies e servidores costumam **não** registrar, ao contrário da URL. Informe **só um** entre `ispb` (8 dígitos) e `banco` (código COMPE, 1 a 3 dígitos).

![Resposta do "pode pagar?"](/img/screenshots/api-pode-pagar.png)

A resposta tem o mesmo formato da conferência de CNPJ, mais `instituicao` (ISPB, nome, código COMPE, `participa_pix`, modalidade e tipo) e `limites`. Os sinais da empresa e os da instituição se somam.

| Código | Gravidade | Peso | Regra |
|---|---|---|---|
| `INSTITUICAO_NAO_ENCONTRADA` | alto | 50 | ISPB ou código fora da lista de bancos e dos participantes do Pix |
| `NAO_PARTICIPA_PIX` | alto | 40 | Instituição existe, mas não está entre os participantes do Pix |

:::caution Limite importante
Só confirmamos que a **instituição** existe e participa do Pix. **Não** verificamos o titular da chave nem a conta de destino: a BrasilAPI não oferece isso.
:::

### O que volta

| Campo | Significado |
|---|---|
| `nivel` | `sem_indicios`, `atencao` ou `alto` (nunca "seguro") |
| `pontuacao` | Soma dos pesos dos sinais, de 0 a 100 |
| `sinais[]` | Cada indício: `codigo`, `gravidade`, `peso`, `mensagem` e a `regra` que o gerou |
| `empresa` | Dados públicos **minimizados**: situação, idade, atividade, porte, município/UF, quantidade e qualificação dos sócios |
| `aviso` | Lembrete de que é indício, não prova |

## Regras de indício

| Código | Gravidade | Peso | Regra |
|---|---|---|---|
| `SITUACAO_NAO_ATIVA` | alto | 60 | Situação cadastral diferente de ATIVA |
| `EMPRESA_RECEM_ABERTA` | alto | 40 | Início de atividade há menos de 30 dias |
| `EMPRESA_NOVA` | atenção | 25 | Entre 30 e 179 dias |
| `SITUACAO_ESPECIAL` | atenção | 20 | Campo de situação especial preenchido |
| `DADOS_INCOMPLETOS` | atenção | 15 | Data de início de atividade ausente |
| `SEM_CONTATO_PUBLICO` | atenção | 10 | Sem e-mail nem telefone no cadastro |
| `QUADRO_SOCIETARIO_VAZIO` | atenção | 10 | Pessoa jurídica privada sem sócios listados |
| `EMPRESARIO_INDIVIDUAL` | info | 0 | Empresário individual ou MEI: nome e endereço omitidos |

Níveis: `alto` a partir de 50 pontos, `atencao` a partir de 15, senão `sem_indicios`.

## Erros

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `nao_encontrado` | A fonte não conhece o CNPJ |
| 422 | `cnpj_invalido` | Formato ou dígitos verificadores errados (a fonte nem é chamada) |
| 422 | `instituicao_invalida` | Faltou ou sobrou `ispb`/`banco`, ou formato errado |
| 429 | `limite_excedido` | Mais de 30 consultas por minuto (cabeçalho `Retry-After`) |
| 502 | `fonte_indisponivel` | A BrasilAPI não respondeu; nada é inventado |

## Configuração

| Variável | Padrão | Para quê |
|---|---|---|
| `CONFERE_DOCS` | `false` | Liga o `/docs` (só desenvolvimento) |
| `CONFERE_CORS_ORIGENS` | vazio | Origens permitidas, separadas por vírgula |
| `CONFERE_CONFIAR_PROXY` | `false` | Usar o último valor de `X-Forwarded-For` (atrás de **um** proxy seu) |
| `CONFERE_LIMITE_POR_MINUTO` | `30` | Consultas por origem |
| `CONFERE_CACHE_TTL` | `600` | Validade do cache em segundos (0 desliga) |
| `CONFERE_CACHE_TTL_DIRETORIO` | `3600` | Validade das listas públicas de bancos e Pix |
