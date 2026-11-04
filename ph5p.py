"""ph5p: montaje de cursos en H5P (CoursePresentation) y Moodle a partir de plantillas institucionales.

Uso:  python -I ph5p.py <comando> [opciones]      (python -I ph5p.py -h para la ayuda)

Comandos principales
  plantilla agregar <archivo.h5p> <nombre>   Registra una plantilla y genera su ficha
  plantilla ficha <nombre>                   Regenera FICHA.md (slides, elementos, paleta)
  plantilla lista                            Plantillas registradas
  curso nuevo <nombre> --plantilla <p>       Crea un curso a partir de cursos/ejemplo
  construir <curso> [--actividad <id>]       Genera los .h5p y los libros del curso en trabajo/
  vista-previa [--puerto 8765]               Servidor local para ver los .h5p sin Moodle
  moodle configurar <carpeta server>         Guarda dónde está el Moodle local (ph5p.local.json)
  moodle iniciar | detener | estado          Arranca/detiene MariaDB y Apache del Moodle local
  moodle hvp [--version 1.28.3]              Instala mod_hvp (la versión de producción)
  moodle publicar <curso>                    Construye y sube el curso al Moodle local
"""
import argparse
import json
import os
import runpy
import shutil
import socket
import subprocess
import sys
import zipfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "nucleo"))
import h5pkit                      # noqa: E402
import ficha                       # noqa: E402
from moodle_html import Estilo     # noqa: E402

TRABAJO = os.path.join(RAIZ, "trabajo")
CONFIG_LOCAL = os.path.join(RAIZ, "ph5p.local.json")


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)


