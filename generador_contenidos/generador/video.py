"""Arma un video vertical MP4 a partir de las láminas renderizadas."""

import subprocess
from pathlib import Path

import imageio_ffmpeg

SEGUNDOS_POR_ESCENA = 3.5
TRANSICION = 0.5
FPS = 30


def armar_video(laminas: list[Path], destino: Path) -> Path:
    """Une las láminas con un zoom suave y transiciones de fundido."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cuadros = int(SEGUNDOS_POR_ESCENA * FPS)
    entradas, filtros = [], []
    for i, lamina in enumerate(laminas):
        # Una sola imagen por entrada: zoompan genera por sí mismo los cuadros de la escena.
        entradas += ["-i", str(lamina)]
        filtros.append(
            f"[{i}:v]scale=1080:1920,zoompan=z='min(zoom+0.0006,1.06)':d={cuadros}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS},format=yuv420p,setsar=1[v{i}]"
        )

    ultimo = "v0"
    for i in range(1, len(laminas)):
        desfase = i * (SEGUNDOS_POR_ESCENA - TRANSICION)
        salida = f"x{i}"
        filtros.append(
            f"[{ultimo}][v{i}]xfade=transition=fade:duration={TRANSICION}:offset={desfase:.2f}[{salida}]"
        )
        ultimo = salida

    comando = [
        ffmpeg, "-y", "-loglevel", "error", *entradas,
        "-filter_complex", ";".join(filtros),
        "-map", f"[{ultimo}]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(destino),
    ]
    subprocess.run(comando, check=True)
    return destino
