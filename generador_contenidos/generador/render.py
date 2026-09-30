"""Convierte las láminas en PNG con los colores, fuentes y logo de la marca."""

import base64
import mimetypes
import shutil
import subprocess
import tempfile
import os
import re
from pathlib import Path

import imageio_ffmpeg
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape
from playwright.sync_api import sync_playwright

from .marca import EstiloVisual, Marca, Tema
from .modelos import Formato, Pieza

PLANTILLAS = Path(__file__).parent / "plantillas"

# Ancho x alto en píxeles. Imagen y carrusel en 4:5 (feed); video en 9:16 (reels, TikTok).
TAMANOS = {"imagen": (1080, 1350), "carrusel": (1080, 1350), "video": (1080, 1920)}

_entorno = Environment(loader=FileSystemLoader(PLANTILLAS), autoescape=select_autoescape(["html"]))


def _embebido(ruta: Path | None) -> str | None:
    if ruta is None:
        return None
    tipo = mimetypes.guess_type(ruta.name)[0] or ("font/woff2" if ruta.suffix == ".woff2" else "image/png")
    return f"data:{tipo};base64," + base64.b64encode(ruta.read_bytes()).decode()


# Estilos que se alternan según el tipo de lámina cuando la lámina pide "auto".
ROTACION = {
    "portada": ["oscuro"],
    "texto": ["claro", "azul"],
    "dato": ["acento", "azul", "claro", "oscuro"],
    "lista": ["claro", "oscuro"],
    "comparacion": ["oscuro", "claro"],
    "cita": ["azul", "claro"],
    "cierre": ["acento"],
    "persona": ["oscuro", "azul"],
}


def temas(e: EstiloVisual) -> dict[str, Tema]:
    """Paletas disponibles: las del kit de marca y, si faltan, derivadas de sus colores."""
    a2 = e.color_acento_2 or e.color_acento
    derivados = {
        "oscuro": Tema(fondo=e.color_fondo, texto=e.color_texto, secundario=e.color_secundario,
                       acento=e.color_acento, acento_2=a2),
        "claro": Tema(fondo=e.color_texto, texto=e.color_fondo, secundario=e.color_fondo + "B3",
                      acento=a2, acento_2=e.color_acento, marcador=e.color_acento,
                      marcador_texto=e.color_fondo, logo_oscuro=True),
        "azul": Tema(fondo=a2, texto=e.color_texto, secundario=e.color_texto + "CC",
                     acento=e.color_acento, acento_2=e.color_acento),
        "acento": Tema(fondo=e.color_acento, texto=e.color_fondo, secundario=e.color_fondo + "CC",
                       acento=e.color_fondo, acento_2=e.color_fondo, marcador=e.color_fondo,
                       marcador_texto=e.color_acento, logo_oscuro=True),
    }
    return derivados | e.temas


def estilos_de(pieza: Pieza) -> list[str]:
    """Elige el estilo de cada lámina, alternando para que dos seguidas no se repitan."""
    elegidos: list[str] = []
    usos: dict[str, int] = {}
    for slide in pieza.slides:
        if slide.estilo != "auto":
            elegidos.append(slide.estilo)
            continue
        opciones = ROTACION.get(slide.tipo, ["oscuro"])
        n = usos.get(slide.tipo, 0)
        usos[slide.tipo] = n + 1
        estilo = opciones[n % len(opciones)]
        if elegidos and estilo == elegidos[-1] and len(opciones) > 1:
            estilo = opciones[(n + 1) % len(opciones)]
        elegidos.append(estilo)
    return elegidos


def _marcar(texto: str) -> Markup:
    """*palabra* se resalta con marcador y _palabra_ pasa a serif itálica."""
    html = str(escape(texto))
    html = re.sub(r"\*(.+?)\*", r"<mark>\1</mark>", html)
    html = re.sub(r"(?<![\w/])_(.+?)_(?![\w/])", r'<i class="serif">\1</i>', html)
    return Markup(html)


def _numero(texto: str) -> float | None:
    """Lee '3', '10x', '20.000 UTM' o '4,5 %' como número (formato chileno)."""
    m = re.search(r"\d[\d.,]*", texto)
    if not m:
        return None
    limpio = re.sub(r"\.(?=\d{3}(\D|$))", "", m.group()).replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        return None


def _barras(antes: str, despues: str, alto_max: int) -> tuple[int, int] | None:
    a, d = _numero(antes), _numero(despues)
    if a is None or d is None or max(a, d) <= 0:
        return None
    tope = max(a, d)
    return max(24, round(alto_max * a / tope)), max(24, round(alto_max * d / tope))


