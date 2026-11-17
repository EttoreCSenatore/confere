---
id: experimente
title: Experimente
---

# Experimente o Confere

Dá para testar tudo no seu computador em poucos minutos, sem conta e sem Docker.

## Subir o app

Precisa de Python 3.13+ e Node 24+. Na raiz do repositório:

```bash
./scripts/dev.sh
```

O script cria o ambiente, sobe a API (porta 8000) e o app (porta 5173) e imprime os endereços. `Ctrl+C` encerra os dois.

![Saída do scripts/dev.sh](/img/screenshots/experimente-dev.png)

## O que testar no app

Abra `http://127.0.0.1:5173`. Sugestões:

- **Conferir**: o CNPJ `00.000.000/0001-91` (um banco público) deve dar "Sem indícios". Teste um CNPJ com um dígito errado e veja a mensagem de erro.
- **Pode pagar?**: use o mesmo CNPJ com o ISPB `00000000` (participa do Pix) e depois com `12345678` (não existe: o nível sobe).
- **Explorar**: procure `cafe` no NCM, escolha SP em Municípios e baixe o CSV.
- **Idioma e tema**: troque para inglês e teste o tema escuro do sistema.

![Resultado de uma consulta no app](/img/screenshots/app-resultado-atencao.png)

## Testar a linha de comando

Com o app no ar, em outro terminal:

```bash
pip install -e cli
confere cnpj 00000000000191
confere pagar 00000000000191 --ispb 12345678 --falhar-se alto; echo $?
```

![Exemplo da CLI](/img/screenshots/cli-pagar-alto.png)

## Testar como em produção (Docker)

Para ver o HTTPS, os cabeçalhos de segurança e o `smoke.sh`, veja a página [Implantação](../tecnico/implantacao.md). Para testes locais use `CONFERE_DOMAIN=localhost` e portas sem privilégio.

## Achou um problema?

Abra uma issue no GitHub (sem dados pessoais) ou, se for uma vulnerabilidade, use o relato privado descrito em `SECURITY.md`.
