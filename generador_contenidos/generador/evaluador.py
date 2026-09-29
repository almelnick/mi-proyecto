"""Control de marca con TypeSafe: juzga cada variante y decide cuál publicar.

TypeSafe no redacta: responde preguntas tipadas (puntajes y probabilidades) sobre cada
variante. Las reglas de negocio (umbrales, descarte, ranking) quedan en este código.
"""

from typesafe_sdk import Noul, Score, TypeSafeClient

from .marca import Marca
from .modelos import Evaluacion, Pieza, Red, Resultado

# Umbrales iniciales: conviene ajustarlos revisando piezas reales de cada marca.
UMBRAL_REGLA = 0.5  # probabilidad desde la que se considera que una regla se rompió
UMBRAL_TONO = 2.0  # puntaje mínimo (0 a 3) para publicar sin revisión humana
UMBRAL_CONFIANZA = 0.5

NIVELES_TONO = [
    "The piece contradicts the brand voice: it uses registers, words or attitudes listed in `marca.tono.no`, "
    "or it reads like a different brand.",
    "The piece is neutral or generic: nothing clashes, but it could belong to any brand and ignores "
    "`marca.tono.si` and `marca.vocabulario_preferido`.",
    "The piece mostly sounds like the brand: it follows `marca.tono.descripcion` with a few generic "
    "or slightly off phrases.",
    "The piece sounds unmistakably like the brand: its wording, rhythm and attitude match "
    "`marca.tono.descripcion`, `marca.tono.si` and the style of `marca.ejemplos`.",
]


def _preguntas(marca: Marca) -> dict:
    preguntas = {
        "tono": Score(
            instructions=(
                "Rate how faithfully `pieza` (its slides, caption and call to action) matches the "
                "brand voice defined in `marca`, for a post on `red_social`."
            ),
            criteria=NIVELES_TONO,
        ),
        "cta": Noul(
            instructions="`pieza` gives the reader one clear, concrete next action.",
            criteria={
                "true": "The call to action says exactly what to do (visit, write, buy, save...).",
                "false": "There is no call to action, or it is vague.",
            },
        ),
    }
    for i, regla in enumerate(marca.reglas_prohibidas):
        preguntas[f"regla_{i}"] = Noul(
            instructions=(
                "Some text in `pieza` (slides, caption, call to action or hashtags) breaks this "
                f"brand rule: \"{regla}\"."
            ),
        )
    return preguntas


def evaluar(cliente: TypeSafeClient, marca: Marca, pieza: Pieza, red: Red) -> Evaluacion:
    respuesta = cliente.system_one(
        state={"marca": marca.resumen_para_ia(), "red_social": red, "pieza": pieza.model_dump()},
        questions=_preguntas(marca),
    )
    tono = respuesta.scores["tono"]
    return Evaluacion(
        tono=tono.score,
        tono_confianza=tono.confidence,
        reglas_violadas={
            regla: respuesta.nouls[f"regla_{i}"].noul for i, regla in enumerate(marca.reglas_prohibidas)
        },
        tiene_cta_claro=respuesta.nouls["cta"].noul,
    )


def clasificar(resultados: list[Resultado]) -> list[Resultado]:
    """Marca las variantes que rompen reglas y ordena el resto de mejor a peor."""
    for r in resultados:
        ev = r.evaluacion
        if ev is None:
            continue
        rotas = [regla for regla, p in ev.reglas_violadas.items() if p >= UMBRAL_REGLA]
        if rotas:
            r.descartada = True
            r.motivo = "Rompe reglas de marca: " + "; ".join(rotas)

    def orden(r: Resultado) -> tuple:
        ev = r.evaluacion
        if ev is None:
            return (0, 0.0, 0.0)
        return (0 if r.descartada else 1, ev.tono, ev.tiene_cta_claro)

    return sorted(resultados, key=orden, reverse=True)


def necesita_revision(r: Resultado) -> str | None:
    """Devuelve el motivo si la mejor variante debería pasar por una persona antes de publicarse."""
    ev = r.evaluacion
    if ev is None:
        return "No se evaluó con TypeSafe."
    if r.descartada:
        return r.motivo
    if ev.tono < UMBRAL_TONO:
        return f"Tono de marca bajo ({ev.tono:.1f} de 3)."
    if ev.tono_confianza < UMBRAL_CONFIANZA:
        return f"TypeSafe no está seguro del tono (confianza {ev.tono_confianza:.2f})."
    return None


def correcciones_para_redactor(resultados: list[Resultado]) -> list[str]:
    """Resume los problemas de una ronda para pedirle a Claude que los corrija."""
    problemas = []
    for r in resultados:
        if r.descartada:
            problemas.append(f"Variante «{r.pieza.gancho}»: {r.motivo}")
        elif r.evaluacion and r.evaluacion.tono < UMBRAL_TONO:
            problemas.append(f"Variante «{r.pieza.gancho}»: el tono no suena a la marca.")
    return problemas
