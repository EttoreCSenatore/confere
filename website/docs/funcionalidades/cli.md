---
id: cli
title: Linha de comando (CLI)
---

# Linha de comando (CLI)

A CLI é um **cliente fino da API**: não tem regra própria, não guarda configuração, histórico nem cache. Tudo o que o app web faz está nela.

## Instalar e configurar

```bash
pipx install ./cli                       # a partir da raiz do repositório
export CONFERE_API_URL=https://SEU-SERVIDOR   # padrão: http://127.0.0.1:8000
export CONFERE_LANG=pt-BR                # ou en; padrão: o idioma do sistema
```

Por segurança, a CLI **só aceita `https`** (e `http` apenas em `localhost`), não segue redirecionamentos e não envia cookies.

## Conferir um CNPJ

`confere cnpj` mostra o nível, os sinais com a regra que os gerou e os dados públicos da empresa.

![Saída de confere cnpj](/img/screenshots/cli-cnpj.png)

Para o CNPJ **não ficar no histórico do shell**, passe `-` e envie pela entrada padrão:

![CNPJ lido da entrada padrão](/img/screenshots/cli-stdin.png)

## Pode pagar?

`confere pagar` confere o CNPJ e a instituição (`--ispb` ou `--banco`, só um). Não verifica o titular da chave Pix.

![Saída de confere pagar](/img/screenshots/cli-pagar.png)

Uma instituição desconhecida eleva o nível e o motivo aparece explicado:

![Instituição não encontrada](/img/screenshots/cli-pagar-alto.png)

## Usar em scripts

`--json` imprime a resposta da API. `--falhar-se atencao|alto` sai com **código 3** quando o nível é igual ou pior, útil em automações. Erros saem com código 2 e mensagem simples.

![Código de saída com --falhar-se](/img/screenshots/cli-falhar.png)

## Explorar dados abertos

`confere dados` lista `bancos`, `pix`, `municipios` (exige `--uf`), `ncm` e `corretoras`, com `--q`, `--limite` e `--offset`.

![Busca no NCM](/img/screenshots/cli-dados-ncm.png)

![Busca de bancos](/img/screenshots/cli-dados-bancos.png)

Com `--csv` a CLI baixa **todas as linhas do filtro** (UTF-8 com BOM, protegido contra injeção de fórmula). Sem `-o`, o CSV sai na saída padrão; com `-o`, a CLI **não sobrescreve** arquivos sem `--forcar`:

```bash
confere dados corretoras --uf SP --csv -o corretoras.csv
```

## Erros

Os erros da API viram mensagens claras no seu idioma, sem rastros técnicos.

![Mensagem de CNPJ inválido](/img/screenshots/cli-erro.png)
