# Confere CLI

**PT-BR** — Cliente de linha de comando do [Confere](https://github.com/EttoreCSenatore/confere): confira empresas (CNPJ), bancos e participantes do Pix com dados públicos da BrasilAPI, com sinais **explicados** (indício, não prova de fraude).
**EN** — Command-line client of [Confere](https://github.com/EttoreCSenatore/confere): check companies (CNPJ), banks and Pix participants with public BrasilAPI data and **explained** warning signs (an indication, not proof of fraud).

```bash
pipx install confere-cli                  # PyPI (quando publicado / when published)
# ou / or:
pipx install "git+https://github.com/EttoreCSenatore/confere#subdirectory=cli"

export CONFERE_API_URL=https://SEU-SERVIDOR     # https obrigatório (http só em localhost) / https required
confere cnpj 00000000000191
echo 00000000000191 | confere cnpj -            # fora do histórico do shell / keeps it out of shell history
confere pagar 00000000000191 --ispb 00000000    # pode pagar? / safe to pay?
confere dados ncm --q cafe
confere dados corretoras --uf SP --csv -o corretoras.csv
confere cnpj 00000000000191 --falhar-se alto    # exit code 3 em scripts / in scripts
```

- Sem estado: não guarda configuração, histórico nem cache. / Stateless: no config, history or cache.
- Documentação / Docs: https://ettorecsenatore.github.io/confere/docs/funcionalidades/cli
- Licença / License: AGPL-3.0-or-later.
