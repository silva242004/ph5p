"""Inspección de una plantilla CoursePresentation: paleta de colores y ficha de slides/elementos.

La ficha (FICHA.md) es la referencia para escribir actividades: dice qué slide clonar y qué índice
tiene cada elemento (texto, imagen, forma, interacción) para usar Slide.texto(i, ...), Slide.caja(i, ...), etc.
"""
import collections
import colorsys
import json
import re


def _norm(v):
    v = v.strip().lower().replace(" ", "")
    if m := re.fullmatch(r"#([0-9a-f]{3})", v):
        v = "#" + "".join(ch * 2 for ch in m[1])
    if re.fullmatch(r"#[0-9a-f]{6}", v):
        return v.upper()
    if m := re.fullmatch(r"rgba?\((\d+),(\d+),(\d+)(?:,([\d.]+))?\)", v):
        if m[4] is not None and float(m[4]) == 0:
            return None                                   # totalmente transparente
        return "#%02X%02X%02X" % tuple(int(x) for x in m.groups()[:3])
    if m := re.fullmatch(r"hsl\(([\d.]+),([\d.]+)%,([\d.]+)%\)", v):
        h, s, l = (float(x) for x in m.groups())
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
    return v


def paleta(content):
    """{color_hex: {uso: set(slides)}} con los colores de formas, textos y fondos (no los de las imágenes)."""
    uso = collections.defaultdict(lambda: collections.defaultdict(set))

    def add(color, donde, n):
        c = _norm(color)
        if c:
            uso[c][donde].add(n)

    for n, s in enumerate(content["presentation"]["slides"], 1):
        for e in s.get("elements", []):
            p = e.get("action", {}).get("params", {})
            if "shape" in p:
                add(p["shape"]["fillColor"], "relleno de forma", n)
                if str(p["shape"].get("borderWidth", "0")) not in ("0", ""):
                    add(p["shape"]["borderColor"], "borde de forma", n)
            texto = json.dumps(p, ensure_ascii=False)
            for col in re.findall(r"(?<![-\w])color:\s*([^;\"]+)", texto):
                add(col, "texto", n)
            for col in re.findall(r"background-color:\s*([^;\"]+)", texto):
                add(col, "fondo de texto", n)
    return uso


def tabla_paleta(uso):
    total = lambda k: sum(len(v) for v in uso[k].values())
    filas = ["| Color | Usos | Dónde (slides) |", "|---|---|---|"]
    for col in sorted(uso, key=total, reverse=True):
        donde = "; ".join(f"{k}: {','.join(map(str, sorted(v)))}" for k, v in uso[col].items())
        filas.append(f"| `{col}` | {total(col)} | {donde} |")
    return "\n".join(filas)


def _resumen_elemento(e):
    a = e.get("action")
    if not a:
        return "Ir a slide", f"→ {e.get('goToSlideType')} {e.get('goToSlide', '')}"
    lib = a["library"].split(" ")[0].replace("H5P.", "")
    p = a.get("params", {})
    if "text" in p:
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", p["text"])).replace("&nbsp;", " ").strip()
        tam = re.search(r"font-size:\s*([\d.]+em)", p["text"])
        extra = f"{t[:60]}" + (f" ({tam[1]})" if tam else "")
        if e.get("displayAsButton"):
            extra = "[botón emergente] " + extra
        return lib, extra
    if "file" in p:
        return lib, "imagen: " + p["file"].get("path", "")
    if lib == "Image":
        return lib, "**vacía: se ve como recuadro negro**"
    if "shape" in p:
        return lib, f"{p.get('type')} {_norm(p['shape']['fillColor']) or 'transparente'}"
    return lib, "interacción"


def ficha_md(nombre, content, h5pjson):
    slides = content["presentation"]["slides"]
    out = [f"# Ficha de la plantilla `{nombre}`", "",
           f"- Título del paquete: {h5pjson.get('title', '')}",
           f"- Librería principal: {h5pjson.get('mainLibrary')}",
           f"- Slides: {len(slides)}", "",
           "Generada con `python -I ph5p.py plantilla ficha " + nombre + "`. No editar a mano.", "",
           "Posiciones en % del slide (x, y, ancho, alto). Usa el **número de slide** en `T.slide(n)` y el "
           "**índice** del elemento en `Slide.texto(i, ...)`, `Slide.caja(i, ...)`, `Slide.quitar(i)`, etc.", "",
           "## Paleta detectada", "", tabla_paleta(paleta(content)), "", "## Slides", ""]
    for n, s in enumerate(slides, 1):
        kw = ", ".join(k.get("main", "") for k in s.get("keywords", [])) or "(sin título de menú)"
        out += [f"### Slide {n}: {kw}", "", "| i | Tipo | x | y | ancho | alto | Contenido |", "|---|---|---|---|---|---|---|"]
        for i, e in enumerate(s.get("elements", [])):
            tipo, extra = _resumen_elemento(e)
            extra = extra.replace("|", "\\|")
            out.append(f"| {i} | {tipo} | {e['x']:.0f} | {e['y']:.0f} | {e['width']:.0f} | {e['height']:.0f} | {extra} |")
        out.append("")
    return "\n".join(out)
