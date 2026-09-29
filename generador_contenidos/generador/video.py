"""Arma un video vertical MP4 a partir de las láminas renderizadas."""

import subprocess
from pathlib import Path

import imageio_ffmpeg

from .voz import duracion

SEGUNDOS_POR_ESCENA = 3.5
TRANSICION = 0.5
FPS = 30
PAUSA_ANTES_DE_HABLAR = 0.2
PAUSA_DESPUES_DE_HABLAR = 0.4


def duraciones_por_escena(audios: list[Path | None] | None, escenas: int) -> list[float]:
    """Cada escena dura lo necesario para que su locución termine antes de la transición."""
    if not audios:
        return [SEGUNDOS_POR_ESCENA] * escenas
    return [
        max(SEGUNDOS_POR_ESCENA, PAUSA_ANTES_DE_HABLAR + duracion(a) + PAUSA_DESPUES_DE_HABLAR + TRANSICION)
        if a
        else SEGUNDOS_POR_ESCENA
        for a in audios
    ]


def armar_video(laminas: list[Path], destino: Path, audios: list[Path | None] | None = None) -> Path:
    """Une las láminas con un zoom suave y fundidos; si hay voz en off, la sincroniza por escena."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    duraciones = duraciones_por_escena(audios, len(laminas))
    entradas, filtros = [], []
    for i, lamina in enumerate(laminas):
        # Una sola imagen por entrada: zoompan genera por sí mismo los cuadros de la escena.
        entradas += ["-i", str(lamina)]
        cuadros = round(duraciones[i] * FPS)
        filtros.append(
            f"[{i}:v]scale=1080:1920,zoompan=z='min(zoom+0.0006,1.06)':d={cuadros}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS},format=yuv420p,setsar=1[v{i}]"
        )

    # Momento en que empieza cada escena, descontando el solape de los fundidos.
    inicios = [sum(duraciones[:i]) - i * TRANSICION for i in range(len(laminas))]

    ultimo = "v0"
    for i in range(1, len(laminas)):
        salida = f"x{i}"
        filtros.append(
            f"[{ultimo}][v{i}]xfade=transition=fade:duration={TRANSICION}:offset={inicios[i]:.3f}[{salida}]"
        )
        ultimo = salida

    mapas = ["-map", f"[{ultimo}]"]
    con_voz = [(i, a) for i, a in enumerate(audios or []) if a]
    if con_voz:
        pistas = []
        for n, (i, audio) in enumerate(con_voz):
            entradas += ["-i", str(audio)]
            retardo = round((inicios[i] + PAUSA_ANTES_DE_HABLAR) * 1000)
            filtros.append(f"[{len(laminas) + n}:a]adelay={retardo}:all=1[a{n}]")
            pistas.append(f"[a{n}]")
        filtros.append(f"{''.join(pistas)}amix=inputs={len(pistas)}:normalize=0[voz]")
        mapas += ["-map", "[voz]", "-c:a", "aac", "-b:a", "160k"]

    comando = [
        ffmpeg, "-y", "-loglevel", "error", *entradas,
        "-filter_complex", ";".join(filtros),
        *mapas, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(destino),
    ]
    subprocess.run(comando, check=True)
    return destino
