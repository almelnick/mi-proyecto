"""Pruebas de fondos, voz y video con archivos generados localmente (sin llamar a las APIs)."""

import base64
import subprocess
from pathlib import Path
from types import SimpleNamespace

import imageio_ffmpeg

from generador import imagenes, voz
from generador.marca import Marca
from generador.modelos import Pieza, Slide
from generador.render import renderizar
from generador.video import armar_video

MARCA = Marca.cargar(Path(__file__).parent.parent / "marcas" / "ejemplo.yaml")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def _pieza(escenas: int) -> Pieza:
    return Pieza(
        gancho="Prueba",
        slides=[
            Slide(titulo=f"Escena {i}", texto="Texto", locucion=f"Locución {i}" if i != 2 else "", imagen="Una taza")
            for i in range(1, escenas + 1)
        ],
        caption="Caption",
        cta="Ven",
        hashtags=["#prueba"],
    )


def _ffmpeg(*args: str) -> None:
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *args], check=True)


def _png(destino: Path) -> Path:
    _ffmpeg("-f", "lavfi", "-i", "testsrc=size=1024x1536", "-frames:v", "1", str(destino))
    return destino


def _mp3(destino: Path, segundos: float) -> Path:
    _ffmpeg("-f", "lavfi", "-i", f"sine=frequency=440:duration={segundos}", str(destino))
    return destino


def _info(video: Path) -> str:
    return subprocess.run([FFMPEG, "-i", str(video)], capture_output=True, text=True).stderr


def test_generar_fondos_pide_una_imagen_por_lamina_sin_texto(tmp_path, monkeypatch):
    llamadas = []
    png = _png(tmp_path / "muestra.png").read_bytes()

    class OpenAIFalso:
        def __init__(self):
            self.images = SimpleNamespace(generate=self.generate)

        def generate(self, **kwargs):
            llamadas.append(kwargs)
            return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(png).decode())])

    monkeypatch.setattr(imagenes, "OpenAI", OpenAIFalso)
    fondos = imagenes.generar_fondos(MARCA, _pieza(3), tmp_path / "fondos")

    assert len(fondos) == 3 and all(f.read_bytes() == png for f in fondos)
    assert "No incluyas texto" in llamadas[0]["prompt"]
    assert MARCA.estilo_visual.color_acento in llamadas[0]["prompt"]


def test_locutar_omite_escenas_sin_locucion(tmp_path, monkeypatch):
    textos = []

    class ElevenLabsFalso:
        def __init__(self):
            self.text_to_speech = SimpleNamespace(convert=self.convert)

        def convert(self, voice_id, **kwargs):
            textos.append(kwargs["text"])
            return iter([b"ID3", b"audio"])

    monkeypatch.setattr(voz, "ElevenLabs", ElevenLabsFalso)
    audios = voz.locutar(MARCA, _pieza(3), tmp_path / "voz")

    assert audios[1] is None
    assert textos == ["Locución 1", "Locución 3"]
    assert audios[0].read_bytes() == b"ID3audio"


def test_render_con_fondo(tmp_path):
    fondo = _png(tmp_path / "fondo.png")
    laminas = renderizar(MARCA, _pieza(1), "imagen", tmp_path / "laminas", [fondo])
    assert laminas[0].stat().st_size > 10_000


def test_video_con_voz_alarga_la_escena_y_lleva_audio(tmp_path):
    laminas = [_png(tmp_path / f"l{i}.png") for i in range(3)]
    audios = [_mp3(tmp_path / "a0.mp3", 6.0), None, _mp3(tmp_path / "a2.mp3", 1.0)]

    video = armar_video(laminas, tmp_path / "video.mp4", audios)
    info = _info(video)

    # Escena 1: 0.2 + 6.0 + 0.4 + 0.5 = 7.1 s; escenas 2 y 3: 4.0 s; menos dos transiciones de 0.5 s.
    assert "Duration: 00:00:14.1" in info
    assert "Audio: aac" in info
