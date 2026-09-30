"""Lectura del CSV de keywords y de la ficha del negocio."""

import csv
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Nombres de columna que usan Ubersuggest, Semrush, Ahrefs, Keyword Planner y otras herramientas.
COLUMNAS = {
    "keyword": ["keyword", "keywords", "palabra clave", "palabras clave", "query", "consulta", "termino"],
    "volumen": ["volumen", "volume", "search volume", "vol", "avg. monthly searches", "busquedas mensuales"],
    "dificultad": ["dificultad", "difficulty", "kd", "sd", "seo difficulty", "keyword difficulty", "kd %"],
    "cpc": ["cpc", "cpc (usd)", "cpcdollars", "costo por clic"],
}


@dataclass
class Keyword:
    keyword: str
    volumen: int = 0
    dificultad: float | None = None  # 0 a 100
    cpc: float | None = None


@dataclass
class Negocio:
    nombre: str
    descripcion: str
    servicios: dict[str, str]
    pais: str = ""
    sitio: str = ""
    clientes_ideales: str = ""
    competidores_conocidos: list[str] = field(default_factory=list)

    @classmethod
    def cargar(cls, ruta: str | Path) -> "Negocio":
        datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))
        if not datos.get("servicios"):
            raise ValueError("La ficha del negocio necesita al menos un servicio en `servicios`.")
        return cls(**datos)

    def para_ia(self) -> dict:
        return {
            "nombre": self.nombre,
            "sitio": self.sitio,
            "pais": self.pais,
            "descripcion": self.descripcion,
            "clientes_ideales": self.clientes_ideales,
            "servicios": self.servicios,
            "competidores_conocidos": self.competidores_conocidos,
        }


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", texto.strip().lower())


def _numero(valor: str) -> float | None:
    valor = (valor or "").strip().replace("%", "").replace("$", "")
    if not valor or valor in {"-", "n/a"}:
        return None
    # "1.600" (miles con punto) o "1,600" (miles con coma) o "0,45" (decimal con coma)
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", valor):
        valor = re.sub(r"[.,]", "", valor)
    else:
        valor = valor.replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return None


def leer_keywords(ruta: str | Path) -> list[Keyword]:
    texto = Path(ruta).read_text(encoding="utf-8-sig")
    separador = csv.Sniffer().sniff(texto.splitlines()[0], delimiters=",;\t").delimiter
    filas = list(csv.DictReader(texto.splitlines(), delimiter=separador))
    if not filas:
        return []

    encabezados = {_normalizar(c): c for c in filas[0].keys() if c}
    columnas = {}
    for campo, alias in COLUMNAS.items():
        for a in alias:
            if a in encabezados:
                columnas[campo] = encabezados[a]
                break
    if "keyword" not in columnas:
        raise ValueError(f"No encontré la columna de keywords. Columnas del archivo: {list(filas[0].keys())}")

    vistas, keywords = set(), []
    for fila in filas:
        kw = (fila.get(columnas["keyword"]) or "").strip()
        if not kw or _normalizar(kw) in vistas:
            continue
        vistas.add(_normalizar(kw))
        volumen = _numero(fila.get(columnas.get("volumen", ""), "")) if "volumen" in columnas else None
        keywords.append(
            Keyword(
                keyword=kw,
                volumen=int(volumen or 0),
                dificultad=_numero(fila.get(columnas["dificultad"], "")) if "dificultad" in columnas else None,
                cpc=_numero(fila.get(columnas["cpc"], "")) if "cpc" in columnas else None,
            )
        )
    return keywords
