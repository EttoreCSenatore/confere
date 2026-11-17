#!/usr/bin/env python3
"""Atualiza as cópias locais dos dados abertos (api/confere/snapshots/*.json.gz) a partir da BrasilAPI.

Uso (com o venv da API ativo):   python scripts/atualizar-snapshots.py
Só mexe nos arquivos que mudaram (gravação determinística) e já grava os dados minimizados: das corretoras não
entram e-mail, telefone nem endereço. Falha, sem gravar nada, se alguma lista vier vazia ou pequena demais."""

import asyncio
import sys
from datetime import date
from pathlib import Path

from confere.brasilapi import BrasilApi, FonteIndisponivel
from confere.cache import CacheTTL
from confere.dados import ARQUIVOS, CONJUNTOS, UFS, Dados, Snapshots, gravar_copia, ordenar

DESTINO = Path(__file__).resolve().parent.parent / "api" / "confere" / "snapshots"
MINIMO = {"bancos": 300, "pix": 500, "ncm": 10_000, "corretoras": 100, "ufs": 27}  # evita gravar uma lista truncada
MINIMO_MUNICIPIOS = 5_000


async def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    fonte = BrasilApi(timeout=60)
    dados = Dados(fonte, CacheTTL(0), Snapshots(DESTINO), max_dias=0)  # max_dias=0: sempre a fonte
    hoje = date.today()
    novos: dict[str, object] = {}
    try:
        for nome in ARQUIVOS:
            if nome == "municipios":
                por_uf = {}
                for uf in sorted(UFS):
                    por_uf[uf] = ordenar("municipios", await dados.baixar("municipios", uf))
                    await asyncio.sleep(0.2)
                total = sum(len(v) for v in por_uf.values())
                if total < MINIMO_MUNICIPIOS or any(not v for v in por_uf.values()):
                    raise SystemExit(f"municipios: só {total} linhas ou UF vazia; nada foi gravado")
                novos[nome] = por_uf
            else:
                linhas = ordenar(nome, await dados.baixar(nome))
                if len(linhas) < MINIMO[nome]:
                    raise SystemExit(f"{nome}: só {len(linhas)} linhas (mínimo {MINIMO[nome]}); nada foi gravado")
                novos[nome] = linhas
    except FonteIndisponivel as e:
        print(f"BrasilAPI indisponível ({e}); nada foi gravado", file=sys.stderr)
        return 1
    finally:
        await fonte.fechar()
    mudaram = [n for n, itens in novos.items() if gravar_copia(DESTINO, n, itens, hoje)]
    print("atualizados:", ", ".join(mudaram) if mudaram else "nenhum (sem mudanças)")
    assert set(novos) == set(ARQUIVOS) and set(CONJUNTOS) <= set(ARQUIVOS)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
