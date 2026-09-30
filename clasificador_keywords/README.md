# Clasificador de keywords con Jev

Toma una lista de keywords (de Ubersuggest, Semrush, Ahrefs o Keyword Planner) y la ficha de un negocio, y entrega un Excel con cada keyword clasificada y priorizada: qué atacar primero, con qué tipo de página y qué descartar.

## Qué hace Jev y qué hace el código

**Jev (TypeSafe)** responde siete preguntas cerradas por keyword, cada una con su probabilidad o confianza:

| Pregunta | Tipo | Respuestas |
|---|---|---|
| Intención de búsqueda | elección | informacional, comercial, transaccional, navegacional |
| Etapa del embudo | elección | TOFU, MOFU, BOFU |
| Servicio que la responde | elección | los servicios de la ficha, o "ninguno" |
| Relevancia para ganar clientes | puntaje 0–3 | de "no tiene relación" a "es exactamente lo que vende" |
| ¿Nombra a otra marca? | probabilidad | competidores, herramientas |
| ¿Busca empleo, curso, recurso gratis o login? | probabilidad | |
| ¿Es de otro país? | probabilidad | |

**El código** (`clasificador/prioridad.py`) decide con esas respuestas:

- **Excluir** si nombra a otra marca, no es un cliente potencial o es de otro país (probabilidad ≥ 60 %).
- **Baja relevancia** si la relevancia es menor a 1,5 o no calza con ningún servicio.
- **Revisar** si Jev tiene poca confianza (< 50 %) en la intención, la etapa, el servicio o la relevancia.
- **Atacar** en el resto, con una prioridad de 0 a 100 aprox.:
  `relevancia/3 × peso de la intención × log10(volumen + 10) × (1 − dificultad/100) × 100`.
  Pesos: transaccional 1, comercial 0,8, informacional 0,4 y navegacional 0,1. Si falta la dificultad, se usa 50.
  También sugiere qué crear: una página de servicio o landing, una comparativa o caso, o un artículo de blog.

Los umbrales y pesos están al inicio de `prioridad.py`. Son valores iniciales y conviene ajustarlos después de la primera corrida.

## Excel de salida

- **Keywords**: todas las keywords con sus métricas, la decisión (con color), la prioridad y lo que respondió Jev.
- **Prioridades**: solo las keywords para atacar, en orden, con el tipo de página sugerido.
- **Servicio x etapa**: cuántas keywords y cuánto volumen hay por servicio y etapa. Muestra dónde faltan contenidos.
- **Costo**: solicitudes, tokens y dólares exactos de la corrida, según el `usage` que devuelve Jev.

## Cómo correrlo en tu Mac

```bash
cd clasificador_keywords
pip install -r requirements.txt
export TYPESAFE_API_KEY=...   # la clave de typesafe.ai

# Ejemplo con 106 keywords reales de Sprint LATAM (Ubersuggest, Chile, sep 2026)
python -m clasificador --negocio negocios/sprint_latam.yaml --keywords ejemplos/sprint_keywords_chile.csv
```

Opciones:

- `--limite 50`: clasifica solo las 50 keywords con más volumen, útil para una prueba barata.
- `--volumen-minimo 20`: ignora keywords con menos de 20 búsquedas al mes.
- `--presupuesto 0.05`: deja de consultar a Jev cuando el gasto llega a US$0,05.
- `--salida archivo.xlsx`: por defecto el Excel queda en `salida/<negocio>-<fecha>.xlsx`.

Al terminar muestra en pantalla el conteo por decisión, las 10 keywords más prioritarias y el costo.

## Costo

Jev cobra US$0,042 por millón de tokens de entrada y no cobra los de salida. Cada keyword usa del orden de 1.000 a 1.500 tokens, así que:

- 100 keywords cuestan cerca de US$0,005;
- 10.000 keywords cuestan cerca de US$0,50.

El Excel informa el costo real de cada corrida.

## Para otro negocio

Copia `negocios/sprint_latam.yaml`, cambia la descripción, el país, los clientes ideales, los servicios (con una línea de descripción por servicio) y los competidores conocidos. El CSV puede venir de cualquier herramienta. El programa reconoce columnas como `Keyword`/`Palabra clave`, `Volume`/`Volumen`, `SD`/`KD`/`Dificultad` y `CPC`, separadas por coma, punto y coma o tabulación.

## Pruebas

```bash
python -m pytest tests
```

Las pruebas usan un cliente falso, así que no gastan tokens.
