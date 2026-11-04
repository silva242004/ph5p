"""Motor de ph5p: arma un H5P.CoursePresentation clonando slides de una plantilla.

Flujo: cargar plantilla -> clonar slides con ediciones -> IDs nuevos -> traducir interfaz -> empaquetar.
Los colores salen de plantillas/<nombre>/plantilla.json (ver configurar_colores); los scripts de actividad
importan las funciones de este módulo después de que el CLI configuró la paleta.
"""
import copy
import html
import json
import os
import re
import shutil
import uuid
import zipfile

# ---------- Paleta (la reemplaza configurar_colores con la de la plantilla) ----------
NEGRO = "hsl(0,0%,0%)"              # texto
BLANCO = "hsl(0, 0%, 100%)"         # texto sobre color
AZUL = "hsl( 200, 100%, 45% )"      # acento de títulos de dos tonos
GRANATE = "hsl( 350, 75%, 31% )"    # color principal
FONDO = "rgb(224, 243, 250)"        # fondo suave de recuadros
NARANJA = "#FE9800"                 # marca PENDIENTE (no es institucional; desaparece al completar)

ROLES = {"texto": "NEGRO", "texto_sobre_color": "BLANCO", "acento": "AZUL", "principal": "GRANATE",
         "fondo_suave": "FONDO", "pendiente": "NARANJA"}


def configurar_colores(colores):
    """colores: dict rol -> color CSS (ver ROLES). Lo llama el CLI con los de plantilla.json."""
    g = globals()
    for rol, valor in (colores or {}).items():
        if rol not in ROLES:
            raise ValueError(f"rol de color desconocido: {rol} (válidos: {', '.join(ROLES)})")
        g[ROLES[rol]] = valor


def esc(t):
    return html.escape(t, quote=False)


def titulo(negro, azul="", tam="1.375em", tag="h2"):
    """Título de dos tonos como en la plantilla: parte negra + parte azul."""
    s = f'<span style="font-size:{tam};color:{NEGRO};"><strong>{esc(negro)}</strong></span>'
    if azul:
        s += f'<span style="font-size:{tam};color:{AZUL};"><strong>{esc(azul)}</strong></span>'
    return f"<{tag}>{s}</{tag}>"


def parrafos(*ps, tam="0.875em", color=NEGRO):
    """Párrafos de cuerpo. Cada item puede ser str o ('b', str) para negrita."""
    out = []
    for p in ps:
        if isinstance(p, tuple):
            out.append(f'<p><span style="font-size:{tam};color:{color};"><strong>{esc(p[1])}</strong></span></p>')
        else:
            out.append(f'<p><span style="font-size:{tam};color:{color};">{esc(p)}</span></p>')
    return "".join(out)


def enlace(texto, url, tam="0.875em"):
    return (f'<span style="font-size:{tam};color:{NEGRO};">{esc(texto)} </span>'
            f'<a href="{html.escape(url)}" target="_blank" rel="noopener" style="word-break:break-all;">'
            f'<span style="font-size:{tam};">{esc(url)}</span></a>')


def lista(items, tam="0.875em"):
    """<ul> con items: str (texto plano) o html ya armado si empieza con '<'."""
    lis = "".join(f"<li>{i if i.startswith('<') else f'<span style=\"font-size:{tam};color:{NEGRO};\">{esc(i)}</span>'}</li>"
                  for i in items)
    return f"<ul>{lis}</ul>"


def destacado(t):
    """Texto del recuadro azul claro (cursiva + negrita, 1em)."""
    return f'<p><span style="font-size:1em;color:{NEGRO};"><em><strong>{esc(t)}</strong></em></span></p>'


def pendiente(t, tam="0.875em"):
    """Marca visible de contenido que falta (lo completa el profesor)."""
    return (f'<p><span style="font-size:{tam};color:{NARANJA};"><strong>PENDIENTE: </strong></span>'
            f'<span style="font-size:{tam};color:{NARANJA};">{esc(t)}</span></p>')


# ---------- Carga ----------
class Plantilla:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        with open(os.path.join(carpeta, "content", "content.json"), encoding="utf-8") as f:
            self.content = json.load(f)
        self.slides = self.content["presentation"]["slides"]

    def slide(self, n):
        """Copia profunda del slide n (numeración 1-based, como en el editor)."""
        return copy.deepcopy(self.slides[n - 1])


