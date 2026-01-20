# Guía de Inicio Rápido

Comienza a monitorear tu marca en 5 minutos.

## 1. Obtén credenciales de Reddit

1. Ve a https://www.reddit.com/prefs/apps
2. Haz clic en "create another app..." o "create app"
3. Completa el formulario:
   - **name**: BrandMentionDetector
   - **app type**: script
   - **description**: Monitor de menciones de marca
   - **about url**: (opcional)
   - **redirect uri**: http://localhost:8080
4. Haz clic en "create app"
5. Anota el **client id** (debajo del nombre de la app)
6. Anota el **secret**

## 2. Configura el proyecto

```bash
# Instala dependencias
pip install -r requirements.txt

# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env
nano .env  # o usa tu editor favorito
```

## 3. Configura tus variables

En el archivo `.env`, configura:

```env
# Credenciales de Reddit (del paso 1)
REDDIT_CLIENT_ID=tu_client_id_aqui
REDDIT_CLIENT_SECRET=tu_client_secret_aqui
REDDIT_USER_AGENT=BrandMentionDetector/1.0

# Tu marca
BRAND_NAME=TuMarca
BRAND_KEYWORDS=TuMarca,tu marca,tumarca,keyword relacionado

# Subreddits a monitorear (separados por coma)
# Usa "all" para todos, o especifica: technology,startups,marketing
BRAND_SUBREDDITS=all
```

## 4. Primer escaneo

```bash
# Escanea Reddit
python -m src.main scan --limit 50
```

Verás algo como:
```
✓ Reddit detector initialized successfully
ℹ Scanning Reddit for mentions of: TuMarca, tu marca
ℹ Found 15 potential mentions
✓ New Mention on REDDIT
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Author: user123               ┃
┃ Sentiment: positive (0.65)    ┃
┃ Has Links: Yes                ┃
┃ ...                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
✓ Added 15 new mentions to database
```

## 5. Explora los resultados

```bash
# Ver estadísticas
python -m src.main stats

# Ver menciones recientes
python -m src.main recent --limit 10

# Ver menciones negativas (¡importante!)
python -m src.main negative

# Ver menciones con links
python -m src.main links
```

## 6. Automatiza el monitoreo

### Opción A: Script de Python

```bash
python examples/monitor_script.py monitor --interval 15
```

Esto ejecutará escaneos cada 15 minutos.

### Opción B: Cron Job (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Agregar línea (cada hora)
0 * * * * cd /ruta/completa/a/mi-proyecto && /usr/bin/python3 -m src.main scan --limit 50 --no-notify
```

### Opción C: Task Scheduler (Windows)

1. Abre "Task Scheduler"
2. Create Basic Task
3. Nombre: "Brand Mention Detector"
4. Trigger: Daily o Custom
5. Action: Start a Program
   - Program: `python`
   - Arguments: `-m src.main scan --limit 50`
   - Start in: `C:\ruta\a\mi-proyecto`

## Comandos Útiles

### Análisis de reputación
```bash
python examples/monitor_script.py reputation
```

### Encontrar oportunidades de links
```bash
python examples/monitor_script.py links
```

### Escaneo sin notificaciones (para automatización)
```bash
python -m src.main scan --limit 100 --no-notify
```

## Casos de Uso Comunes

### 1. Gestión de Crisis
Monitorea menciones negativas en tiempo real:
```bash
# Escaneo frecuente
python -m src.main scan --limit 50
python -m src.main negative
```

### 2. Construcción de Links
Encuentra oportunidades donde mencionan tu marca:
```bash
python -m src.main links --limit 50
```

Visita esas URLs y participa genuinamente en la conversación.

### 3. Análisis de Competencia
Modifica `BRAND_KEYWORDS` para incluir competidores:
```env
BRAND_KEYWORDS=MiMarca,Competidor1,Competidor2
```

### 4. Monitoreo de Producto
Para lanzamientos de productos:
```env
BRAND_KEYWORDS=NuevoProducto,ProductoX,nombre producto
BRAND_SUBREDDITS=technology,producthunt,startups
```

## Troubleshooting Rápido

### ❌ "Reddit credentials not found"
→ Verifica que el archivo `.env` existe y tiene las variables correctas

### ❌ "401 Unauthorized"
→ Revisa que client_id y client_secret son correctos

### ℹ️ "Found 0 potential mentions"
→ Prueba con keywords más amplios o diferentes subreddits

### ⚠️ Muchos duplicados
→ Reduce el `--limit` en escaneos frecuentes

## Próximos Pasos

1. **Personaliza keywords**: Incluye variaciones, typos comunes, nombres de productos
2. **Enfoca subreddits**: Identifica los subreddits más relevantes para tu industria
3. **Configura alertas**: Usa el script de monitoreo para alertas automáticas
4. **Integra con tu workflow**: Conecta con Slack, email, o tu CRM

## Recursos

- [README completo](README.md) - Documentación detallada
- [Scripts de ejemplo](examples/) - Scripts de automatización
- [Código fuente](src/) - Explora y personaliza

---

¿Preguntas? Abre un issue en el repositorio.
