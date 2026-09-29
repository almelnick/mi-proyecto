"""Estructuras de las piezas de contenido."""

from typing import Literal

from pydantic import BaseModel, Field

Formato = Literal["imagen", "carrusel", "video"]
Red = Literal["instagram", "linkedin", "tiktok", "facebook"]


class Slide(BaseModel):
    titulo: str = Field(description="Texto grande de la lámina o escena. Máximo 8 palabras.")
    texto: str = Field(description="Texto de apoyo. Máximo 25 palabras. Puede ir vacío.")
    locucion: str = Field(
        description="Solo para video: lo que dice la voz en off en esta escena. Vacío en otros formatos."
    )
    imagen: str = Field(
        description="Qué se ve en la imagen de fondo de esta lámina, en una o dos frases. Sin texto ni letras."
    )


class Pieza(BaseModel):
    gancho: str = Field(description="La idea central de la pieza en una frase.")
    slides: list[Slide] = Field(
        description="Imagen: 1 lámina. Carrusel: entre 5 y 8 láminas. Video: entre 4 y 6 escenas."
    )
    caption: str = Field(description="Texto que acompaña la publicación.")
    cta: str = Field(description="Llamado a la acción concreto.")
    hashtags: list[str] = Field(description="Entre 3 y 8 hashtags, cada uno con #.")


class Variantes(BaseModel):
    variantes: list[Pieza]


class Evaluacion(BaseModel):
    """Juicios de TypeSafe sobre una variante."""

    tono: float  # 0 a 3: qué tan fiel es al tono de la marca
    tono_confianza: float
    reglas_violadas: dict[str, float]  # regla -> probabilidad de que se viole
    tiene_cta_claro: float  # probabilidad


class Resultado(BaseModel):
    pieza: Pieza
    evaluacion: Evaluacion | None = None
    descartada: bool = False
    motivo: str = ""