# ---------- Edición de un slide ----------
class Slide:
    def __init__(self, data, origen):
        self.d = data
        self.origen = origen
        self._borrar = set()
        self._extra = {}
        self._nuevos = []

    @property
    def els(self):
        return self.d["elements"]

    def texto(self, i, html_):
        p = self.els[i]["action"]["params"]
        assert "text" in p, f"slide {self.origen} elemento {i} no es texto"
        p["text"] = html_
        return self

    def caja(self, i, x=None, y=None, w=None, h=None):
        e = self.els[i]
        for k, v in (("x", x), ("y", y), ("width", w), ("height", h)):
            if v is not None:
                e[k] = v
        return self

    def quitar(self, *idx):
        self._borrar.update(idx)
        return self

    def menu(self, titulo_):
        """Título que aparece en el menú de navegación (keywords)."""
        self.d["keywords"] = [{"main": titulo_}]
        return self

    def imagen_pendiente(self, i, descripcion):
        """Reemplaza una imagen vacía (se ve como recuadro negro) por un marcador visible."""
        e = self.els[i]
        assert e["action"]["library"].startswith("H5P.Image"), f"elemento {i} no es imagen"
        base = {k: e[k] for k in ("x", "y", "width", "height")}
        forma = {
            **base, "backgroundOpacity": 0, "displayAsButton": False, "buttonSize": "big",
            "goToSlideType": "specified", "invisible": False,
            "action": {"library": "H5P.Shape 1.0", "metadata": {"contentType": "Shapes", "license": "U"},
                       "params": {"type": "rectangle",
                                  "shape": {"fillColor": FONDO, "borderWidth": "2",
                                            "borderStyle": "dashed", "borderColor": NARANJA,
                                            "borderRadius": "4"},
                                  "line": {"borderColor": "#000000", "borderWidth": "1", "borderStyle": "solid"}}},
        }
        texto = {
            "x": base["x"] + 2, "y": base["y"] + base["height"] / 2 - 8,
            "width": max(base["width"] - 4, 10), "height": 16,
            "backgroundOpacity": 0, "displayAsButton": False, "buttonSize": "big",
            "goToSlideType": "specified", "invisible": False, "alwaysDisplayComments": False, "solution": "",
            "action": {"library": "H5P.AdvancedText 1.1",
                       "metadata": {"contentType": "Text", "license": "U", "title": "Imagen pendiente"},
                       "params": {"text": f'<p style="text-align:center;">'
                                          f'<span style="font-size:0.75em;color:{NARANJA};"><strong>IMAGEN PENDIENTE</strong><br>'
                                          f'{esc(descripcion)}</span></p>'}},
        }
        self._extra[i] = [forma, texto]   # mismo orden de capas que la imagen original
        return self

    def clave(self, k):
        """Nombre interno del slide, para que los botones 'ir a' lo encuentren por clave."""
        self.d["_clave"] = k
        return self

    def agregar_texto(self, html_, x, y, w, h):
        self._nuevos.append({
            "x": x, "y": y, "width": w, "height": h, "backgroundOpacity": 0, "displayAsButton": False,
            "buttonSize": "big", "goToSlideType": "specified", "invisible": False, "alwaysDisplayComments": False,
            "solution": "",
            "action": {"library": "H5P.AdvancedText 1.1",
                       "metadata": {"contentType": "Text", "license": "U", "title": "Texto"},
                       "params": {"text": html_}},
        })
        return self

    def boton(self, i, titulo_, x, y, w, h):
        """Convierte el texto i en botón emergente (como el botón 'Referencias' de la plantilla)."""
        e = self.els[i]
        e.update({"x": x, "y": y, "width": w, "height": h, "displayAsButton": True, "buttonSize": "small"})
        e["action"]["metadata"]["title"] = titulo_
        return self

    def ir_a(self, destino, x, y, w, h):
        """Zona clicable invisible que salta al slide con esa clave (se resuelve al construir)."""
        self._nuevos.append({
            "x": x, "y": y, "width": w, "height": h, "goToSlide": destino,
            "goToSlideType": "specified", "invisible": True, "backgroundOpacity": 0,
            "displayAsButton": False, "buttonSize": "big",
        })
        return self

    def preguntas_unica(self, i, preguntas, retro):
        """SingleChoiceSet: lista de (pregunta, [correcta, incorrecta, ...]). La primera respuesta es la correcta."""
        p = self.els[i]["action"]["params"]
        assert "choices" in p, f"elemento {i} no es SingleChoiceSet"
        p["choices"] = [{"question": f"<p><strong>{esc(q)}</strong></p>\n",
                         "answers": [f"<p>{esc(a)}</p>\n" for a in resp]} for q, resp in preguntas]
        p["overallFeedback"] = [{"from": 0, "to": 100, "feedback": retro}]
        return self

    def cerrar(self):
        out = []
        for i, e in enumerate(self.els):
            if i in self._extra:
                out += self._extra[i]
            elif i not in self._borrar:
                out.append(e)
        self.d["elements"] = out + self._nuevos
        return self.d


