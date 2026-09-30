# Instrucciones SEO para Contenido — seopley.com
**Fecha:** 2026-09-30
**Tipo:** auditoría básica (lectura vía Apify + métricas de Ubersuggest para Chile).
**Páginas auditadas:** `/`, `/seo/`, `/seo/seo-tecnico-auditoria/`, `/seo/posicionamiento-en-ia-geo/`, `/quienes-somos/`, `/contacto/`, `/blog/temas/seo/`, `/blog/mejor-agencia-seo/`, `/blog/auditoria-seo-guia-completa...`

**Contexto:** el sitio es nuevo en Google. Empezó a rankear en junio 2026, tiene 10 keywords, unas 11 visitas orgánicas al mes y autoridad de dominio 4. La base on-page es buena: titles y descripciones únicas de buen largo, FAQs en home y servicios, y posts con autor, fecha y migas de pan. Lo que falta es foco en intención de búsqueda, señales de confianza (E-E-A-T) y formatos que la IA pueda citar.

**Lo que ya está bien:**
- El H1 del home ("Agencia SEO en Chile: tu sitio en Google, tu marca en la IA") y su title (52 caracteres) están bien alineados con la keyword principal.
- La página de GEO es la más completa: 2.389 palabras y 9 preguntas frecuentes.

---

## 🔴 CRÍTICOS

No encontré problemas de contenido que bloqueen el posicionamiento. El único crítico es técnico (la verificación anti-bots) y está en el documento para el desarrollador.

---

## 🟡 MEDIOS

### 1. Los H1 de servicios son etiquetas, no respuestas a una búsqueda
**Qué está pasando:** `/seo/` tiene el H1 "SEO: Search Engine Optimization" y `/seo/seo-tecnico-auditoria/` tiene "SEO Técnico". Describen el tema, pero no dicen qué ofrece la página, para quién ni dónde. Compiten con Wikipedia y con guías genéricas en vez de hacerlo con agencias.
**Dónde:** servicios bajo `/seo/`.
**Qué escribir exactamente:**
> `/seo/` → H1: **"Servicio de SEO en Chile: posicionamiento web medido en leads"**
> `/seo/seo-tecnico-auditoria/` → H1: **"Auditoría SEO técnica: encontramos lo que frena tu sitio en Google"**
> Meta description de la auditoría (≈150 caracteres): **"Auditoría SEO técnica para empresas en Chile: rastreo, indexación, velocidad y schema. Recibe un plan priorizado con lo que hay que arreglar primero."**

**Por qué importa:** la intención comercial ("agencia", "servicio", "auditoría") es la que trae clientes. Un H1 de glosario atrae tráfico informacional que no convierte.

### 2. "Quiénes somos" tiene 195 palabras y ninguna persona
**Qué está pasando:** `/quienes-somos/` tiene el H1 "SEO pensado para el futuro" y unas 195 palabras de contenido principal. Para una agencia que vende confianza, y para los LLM que evalúan E-E-A-T, falta saber **quién** está detrás.
**Dónde:** `/quienes-somos/`
**Qué escribir exactamente:**
> H1: **"El equipo detrás de seopley"**
> Por cada integrante, un bloque con: nombre, cargo, años de experiencia en SEO, 2 o 3 logros verificables, foto real y enlace a LinkedIn.
> Un párrafo de origen (60–80 palabras): cuándo nació la agencia, por qué crearon Cerebro y qué la diferencia.
> Cifras reales (las mismas de los contadores del home) con su fuente o periodo, por ejemplo: "X proyectos en primera página entre [año] y [año]".

**Por qué importa:** Google y los motores de IA priorizan fuentes con autores identificables y experiencia demostrable. Es la página que un cliente revisa antes de escribir.

### 3. Contacto: title de 18 caracteres y ningún dato visible
**Qué está pasando:** el title de `/contacto/` tiene 18 caracteres, el contenido principal unas 66 palabras, y no hay correo, teléfono ni dirección visibles: solo un formulario.
**Dónde:** `/contacto/`
**Qué escribir exactamente:**
> Title: **"Contacto | Agencia SEO en Chile | seopley"** (41 caracteres)
> Bajo el H1, un bloque visible con correo, WhatsApp o teléfono, comuna y horario, más una frase de expectativa: **"Te respondemos en menos de [X] horas hábiles con un primer diagnóstico de tu sitio."**

**Por qué importa:** tener datos de contacto consistentes (NAP) es señal de confianza y requisito para SEO local. Hoy el sitio no tiene ninguno.

### 4. La página de keyword research está en #32 para una búsqueda de 1.000/mes
**Qué está pasando:** `/seo/keyword-research/` es la página con más tráfico estimado del sitio y aparece en el puesto #32 para "keyword research" en Chile (1.000 búsquedas al mes, dificultad 47). Está en la página 4: hay espacio para subir.
**Dónde:** `/seo/keyword-research/`
**Qué escribir exactamente:**
> Primeras 2 líneas (definición citable, unas 45 palabras): **"El keyword research es el proceso de encontrar qué buscan tus clientes en Google, cuánto lo buscan y con qué intención, para decidir qué páginas crear u optimizar. Es la base de cualquier estrategia SEO y de contenidos."**
> Nuevos H2:
> - "¿Cómo se hace un keyword research paso a paso?" (lista numerada de 5 a 7 pasos)
> - "Herramientas para keyword research: comparativa" (tabla con herramienta, gratis/pago, para qué sirve)
> - "Ejemplo real de keyword research para una empresa en Chile"
> Enlaces internos hacia esta página desde el home, desde `/seo/` y desde 3 posts del blog, con el texto "keyword research".

**Por qué importa:** es la página con más potencial rápido. Pasar de #32 a la primera página multiplica el tráfico del sitio.

