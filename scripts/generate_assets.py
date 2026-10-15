"""Genera las imagenes SVG del README del perfil (cabecera y lenguajes).

Uso:
    python3 scripts/generate_assets.py

Requiere la CLI de GitHub (`gh`) autenticada. La distribucion de lenguajes se
calcula sumando los bytes de codigo de todos los repositorios propios (no forks),
incluidos los privados, para que refleje el trabajo real y no solo lo publico.
"""

import json
import subprocess
from pathlib import Path

USER = "mjsanchezr"
ASSETS = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#2f81f7",
        "grid": "#21262d",
        "node": "#161b22",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#0969da",
        "grid": "#eaeef2",
        "node": "#f6f8fa",
    },
}

# Colores de GitHub Linguist, para que coincidan con los que muestra GitHub.
LANG_COLORS = {
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "Java": "#b07219",
    "JavaScript": "#f1e05a",
    "CSS": "#663399",
    "Python": "#3572a5",
    "SQL": "#336790",
    "Shell": "#89e051",
    "Otros": "#8b949e",
}

# Lenguajes que se agrupan bajo otro nombre o se descartan por ser configuracion.
LANG_ALIASES = {"PLpgSQL": "SQL", "TSQL": "SQL"}
LANG_IGNORED = {"Dockerfile", "PowerShell", "Batchfile", "Makefile"}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def gh(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return out.stdout


def language_totals():
    repos = json.loads(gh("repo", "list", USER, "--limit", "200", "--json", "name,isFork"))
    totals = {}
    for repo in repos:
        if repo["isFork"]:
            continue
        langs = json.loads(gh("api", f"repos/{USER}/{repo['name']}/languages"))
        for lang, size in langs.items():
            if lang in LANG_IGNORED:
                continue
            lang = LANG_ALIASES.get(lang, lang)
            totals[lang] = totals.get(lang, 0) + size
    return totals


def top_languages(totals, limit=6):
    ordered = sorted(totals.items(), key=lambda kv: -kv[1])
    top = ordered[:limit]
    rest = sum(size for _, size in ordered[limit:])
    if rest:
        top.append(("Otros", rest))
    total = sum(size for _, size in top)
    return [(lang, size / total * 100) for lang, size in top]


def header_svg(t):
    width, height = 1280, 300
    # Diagrama de arquitectura a la derecha: cliente -> API -> base de datos.
    nodes = [("cliente", 860, 70), ("api", 1010, 140), ("datos", 860, 210)]
    node_w, node_h = 130, 44
    links = [(0, 1), (1, 2)]

    def center(i):
        _, x, y = nodes[i]
        return x + node_w / 2, y + node_h / 2

    link_paths = "".join(
        f'<path d="M{center(a)[0] + node_w / 2} {center(a)[1]} '
        f'C{center(b)[0] - 30} {center(a)[1]}, {center(b)[0] - 30} {center(b)[1]}, '
        f'{center(b)[0] - node_w / 2} {center(b)[1]}" fill="none" stroke="{t["accent"]}" '
        f'stroke-width="1.5" stroke-dasharray="4 4" opacity="0.7"/>'
        if a == 0 else
        f'<path d="M{center(a)[0] - node_w / 2} {center(a)[1]} '
        f'C{center(b)[0] + 30} {center(a)[1]}, {center(b)[0] + 30} {center(b)[1]}, '
        f'{center(b)[0] + node_w / 2} {center(b)[1]}" fill="none" stroke="{t["accent"]}" '
        f'stroke-width="1.5" stroke-dasharray="4 4" opacity="0.7"/>'
        for a, b in links
    )
    node_boxes = "".join(
        f'<rect x="{x}" y="{y}" width="{node_w}" height="{node_h}" rx="8" '
        f'fill="{t["node"]}" stroke="{t["border"]}"/>'
        f'<circle cx="{x + 20}" cy="{y + node_h / 2}" r="4" fill="{t["accent"]}"/>'
        f'<text x="{x + 34}" y="{y + node_h / 2 + 5}" font-family="{MONO}" '
        f'font-size="14" fill="{t["text"]}">{label}</text>'
        for label, x, y in nodes
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Mario Sanchez - Desarrollador Full Stack">
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="{t["grid"]}"/>
    </pattern>
    <linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/>
      <stop offset="0.55" stop-color="{t["bg"]}" stop-opacity="0.6"/>
      <stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="url(#grid)"/>
  <rect x="1" y="1" width="820" height="{height - 2}" rx="12" fill="url(#fade)"/>
  <rect x="64" y="68" width="4" height="22" rx="2" fill="{t["accent"]}"/>
  <text x="80" y="85" font-family="{MONO}" font-size="16" fill="{t["accent"]}">github.com/{USER}</text>
  <text x="62" y="152" font-family="{SANS}" font-size="56" font-weight="700" fill="{t["text"]}">Mario S&#225;nchez</text>
  <text x="64" y="194" font-family="{SANS}" font-size="22" fill="{t["muted"]}">Desarrollador Full Stack  &#183;  Ingenier&#237;a Inform&#225;tica, UCAB</text>
  <text x="64" y="240" font-family="{MONO}" font-size="15" fill="{t["muted"]}">TypeScript / React / Node.js / NestJS / Java / PostgreSQL / Docker</text>
  {link_paths}
  {node_boxes}
</svg>
"""


def languages_svg(t, langs):
    width = 1280
    pad = 32
    bar_y, bar_h = 32, 12
    cols = 4
    row_h = 34
    rows = (len(langs) + cols - 1) // cols
    height = bar_y + bar_h + 32 + rows * row_h + 12
    bar_w = width - 2 * pad

    segments, x = [], pad
    for i, (lang, pct) in enumerate(langs):
        w = bar_w * pct / 100
        # Separacion de 2px entre segmentos; el ultimo cierra exacto el ancho.
        seg_w = max(w - 2, 1) if i < len(langs) - 1 else pad + bar_w - x
        segments.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{seg_w:.2f}" height="{bar_h}" fill="{LANG_COLORS.get(lang, LANG_COLORS["Otros"])}"/>')
        x += w

    col_w = bar_w / cols
    legend = []
    for i, (lang, pct) in enumerate(langs):
        cx = pad + (i % cols) * col_w
        cy = bar_y + bar_h + 40 + (i // cols) * row_h
        color = LANG_COLORS.get(lang, LANG_COLORS["Otros"])
        legend.append(
            f'<circle cx="{cx + 6}" cy="{cy - 5}" r="6" fill="{color}"/>'
            f'<text x="{cx + 22}" y="{cy}" font-family="{SANS}" font-size="16" fill="{t["text"]}">{lang}</text>'
            f'<text x="{cx + col_w - 24}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="15" fill="{t["muted"]}">{pct:.1f}%</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Distribucion de lenguajes">
  <defs>
    <clipPath id="bar"><rect x="{pad}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6"/></clipPath>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <g clip-path="url(#bar)">{"".join(segments)}</g>
  {"".join(legend)}
</svg>
"""


def main():
    ASSETS.mkdir(exist_ok=True)
    langs = top_languages(language_totals())
    for name, theme in THEMES.items():
        (ASSETS / f"header-{name}.svg").write_text(header_svg(theme), encoding="utf-8")
        (ASSETS / f"languages-{name}.svg").write_text(languages_svg(theme, langs), encoding="utf-8")
    for lang, pct in langs:
        print(f"{lang:12} {pct:5.1f}%")


if __name__ == "__main__":
    main()
