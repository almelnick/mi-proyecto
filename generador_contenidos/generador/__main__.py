"""Uso: python -m generador --marca marcas/ejemplo.yaml --tema "..." --formato carrusel"""

import argparse
from pathlib import Path

from .marca import Marca
from .modelos import Pieza
from .pipeline import generar


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera contenido para redes sociales respetando la marca.")
    parser.add_argument("--marca", required=True, help="Ruta al archivo YAML del kit de marca.")
    parser.add_argument("--tema", help="De qué trata la publicación.")
    parser.add_argument(
        "--pieza", type=Path, help="JSON con una pieza ya escrita: se diseña tal cual, sin redactar con IA."
    )
    parser.add_argument("--formato", choices=["imagen", "carrusel", "video"], default="carrusel")
    parser.add_argument("--red", choices=["instagram", "linkedin", "tiktok", "facebook"], default="instagram")
    parser.add_argument("--variantes", type=int, default=3, help="Cuántas propuestas redactar por ronda.")
    parser.add_argument("--salida", type=Path, default=Path("salida"))
    parser.add_argument(
        "--sin-ia", action="store_true", help="Usa textos de prueba, sin llamar a Claude ni a TypeSafe."
    )
    parser.add_argument(
        "--imagenes-ia", action="store_true", help="Genera un fondo con IA para cada lámina (OpenAI)."
    )
    parser.add_argument(
        "--voz", action="store_true", help="Agrega voz en off al video con el guion de locución (ElevenLabs)."
    )
    parser.add_argument(
        "--video-simple", action="store_true", help="Video con láminas fijas y zoom, sin animaciones (más rápido)."
    )
    args = parser.parse_args()
    pieza = Pieza.model_validate_json(args.pieza.read_text(encoding="utf-8")) if args.pieza else None
    if pieza is None and not args.tema:
        parser.error("Indica --tema o --pieza.")
    if args.voz and args.formato != "video":
        parser.error("--voz solo aplica al formato video.")

    carpeta = generar(
        Marca.cargar(args.marca),
        args.tema or pieza.gancho,
        args.formato,
        args.red,
        variantes=args.variantes,
        salida=args.salida,
        sin_ia=args.sin_ia,
        imagenes_ia=args.imagenes_ia,
        voz=args.voz,
        pieza=pieza,
        animar=not args.video_simple,
    )
    print(f"Listo. Archivos en: {carpeta}")


if __name__ == "__main__":
    main()
