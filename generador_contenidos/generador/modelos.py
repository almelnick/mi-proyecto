"""Estructuras de las piezas de contenido."""

from typing import Literal

from pydantic import BaseModel, Field

Formato = Literal["imagen", "carrusel", "video"]
Red = Literal["instagram", "linkedin", "tiktok", "facebook"]


TipoLamina = Literal["portada", "texto", "dato", "lista", "comparacion", "cita", "cierre"]


class Slide(BaseModel):
    tipo: TipoLamina = Field(
        default="texto",
        description=(
            "Diseño de la lámina. portada: primera lámina, título grande con etiqueta. "
            "texto: título y texto de apoyo. dato: una cifra protagonista en `dato`. "
            "lista: 2 a 4 puntos breves en `items`. comparacion: un antes y un después numéricos "
            "en `antes` y `despues`, se dibuja como gráfico de barras. cita: una frase destacada en "
            "`titulo`. cierre: última lámina con el llamado a la acción. Varía los tipos para que "
            "la pieza no sea solo texto."
        ),
    )
    etiqueta: str = Field(default="", description="Etiqueta corta sobre el título (2 a 4 palabras). Opcional.")
    dato: str = Field(default="", description="Solo tipo dato: la cifra grande, por ejemplo '20.000 UTM'.")
    items: list[str] = Field(default_factory=list, description="Solo tipo lista: 2 a 4 puntos de máximo 8 palabras.")
    antes: str = Field(default="", description="Solo tipo comparacion: valor inicial con su unidad, por ejemplo '3'.")
    despues: str = Field(default="", description="Solo tipo comparacion: valor final, por ejemplo '10'.")
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
