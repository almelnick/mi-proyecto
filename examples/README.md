# Ejemplos y Scripts

Esta carpeta contiene scripts de ejemplo para casos de uso comunes.

## monitor_script.py

Script de monitoreo automatizado con tres modos:

### Modo Monitor
Escaneos automáticos en intervalos regulares:

```bash
python examples/monitor_script.py monitor --interval 15
```

Características:
- Escanea cada N minutos (default: 15)
- Muestra notificaciones en tiempo real
- Alerta sobre menciones negativas
- Estadísticas continuas

Ideal para:
- Monitoreo 24/7
- Gestión de crisis
- Atención al cliente en redes

### Modo Reputación
Análisis rápido de reputación:

```bash
python examples/monitor_script.py reputation
```

Muestra:
- Score de reputación (-100 a +100)
- Distribución de sentimientos
- Menciones negativas recientes para atender
- Estado general de la marca

Ideal para:
- Reportes diarios/semanales
- Evaluación rápida de reputación
- Identificar problemas

### Modo Links
Encuentra oportunidades de participación:

```bash
python examples/monitor_script.py links
```

Muestra:
- Menciones que contienen URLs
- Score y sentimiento
- Links para participar

Ideal para:
- Estrategia de links
- Relaciones públicas
- Construcción de comunidad

## Personalización

Puedes modificar estos scripts para:

1. **Agregar webhooks**: Enviar notificaciones a Slack/Discord
2. **Filtros personalizados**: Ignorar ciertos autores o subreddits
3. **Exportar reportes**: Generar PDFs o CSVs
4. **Integración con CRM**: Sincronizar con tu sistema

## Crear tu propio script

Template básico:

```python
from src.main import BrandMentionDetector

detector = BrandMentionDetector()

try:
    # Tu lógica aquí
    detector.scan_reddit(limit=50)
    stats = detector.db.get_stats()
    print(stats)

finally:
    detector.close()
```

## Automatización

### Linux/Mac - Cron

```bash
# Monitoreo cada hora
0 * * * * cd /ruta/a/mi-proyecto && python examples/monitor_script.py monitor --interval 60

# Reporte diario a las 9am
0 9 * * * cd /ruta/a/mi-proyecto && python examples/monitor_script.py reputation > /tmp/daily_report.txt
```

### Windows - Task Scheduler

1. Abre Task Scheduler
2. Create Basic Task
3. Configura trigger (hourly, daily, etc.)
4. Action: Start Program
   - Program: `python`
   - Arguments: `examples/monitor_script.py monitor --interval 60`
   - Start in: ruta al proyecto

### Docker (Avanzado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "examples/monitor_script.py", "monitor", "--interval", "30"]
```

```bash
docker build -t brand-detector .
docker run -d --env-file .env brand-detector
```

## Mejores Prácticas

1. **Logging**: Agrega logging para debugging
2. **Error handling**: Captura excepciones de red
3. **Rate limiting**: Respeta los límites de Reddit API
4. **Backup**: Respalda la base de datos periódicamente

## Contribuir

¿Tienes un script útil? Compártelo:

1. Agrega tu script a esta carpeta
2. Documenta su uso aquí
3. Crea un Pull Request

---

Para más información, ve el [README principal](../README.md).
