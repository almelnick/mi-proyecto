"""Uso: python -m clasificador --negocio negocios/sprint_latam.yaml --keywords ejemplos/sprint_keywords_chile.csv"""

import argparse
import asyncio
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from .entrada import Negocio, leer_keywords
from .excel import exportar
from .jev import clasificar
from .prioridad import priorizar


def main() -> None:
    p = argparse.ArgumentParser(description="Clasifica keywords con Jev (TypeSafe) y entrega un Excel priorizado.")
    p.add_argument("--negocio", required=True, help="Ficha YAML del negocio")
    p.add_argument("--keywords", required=True, help="CSV con keywords (Ubersuggest, Semrush, Ahrefs...)")
    p.add_argument("--salida", help="Excel de salida (por defecto salida/<negocio>-<fecha>.xlsx)")
    p.add_argument("--volumen-minimo", type=int, default=0, help="Ignora keywords con menos búsquedas")
    p.add_argument("--limite", type=int, help="Clasifica solo las N keywords con más volumen")
    p.add_argument("--presupuesto", type=float, help="Tope de gasto en USD; al llegar, deja de consultar a Jev")
    a = p.parse_args()

    if not os.environ.get("TYPESAFE_API_KEY"):
        sys.exit("Falta la variable de entorno TYPESAFE_API_KEY.")

    negocio = Negocio.cargar(a.negocio)
    keywords = [k for k in leer_keywords(a.keywords) if k.volumen >= a.volumen_minimo]
    keywords.sort(key=lambda k: k.volumen, reverse=True)
    if a.limite:
        keywords = keywords[: a.limite]
    if not keywords:
        sys.exit("No hay keywords para clasificar.")

    from typesafe_sdk import AsyncTypeSafeClient

    hechas = 0

    def avanzar():
        nonlocal hechas
        hechas += 1
        print(f"\r  {hechas}/{len(keywords)} keywords", end="", flush=True)

    print(f"Clasificando {len(keywords)} keywords de {negocio.nombre} con Jev...")

    async def correr():
        async with AsyncTypeSafeClient() as cliente:
            return await clasificar(cliente, negocio, keywords, a.presupuesto, avanzar)

    clasificaciones, costo = asyncio.run(correr())
    print()
    clasificaciones = priorizar(clasificaciones)

    nombre = Path(a.negocio).stem
    destino = exportar(
        clasificaciones, costo, a.salida or f"salida/{nombre}-{date.today().isoformat()}.xlsx", negocio.nombre
    )

    decisiones = Counter(c.decision for c in clasificaciones)
    print(f"\nListo: {destino}")
    for decision, n in decisiones.most_common():
        print(f"  {decision}: {n}")
    print("\nTop 10 para atacar:")
    for c in [c for c in clasificaciones if c.decision == "atacar"][:10]:
        print(f"  {c.prioridad:6.1f}  {c.keyword.keyword}  ({c.keyword.volumen}/mes, {c.servicio}, {c.etapa})")
    print(
        f"\nCosto Jev: {costo.tokens_entrada:,} tokens de entrada + {costo.tokens_salida:,} de salida "
        f"= US${costo.usd:.4f}"
    )


if __name__ == "__main__":
    main()
