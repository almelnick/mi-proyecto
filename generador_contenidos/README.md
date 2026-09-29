# Generador de contenidos para redes sociales

Crea imágenes, carruseles y videos cortos para redes sociales que respetan el tono y el estilo visual de cada marca.

## Cómo funciona

1. **Kit de marca** (`marcas/*.yaml`): tono, lo que sí y lo que no, reglas prohibidas, vocabulario, ejemplos, colores, fuentes y logo.
2. **Redacción (Claude)**: escribe varias variantes del contenido siguiendo el kit de marca.
3. **Control de marca (TypeSafe)**: evalúa cada variante con preguntas tipadas:
   - un puntaje de 0 a 3 de qué tan fiel es al tono de la marca;
   - la probabilidad de que rompa cada regla prohibida (una pregunta por regla);
   - si tiene un llamado a la acción claro.

   El código descarta las variantes que rompen reglas y ordena el resto por tono. Si ninguna alcanza el mínimo, le pide a Claude una segunda ronda con las correcciones. Si aun así no alcanza, la pieza queda marcada para **revisión humana**.
4. **Fondos con IA (opcional, `--imagenes-ia`)**: Claude describe qué debe verse en cada lámina y OpenAI genera la imagen con el estilo fotográfico y la paleta de la marca, sin texto.
5. **Diseño**: dibuja cada lámina con los colores, fuentes y logo de la marca y la guarda como PNG. Con fondo, la foto queda arriba y el texto abajo sobre un degradado del color de la marca.
6. **Video**: une las láminas en un MP4 vertical con zoom suave y transiciones. Con `--voz`, ElevenLabs lee el guion de locución y cada escena dura lo necesario para que la frase termine antes del cambio.

## Instalación

```bash
cd generador_contenidos
pip install -r requirements.txt
playwright install chromium   # solo la primera vez
export ANTHROPIC_API_KEY=...
export TYPESAFE_API_KEY=...
```

Claves necesarias (como variables de entorno; `.env.example` muestra la lista):

- `ANTHROPIC_API_KEY`: para redactar con Claude.
- `TYPESAFE_API_KEY`: para el control de marca con TypeSafe.
- `OPENAI_API_KEY`: solo si usas `--imagenes-ia`. El modelo se cambia con `IMAGEN_MODELO` (por defecto `gpt-image-2`).
- `ELEVENLABS_API_KEY`: solo si usas `--voz`.

## Uso

```bash
# Carrusel para Instagram
python -m generador --marca marcas/ejemplo.yaml --tema "nuevo café de Huila" --formato carrusel

# Imagen única para LinkedIn
python -m generador --marca marcas/ejemplo.yaml --tema "abrimos los domingos" --formato imagen --red linkedin

# Video vertical para TikTok o Reels
python -m generador --marca marcas/ejemplo.yaml --tema "cómo tostamos" --formato video --red tiktok

# Carrusel con fondos generados con IA
python -m generador --marca marcas/ejemplo.yaml --tema "nuevo café de Huila" --formato carrusel --imagenes-ia

# Video con fondos con IA y voz en off
python -m generador --marca marcas/ejemplo.yaml --tema "cómo tostamos" --formato video --imagenes-ia --voz

# Probar sin claves de API (usa textos de relleno)
python -m generador --marca marcas/ejemplo.yaml --tema "prueba" --formato carrusel --sin-ia
```

Cada ejecución crea una carpeta en `salida/` con:

- `laminas/`: las imágenes PNG (1080×1350 para imagen y carrusel; 1080×1920 para video).
- `fondos/`: las imágenes generadas con IA (con `--imagenes-ia`).
- `voz/`: un audio por escena (con `--voz`).
- `video.mp4`: solo en formato video.
- `publicacion.md`: texto de la publicación, llamado a la acción, hashtags y, en video, el guion de locución.
- `informe.json`: todas las variantes con sus puntajes de TypeSafe y el motivo si requiere revisión.

## Agregar una marca

Copia `marcas/ejemplo.yaml`, cambia los valores y, si tienes logo, ponlo junto al YAML e indica su nombre en `estilo_visual.logo`.
Mientras más concretos sean el tono, las reglas y los ejemplos, mejor redacta Claude y mejor juzga TypeSafe.

## Ajustes

Los umbrales del control de marca están al inicio de `generador/evaluador.py` (`UMBRAL_REGLA`, `UMBRAL_TONO`, `UMBRAL_CONFIANZA`). Son valores iniciales: conviene revisarlos con piezas reales de cada marca.

## Pruebas

```bash
python -m pytest tests
```
