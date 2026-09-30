"""Arma el PDF de la auditoría SEO de seopley.com a partir de los dos markdowns.

Uso: python auditorias/seopley.com/generar_pdf.py
"""

import base64
import re
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).parent
RAIZ = AQUI.parent.parent
MARCA = RAIZ / "generador_contenidos" / "marcas" / "sprint_latam"
FECHA = "30 de septiembre de 2026"
DOMINIO = "seopley.com"

DEV = AQUI / "SEO-DEV-seopley.com-2026-09-30.md"
CONTENIDO = AQUI / "SEO-CONTENT-seopley.com-2026-09-30.md"
SALIDA = AQUI / "Auditoria-SEO-seopley.com-2026-09-30.pdf"

# Datos medidos (Ubersuggest, Chile, septiembre 2026; lectura del sitio vía Apify).
INDICADORES = [
    ("4", "Autoridad de dominio", "de 100"),
    ("26", "Dominios que enlazan", "76 backlinks, 44 nofollow"),
    ("11", "Visitas orgánicas / mes", "estimado en Chile"),
    ("10", "Keywords en Google", "desde junio 2026"),
    ("3,8 s", "LCP en móvil", "objetivo ≤ 2,5 s"),
    ("40 %", "Lecturas bloqueadas", "por verificación anti-bots"),
]
VELOCIDAD = {  # segundos
    "Escritorio": {"FCP": 0.651, "LCP": 0.838, "Speed Index": 1.9, "Interactivo": 1.8},
    "Móvil": {"FCP": 2.8, "LCP": 3.8, "Speed Index": 3.4, "Interactivo": 7.4},
}
ACCIONES = [
    ("🔴", "Dejar pasar a Google y a los bots de IA", "La verificación anti-bots responde 200 con un spinner en ~40 % de las lecturas."),
    ("🟡", "Un solo 301 hacia https://www", "La cadena de redirecciones cuesta 1,1 s de LCP en móvil."),
    ("🟡", "Cifras reales en el HTML del home", "Los rastreadores leen \"0 años de experiencia\"."),
    ("🟡", "Completar schema y datos de contacto", "Organization vacío, sin correo ni teléfono visibles."),
    ("🟡", "Empujar /seo/keyword-research/", "Puesto #32 para una búsqueda de 1.000/mes en Chile."),
]


def _b64(ruta: Path, tipo: str) -> str:
    return f"data:{tipo};base64," + base64.b64encode(ruta.read_bytes()).decode()


def _contar(md: str) -> dict[str, int]:
    """Cuenta los hallazgos (### ...) bajo cada sección de prioridad (## 🔴/🟡/🟢)."""
    cuenta = {"🔴": 0, "🟡": 0, "🟢": 0}
    actual = None
    en_codigo = False
    for linea in md.splitlines():
        if linea.startswith("```"):
            en_codigo = not en_codigo
        elif en_codigo:
            continue
        elif linea.startswith("## "):
            actual = next((p for p in cuenta if p in linea), None)
        elif linea.startswith("### ") and actual:
            cuenta[actual] += 1
    return cuenta


def _cuerpo(md: str, clase: str) -> str:
    """Markdown a HTML, sin el H1 original, con las secciones marcadas por prioridad."""
    md = re.sub(r"^# .*\n", "", md, count=1)
    # Los markdowns se escribieron con saltos simples: separa listas y citas del párrafo anterior.
    lineas, previa, en_codigo = [], "", False
    for linea in md.splitlines():
        if linea.startswith("```"):
            en_codigo = not en_codigo
        bloque = re.match(r"^(\d+\. |- |> |\|)", linea)
        if not en_codigo and bloque and previa.strip() and not re.match(r"^(\d+\. |- |> |\||\s)", previa):
            lineas.append("")
        lineas.append(linea)
        previa = linea
    md = "\n".join(lineas)
    html = markdown.markdown(md, extensions=["fenced_code", "tables", "sane_lists", "nl2br"])
    for emoji, prioridad in (("🔴", "critico"), ("🟡", "medio"), ("🟢", "oportunidad")):
        html = re.sub(rf"<h2>{emoji}\s*", f'<h2 class="prioridad {prioridad}"><span class="punto"></span>', html)
    return f'<section class="documento {clase}">{html}</section>'


