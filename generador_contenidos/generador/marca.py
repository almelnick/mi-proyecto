"""Kit de marca: tono, reglas y estilo visual que toda pieza debe respetar."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Tono(BaseModel):
    descripcion: str
    si: list[str] = Field(default_factory=list)
    no: list[str] = Field(default_factory=list)


class EstiloVisual(BaseModel):
    color_fondo: str = "#1F2A44"
    color_texto: str = "#FFFFFF"
    color_acento: str = "#F2A541"
    color_secundario: str = "#E8E1D5"
    color_acento_2: str | None = None  # segundo acento para detalles (líneas, etiquetas, datos)
    fuente_titulos: str = "Georgia"
    fuente_texto: str = "Helvetica"
    logo: str | None = None  # ruta relativa al YAML de la marca
    # Tipografías propias: nombre de la familia -> archivo (woff2/ttf/otf) relativo al YAML.
    archivos_fuentes: dict[str, str] = Field(default_factory=dict)
    estilo_imagenes: str = "Fotografía natural, luz suave, composición limpia."


class Voz(BaseModel):
    id_voz: str | None = None  # ID de la voz en ElevenLabs
    modelo: str = "eleven_multilingual_v2"


class Marca(BaseModel):
    nombre: str
    descripcion: str
    publico: str
    tono: Tono
    reglas_prohibidas: list[str] = Field(default_factory=list)
    vocabulario_preferido: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    ejemplos: list[str] = Field(default_factory=list)
    estilo_visual: EstiloVisual = Field(default_factory=EstiloVisual)
    voz: Voz = Field(default_factory=Voz)

    carpeta: Path | None = Field(default=None, exclude=True)

    @classmethod
    def cargar(cls, ruta: str | Path) -> "Marca":
        ruta = Path(ruta)
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        marca = cls.model_validate(datos)
        marca.carpeta = ruta.parent
        return marca

    def ruta_logo(self) -> Path | None:
        if not self.estilo_visual.logo or self.carpeta is None:
            return None
        ruta = (self.carpeta / self.estilo_visual.logo).resolve()
        return ruta if ruta.exists() else None

    def rutas_fuentes(self) -> dict[str, Path]:
        if self.carpeta is None:
            return {}
        rutas = {familia: (self.carpeta / archivo).resolve() for familia, archivo in self.estilo_visual.archivos_fuentes.items()}
        return {familia: ruta for familia, ruta in rutas.items() if ruta.exists()}

    def resumen_para_ia(self) -> dict:
        """Datos de la marca que se envían a los modelos (sin estilo visual)."""
        return self.model_dump(exclude={"estilo_visual", "voz", "carpeta"})
