# Brand Mention Detector

Aplicación para detectar y monitorear menciones de tu marca en plataformas sociales, con enfoque en análisis de reputación y detección de links.

## Características

- **Monitoreo de Reddit**: Busca menciones de tu marca en posts y comentarios
- **Análisis de Sentimiento**: Clasifica menciones como positivas, negativas o neutrales usando VADER
- **Detección de Links**: Identifica y extrae URLs en las menciones
- **Análisis de Reputación**: Monitorea la percepción de tu marca
- **Almacenamiento Persistente**: Base de datos SQLite para histórico de menciones
- **CLI Interactivo**: Interfaz de línea de comandos con visualización rica
- **Extensible**: Arquitectura modular para agregar nuevas plataformas

## Instalación

### Requisitos

- Python 3.9 o superior
- Cuenta de Reddit (para API credentials)

### Pasos

1. Clona el repositorio:
```bash
git clone <repository-url>
cd mi-proyecto
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las credenciales de Reddit:
   - Ve a https://www.reddit.com/prefs/apps
   - Crea una nueva aplicación (script type)
   - Copia el client ID y secret

4. Crea el archivo `.env`:
```bash
cp .env.example .env
```

5. Edita `.env` con tus credenciales:
```env
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
REDDIT_USER_AGENT=BrandMentionDetector/1.0

BRAND_NAME=TuMarca
BRAND_KEYWORDS=TuMarca,tu marca,tumarca
BRAND_SUBREDDITS=all
```

## Uso

### Comandos Disponibles

#### Escanear Reddit por menciones
```bash
python -m src.main scan --limit 100
```

#### Ver menciones recientes
```bash
python -m src.main recent --limit 20
```

#### Ver menciones por sentimiento
```bash
python -m src.main positive --limit 20
python -m src.main negative --limit 20
python -m src.main neutral --limit 20
```

#### Ver menciones que contienen links
```bash
python -m src.main links --limit 20
```

#### Ver estadísticas
```bash
python -m src.main stats
```

### Opciones

- `--limit N`: Limita el número de resultados (default: 50)
- `--no-notify`: Desactiva notificaciones durante el escaneo

## Ejemplos de Uso

### Caso 1: Monitoreo inicial de marca

```bash
# Escanear Reddit buscando menciones
python -m src.main scan --limit 100

# Ver estadísticas generales
python -m src.main stats

# Revisar menciones negativas para gestión de reputación
python -m src.main negative --limit 10
```

### Caso 2: Detección de links y referencias

```bash
# Buscar menciones que incluyen links
python -m src.main links --limit 50
```

Esto es útil para:
- Detectar cuando mencionan tu sitio web
- Identificar links a competidores
- Encontrar oportunidades de participación

### Caso 3: Monitoreo de reputación

```bash
# Ver menciones positivas
python -m src.main positive

# Ver menciones negativas para responder rápidamente
python -m src.main negative
```

### Caso 4: Escaneo programado

Crea un cron job para escanear automáticamente:

```bash
# Editar crontab
crontab -e

# Agregar línea para escanear cada hora
0 * * * * cd /path/to/mi-proyecto && python -m src.main scan --limit 50 --no-notify
```

## Arquitectura

```
src/
├── main.py                 # CLI principal y aplicación
├── detectors/
│   ├── base.py            # Detector base abstracto
│   └── reddit_detector.py # Implementación Reddit
├── analyzers/
│   ├── sentiment.py       # Análisis de sentimiento (VADER)
│   └── link_analyzer.py   # Extracción de URLs
├── storage/
│   └── database.py        # Gestión de base de datos
└── notifiers/
    └── console_notifier.py # Notificaciones en consola
```

## Base de Datos

La aplicación usa SQLite para almacenar menciones. Cada mención incluye:

- Plataforma (reddit, twitter, etc.)
- Autor y contenido
- URL del post/comentario
- Análisis de sentimiento (score y etiqueta)
- Links detectados
- Metadata (subreddit, score, comentarios)
- Timestamps

## Análisis de Sentimiento

Usa VADER (Valence Aware Dictionary and sEntiment Reasoner), optimizado para texto de redes sociales.

Scores:
- **Positive**: compound >= 0.05
- **Negative**: compound <= -0.05
- **Neutral**: -0.05 < compound < 0.05

Compound score: -1.0 (más negativo) a 1.0 (más positivo)

## Detección de Links

El sistema extrae automáticamente:
- URLs completas (http/https)
- Dominios únicos
- Conteo de links por mención

Casos de uso:
- Detectar menciones con links a tu sitio
- Identificar referencias a competidores
- Encontrar oportunidades de backlinks

## Extensibilidad

### Agregar nueva plataforma

1. Crear nuevo detector heredando de `BaseDetector`:

```python
from src.detectors.base import BaseDetector

class TwitterDetector(BaseDetector):
    def search_mentions(self, limit: int = 100):
        # Implementar búsqueda
        pass

    def get_platform_name(self):
        return 'twitter'
```

2. Integrar en `main.py`

### Agregar nuevo tipo de análisis

1. Crear nuevo analizador en `src/analyzers/`
2. Integrar en el pipeline de procesamiento

## Mejores Prácticas

### Gestión de Reputación

1. **Escanea regularmente**: Configura escaneos automáticos cada 15-30 minutos
2. **Prioriza negativos**: Revisa menciones negativas primero para responder rápido
3. **Participa estratégicamente**: Usa las URLs para unirte a conversaciones relevantes
4. **Monitorea competidores**: Configura keywords para competencia

### Optimización

- Usa subreddits específicos en vez de "all" para resultados más relevantes
- Ajusta `BRAND_KEYWORDS` para capturar variaciones (mayúsculas, typos)
- Limita resultados en escaneos frecuentes para evitar duplicados

### Privacidad y Ética

- Respeta las reglas de cada subreddit
- No hagas spam
- Participa de forma genuina y aporta valor
- Identifícate como representante de la marca

## Troubleshooting

### Error: Reddit credentials not found
- Verifica que `.env` existe y contiene las credenciales correctas
- Asegúrate de que los nombres de las variables coinciden con `.env.example`

### Error: 401 Unauthorized
- Verifica client_id y client_secret
- Regenera las credenciales en Reddit si es necesario

### No se encuentran menciones
- Verifica que `BRAND_KEYWORDS` está configurado correctamente
- Prueba con keywords más genéricos
- Cambia de "all" a subreddits específicos de tu industria

## Roadmap

- [ ] Soporte para Twitter/X
- [ ] Webhooks para notificaciones en tiempo real
- [ ] Dashboard web
- [ ] Exportación de reportes (PDF, CSV)
- [ ] Integración con Slack/Discord
- [ ] Machine Learning para clasificación avanzada
- [ ] Detección de influencers

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push y crea un Pull Request

## Licencia

MIT License - ve LICENSE para detalles

## Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.

---

Desarrollado para ayudar a las marcas a monitorear su presencia online y gestionar su reputación digital.
