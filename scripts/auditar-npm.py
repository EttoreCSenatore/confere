#!/usr/bin/env python3
"""`npm audit` (só dependências de produção) com lista curta de avisos aceitos, cada um com motivo.

Falha se houver aviso de severidade alta ou crítica que não esteja em ACEITOS. Só biblioteca padrão.
"""

import json
import subprocess
import sys

# GHSA -> motivo. Revisar a cada atualização do Docusaurus; remover quando houver versão corrigida.
ACEITOS = {
    "GHSA-fc5q-39xc-vjpf": "picomatch (ReDoS em extglob): só na ferramenta de build do site, com padrões do próprio repositório; "
    "não vai para o site publicado; sem versão corrigida em 2026-11-17 (latest 4.0.7 também afetada)",
}


def main() -> int:
    pasta = sys.argv[1] if len(sys.argv) > 1 else "."
    saida = subprocess.run(
        ["npm", "audit", "--omit=dev", "--json"], cwd=pasta, capture_output=True, text=True, check=False
    ).stdout
    dados = json.loads(saida)
    novos = []
    for nome, v in dados.get("vulnerabilities", {}).items():
        if v["severity"] not in ("high", "critical"):
            continue
        avisos = [x for x in v["via"] if isinstance(x, dict)]
        if not avisos:  # só herda de outro pacote; o aviso original é checado na entrada dele
            continue
        for a in avisos:
            ghsa = a["url"].rsplit("/", 1)[-1]
            if ghsa not in ACEITOS:
                novos.append(f"{nome}: {a['title']} ({a['url']})")
    if novos:
        print("avisos de segurança não aceitos:\n" + "\n".join(sorted(set(novos))), file=sys.stderr)
        return 1
    print("ok: nenhum aviso alto/crítico fora da lista de aceitos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
