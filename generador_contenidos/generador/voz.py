"""Voz en off con ElevenLabs: un audio por escena a partir del guion de locución."""

import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
from elevenlabs.client import ElevenLabs

from .marca import Marca
from .modelos import Pieza

# Voz multilingüe de la biblioteca de ElevenLabs; cada marca puede definir la suya en el YAML.
VOZ_POR_DEFECTO = "EXAVITQu4vr4xnSDxMaL"


def locutar(marca: Marca, pieza: Pieza, carpeta: Path) -> list[Path | None]:
    carpeta.mkdir(parents=True, exist_ok=True)
    cliente = ElevenLabs()
    audios: list[Path | None] = []
    for i, slide in enumerate(pieza.slides, 1):
        if not slide.locucion.strip():
            audios.append(None)
            continue
        partes = cliente.text_to_speech.convert(
            marca.voz.id_voz or VOZ_POR_DEFECTO,
            text=slide.locucion,
            model_id=marca.voz.modelo,
            language_code="es",
            output_format="mp3_44100_128",
        )
        destino = carpeta / f"escena_{i:02d}.mp3"
        destino.write_bytes(b"".join(partes))
        audios.append(destino)
    return audios


def duracion(audio: Path) -> float:
    """Duración en segundos, leída con ffmpeg."""
    salida = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(audio)], capture_output=True, text=True
    ).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", salida).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)
