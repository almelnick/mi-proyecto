"""Redacción de variantes con Claude, siguiendo el kit de marca."""

import json

import anthropic

from .marca import Marca
from .modelos import Formato, Pieza, Red, Slide, Variantes

MODELO = "claude-opus-5-5"

INSTRUCCIONES_FORMATO = {
    "imagen": "Una sola lámina: un título potente y un texto breve de apoyo.",
    "carrusel": (
        "Entre 5 y 8 láminas. La primera engancha, las del medio desarrollan una idea por lámina "
        "y la última cierra con el llamado a la acción."
    ),
    "video": (
        "Video vertical corto de 4 a 6 escenas (unos 15 a 30 segundos). Cada escena tiene un texto en "
        "pantalla breve y una locución natural para voz en off."
    ),
}

SISTEMA = """Eres el redactor de contenidos para redes sociales de una marca.
Tu prioridad es sonar exactamente como la marca: respeta su tono, lo que sí hace, lo que no hace,
su vocabulario y sus reglas prohibidas. Escribe en español neutro, sin voseo.
Cada variante debe ser una propuesta distinta (otro ángulo, otro gancho), no una reescritura."""


def redactar(
    marca: Marca,
    tema: str,
    formato: Formato,
    red: Red,
    cantidad: int,
    correcciones: list[str] | None = None,
) -> list[Pieza]:
    pedido = {
        "marca": marca.resumen_para_ia(),
        "tema": tema,
        "red_social": red,
        "formato": formato,
        "instrucciones_formato": INSTRUCCIONES_FORMATO[formato],
        "cantidad_de_variantes": cantidad,
    }
    if correcciones:
        pedido["problemas_de_la_ronda_anterior"] = correcciones

    cliente = anthropic.Anthropic()
    respuesta = cliente.beta.messages.parse(
        model=MODELO,
        max_tokens=16000,
        system=SISTEMA,
        output_config={"effort": "medium"},
        # Si Claude declina por un filtro de seguridad, la API reintenta con otro modelo.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Escribe {cantidad} variantes de contenido según este pedido:\n\n"
                    + json.dumps(pedido, ensure_ascii=False, indent=2)
                ),
            }
        ],
        output_format=Variantes,
    )
    if respuesta.stop_reason == "refusal" or respuesta.parsed_output is None:
        raise RuntimeError(f"Claude no generó contenido (stop_reason={respuesta.stop_reason}).")
    return respuesta.parsed_output.variantes


def redactar_sin_ia(marca: Marca, tema: str, formato: Formato, cantidad: int) -> list[Pieza]:
    """Contenido de relleno para probar el flujo sin claves de API."""
    laminas = {"imagen": 1, "carrusel": 5, "video": 4}[formato]
    piezas = []
    for n in range(1, cantidad + 1):
        slides = [
            Slide(
                titulo=tema[:1].upper() + tema[1:] if i == 0 else f"Idea {i}",
                texto=f"{marca.nombre}: variante {n}, lámina {i + 1}.",
                locucion=f"Escena {i + 1} sobre {tema}." if formato == "video" else "",
            )
            for i in range(laminas)
        ]
        piezas.append(
            Pieza(
                gancho=f"{tema} (variante {n})",
                slides=slides,
                caption=f"{tema[:1].upper() + tema[1:]} con {marca.nombre}.",
                cta="Visítanos hoy",
                hashtags=marca.hashtags[:5] or ["#marca"],
            )
        )
    return piezas