def error(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- plantillas
def carpeta_plantilla(nombre):
    return os.path.join(RAIZ, "plantillas", nombre)


def plantilla_extraida(nombre):
    """Descomprime plantillas/<nombre>/plantilla.h5p en trabajo/plantillas/<nombre>/ (una sola vez)."""
    origen = os.path.join(carpeta_plantilla(nombre), "plantilla.h5p")
    destino = os.path.join(TRABAJO, "plantillas", nombre)
    if not os.path.exists(origen):
        error(f"falta {origen}. Regístrala con: python -I ph5p.py plantilla agregar <archivo.h5p> {nombre}")
    marca = os.path.join(destino, ".origen")
    firma = f"{os.path.getsize(origen)}-{int(os.path.getmtime(origen))}"
    if not (os.path.exists(marca) and open(marca).read() == firma):
        shutil.rmtree(destino, ignore_errors=True)
        with zipfile.ZipFile(origen) as z:
            z.extractall(destino)
        with open(marca, "w") as f:
            f.write(firma)
    return destino


def config_plantilla(nombre):
    ruta = os.path.join(carpeta_plantilla(nombre), "plantilla.json")
    if not os.path.exists(ruta):
        error(f"falta {ruta}")
    return leer_json(ruta)


def cmd_plantilla_agregar(a):
    if not zipfile.is_zipfile(a.archivo):
        error(f"{a.archivo} no es un .h5p válido (debe ser un ZIP)")
    with zipfile.ZipFile(a.archivo) as z:
        h5pjson = json.loads(z.read("h5p.json"))
    if h5pjson.get("mainLibrary") != "H5P.CoursePresentation":
        error(f"la plantilla debe ser H5P.CoursePresentation (es {h5pjson.get('mainLibrary')})")
    dest = carpeta_plantilla(a.nombre)
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(a.archivo, os.path.join(dest, "plantilla.h5p"))
    cfg = os.path.join(dest, "plantilla.json")
    if not os.path.exists(cfg):
        escribir_json(cfg, {
            "nombre": h5pjson.get("title", a.nombre),
            "descripcion": "COMPLETAR: de qué institución o facultad es y de dónde se descargó.",
            "colores": {"texto": "hsl(0,0%,0%)", "texto_sobre_color": "hsl(0, 0%, 100%)",
                        "acento": "COMPLETAR (ver FICHA.md)", "principal": "COMPLETAR (ver FICHA.md)",
                        "fondo_suave": "COMPLETAR (ver FICHA.md)", "pendiente": "#FE9800"},
            "reglas": ["COMPLETAR: reglas de uso de la plantilla (por ejemplo, las del slide de instrucciones)."],
        })
        print(f"Creado {cfg}: completa los colores con la paleta de la ficha.")
    cmd_plantilla_ficha(argparse.Namespace(nombre=a.nombre))


def cmd_plantilla_ficha(a):
    d = plantilla_extraida(a.nombre)
    md = ficha.ficha_md(a.nombre, leer_json(os.path.join(d, "content", "content.json")),
                        leer_json(os.path.join(d, "h5p.json")))
    ruta = os.path.join(carpeta_plantilla(a.nombre), "FICHA.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Ficha: {ruta}")


def cmd_plantilla_lista(a):
    base = os.path.join(RAIZ, "plantillas")
    for n in sorted(os.listdir(base)):
        if os.path.isdir(os.path.join(base, n)):
            tiene = os.path.exists(os.path.join(base, n, "plantilla.h5p"))
            print(f"{n:30} {'listo' if tiene else 'FALTA plantilla.h5p'}")


# ---------------------------------------------------------------- cursos
def carpeta_curso(nombre):
    d = os.path.join(RAIZ, "cursos", nombre)
    if not os.path.isfile(os.path.join(d, "curso.json")):
        error(f"no existe cursos/{nombre}/curso.json")
    return d


def salida_curso(nombre):
    return os.path.join(TRABAJO, "salida", nombre)


def cmd_curso_nuevo(a):
    dest = os.path.join(RAIZ, "cursos", a.nombre)
    if os.path.exists(dest):
        error(f"ya existe cursos/{a.nombre}")
    shutil.copytree(os.path.join(RAIZ, "cursos", "ejemplo"), dest)
    cfg = leer_json(os.path.join(dest, "curso.json"))
    cfg["plantilla"] = a.plantilla
    cfg["nombre"] = a.nombre
    cfg["moodle"]["shortname"] = a.nombre.upper()[:20]
    escribir_json(os.path.join(dest, "curso.json"), cfg)
    print(f"Curso creado en cursos/{a.nombre}. Edita curso.json y actividades/.")


def construir_curso(nombre, solo=None):
    d = carpeta_curso(nombre)
    cfg = leer_json(os.path.join(d, "curso.json"))
    pcfg = config_plantilla(cfg["plantilla"])
    faltan = [rol for rol, v in pcfg.get("colores", {}).items() if "COMPLETAR" in str(v)]
    if faltan:
        error(f"completa los colores {', '.join(faltan)} en plantillas/{cfg['plantilla']}/plantilla.json "
              f"(usa la paleta de FICHA.md; ver docs/04-plantillas.md)")
    h5pkit.configurar_colores(pcfg.get("colores"))
    plantilla = h5pkit.Plantilla(plantilla_extraida(cfg["plantilla"]))
    sys.path[:0] = [d, os.path.join(d, "actividades")]
    out = salida_curso(nombre)
    hechos = []
    for act in cfg.get("actividades", []):
        if solo and act["id"] != solo:
            continue
        g = runpy.run_path(os.path.join(d, act["script"]),
                           init_globals={"PLANTILLA": plantilla, "CURSO_DIR": d, "COLORES": pcfg.get("colores", {})})
        for var in ("TITULO", "SLIDES"):
            if var not in g:
                error(f"{act['script']} debe definir {var}")
        destino_h5p = os.path.join(out, f"{act['id']}.h5p")
        content = h5pkit.construir(plantilla, g["SLIDES"], g["TITULO"], os.path.join(out, act["id"]), destino_h5p)
        info = h5pkit.verificar(content)
        print(f"  {act['id']}: {info['slides']} slides -> {os.path.relpath(destino_h5p, RAIZ)}")
        hechos.append({**act, "archivo": destino_h5p})
    libros = []
    for lib in cfg.get("libros", []):
        if solo and lib["id"] != solo:
            continue
        g = runpy.run_path(os.path.join(d, lib["script"]),
                           init_globals={"CURSO_DIR": d, "COLORES": pcfg.get("colores", {})})
        if "DATOS" not in g:
            error(f"{lib['script']} debe definir DATOS")
        ruta = os.path.join(out, f"{lib['id']}.json")
        escribir_json(ruta, g["DATOS"])
        print(f"  {lib['id']}: libro de {len(g['DATOS']['libro']['capitulos'])} capítulos -> {os.path.relpath(ruta, RAIZ)}")
        libros.append(g["DATOS"])
    return cfg, pcfg, hechos, libros


def cmd_construir(a):
    print(f"Construyendo {a.curso}...")
    construir_curso(a.curso, a.actividad)


def cmd_vista_previa(a):
    base = os.path.join(TRABAJO, "salida")
    print(f"Vista previa en http://127.0.0.1:{a.puerto}/preview/index.html?h=<carpeta>")
    if os.path.isdir(base):
        for curso in sorted(os.listdir(base)):
            for act in sorted(os.listdir(os.path.join(base, curso))):
                if os.path.isdir(os.path.join(base, curso, act)):
                    print(f"  http://127.0.0.1:{a.puerto}/preview/index.html?h=trabajo/salida/{curso}/{act}")
    print("Ctrl+C para detener.")
    subprocess.run([sys.executable, "-m", "http.server", str(a.puerto), "--bind", "127.0.0.1"], cwd=RAIZ)


# ---------------------------------------------------------------- moodle local
def config_moodle():
    if not os.path.exists(CONFIG_LOCAL):
        error("falta configurar el Moodle local: python -I ph5p.py moodle configurar <carpeta server>")
    cfg = leer_json(CONFIG_LOCAL)
    server = cfg["moodle_server"]
    php = os.path.join(server, "php", "php.exe" if os.name == "nt" else "php")
    if not os.path.exists(php):
        php = shutil.which("php") or error("no se encontró php")
    return cfg, server, php


def puerto_abierto(p):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", p)) == 0


def cmd_moodle_configurar(a):
    server = os.path.abspath(a.carpeta)
    if not os.path.isfile(os.path.join(server, "moodle", "version.php")):
        error(f"{server} no parece la carpeta 'server' del paquete de Moodle (falta moodle/version.php)")
    escribir_json(CONFIG_LOCAL, {"moodle_server": server, "url": a.url})
    print(f"Guardado en {CONFIG_LOCAL}")


def cmd_moodle_iniciar(a):
    cfg, server, _ = config_moodle()
    logs = os.path.join(TRABAJO, "logs")
    os.makedirs(logs, exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0
    pids = {}
    for nombre, puerto, cmd in (
            ("mariadb", 3306, [os.path.join(server, "mysql", "bin", "mysqld"), "--defaults-file=mysql/bin/my.ini",
                               "--standalone"]),
            ("apache", 80, [os.path.join(server, "apache", "bin", "httpd")])):
        if puerto_abierto(puerto):
            print(f"  {nombre}: ya hay algo escuchando en el puerto {puerto}")
            continue
        log = open(os.path.join(logs, f"{nombre}.log"), "a")
        p = subprocess.Popen(cmd, cwd=server, stdout=log, stderr=log, creationflags=flags)
        pids[nombre] = p.pid
        print(f"  {nombre}: iniciado (pid {p.pid}, log en trabajo/logs/{nombre}.log)")
    if pids:
        escribir_json(os.path.join(TRABAJO, "moodle_pids.json"), pids)
    print(f"Moodle: {cfg.get('url', 'http://localhost')}/")


def cmd_moodle_detener(a):
    ruta = os.path.join(TRABAJO, "moodle_pids.json")
    if not os.path.exists(ruta):
        error("no hay procesos registrados por 'moodle iniciar'")
    for nombre, pid in leer_json(ruta).items():
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        else:
            subprocess.run(["kill", str(pid)])
        print(f"  {nombre}: detenido")
    os.remove(ruta)


def cmd_moodle_estado(a):
    for nombre, puerto in (("MariaDB", 3306), ("Apache", 80)):
        print(f"  {nombre} (puerto {puerto}): {'activo' if puerto_abierto(puerto) else 'detenido'}")


def cmd_moodle_hvp(a):
    _, server, php = config_moodle()
    destino = os.path.join(server, "moodle", "mod", "hvp")
    if os.path.exists(destino):
        error(f"ya existe {destino}; bórralo si quieres instalar otra versión")
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", a.version, "--recurse-submodules",
                    "--shallow-submodules", "https://github.com/h5p/h5p-moodle-plugin.git", destino], check=True)
    subprocess.run([php, os.path.join("moodle", "admin", "cli", "upgrade.php"), "--non-interactive"],
                   cwd=server, check=True)
    print(f"mod_hvp {a.version} instalado.")


