"""Reglas de negocio: prioridad de cada keyword y qué hacer con ella."""

import math

from .jev import Clasificacion

# Valores iniciales: conviene ajustarlos con los resultados reales de cada negocio.
PESO_INTENCION = {"transaccional": 1.0, "comercial": 0.8, "informacional": 0.4, "navegacional": 0.1}
UMBRAL_EXCLUSION = 0.6  # probabilidad desde la que se excluye (competidor, no cliente, otro país)
UMBRAL_CONFIANZA = 0.5  # por debajo, la fila queda para revisar a mano
RELEVANCIA_MINIMA = 1.5  # puntaje de 0 a 3


def calcular(c: Clasificacion) -> Clasificacion:
    if c.error:
        c.decision, c.motivo = "sin clasificar", c.error
        return c

    motivos_exclusion = []
    if c.competidor >= UMBRAL_EXCLUSION:
        motivos_exclusion.append("nombra a otra marca")
    if c.no_cliente >= UMBRAL_EXCLUSION:
        motivos_exclusion.append("busca empleo, curso, recurso gratis o login")
    if c.otro_pais >= UMBRAL_EXCLUSION:
        motivos_exclusion.append("es de otro país")

    kw = c.keyword
    dificultad = kw.dificultad if kw.dificultad is not None else 50
    c.prioridad = round(
        (c.relevancia / 3)
        * PESO_INTENCION.get(c.intencion, 0.3)
        * math.log10(kw.volumen + 10)
        * (1 - min(dificultad, 99) / 100)
        * 100,
        1,
    )

    dudosas = [
        nombre
        for nombre, conf in (
            ("intención", c.intencion_confianza),
            ("etapa", c.etapa_confianza),
            ("servicio", c.servicio_confianza),
            ("relevancia", c.relevancia_confianza),
        )
        if conf < UMBRAL_CONFIANZA
    ]

    if motivos_exclusion:
        c.decision, c.motivo, c.prioridad = "excluir", "; ".join(motivos_exclusion), 0.0
    elif c.relevancia < RELEVANCIA_MINIMA or c.servicio == "ninguno":
        c.decision, c.motivo = "baja relevancia", f"relevancia {c.relevancia:.1f} de 3"
    elif dudosas:
        c.decision, c.motivo = "revisar", "Jev no está seguro de: " + ", ".join(dudosas)
    else:
        c.decision, c.motivo = "atacar", _accion(c)
    return c


def _accion(c: Clasificacion) -> str:
    """Tipo de página sugerido según intención y etapa."""
    if c.intencion == "transaccional" or c.etapa == "bofu":
        return "página de servicio o landing con formulario"
    if c.intencion == "comercial":
        return "página comparativa, precios o caso de éxito"
    return "artículo de blog o guía que enlace al servicio"


def priorizar(clasificaciones: list[Clasificacion]) -> list[Clasificacion]:
    orden = {"atacar": 0, "revisar": 1, "baja relevancia": 2, "excluir": 3, "sin clasificar": 4}
    return sorted(
        (calcular(c) for c in clasificaciones),
        key=lambda c: (orden.get(c.decision, 9), -c.prioridad, -c.keyword.volumen),
    )
