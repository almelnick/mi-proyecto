from pathlib import Path

from typesafe_sdk import NoulAnswer, ScoreAnswer

from generador import evaluador
from generador.marca import Marca
from generador.modelos import Pieza, Resultado, Slide

MARCA = Marca.cargar(Path(__file__).parent.parent / "marcas" / "ejemplo.yaml")


def _pieza(gancho: str) -> Pieza:
    return Pieza(
        gancho=gancho,
        slides=[Slide(titulo="Hola", texto="", locucion="")],
        caption="Ven a probarlo.",
        cta="Visítanos",
        hashtags=["#CaféAurora"],
    )


class _Respuesta:
    def __init__(self, tono: float, reglas: list[float], cta: float):
        self.scores = {
            "tono": ScoreAnswer(
                type="score", score=tono, confidence=0.9,
                legend={0: "a", 1: "b", 2: "c", 3: "d"}, probabilities={0: 0.0, 1: 0.1, 2: 0.2, 3: 0.7},
            )
        }
        self.nouls = {f"regla_{i}": NoulAnswer(type="noul", noul=p) for i, p in enumerate(reglas)}
        self.nouls["cta"] = NoulAnswer(type="noul", noul=cta)


class _ClienteFalso:
    def __init__(self, respuesta: _Respuesta):
        self.respuesta = respuesta
        self.llamadas = []

    def system_one(self, state, questions):
        self.llamadas.append((state, questions))
        return self.respuesta


def test_evaluar_hace_una_pregunta_por_regla():
    cliente = _ClienteFalso(_Respuesta(2.6, [0.1, 0.9, 0.0, 0.2], 0.8))
    ev = evaluador.evaluar(cliente, MARCA, _pieza("A"), "instagram")

    _, preguntas = cliente.llamadas[0]
    assert set(preguntas) == {"tono", "cta", "regla_0", "regla_1", "regla_2", "regla_3"}
    assert ev.tono == 2.6
    assert ev.reglas_violadas[MARCA.reglas_prohibidas[1]] == 0.9


def _resultado(gancho, tono, regla_max=0.0, cta=0.9):
    reglas = {r: 0.0 for r in MARCA.reglas_prohibidas}
    reglas[MARCA.reglas_prohibidas[0]] = regla_max
    return Resultado(
        pieza=_pieza(gancho),
        evaluacion=evaluador.Evaluacion(tono=tono, tono_confianza=0.9, reglas_violadas=reglas, tiene_cta_claro=cta),
    )


def test_clasificar_descarta_reglas_rotas_aunque_el_tono_sea_alto():
    ordenados = evaluador.clasificar(
        [_resultado("rompe", 3.0, regla_max=0.8), _resultado("buena", 2.4), _resultado("floja", 1.2)]
    )
    assert [r.pieza.gancho for r in ordenados] == ["buena", "floja", "rompe"]
    assert ordenados[-1].descartada
    assert evaluador.necesita_revision(ordenados[0]) is None


def test_tono_bajo_pide_revision_humana():
    ordenados = evaluador.clasificar([_resultado("floja", 1.5)])
    assert "Tono" in evaluador.necesita_revision(ordenados[0])
    assert evaluador.correcciones_para_redactor(ordenados)
