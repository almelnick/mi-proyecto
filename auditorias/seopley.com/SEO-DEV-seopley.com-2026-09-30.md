# Instrucciones SEO para Developer — seopley.com
**Fecha:** 2026-09-30
**Tipo:** auditoría básica (lectura vía Apify + métricas de Ubersuggest). No incluye rastreo completo ni análisis de Jev/TypeSafe.
**Páginas auditadas (9 de 71 del sitemap):** `/`, `/seo/`, `/seo/seo-tecnico-auditoria/`, `/seo/posicionamiento-en-ia-geo/`, `/quienes-somos/`, `/contacto/`, `/blog/temas/seo/`, `/blog/mejor-agencia-seo/`, `/blog/auditoria-seo-guia-completa...`
**Stack detectado:** WordPress + Yoast SEO, tema propio `seopley-v1` (Tailwind), Cloudways + Breeze, Cloudflare delante.
**Prioridad total:** 1 crítico · 7 medios · 4 oportunidades

**Lo que ya está bien (no tocar):** un H1 por página, titles de 49–55 caracteres sin duplicados, canonical autorreferente en todas, `lang="es-CL"`, viewport correcto, sin scripts bloqueantes en `<head>` (solo `acordeon.js` con `defer`), fuentes autoalojadas con preload, 60 de 68 imágenes del home en WebP, CLS = 0, FAQPage en home y servicios, sitemap Yoast con 71 URLs enlazado en robots.txt.

---

## 🔴 CRÍTICOS — Hacer primero

### 1. Una verificación anti-bots se muestra en vez del contenido (con código 200)
**Qué está pasando:** 9 de 22 descargas (≈40 %) recibieron una página "One moment, please..." en vez del contenido real. Esa página responde **200**, trae un formulario `wsidchk` y un spinner. La firma coincide con la protección anti-bots de Imunify360 (WebShield) que usan los servidores Cloudways. Entre las páginas afectadas están `/sitemap.xml`, servicios y variantes de dominio (`https://seopley.com/`, `http://www.seopley.com/`).
**Dónde:** todo el sitio, de forma intermitente. Las pruebas salieron de IPs de datacenter (Apify), que es el mismo tipo de IP que usan GPTBot, PerplexityBot, ClaudeBot y Google-Extended.
**Por qué es crítico:** el sitio vende posicionamiento en IA (GEO). Si los rastreadores de IA ven un spinner, no pueden citar el sitio. Además, un 200 con contenido de relleno puede llegar a indexarse como página delgada.
**Qué hacer exactamente:**
1. Confirmar que Googlebot no se ve afectado. En Search Console, revisar *Configuración → Estadísticas de rastreo → Por respuesta* y usar *Inspección de URLs → Probar URL publicada* en `/`, `/seo/` y `/sitemap_index.xml`. La captura tiene que mostrar el contenido real.
2. En Cloudways (*Application Settings → Bot Protection* / Imunify360), agregar a la lista blanca los bots verificados, o bajar la sensibilidad. Si no se puede por agente de usuario, excluir al menos `/robots.txt`, `/sitemap*.xml` y `/llms.txt`.
3. En Cloudflare, activar *Security → Bots → Verified bots: Allow*. Revisar además *AI Crawl Control* (antes "Block AI bots") y asegurarse de que **no** bloquee GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot ni Google-Extended.
4. Si la verificación se va a mantener para humanos sospechosos, que responda **403 o 503**, no 200.
5. Verificar desde fuera:
```bash
for ua in "Mozilla/5.0 (compatible; GPTBot/1.2; +https://openai.com/gptbot)" \
          "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)" \
          "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"; do
  curl -s -A "$ua" https://www.seopley.com/seo/ | grep -o "<title>[^<]*" ; done
# Debe imprimir el title real 3 veces, nunca "One moment, please..."
```
**Impacto esperado:** que los motores de IA y Google puedan leer siempre el contenido real. Este es el requisito básico para todo lo demás.