def cmd_moodle_publicar(a):
    cfg_local, server, php = config_moodle()
    if not puerto_abierto(80):
        error("el Moodle local no está corriendo: python -I ph5p.py moodle iniciar")
    print(f"Construyendo {a.curso}...")
    cfg, pcfg, hechos, libros = construir_curso(a.curso)
    m = cfg["moodle"]
    est = Estilo(pcfg.get("colores", {}))
    plan = {
        "curso": {"shortname": m["shortname"], "nombre": m["nombre"], "secciones": len(m["secciones"]) - 1},
        "secciones": [{"numero": s["numero"], "nombre": s["nombre"], "resumen": est.html(s.get("resumen")),
                       "visible": s.get("visible", True)} for s in m["secciones"]],
        "recursos": [{**r, "intro": est.html(r.get("intro")), "contenido": est.html(r.get("contenido"))}
                     for r in m.get("recursos", [])],
        "h5p": [{"archivo": h["archivo"], "seccion": h["seccion"], "nombre": h["nombre_moodle"]} for h in hechos],
        "libros": libros,
        "renombrar_avisos": m.get("renombrar_avisos"),
        "eliminar": m.get("eliminar", []),
        "mover": m.get("mover", []),
        "orden": m.get("orden", {}),
    }
    ruta_plan = os.path.join(salida_curso(a.curso), "plan_moodle.json")
    escribir_json(ruta_plan, plan)
    print("Publicando en el Moodle local...")
    r = subprocess.run([php, os.path.join(RAIZ, "moodle", "aplicar_plan.php"), os.path.join(server, "moodle", "config.php"),
                        ruta_plan], cwd=server)
    sys.exit(r.returncode)