def _grafico_velocidad() -> str:
    """Barras horizontales de escritorio vs móvil, con la línea de 2,5 s para el LCP."""
    metricas = ["FCP", "LCP", "Speed Index", "Interactivo"]
    tope, ancho, fila = 8.0, 330, 48
    colores = {"Escritorio": "#0089ED", "Móvil": "#040A14"}
    partes = [f'<svg viewBox="0 0 560 {len(metricas) * fila + 30}" class="grafico" role="img" '
              f'aria-label="Velocidad escritorio vs móvil">']
    for i, m in enumerate(metricas):
        y = 10 + i * fila
        partes.append(f'<text x="0" y="{y + 27}" class="eje">{m}</text>')
        for j, (dispositivo, datos) in enumerate(VELOCIDAD.items()):
            v = datos[m]
            w = max(4, v / tope * ancho)
            yy = y + j * 22
            partes.append(f'<rect x="130" y="{yy}" width="{w:.0f}" height="19" rx="4" fill="{colores[dispositivo]}"/>')
            partes.append(f'<text x="{130 + w + 8:.0f}" y="{yy + 15}" class="valor">{str(v).replace(".", ",")} s</text>')
    x_lcp = 130 + 2.5 / tope * ancho
    alto = len(metricas) * fila
    partes.append(f'<line x1="{x_lcp:.0f}" x2="{x_lcp:.0f}" y1="0" y2="{alto}" class="umbral"/>')
    partes.append(f'<text x="{x_lcp + 6:.0f}" y="{alto + 18}" class="nota">2,5 s = LCP "bueno"</text>')
    partes.append('</svg>')
    leyenda = "".join(f'<span><i style="background:{c}"></i>{d}</span>' for d, c in colores.items())
    return "".join(partes) + f'<div class="leyenda">{leyenda}</div>'


