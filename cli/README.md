# Confere CLI

Cliente de linha de comando da API do [Confere](https://github.com/EttoreCSenatore/confere). / Command-line client for the Confere API.

```bash
pipx install ./cli          # a partir da raiz do repositório
export CONFERE_API_URL=https://SEU-SERVIDOR
confere cnpj 00000000000191
echo 00000000000191 | confere cnpj -        # sem deixar o CNPJ no histórico do shell
confere pagar 00000000000191 --ispb 00000000
confere dados ncm --q cafe
confere dados corretoras --uf SP --csv -o corretoras.csv
```

Documentação completa: https://ettorecsenatore.github.io/confere/docs/funcionalidades/cli — Licença AGPL-3.0-or-later.