---

## 🟡 MEDIOS — Segunda pasada

### 2. LCP móvil de 3,8 s: una cadena de redirecciones cuesta 1,1 s
**Qué está pasando:** PageSpeed (vía Ubersuggest) mide un LCP móvil de **3,8 s** (el objetivo es ≤ 2,5 s) y un tiempo hasta interactividad de 7,4 s. La mayor pérdida es **"Redirects": 1,1 s en móvil y 340 ms en escritorio**. En escritorio todo está bien (LCP 838 ms).
**Dónde:** entrada por `http://seopley.com/` o `https://seopley.com/`. Todos los canonical apuntan a `https://www.seopley.com/`.
**Qué hacer exactamente:** dejar **un solo salto 301** hacia la versión canónica. En Cloudflare, *Rules → Redirect Rules*:
```
Si: (http.host eq "seopley.com") or (not ssl)
Entonces: Dynamic redirect → concat("https://www.seopley.com", http.request.uri.path)
          Status 301, Preserve query string: on
```
Verificar que quede un solo salto:
```bash
curl -sIL http://seopley.com/ | grep -Ei "^(HTTP|location)"
# Esperado: 301 → https://www.seopley.com/ → 200 (sin pasos intermedios)
```
Revisar además que perfiles sociales, firmas de correo y Google Business Profile enlacen directo a `https://www.seopley.com/`.
**Impacto esperado:** hasta 1,1 s menos de LCP móvil, lo que lo acerca al umbral "bueno".

### 3. La primera imagen del home carga en diferido (lazy)
**Qué está pasando:** la primera imagen del `<body>` (`Gemini_Generated_Image_wqxx8pwqxx8pwqxx_peeled.webp`, 1376×768) tiene `loading="lazy"` y no tiene `fetchpriority`. En total, 65 de las 68 imágenes del home son lazy.
**Dónde:** `/`, sección hero y panel de Cerebro.
**Qué hacer exactamente:** en la plantilla del hero del tema `seopley-v1`:
```html
<img src="https://www.seopley.com/wp-content/uploads/2026/04/Gemini_Generated_Image_wqxx8pwqxx8pwqxx_peeled.webp"
     alt="Panel de análisis SEO del software Cerebro de seopley."
     width="1376" height="768" loading="eager" fetchpriority="high" decoding="async">
```
Si esa imagen no está en la primera pantalla en móvil, aplicar `eager` + `fetchpriority="high"` a la imagen que sí sea el elemento LCP (se identifica en PageSpeed → *Largest Contentful Paint element*). El resto puede seguir en lazy.
**Impacto esperado:** mejor LCP móvil, que se suma a la mejora del punto 2.

### 4. Los contadores del home dicen "0" para los rastreadores
**Qué está pasando:** la sección "Resultados que se pueden medir" anima las cifras con JavaScript. En el HTML que reciben Google y los rastreadores de IA (muchos no ejecutan JS) aparece literalmente **"0 + Años de experiencia"**, y lo mismo pasa con "Proyectos en primera página" y "Crecimiento promedio de visitas".
**Dónde:** `/`, H2 "Resultados que se pueden medir".
**Qué hacer exactamente:** escribir el número final en el HTML y que el JS solo anime desde ese valor:
```html
<span class="contador" data-final="12">12</span> + Años de experiencia
<!-- JS: leer data-final, poner el texto en 0 y animar. Sin JS, se ve "12". -->
```
(El 12 es un ejemplo: usar las cifras reales.)
**Impacto esperado:** los LLM y los rich results leen las cifras de confianza correctas en vez de ceros.

