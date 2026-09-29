"""Uso: python -m generador --marca marcas/ejemplo.yaml --tema "..." --formato carrusel"""

import argparse
from pathlib import Path

from .marca import Marca
from .pipeline import generar


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera contenido para redes sociales respetando la marca.")
    parser.add_argument("--marca", required=True, help="Ruta al archivo YAML del kit de marca.")
    parser.add_argument("--tema", required=True, help="De qué trata la publicación.")
    parser.add_argument("--formato", choices=["imagen", "carrusel", "video"], default="carrusel")
    parser.add_argument("--red", choices=["instagram", "linkedin", "tiktok", "facebook"], default="instagram")
    parser.add_argument("--variantes", type=int, default=3, help="Cuántas propuestas redactar por ronda.")
    parser.add_argument("--salida", type=Path, default=Path("salida"))
    parser.add_argument(
        "--sin-ia", action="store_true", help="Usa textos de prueba, sin llamar a Claude ni a TypeSafe."
    )
    args = parser.parse_args()

    carpeta = generar(
        Marca.cargar(args.marca),
        args.tema,
        args.formato,
        args.red,
        variantes=args.variantes,
        salida=args.salida,
        sin_ia=args.sin_ia,
    )
    print(f"Listo. Archivos en: {carpeta}")


if __name__ == "__main__":
    main()