### 5. El post de AI Overviews rankea por "overviews" en vez de por su tema real
**Qué está pasando:** `/blog/ai-overviews-google-ai-mode-optimizar-respuestas-para-seo/` aparece en el #26 para "overviews" (590 búsquedas al mes), una palabra suelta y ambigua. Debería competir por "AI Overviews", "qué es AI Overviews" y "Google AI Mode".
**Qué escribir exactamente:**
> Title: **"AI Overviews y Google AI Mode: qué son y cómo aparecer (2026)"**
> Primer párrafo: **"AI Overviews son los resúmenes generados por IA que Google muestra sobre los resultados orgánicos. AI Mode es la búsqueda conversacional de Google basada en Gemini. Para aparecer en ambos, tu página debe responder la pregunta de forma directa, estar bien estructurada y ser una fuente confiable."**
> Un H2 por pregunta: "¿Qué es AI Overviews?", "¿Qué es Google AI Mode?", "¿Cómo aparecer en AI Overviews?", "¿AI Overviews quita tráfico a los sitios?"

**Por qué importa:** alinea la página con la intención real y con las preguntas que la IA de Google usa para armar sus resúmenes.

### 6. Pocos backlinks y la mayoría nofollow
**Qué está pasando:** hay 26 dominios que enlazan al sitio, y 44 de los 76 enlaces son nofollow. Con autoridad 4, el contenido solo no alcanza para keywords comerciales como "agencia SEO Chile".
**Qué hacer (desde contenido):**
> - Publicar **1 estudio propio al trimestre** con datos de Cerebro, por ejemplo: "¿Qué sitios chilenos cita ChatGPT? Análisis de N marcas". Los datos originales son lo que más enlaces atrae.
> - Proponer columnas o entrevistas a medios de marketing chilenos y a asociaciones gremiales, siempre enlazando a una página de servicio y no solo al home.
> - Pedir a clientes satisfechos un caso de estudio en su propio blog o LinkedIn, con enlace.

**Por qué importa:** la autoridad es hoy el principal límite para rankear en búsquedas comerciales.

---

## 🟢 OPORTUNIDADES — GEO / AEO

### Agregar una tabla comparativa en `/seo/posicionamiento-en-ia-geo/`
**Qué está pasando:** ninguna de las páginas revisadas tiene tablas, que son un formato que Google y los LLM citan con facilidad.
**Qué escribir exactamente:** un H2 **"SEO vs GEO vs AEO: diferencias"** con esta tabla:

| | SEO | AEO | GEO |
|---|---|---|---|
| Objetivo | Rankear en resultados de Google | Ser la respuesta directa (snippet, AI Overviews) | Ser citado por ChatGPT, Gemini, Perplexity |
| Dónde se ve | Lista de 10 resultados | Recuadro sobre los resultados | Respuesta conversacional con fuentes |
| Qué optimiza | Relevancia, autoridad, técnica | Respuestas breves y estructuradas | Claridad, datos verificables, autoridad de entidad |
| Cómo se mide | Posiciones y clics | Presencia en snippets | Menciones y citas en respuestas de IA |

### Definición citable al inicio de cada servicio
**Agregar en `/seo/posicionamiento-en-ia-geo/`, antes de todo lo demás:**
> "El posicionamiento en IA (GEO, Generative Engine Optimization) es la optimización de un sitio y de su marca para que motores como ChatGPT, Gemini, Perplexity y AI Overviews de Google lo mencionen y lo citen como fuente en sus respuestas."

**Agregar en `/seo/seo-tecnico-auditoria/`:**
> "Una auditoría SEO técnica revisa si Google puede rastrear, entender e indexar un sitio: arquitectura, velocidad, errores, redirecciones, datos estructurados y versiones duplicadas. El resultado es una lista priorizada de arreglos."

**Por qué:** los LLM priorizan las páginas que definen el concepto de forma autocontenida en las primeras líneas.

### Ampliar las preguntas frecuentes de `/seo/` (hoy son 3)
Preguntas recomendadas, cada una con una respuesta de 40–60 palabras, en la FAQ y en el schema FAQPage:
1. **¿Cuánto cuesta un servicio de SEO en Chile?**
   → "Depende del tamaño del sitio, la competencia del rubro y si incluye contenidos y link building. En seopley partimos con un diagnóstico para definir alcance y plazos; la propuesta detalla entregables y precio antes de empezar." *(ajustar si publican rangos)*
2. **¿En cuánto tiempo se ven resultados de SEO?**
   → "Los arreglos técnicos pueden mostrar efecto en semanas; el crecimiento sostenido de posiciones y tráfico suele verse entre 3 y 6 meses, según la competencia y la autoridad de partida del sitio."
3. **¿El SEO sirve para aparecer en ChatGPT?**
   → "Sí, pero no basta. Los motores de IA usan fuentes que ya son relevantes en la web; además priorizan contenido claro, datos verificables y marcas reconocibles. Por eso combinamos SEO con GEO."
4. **¿Qué diferencia a seopley de otras agencias SEO?**
   → "[COMPLETAR con el diferencial real: Cerebro, metodología, reportes. Mencionar algo verificable.]"

### Quitar el "0" que ven los rastreadores en el home
Está en el documento para el desarrollador, pero conviene revisarlo desde contenido: las cifras de "Resultados que se pueden medir" tienen que ser **reales y defendibles** (años, proyectos, porcentaje de crecimiento con su periodo), porque la IA las repetirá tal como aparecen.

---

*Esta es una auditoría básica: revisa 9 de las 71 URLs del sitemap, sin rastreo completo ni análisis de Jev/TypeSafe página por página. La auditoría completa con jev-seo se puede correr cuando el entorno tenga acceso a seopley.com.*
