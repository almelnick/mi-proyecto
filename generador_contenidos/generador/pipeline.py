"""Flujo completo: redactar variantes, filtrarlas por marca y producir los archivos."""

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from . import evaluador, redactor
from .marca import Marca
from .modelos import Formato, Pieza, Red, Resultado
from .render import renderizar, renderizar_animado
from .video import armar_video, duraciones_por_escena

MAX_RONDAS = 2


def _slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")[:40] or "pieza"


def _elegir(marca: Marca, tema: str, formato: Formato, red: Red, variantes: int) -> list[Resultado]:
    from typesafe_sdk import TypeSafeClient

    correcciones: list[str] = []
    resultados: list[Resultado] = []
    with TypeSafeClient() as cliente:
        for _ in range(MAX_RONDAS):
            piezas = redactor.redactar(marca, tema, formato, red, variantes, correcciones or None)
            ronda = [
                Resultado(pieza=p, evaluacion=evaluador.evaluar(cliente, marca, p, red)) for p in piezas
            ]
            resultados = evaluador.clasificar(resultados + ronda)
            if evaluador.necesita_revision(resultados[0]) is None:
                break
            correcciones = evaluador.correcciones_para_redactor(ronda)
    return resultados


def _texto_publicacion(r: Resultado, formato: Formato, revision: str | None) -> str:
    p = r.pieza
    lineas = [f"# {p.gancho}", ""]
    if revision:
        lineas += [f"> ⚠️ Revisar antes de publicar: {revision}", ""]
    lineas += ["## Texto de la publicación", "", p.caption, "", f"**Llamado a la acción:** {p.cta}", ""]
    lineas += [" ".join(p.hashtags), ""]
    if formato == "video":
        lineas += ["## Guion de locución", ""]
        lineas += [f"{i}. **{s.titulo}**: {s.locucion}" for i, s in enumerate(p.slides, 1)]
        lineas.append("")
    return "\n".join(lineas)


def generar(
    marca: Marca,
    tema: str,
    formato: Formato,
    red: Red,
    variantes: int = 3,
    salida: Path = Path("salida"),
    sin_ia: bool = False,
    imagenes_ia: bool = False,
    voz: bool = False,
    pieza: Pieza | None = None,
    animar: bool = True,
) -> Path:
    if pieza is not None:
        resultados = [Resultado(pieza=pieza)]
    elif sin_ia:
        resultados = [Resultado(pieza=p) for p in redactor.redactar_sin_ia(marca, tema, formato, variantes)]
    else:
        resultados = _elegir(marca, tema, formato, red, variantes)

    elegida = resultados[0]
    revision = evaluador.necesita_revision(elegida)

    carpeta = salida / f"{datetime.now():%Y%m%d-%H%M%S}-{_slug(tema)}-{formato}"
    fondos = None
    if imagenes_ia:
        from .imagenes import generar_fondos

        fondos = generar_fondos(marca, elegida.pieza, carpeta / "fondos")
    laminas = renderizar(marca, elegida.pieza, formato, carpeta / "laminas", fondos)
    if formato == "video":
        audios = None
        if voz:
            from .voz import locutar

            audios = locutar(marca, elegida.pieza, carpeta / "voz")
        clips = None
        if animar:
            duraciones = duraciones_por_escena(audios, len(laminas))
            clips = renderizar_animado(marca, elegida.pieza, carpeta / "escenas", duraciones, fondos)
        armar_video(laminas, carpeta / "video.mp4", audios, clips)

    (carpeta / "publicacion.md").write_text(_texto_publicacion(elegida, formato, revision), encoding="utf-8")
    informe = {
        "marca": marca.nombre,
        "tema": tema,
        "formato": formato,
        "red": red,
        "revision_humana": revision,
        "variantes": [r.model_dump() for r in resultados],
    }
    (carpeta / "informe.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    return carpeta
