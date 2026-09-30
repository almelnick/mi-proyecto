"""Preguntas tipadas a Jev (TypeSafe) para clasificar cada keyword.

Jev no inventa keywords ni escribe: responde, para cada keyword, preguntas cerradas con
probabilidades. Las reglas de negocio (prioridad, exclusiones, umbrales) quedan en
`prioridad.py`.
"""

import asyncio
from dataclasses import dataclass, field

from typesafe_sdk import Choice, Noul, Score

from .entrada import Keyword, Negocio

USD_POR_MILLON_ENTRADA = 0.042  # precio de Jev publicado en jev-seo; los tokens de salida no se cobran
CONCURRENCIA = 8

INTENCIONES = {
    "informacional": "The searcher wants to learn or understand something (what is, how to, guide, examples).",
    "comercial": "The searcher is comparing or researching providers or options before buying "
    "(best, agency, prices, reviews, vs).",
    "transaccional": "The searcher wants to hire, buy or contact now (contratar, cotizar, agencia + city, service + precio).",
    "navegacional": "The searcher wants a specific website, tool, login or brand page.",
}

ETAPAS = {
    "tofu": "Top of funnel: early awareness, the searcher does not yet know they need `negocio`'s services.",
    "mofu": "Middle of funnel: the searcher knows the problem and is evaluating solutions or providers.",
    "bofu": "Bottom of funnel: the searcher is ready to hire or buy a service like those in `negocio.servicios`.",
}

NIVELES_RELEVANCIA = [
    "Unrelated: someone searching `keyword` would never become a client of `negocio`.",
    "Loosely related: same topic, but the searcher is very unlikely to hire `negocio` "
    "(different country, do-it-yourself, student, or a different need).",
    "Related: the searcher could need `negocio`'s services, although the intent is not explicit.",
    "Core: the searcher is looking for exactly what `negocio` sells, in `negocio.pais` or without a location.",
]


def preguntas(negocio: Negocio) -> dict:
    servicios = {nombre: descripcion for nombre, descripcion in negocio.servicios.items()}
    servicios["ninguno"] = "The keyword does not match any service in `negocio.servicios`."
    return {
        "intencion": Choice(
            instructions="Main search intent behind `keyword` for a searcher in `pais`.",
            criteria=INTENCIONES,
        ),
        "etapa": Choice(
            instructions="Funnel stage of someone searching `keyword`, from the point of view of `negocio`.",
            criteria=ETAPAS,
        ),
        "servicio": Choice(
            instructions="Which service of `negocio` best answers `keyword`.",
            criteria=servicios,
        ),
        "relevancia": Score(
            instructions="How relevant `keyword` is as a way to win clients for `negocio`.",
            criteria=NIVELES_RELEVANCIA,
        ),
        "competidor": Noul(
            instructions="`keyword` names a specific company, agency, tool or brand other than `negocio` "
            "(for example one in `negocio.competidores_conocidos`, or a product like Google Ads Editor).",
        ),
        "no_cliente": Noul(
            instructions="The person searching `keyword` is looking for a job, a course, a certification, "
            "a free resource, a login page or technical support, not for a provider to hire.",
        ),
        "otro_pais": Noul(
            instructions="`keyword` names a city or country outside `pais`.",
        ),
    }


@dataclass
class Clasificacion:
    keyword: Keyword
    intencion: str = ""
    intencion_confianza: float = 0.0
    etapa: str = ""
    etapa_confianza: float = 0.0
    servicio: str = ""
    servicio_confianza: float = 0.0
    relevancia: float = 0.0
    relevancia_confianza: float = 0.0
    competidor: float = 0.0
    no_cliente: float = 0.0
    otro_pais: float = 0.0
    error: str = ""
    # Los completa prioridad.py
    prioridad: float = 0.0
    decision: str = ""
    motivo: str = ""


@dataclass
class Costo:
    solicitudes: int = 0
    fallidas: int = 0
    omitidas_por_presupuesto: int = 0
    tokens_entrada: int = 0
    tokens_salida: int = 0
    modelo: str = ""
    errores: list[str] = field(default_factory=list)

    @property
    def usd(self) -> float:
        return self.tokens_entrada * USD_POR_MILLON_ENTRADA / 1_000_000


def _leer(respuesta, kw: Keyword) -> Clasificacion:
    c = Clasificacion(keyword=kw)
    for nombre in ("intencion", "etapa", "servicio"):
        eleccion = respuesta.choices[nombre]
        setattr(c, nombre, eleccion.choice)
        setattr(c, f"{nombre}_confianza", eleccion.confidence)
    c.relevancia = respuesta.scores["relevancia"].score
    c.relevancia_confianza = respuesta.scores["relevancia"].confidence
    c.competidor = respuesta.nouls["competidor"].noul
    c.no_cliente = respuesta.nouls["no_cliente"].noul
    c.otro_pais = respuesta.nouls["otro_pais"].noul
    return c


async def clasificar(
    cliente, negocio: Negocio, keywords: list[Keyword], presupuesto_usd: float | None = None, al_avanzar=None
) -> tuple[list[Clasificacion], Costo]:
    """Clasifica todas las keywords en paralelo. `cliente` es un AsyncTypeSafeClient."""
    costo = Costo()
    semaforo = asyncio.Semaphore(CONCURRENCIA)
    lista_preguntas = preguntas(negocio)
    ficha = negocio.para_ia()

    async def una(kw: Keyword) -> Clasificacion:
        async with semaforo:
            if presupuesto_usd is not None and costo.usd >= presupuesto_usd:
                costo.omitidas_por_presupuesto += 1
                return Clasificacion(keyword=kw, error="Omitida: se alcanzó el presupuesto.")
            costo.solicitudes += 1
            try:
                respuesta = await cliente.system_one(
                    state={"negocio": ficha, "pais": negocio.pais, "keyword": kw.keyword},
                    questions=lista_preguntas,
                )
            except Exception as e:  # una keyword que falla no detiene el resto
                costo.fallidas += 1
                costo.errores.append(f"{kw.keyword}: {e}")
                return Clasificacion(keyword=kw, error=str(e))
            finally:
                if al_avanzar:
                    al_avanzar()
            uso = getattr(respuesta, "usage", None)
            if uso is not None:
                costo.tokens_entrada += uso.input_tokens or 0
                costo.tokens_salida += uso.output_tokens or 0
            costo.modelo = getattr(respuesta, "model", None) or costo.modelo
            return _leer(respuesta, kw)

    resultados = await asyncio.gather(*(una(kw) for kw in keywords))
    return list(resultados), costo