def html() -> str:
    dev_md, cont_md = DEV.read_text(encoding="utf-8"), CONTENIDO.read_text(encoding="utf-8")
    c_dev, c_cont = _contar(dev_md), _contar(cont_md)
    fuentes = {
        "Space Grotesk": MARCA / "fuentes/space-grotesk-latin-wght-normal.woff2",
        "Plus Jakarta Sans": MARCA / "fuentes/plus-jakarta-sans-latin-wght-normal.woff2",
        "JetBrains Mono": MARCA / "fuentes/jetbrains-mono-latin-wght-normal.woff2",
    }
    font_face = "\n".join(
        f'@font-face{{font-family:"{f}";src:url("{_b64(r, "font/woff2")}");font-weight:100 900;}}'
        for f, r in fuentes.items()
    )
    logo = _b64(MARCA / "logo.png", "image/png")
    tarjetas = "".join(
        f'<div class="kpi"><b>{v}</b><span>{t}</span><small>{n}</small></div>' for v, t, n in INDICADORES
    )
    conteo = "".join(
        f'<tr><td>{doc}</td><td class="n rojo">{c["🔴"]}</td><td class="n amarillo">{c["🟡"]}</td>'
        f'<td class="n verde">{c["🟢"]}</td></tr>'
        for doc, c in (("Desarrollo", c_dev), ("Contenido", c_cont))
    )
    acciones = "".join(
        f'<li><span class="sem">{e}</span><div><b>{t}</b><p>{d}</p></div></li>' for e, t, d in ACCIONES
    )
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
{font_face}
@page {{ size: A4; margin: 22mm 18mm 20mm; }}
@page :first {{ margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Plus Jakarta Sans", Arial, sans-serif; font-size: 10.2pt; line-height: 1.55; color: #08121F; margin: 0; }}
h1, h2, h3 {{ font-family: "Space Grotesk", Arial, sans-serif; letter-spacing: -.02em; line-height: 1.15; }}
code, pre {{ font-family: "JetBrains Mono", monospace; }}

/* Portada */
.portada {{ height: 297mm; background: #040A14; color: #FBFAF7; padding: 26mm 20mm; position: relative; overflow: hidden; page-break-after: always; }}
.portada .brillo {{ position: absolute; width: 150mm; height: 150mm; border-radius: 50%; right: -50mm; top: -40mm; background: #0089ED; filter: blur(90px); opacity: .45; }}
.portada .trama {{ position: absolute; inset: 0; background-image: radial-gradient(#FBFAF72a 1.2px, transparent 1.2px); background-size: 7mm 7mm; }}
.portada img {{ height: 11mm; position: relative; }}
.portada .etq {{ display: inline-block; margin-top: 70mm; background: #F2F200; color: #040A14; font-family: "JetBrains Mono"; font-size: 10pt; letter-spacing: .12em; text-transform: uppercase; padding: 2.5mm 5mm; transform: rotate(-2deg); position: relative; }}
.portada h1 {{ font-size: 46pt; margin: 8mm 0 4mm; position: relative; }}
.portada h1 mark {{ background: #F2F200; color: #040A14; padding: 0 .08em; }}
.portada .dom {{ font-family: "JetBrains Mono"; font-size: 16pt; color: #A7B2C1; position: relative; }}
.portada .pie {{ position: absolute; left: 20mm; right: 20mm; bottom: 20mm; display: flex; justify-content: space-between; font-family: "JetBrains Mono"; font-size: 9pt; color: #A7B2C1; border-top: 1px solid #FBFAF733; padding-top: 5mm; }}

/* Resumen */
.resumen h2 {{ font-size: 20pt; margin: 0 0 1.5mm; }}
.bajada {{ color: #465466; margin: 0 0 5mm; }}
.kpis {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 3.5mm; margin-bottom: 6mm; }}
.kpi {{ background: #F8F5EC; border-radius: 3mm; padding: 2.8mm 4mm; border-left: 1.5mm solid #0089ED; }}
.kpi b {{ display: block; font-family: "Space Grotesk"; font-size: 19pt; line-height: 1; }}
.kpi span {{ display: block; font-weight: 700; margin-top: 2mm; }}
.kpi small {{ color: #465466; font-size: 8.5pt; }}
.fila {{ display: grid; grid-template-columns: 1.35fr 1fr; gap: 8mm; }}
h3.sub {{ font-size: 12.5pt; margin: 0 0 3mm; }}
.grafico {{ width: 100%; }}
.grafico .eje {{ font: 700 17px "Plus Jakarta Sans"; fill: #08121F; }}
.grafico .valor {{ font: 16px "JetBrains Mono"; fill: #465466; }}
.grafico .umbral {{ stroke: #E0243A; stroke-width: 1.5; stroke-dasharray: 4 4; }}
.grafico .nota {{ font: 15px "JetBrains Mono"; fill: #E0243A; }}
.leyenda {{ display: flex; gap: 6mm; font-size: 8.5pt; color: #465466; }}
.leyenda i {{ display: inline-block; width: 3mm; height: 3mm; border-radius: 1mm; margin-right: 1.5mm; vertical-align: -0.3mm; }}
table.conteo {{ width: 100%; border-collapse: collapse; }}
table.conteo th, table.conteo td {{ padding: 2.2mm 2mm; border-bottom: 1px solid #E9E4D7; text-align: left; }}
table.conteo th {{ font-family: "JetBrains Mono"; font-size: 8pt; text-transform: uppercase; color: #465466; }}
td.n {{ font-family: "Space Grotesk"; font-weight: 700; font-size: 14pt; text-align: center !important; }}
.rojo {{ color: #D6263B; }} .amarillo {{ color: #B98A00; }} .verde {{ color: #13895A; }}
ol.acciones {{ list-style: none; padding: 0; margin: 0; }}
ol.acciones li {{ display: flex; gap: 3mm; padding: 1.3mm 0; border-bottom: 1px solid #E9E4D7; }}
ol.acciones .sem {{ font-size: 11pt; }}
ol.acciones p {{ margin: .5mm 0 0; color: #465466; font-size: 9pt; }}
.alcance {{ margin-top: 4mm; background: #040A14; color: #D3DEF2; border-radius: 2.5mm; padding: 3mm 4.5mm; font-size: 8pt; line-height: 1.45; }}
.alcance b {{ color: #F2F200; }}

/* Documentos */
.documento {{ page-break-before: always; }}
.documento .apertura {{ background: #040A14; color: #FBFAF7; border-radius: 3mm; padding: 7mm; margin-bottom: 6mm; }}
.documento .apertura small {{ font-family: "JetBrains Mono"; color: #F2F200; letter-spacing: .12em; text-transform: uppercase; font-size: 8.5pt; }}
.documento .apertura h1 {{ margin: 2mm 0 0; font-size: 24pt; }}
.documento h2 {{ font-size: 16pt; margin: 9mm 0 4mm; padding-bottom: 2mm; border-bottom: 2px solid #08121F; page-break-after: avoid; }}
.documento h2.prioridad .punto {{ display: inline-block; width: 4mm; height: 4mm; border-radius: 50%; margin-right: 2.5mm; vertical-align: 0; }}
h2.critico .punto {{ background: #D6263B; }} h2.medio .punto {{ background: #F2C200; }} h2.oportunidad .punto {{ background: #13A56B; }}
.documento h3 {{ font-size: 12.5pt; margin: 7mm 0 2mm; page-break-after: avoid; }}
.documento p {{ margin: 1.8mm 0; }}
.documento ul, .documento ol {{ margin: 1.5mm 0; padding-left: 5.5mm; }}
.documento li {{ margin: .8mm 0; }}
.documento blockquote {{ margin: 3mm 0; padding: 3mm 4.5mm; background: #F8F5EC; border-left: 1.2mm solid #F2F200; border-radius: 0 2mm 2mm 0; }}
.documento blockquote p {{ margin: 1mm 0; }}
.documento pre {{ background: #0B1424; color: #E6EDF7; padding: 4mm; border-radius: 2.5mm; font-size: 7.6pt; line-height: 1.5; white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }}
.documento code {{ font-size: .88em; background: #EEF2F8; padding: .2mm 1.2mm; border-radius: 1mm; }}
.documento pre code {{ background: none; padding: 0; font-size: inherit; }}
.documento table {{ width: 100%; border-collapse: collapse; margin: 3mm 0; font-size: 9pt; page-break-inside: avoid; }}
.documento th, .documento td {{ border: 1px solid #D9D3C4; padding: 2mm; vertical-align: top; text-align: left; }}
.documento th {{ background: #040A14; color: #FBFAF7; }}
.documento hr {{ border: 0; border-top: 1px dashed #D9D3C4; margin: 6mm 0; }}
a {{ color: #004F9E; }}
</style></head><body>

<div class="portada">
  <div class="brillo"></div><div class="trama"></div>
  <img src="{logo}" alt="Sprint">
  <br><div class="etq">Auditoría SEO básica</div>
  <h1>¿Qué frena a <mark>{DOMINIO}</mark> en Google y en la IA?</h1>
  <div class="dom">https://www.{DOMINIO}/</div>
  <div class="pie"><span>Preparado por Sprint LATAM</span><span>{FECHA}</span></div>
</div>

<section class="resumen">
  <h2>Resumen ejecutivo</h2>
  <p class="bajada">El sitio tiene una base técnica sana (titles, H1, canonicals, FAQs y fuentes bien resueltos), pero es nuevo, tiene poca autoridad y una verificación anti-bots impide leerlo en parte de las visitas automáticas, incluidas las de rastreadores de IA.</p>
  <div class="kpis">{tarjetas}</div>
  <div class="fila">
    <div>
      <h3 class="sub">Velocidad: escritorio vs móvil</h3>
      {_grafico_velocidad()}
    </div>
    <div>
      <h3 class="sub">Hallazgos por prioridad</h3>
      <table class="conteo"><tr><th>Documento</th><th>Crítico</th><th>Medio</th><th>Oport.</th></tr>{conteo}</table>
    </div>
  </div>
  <h3 class="sub" style="margin-top:5mm">Las 5 acciones que más mueven la aguja</h3>
  <ol class="acciones">{acciones}</ol>
  <div class="alcance"><b>Alcance.</b> Auditoría básica: 9 de las 71 URLs del sitemap leídas vía Apify, velocidad (PageSpeed) y datos de visibilidad de Ubersuggest para Chile. No incluye rastreo completo ni el análisis semántico página por página con Jev (TypeSafe), que se hará en la auditoría completa.</div>

</section>

{_cuerpo(dev_md, "dev").replace('<section class="documento dev">', '<section class="documento dev"><div class="apertura"><small>Parte 1</small><h1>Instrucciones para el desarrollador</h1></div>', 1)}
{_cuerpo(cont_md, "contenido").replace('<section class="documento contenido">', '<section class="documento contenido"><div class="apertura"><small>Parte 2</small><h1>Instrucciones para contenido</h1></div>', 1)}
</body></html>"""


def main() -> None:
    import sys

    # Reutiliza el lanzador de Chromium del generador de contenidos.
    sys.path.insert(0, str(RAIZ / "generador_contenidos"))
    from generador.render import _lanzar

    with sync_playwright() as p:
        navegador = _lanzar(p)
        pagina = navegador.new_page()
        pagina.set_content(html(), wait_until="load")
        pagina.pdf(
            path=str(SALIDA),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=(
                '<div style="width:100%;font:8px monospace;color:#8A94A6;padding:0 18mm;'
                'display:flex;justify-content:space-between">'
                f'<span>Auditoría SEO · {DOMINIO} · Sprint LATAM</span>'
                '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
            ),
        )
        navegador.close()
    print(f"PDF generado: {SALIDA}")


if __name__ == "__main__":
    main()