# ---------- Ensamblado ----------
def nuevos_ids(obj):
    """Asigna un subContentId nuevo a cada subcontenido (la plantilla trae duplicados)."""
    if isinstance(obj, dict):
        if "subContentId" in obj or ("library" in obj and "params" in obj):
            obj["subContentId"] = str(uuid.uuid4())
        for v in obj.values():
            nuevos_ids(v)
    elif isinstance(obj, list):
        for v in obj:
            nuevos_ids(v)


def archivos_usados(obj, acc=None):
    acc = set() if acc is None else acc
    if isinstance(obj, dict):
        p = obj.get("path")
        if isinstance(p, str) and not re.match(r"^https?://", p):
            acc.add(p.replace("\\", "/"))
        for v in obj.values():
            archivos_usados(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            archivos_usados(v, acc)
    return acc


def _textos_interfaz(carpeta_lib):
    """Traducciones oficiales de la librería: {grupo: {campo: texto}} para los grupos de textos (l10n, UI...).
    Usa language/es.json y, si un campo quedó en inglés allí, language/es-mx.json."""
    def cargar(nombre):
        ruta = os.path.join(carpeta_lib, "language", nombre)
        return json.load(open(ruta, encoding="utf-8"))["semantics"] if os.path.exists(ruta) else None
    sem = json.load(open(os.path.join(carpeta_lib, "semantics.json"), encoding="utf-8"))
    es, esmx = cargar("es.json"), cargar("es-mx.json")
    if not es:
        return {}
    out = {}
    for k, campo in enumerate(sem):
        if campo.get("type") != "group" or not all(f.get("type") in ("text", None) for f in campo.get("fields", [])):
            continue
        grupo = {}
        for j, f in enumerate(campo.get("fields", [])):
            ingles = f.get("default")
            opciones = [x["fields"][j].get("default") for x in (es[k], (esmx or es)[k])
                        if j < len(x.get("fields", []))]
            trad = next((o for o in opciones if o and o != ingles), None)
            if trad:
                grupo[f["name"]] = trad
        if grupo:
            out[campo["name"]] = grupo
    return out


# Textos que ni es.json ni es-mx.json traducen (revisado con CoursePresentation 1.27 y SingleChoiceSet 1.11).
TRADUCCION_MANUAL = {
    "H5P.CoursePresentation": {"l10n": {
        "slides": "Diapositivas", "resultHeader": "Resultados", "amountCorrect": "@value / @max correctas",
        "amountCorrectAria": "@value de @max correctas"}},
    "H5P.SingleChoiceSet": {"l10n": {
        "nextButton": "Siguiente", "showResultsButtonLabel": "Mostrar resultados", "resultHeader": "Tu resultado:",
        "totalScore": ":score de :maxScore correctas", "resultTableHeader": "Pregunta",
        "resultScoreTableHeader": "Puntaje"}},
}


def traducir_interfaz(content, carpeta_plantilla):
    """Pasa al español los textos de interfaz (botones, resultados) de CoursePresentation y de cada interacción.
    La plantilla institucional los trae en inglés."""
    cache = {}

    def lib_dir(libreria):
        nombre, ver = libreria.split(" ")
        return os.path.join(carpeta_plantilla, f"{nombre}-{ver}")

    def aplicar(params, libreria):
        if libreria not in cache:
            d = lib_dir(libreria)
            cache[libreria] = _textos_interfaz(d) if os.path.isdir(d) else {}
            for grupo, textos in TRADUCCION_MANUAL.get(libreria.split(" ")[0], {}).items():
                cache[libreria].setdefault(grupo, {}).update(textos)
        for grupo, textos in cache[libreria].items():
            if isinstance(params.get(grupo), dict):
                for k, v in textos.items():
                    if k in params[grupo]:
                        params[grupo][k] = v

    def walk(o):
        if isinstance(o, dict):
            if "library" in o and isinstance(o.get("params"), dict):
                aplicar(o["params"], o["library"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    with open(os.path.join(carpeta_plantilla, "h5p.json"), encoding="utf-8") as f:
        principal = json.load(f)["mainLibrary"]
    ver = next(d for d in os.listdir(carpeta_plantilla) if d.startswith(principal + "-")).split("-")[-1]
    aplicar(content, f"{principal} {ver}")
    walk(content)


def construir(plantilla, slides, titulo_h5p, destino_dir, destino_h5p):
    """Escribe la carpeta descomprimida (para la vista previa) y el .h5p."""
    content = copy.deepcopy(plantilla.content)
    # Resolver los botones "ir a" por clave -> número de slide (1-based).
    claves = {s.get("_clave"): n for n, s in enumerate(slides, 1) if s.get("_clave")}
    for s in slides:
        for e in s["elements"]:
            if isinstance(e.get("goToSlide"), str):
                assert e["goToSlide"] in claves, f"clave de slide desconocida: {e['goToSlide']}"
                e["goToSlide"] = claves[e["goToSlide"]]
        s.pop("_clave", None)
    content["presentation"]["slides"] = slides
    nuevos_ids(content)
    traducir_interfaz(content, plantilla.carpeta)

    if os.path.exists(destino_dir):
        shutil.rmtree(destino_dir)
    # Librerías + h5p.json desde la plantilla; content/ solo con los archivos usados.
    for nombre in os.listdir(plantilla.carpeta):
        src = os.path.join(plantilla.carpeta, nombre)
        if nombre == "content" or not os.path.isdir(src):
            continue
        shutil.copytree(src, os.path.join(destino_dir, nombre))
    with open(os.path.join(plantilla.carpeta, "h5p.json"), encoding="utf-8") as f:
        h5pjson = json.load(f)
    h5pjson["title"] = titulo_h5p
    with open(os.path.join(destino_dir, "h5p.json"), "w", encoding="utf-8") as f:
        json.dump(h5pjson, f, ensure_ascii=False)

    usados = archivos_usados(content)
    faltan = [u for u in usados if not os.path.exists(os.path.join(plantilla.carpeta, "content", u))]
    assert not faltan, f"archivos referenciados que no existen: {faltan}"
    os.makedirs(os.path.join(destino_dir, "content"))
    for u in usados:
        dst = os.path.join(destino_dir, "content", u)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(plantilla.carpeta, "content", u), dst)
    with open(os.path.join(destino_dir, "content", "content.json"), "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False)

    # .h5p = zip con h5p.json y content/ en la raíz
    if os.path.exists(destino_h5p):
        os.remove(destino_h5p)
    with zipfile.ZipFile(destino_h5p, "w", zipfile.ZIP_DEFLATED) as z:
        for raiz, _, archivos in os.walk(destino_dir):
            for a in archivos:
                ruta = os.path.join(raiz, a)
                z.write(ruta, os.path.relpath(ruta, destino_dir).replace("\\", "/"))
    return content


def verificar(content):
    """Comprobaciones estructurales antes de subir."""
    ids = []

    def walk(o):
        if isinstance(o, dict):
            if "subContentId" in o:
                ids.append(o["subContentId"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(content)
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, f"subContentId duplicados: {dup}"
    n = len(content["presentation"]["slides"])
    for k, s in enumerate(content["presentation"]["slides"], 1):
        for e in s["elements"]:
            if "goToSlide" in e and e.get("goToSlideType") == "specified":
                assert 1 <= e["goToSlide"] <= n, f"slide {k}: GoToSlide a {e['goToSlide']} fuera de rango"
            if e.get("action", {}).get("library", "").startswith("H5P.Image"):
                assert e["action"]["params"].get("file"), f"slide {k}: imagen vacía (se verá negra)"
        assert s.get("keywords"), f"slide {k} sin título de menú"
    return {"slides": n, "subcontenidos": len(ids)}