def _html(
    marca: Marca,
    pieza: Pieza,
    formato: Formato,
    indice: int,
    fondo: Path | None = None,
    animar: bool = False,
    duracion: float = 0,
) -> str:
    ancho, alto = TAMANOS[formato]
    slide = pieza.slides[indice - 1]
    largo = len(re.sub(r"[*_]", "", slide.titulo))
    e = marca.estilo_visual
    tema = temas(e)[estilos_de(pieza)[indice - 1]]
    alto_grafico = 420 if formato != "video" else 700
    return _entorno.get_template("lamina.html").render(
        ancho=ancho,
        alto=alto,
        margen=96,
        tam_titulo=112 if largo < 30 else 90 if largo < 60 else 72,
        tam_texto=42,
        tam_dato=240 if len(slide.dato) <= 6 else 170 if len(slide.dato) <= 10 else 130,
        alto_grafico=alto_grafico,
        barras=_barras(slide.antes, slide.despues, alto_grafico),
        cta=pieza.cta,
        es_carrusel=formato == "carrusel",
        animar=animar,
        duracion=duracion,
        e=e,
        t=tema,
        titulo=_marcar(slide.titulo),
        texto=_marcar(slide.texto),
        foto_persona=_embebido(marca.ruta_persona(slide.persona)) if slide.tipo == "persona" else None,
        persona=marca.personas.get(slide.persona),
        marca=marca.nombre,
        logo=_embebido(marca.ruta_logo()),
        fuentes={familia: _embebido(ruta) for familia, ruta in marca.rutas_fuentes().items()},
        fondo=_embebido(fondo),
        slide=slide,
        indice=indice,
        total=len(pieza.slides),
    )


def _lanzar(p):
    ruta = os.environ.get("CHROMIUM_PATH")
    if ruta:
        return p.chromium.launch(executable_path=ruta)
    try:
        return p.chromium.launch()
    except Exception:
        # Entornos con un Chromium preinstalado que no coincide con la versión de Playwright.
        for candidato in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"):
            return p.chromium.launch(executable_path=str(candidato))
        raise


def renderizar(
    marca: Marca, pieza: Pieza, formato: Formato, carpeta: Path, fondos: list[Path] | None = None
) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    ancho, alto = TAMANOS[formato]
    archivos = []
    with sync_playwright() as p:
        navegador = _lanzar(p)
        pagina = navegador.new_page(viewport={"width": ancho, "height": alto})
        for i in range(1, len(pieza.slides) + 1):
            fondo = fondos[i - 1] if fondos else None
            pagina.set_content(_html(marca, pieza, formato, i, fondo), wait_until="load")
            destino = carpeta / f"lamina_{i:02d}.png"
            pagina.screenshot(path=str(destino))
            archivos.append(destino)
        navegador.close()
    return archivos


# Pone todas las animaciones CSS en el mismo instante para capturar un cuadro exacto.
_FIJAR_TIEMPO = "t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t; })"


def renderizar_animado(
    marca: Marca,
    pieza: Pieza,
    carpeta: Path,
    duraciones: list[float],
    fondos: list[Path] | None = None,
    fps: int = 30,
) -> list[Path]:
    """Graba un clip MP4 por escena con las animaciones de entrada de la plantilla."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ancho, alto = TAMANOS["video"]
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    clips = []
    with sync_playwright() as p:
        navegador = _lanzar(p)
        pagina = navegador.new_page(viewport={"width": ancho, "height": alto})
        for i, duracion in enumerate(duraciones, 1):
            fondo = fondos[i - 1] if fondos else None
            pagina.set_content(_html(marca, pieza, "video", i, fondo, animar=True, duracion=duracion), wait_until="load")
            cuadros = Path(tempfile.mkdtemp(prefix="cuadros_"))
            try:
                for n in range(round(duracion * fps)):
                    pagina.evaluate(_FIJAR_TIEMPO, n * 1000 / fps)
                    pagina.screenshot(path=str(cuadros / f"{n:05d}.jpg"), type="jpeg", quality=92)
                clip = carpeta / f"escena_{i:02d}.mp4"
                subprocess.run(
                    [ffmpeg, "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(cuadros / "%05d.jpg"),
                     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(clip)],
                    check=True,
                )
                clips.append(clip)
            finally:
                shutil.rmtree(cuadros, ignore_errors=True)
        navegador.close()
    return clips
