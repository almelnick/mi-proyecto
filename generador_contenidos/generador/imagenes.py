"""Fondos generados con IA (OpenAI) para cada lámina, con el estilo de la marca."""

import base64
import os
from pathlib import Path

from openai import OpenAI

from .marca import Marca
from .modelos import Pieza

MODELO = os.environ.get("IMAGEN_MODELO", "gpt-image-2")


def _prompt(marca: Marca, descripcion: str) -> str:
    e = marca.estilo_visual
    return (
        f"{descripcion}\n"
        f"Estilo: {e.estilo_imagenes}\n"
        f"Paleta dominante: {e.color_fondo}, {e.color_acento} y {e.color_secundario}.\n"
        "Formato vertical para redes sociales. Deja zonas despejadas para poner texto encima. "
        "No incluyas texto, letras, números, logos ni marcas de agua."
    )


def generar_fondos(marca: Marca, pieza: Pieza, carpeta: Path) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    cliente = OpenAI()
    fondos = []
    for i, slide in enumerate(pieza.slides, 1):
        respuesta = cliente.images.generate(
            model=MODELO,
            prompt=_prompt(marca, slide.imagen or pieza.gancho),
            size="1024x1536",
            output_format="png",
        )
        destino = carpeta / f"fondo_{i:02d}.png"
        destino.write_bytes(base64.b64decode(respuesta.data[0].b64_json))
        fondos.append(destino)
    return fondos