### 5. El schema de Organization está incompleto y no hay datos de contacto
**Qué está pasando:** el `Organization` de Yoast solo tiene `name`, `url` y `logo`. No hay `address`, `telephone`, `email`, `sameAs` ni `contactPoint`, y en ninguna página hay enlaces `mailto:` o `tel:`. Tampoco hay `ProfessionalService` ni `Service`.
**Dónde:** JSON-LD global (`#organization`).
**Qué hacer exactamente:** completar *Yoast → Configuración → Representación del sitio* (logo, redes, datos de la organización) y agregar este bloque en el `<head>` del home. Los campos `[COMPLETAR]` se llenan con los datos reales; no se deben inventar:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": ["Organization", "ProfessionalService"],
  "@id": "https://www.seopley.com/#organization",
  "name": "seopley",
  "url": "https://www.seopley.com/",
  "logo": "https://www.seopley.com/wp-content/uploads/2026/03/seopley-150x150-1.webp",
  "description": "Agencia SEO en Chile. Posicionamiento en Google y en respuestas de IA (GEO/AEO) con software propio de análisis.",
  "areaServed": { "@type": "Country", "name": "Chile" },
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "[COMPLETAR]",
    "addressRegion": "Región Metropolitana",
    "addressCountry": "CL"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "sales",
    "email": "[COMPLETAR]",
    "telephone": "[COMPLETAR +56...]",
    "availableLanguage": "es"
  },
  "sameAs": [
    "[COMPLETAR URL de LinkedIn de la empresa]"
  ],
  "knowsAbout": ["SEO técnico", "SEO de contenidos", "GEO", "AEO", "Link building", "SEO local"]
}
</script>
```
**Impacto esperado:** la entidad queda más clara para Google (Knowledge Graph) y para los LLM que citan fuentes.

### 6. Los posts tienen Article y BreadcrumbList duplicados
**Qué está pasando:** cada post trae **2 bloques `Article` y 2 `BreadcrumbList`** (uno de Yoast y otro del tema), además de microdatos. Google tiene que resolver entidades en conflicto.
**Dónde:** `/blog/*` (visto en `/blog/mejor-agencia-seo/` y `/blog/auditoria-seo-guia-completa...`).
**Qué hacer exactamente:** conservar el grafo de Yoast y eliminar el del tema. En `seopley-v1`, buscar y quitar la salida propia:
```bash
grep -rn "application/ld+json\|itemtype=\"https://schema.org" wp-content/themes/seopley-v1/
```
Borrar esos bloques y atributos `itemscope`/`itemtype` de `single.php` (o del template del post). Si se quiere enriquecer el Article, hacerlo con el filtro `wpseo_schema_article` de Yoast.
Validar después en https://validator.schema.org con un post.
**Impacto esperado:** una sola entidad Article limpia por post, con mejor elegibilidad para resultados enriquecidos.

### 7. Falta og:image en 6 páginas clave
**Qué está pasando:** `/`, `/seo/`, `/seo/posicionamiento-en-ia-geo/`, `/contacto/`, `/quienes-somos/` y `/blog/temas/seo/` no tienen `og:image`, y solo tienen `twitter:card`. Al compartir en LinkedIn o WhatsApp salen sin imagen.
**Qué hacer exactamente:** en *Yoast → Configuración → Representación en redes sociales*, definir una imagen por defecto de 1200×630. En cada página de servicio, cargar una imagen propia en la pestaña *Redes sociales* de Yoast. El resultado esperado:
```html
<meta property="og:image" content="https://www.seopley.com/wp-content/uploads/[imagen-1200x630].webp">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:image" content="https://www.seopley.com/wp-content/uploads/[imagen-1200x630].webp">
```
**Impacto esperado:** mejor CTR al compartir en redes y en mensajería.

### 8. robots.txt tiene 3 grupos `User-agent: *`
**Qué está pasando:** el bloque de Yoast y dos bloques propios repiten `User-agent: *`. Google los fusiona, pero otros rastreadores aplican solo el primer grupo, que no tiene ningún `Disallow`. Además, la regla `*&paged=*` solo cubre búsquedas con paginación.
**Qué hacer exactamente:** reemplazar el contenido por un solo grupo (desde *Yoast → Herramientas → Editor de archivos*):
```
User-agent: *
Disallow: /?s=
Disallow: /search/
Disallow: /*?s=
Disallow: /*&paged=

Sitemap: https://www.seopley.com/sitemap_index.xml
```
**Impacto esperado:** todos los rastreadores aplican las mismas reglas.

---

## 🟢 OPORTUNIDADES — Cuando haya tiempo

### 9. Crear `/llms.txt`
**Qué está pasando:** `/llms.txt` responde 404 (la página "no encontrada" de WordPress). Para un sitio que vende GEO, conviene tenerlo como señal y como índice para los LLM.
**Qué hacer exactamente:** subir `llms.txt` a la raíz (texto plano, UTF-8), excluido de la verificación anti-bots (punto 1):
```markdown
# seopley
> Agencia SEO en Chile. Posicionamiento en Google y en respuestas de IA (GEO/AEO) con Cerebro, software propio de análisis.

## Servicios
- [SEO](https://www.seopley.com/seo/): estrategia de posicionamiento orgánico.
- [SEO técnico y auditoría](https://www.seopley.com/seo/seo-tecnico-auditoria/)
- [Posicionamiento en IA (GEO/AEO)](https://www.seopley.com/seo/posicionamiento-en-ia-geo/)
- [Keyword research](https://www.seopley.com/seo/keyword-research/)
- [CRO](https://www.seopley.com/cro-conversion-rate-optimization/)
- [Data analytics](https://www.seopley.com/data-analytics/)
- [Cerebro](https://www.seopley.com/cerebro/)

## Empresa
- [Quiénes somos](https://www.seopley.com/quienes-somos/)
- [Contacto](https://www.seopley.com/contacto/)
- [Blog](https://www.seopley.com/blog/)
```

### 10. Schema `Service` en cada página de servicio
**Dónde:** `/seo/*`, `/cro-conversion-rate-optimization/`, `/data-analytics/`. Ejemplo para GEO:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Posicionamiento en IA (GEO/AEO)",
  "serviceType": "Generative Engine Optimization",
  "provider": { "@id": "https://www.seopley.com/#organization" },
  "areaServed": { "@type": "Country", "name": "Chile" },
  "url": "https://www.seopley.com/seo/posicionamiento-en-ia-geo/",
  "description": "Optimización para que la marca aparezca y sea citada en ChatGPT, Gemini, Perplexity y AI Overviews."
}
</script>
```

### 11. JS y CSS sin usar
PageSpeed estima **136–137 KB de JS** y **37–38 KB de CSS** sin usar (150 ms en móvil). Revisar con *Coverage* en Chrome DevTools qué carga GTM (GTM-5TLT2WDC): mover etiquetas no esenciales a disparo tras interacción o carga completa, y cargar reCAPTCHA solo en `/contacto/`. En Breeze, activar *Remove unused CSS* si el tema lo tolera, y probar el resultado antes de publicar.

### 12. `/sitemap.xml` debería redirigir al índice
La prueba recibió la verificación anti-bots, así que no se sabe qué responde. Algunos rastreadores (y herramientas de IA) prueban `/sitemap.xml` por defecto. Asegurarse de que responda **301 → `/sitemap_index.xml`** (Yoast lo hace por defecto si no hay conflicto con el tema o la caché).

---

## Datos de contexto (Ubersuggest, Chile, septiembre 2026)
- Autoridad de dominio **4**, **76 backlinks** de **26 dominios** (44 nofollow).
- Tráfico orgánico estimado: **11 visitas/mes**, 10 keywords. El sitio empezó a rankear en junio 2026.
- Keywords visibles en Chile: "keyword research" (#32, 1.000 búsquedas/mes) y "overviews" (#26, 590).
- Velocidad: escritorio LCP 838 ms, TBT 101 ms, CLS 0 · móvil LCP 3,8 s, TBT 116 ms, CLS 0.
