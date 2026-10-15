"""Genera las imagenes SVG del README del perfil (cabecera, actividad y lenguajes).

Uso:
    python3 scripts/generate_assets.py               # todo
    python3 scripts/generate_assets.py activity      # solo la tarjeta de actividad

Requiere la CLI de GitHub (`gh`) autenticada.

- La actividad sale del calendario de contribuciones del ultimo ano. Como el perfil
  muestra las contribuciones privadas, el calendario publico ya las incluye, asi que
  el GITHUB_TOKEN de la Action basta para regenerarla cada dia.
- Los lenguajes suman los bytes de todos los repositorios propios (no forks),
  incluidos los privados. Eso necesita el token personal, asi que se regeneran
  a mano desde local y no en la Action.
"""

import json
import subprocess
import sys
from datetime import date, timedelta
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
        # Escala del calendario, de "sin actividad" a "maxima actividad".
        "levels": ["#161b22", "#0c2d6b", "#1158c7", "#388bfd", "#79c0ff"],
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#0969da",
        "grid": "#eaeef2",
        "node": "#f6f8fa",
        "levels": ["#ebeef2", "#b6e3ff", "#54aeff", "#0969da", "#0a3069"],
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

LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def gh(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return out.stdout


def thousands(n):
    return f"{n:,}".replace(",", ".")


# --------------------------------------------------------------------- cabecera


def header_svg(t):
    width, height = 1280, 320
    # Diagrama de arquitectura a la derecha: cliente -> API -> datos.
    node_w, node_h = 130, 44
    nodes = [("cliente", 880, 70), ("api", 1060, 138), ("datos", 880, 206)]

    def mid(i):
        _, x, y = nodes[i]
        return x, y + node_h / 2

    (cx, cy), (ax, ay), (dx, dy) = mid(0), mid(1), mid(2)
    # Curvas que salen por la derecha de un nodo y entran por el lado del siguiente.
    links = [
        f"M{cx + node_w} {cy} C{ax - 20} {cy}, {ax - 20} {ay}, {ax} {ay}",
        f"M{ax} {ay} C{ax - 20} {ay}, {ax - 20} {dy}, {dx + node_w} {dy}",
    ]
    # El trazo discontinuo avanza en bucle para sugerir datos fluyendo.
    link_paths = "".join(
        f'<path d="{d}" fill="none" stroke="{t["accent"]}" stroke-width="1.5" '
        f'stroke-dasharray="4 4" opacity="0.75">'
        f'<animate attributeName="stroke-dashoffset" from="16" to="0" dur="1.2s" repeatCount="indefinite"/>'
        f"</path>"
        for d in links
    )
    node_boxes = "".join(
        f'<rect x="{x}" y="{y}" width="{node_w}" height="{node_h}" rx="8" '
        f'fill="{t["node"]}" stroke="{t["border"]}"/>'
        f'<circle cx="{x + 20}" cy="{y + node_h / 2}" r="4" fill="{t["accent"]}">'
        f'<animate attributeName="opacity" values="1;0.35;1" dur="2.4s" begin="{i * 0.8}s" repeatCount="indefinite"/>'
        f"</circle>"
        f'<text x="{x + 34}" y="{y + node_h / 2 + 5}" font-family="{MONO}" '
        f'font-size="16" fill="{t["text"]}">{label}</text>'
        for i, (label, x, y) in enumerate(nodes)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Mario Sanchez - Desarrollador Full Stack">
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="{t["grid"]}"/>
    </pattern>
    <linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/>
      <stop offset="0.6" stop-color="{t["bg"]}" stop-opacity="0.65"/>
      <stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="url(#grid)"/>
  <rect x="1" y="1" width="860" height="{height - 2}" rx="12" fill="url(#fade)"/>
  <rect x="64" y="62" width="4" height="24" rx="2" fill="{t["accent"]}"/>
  <text x="80" y="80" font-family="{MONO}" font-size="18" fill="{t["accent"]}">Caracas, Venezuela</text>
  <text x="62" y="148" font-family="{SANS}" font-size="62" font-weight="700" fill="{t["text"]}">Mario S&#225;nchez</text>
  <text x="64" y="192" font-family="{SANS}" font-size="27" font-weight="600" fill="{t["text"]}">Desarrollador Full Stack</text>
  <text x="64" y="228" font-family="{SANS}" font-size="21" fill="{t["muted"]}">EY  &#183;  BIS Integraciones  &#183;  Bodega Provisions  &#183;  Ingenier&#237;a Inform&#225;tica UCAB</text>
  <text x="64" y="268" font-family="{MONO}" font-size="17" fill="{t["muted"]}">TypeScript / React / Node.js / NestJS / Python / PostgreSQL / Docker</text>
  {link_paths}
  {node_boxes}
</svg>
"""


# -------------------------------------------------------------------- actividad


def contribution_calendar():
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          restrictedContributionsCount
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount contributionLevel } }
          }
        }
      }
    }"""
    data = json.loads(gh("api", "graphql", "-f", f"query={query}", "-F", f"login={USER}"))
    return data["data"]["user"]["contributionsCollection"]


def activity_svg(t, cal):
    weeks = cal["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total = cal["contributionCalendar"]["totalContributions"]
    active = sum(1 for d in days if d["contributionCount"])
    best = max(d["contributionCount"] for d in days)

    width, pad = 840, 28
    grid_top, label_w = 150, 34
    step = (width - 2 * pad - label_w) / len(weeks)
    cell = step - 3
    grid_h = 7 * step
    height = int(grid_top + grid_h + 56)

    # Cabecera de la tarjeta: total a la izquierda, tres metricas a la derecha.
    stats = [
        (thousands(cal["totalCommitContributions"]), "commits"),
        (thousands(active), "d&#237;as activos"),
        (thousands(best), "mejor d&#237;a"),
    ]
    stat_w = 128
    stats_svg = "".join(
        f'<text x="{width - pad - (len(stats) - 1 - i) * stat_w}" y="64" text-anchor="end" '
        f'font-family="{SANS}" font-size="28" font-weight="700" fill="{t["text"]}">{value}</text>'
        f'<text x="{width - pad - (len(stats) - 1 - i) * stat_w}" y="90" text-anchor="end" '
        f'font-family="{SANS}" font-size="14" fill="{t["muted"]}">{label}</text>'
        for i, (value, label) in enumerate(stats)
    )

    cells, month_labels = [], []
    last_month = None
    for wi, week in enumerate(weeks):
        x = pad + label_w + wi * step
        for day in week["contributionDays"]:
            weekday = (date.fromisoformat(day["date"]).weekday() + 1) % 7  # domingo = 0
            y = grid_top + weekday * step
            color = t["levels"][LEVELS.index(day["contributionLevel"])]
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" fill="{color}">'
                f'<title>{day["date"]}: {day["contributionCount"]}</title></rect>'
            )
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        # Etiqueta de mes en la primera semana que empieza en ese mes (sin pisar el borde).
        if first.month != last_month and wi < len(weeks) - 2:
            if last_month is not None or first.day <= 7:
                month_labels.append(
                    f'<text x="{x:.1f}" y="{grid_top - 10}" font-family="{SANS}" font-size="13" '
                    f'fill="{t["muted"]}">{MONTHS_ES[first.month - 1]}</text>'
                )
            last_month = first.month

    weekday_labels = "".join(
        f'<text x="{pad}" y="{grid_top + i * step + cell - 1:.1f}" font-family="{SANS}" font-size="12" '
        f'fill="{t["muted"]}">{label}</text>'
        for i, label in ((1, "lun"), (3, "mi&#233;"), (5, "vie"))
    )

    legend_y = grid_top + grid_h + 26
    legend_x = width - pad - 5 * 16 - 36
    legend = (
        f'<text x="{legend_x - 8}" y="{legend_y + 10}" text-anchor="end" font-family="{SANS}" '
        f'font-size="12" fill="{t["muted"]}">menos</text>'
        + "".join(
            f'<rect x="{legend_x + i * 16}" y="{legend_y}" width="12" height="12" rx="2.5" fill="{c}"/>'
            for i, c in enumerate(t["levels"])
        )
        + f'<text x="{legend_x + 5 * 16 + 4}" y="{legend_y + 10}" font-family="{SANS}" '
        f'font-size="12" fill="{t["muted"]}">m&#225;s</text>'
    )
    updated = date.today()
    footnote = (
        f'<text x="{pad}" y="{legend_y + 10}" font-family="{SANS}" font-size="12" fill="{t["muted"]}">'
        f'{thousands(cal["restrictedContributionsCount"])} contribuciones en repositorios privados  &#183;  '
        f'actualizado el {updated.day} {MONTHS_ES[updated.month - 1]} {updated.year}</text>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contribuciones en el ultimo ano">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
  <text x="{pad}" y="72" font-family="{SANS}" font-size="46" font-weight="700" fill="{t["accent"]}">{thousands(total)}</text>
  <text x="{pad}" y="98" font-family="{SANS}" font-size="15" fill="{t["muted"]}">contribuciones en el &#250;ltimo a&#241;o</text>
  {stats_svg}
  {"".join(month_labels)}
  {weekday_labels}
  {"".join(cells)}
  {footnote}
  {legend}
</svg>
"""


# -------------------------------------------------------------------- lenguajes


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


def languages_svg(t, langs):
    width = 840
    pad = 28
    bar_y, bar_h = 32, 12
    cols = 3
    row_h = 32
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


# ------------------------------------------------------------------------- main


def write(name, render, *args):
    for theme_name, theme in THEMES.items():
        (ASSETS / f"{name}-{theme_name}.svg").write_text(render(theme, *args), encoding="utf-8")


def main():
    targets = set(sys.argv[1:]) or {"header", "activity", "languages"}
    ASSETS.mkdir(exist_ok=True)
    if "header" in targets:
        write("header", header_svg)
    if "activity" in targets:
        cal = contribution_calendar()
        write("activity", activity_svg, cal)
        print(f"actividad: {cal['contributionCalendar']['totalContributions']} contribuciones")
    if "languages" in targets:
        langs = top_languages(language_totals())
        write("languages", languages_svg, langs)
        for lang, pct in langs:
            print(f"{lang:12} {pct:5.1f}%")


if __name__ == "__main__":
    main()
