"""Formatação do resultado em texto simples (sem cores nem dependências extras)."""

from confere_cli.textos import t

NIVEIS = {"sem_indicios": 0, "atencao": 1, "alto": 2}


def _sim_nao(lang: str, v: object) -> str:
    return "—" if v is None else t(lang, "yes" if v else "no")


def texto_resposta(r: dict, lang: str) -> str:
    e = r["empresa"]
    linhas = [
        f"CNPJ {r['cnpj']}",
        f"{t(lang, 'result')}: {t(lang, 'level.' + r['nivel'])} ({t(lang, 'score', n=r['pontuacao'])})",
        f"{t(lang, 'signals')}:",
    ]
    if not r["sinais"]:
        linhas.append(f"  {t(lang, 'none')}")
    for s in r["sinais"]:
        linhas.append(f"  [{s['gravidade']}] {s['mensagem']}")
        linhas.append(f"      {t(lang, 'rule')}: {s['regra']} ({s['codigo']}, +{s['peso']})")
    linhas.append(f"{t(lang, 'company')}:")
    if e["individual"]:
        linhas.append(f"  {t(lang, 'individual')}")
    else:
        nome = e["razao_social"] or "—"
        linhas.append(f"  {nome}" + (f" ({e['nome_fantasia']})" if e["nome_fantasia"] else ""))
    desde = f"{t(lang, 'since')}: {e['data_abertura']}" if e["data_abertura"] else ""
    linhas.append(f"  {t(lang, 'status')}: {e['situacao']}" + (f" · {desde}" if desde else ""))
    linhas.append(f"  {t(lang, 'nature')}: {e['natureza_juridica'] or '—'} · {t(lang, 'size')}: {e['porte'] or '—'}")
    linhas.append(f"  {t(lang, 'cnae')}: {e['cnae_principal']['descricao'] or '—'}")
    local = " / ".join(x for x in (e["municipio"], e["uf"]) if x) or "—"
    linhas.append(f"  {t(lang, 'place')}: {local}")
    linhas.append(f"  {t(lang, 'partners')}: {t(lang, 'partners.v', n=e['socios_total'])}")
    if "instituicao" in r:
        i = r["instituicao"]
        linhas.append(f"{t(lang, 'institution')}:")
        if i is None:
            linhas.append(f"  {t(lang, 'inst.notfound')}")
        else:
            linhas.append(f"  {i['nome']} · ISPB {i['ispb']} · {t(lang, 'pix')}: {_sim_nao(lang, i['participa_pix'])}")
        if r.get("limites"):
            linhas.append(f"  {r['limites']}")
    linhas.append(f"{t(lang, 'notice')}: {r['aviso']}")
    return "\n".join(linhas)


def _cel(v: object, largura: int) -> str:
    texto = "—" if v is None or v == "" else ("true" if v is True else "false" if v is False else str(v))
    texto = " ".join(texto.split())
    return texto if len(texto) <= largura else texto[: largura - 1] + "…"


def tabela(colunas: list[str], itens: list[dict], largura_max: int = 40) -> str:
    linhas = [[_cel(i.get(c), largura_max) for c in colunas] for i in itens]
    larguras = [max(len(c), *(len(l[k]) for l in linhas)) if linhas else len(c) for k, c in enumerate(colunas)]

    def fmt(cel: list[str]) -> str:
        return "  ".join(c.ljust(larguras[k]) for k, c in enumerate(cel)).rstrip()

    saida = [fmt(colunas), fmt(["-" * w for w in larguras])]
    saida += [fmt(l) for l in linhas]
    return "\n".join(saida)