# ---------------------------------------------------------------- argumentos
def main():
    ap = argparse.ArgumentParser(prog="ph5p", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plantilla", help="registrar e inspeccionar plantillas").add_subparsers(dest="sub", required=True)
    x = p.add_parser("agregar"); x.add_argument("archivo"); x.add_argument("nombre"); x.set_defaults(f=cmd_plantilla_agregar)
    x = p.add_parser("ficha"); x.add_argument("nombre"); x.set_defaults(f=cmd_plantilla_ficha)
    x = p.add_parser("lista"); x.set_defaults(f=cmd_plantilla_lista)

    c = sub.add_parser("curso", help="crear cursos").add_subparsers(dest="sub", required=True)
    x = c.add_parser("nuevo"); x.add_argument("nombre"); x.add_argument("--plantilla", required=True)
    x.set_defaults(f=cmd_curso_nuevo)

    x = sub.add_parser("construir", help="generar .h5p y libros"); x.add_argument("curso")
    x.add_argument("--actividad"); x.set_defaults(f=cmd_construir)
    x = sub.add_parser("vista-previa", help="ver los .h5p sin Moodle"); x.add_argument("--puerto", type=int, default=8765)
    x.set_defaults(f=cmd_vista_previa)

    m = sub.add_parser("moodle", help="Moodle local de pruebas").add_subparsers(dest="sub", required=True)
    x = m.add_parser("configurar"); x.add_argument("carpeta"); x.add_argument("--url", default="http://localhost")
    x.set_defaults(f=cmd_moodle_configurar)
    m.add_parser("iniciar").set_defaults(f=cmd_moodle_iniciar)
    m.add_parser("detener").set_defaults(f=cmd_moodle_detener)
    m.add_parser("estado").set_defaults(f=cmd_moodle_estado)
    x = m.add_parser("hvp"); x.add_argument("--version", default="1.28.3"); x.set_defaults(f=cmd_moodle_hvp)
    x = m.add_parser("publicar"); x.add_argument("curso"); x.set_defaults(f=cmd_moodle_publicar)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
