# 5. Crear un curso

## 5.1 Crear la carpeta

```bash
cd "C:/ruta/a/ph5p"
```
```bash
python -I ph5p.py curso nuevo mi-curso --plantilla fiuao-6-215
```

Copia `cursos/ejemplo/` a `cursos/mi-curso/`. Esa carpeta es **privada**: git la ignora (ver [cursos/README.md](../cursos/README.md)).

```
cursos/mi-curso/
├── curso.json              # qué actividades hay y cómo se arma en Moodle
├── actividades/            # un script por actividad H5P o libro
│   └── bienvenida.py
├── contenido_*.py          # (opcional) textos compartidos entre la versión slides y la versión libro
└── docs/                   # (opcional) maqueta evaluada, notas, decisiones
```

## 5.2 `curso.json`

```json
{
 "nombre": "mi-curso",
 "plantilla": "fiuao-6-215",
 "actividades": [
  {"id": "actividad0", "script": "actividades/actividad0.py", "nombre_moodle": "Actividad 0: Bienvenida", "seccion": 1}
 ],
 "libros": [
  {"id": "actividad1_libro", "script": "actividades/actividad1_libro.py"}
 ],
 "moodle": {
  "shortname": "MI-CURSO",
  "nombre": "Mi curso (pruebas locales)",
  "renombrar_avisos": "Anuncios",
  "secciones": [
   {"numero": 0, "nombre": "General", "resumen": [{"titulo_curso": "MI CURSO"}]},
   {"numero": 1, "nombre": "Módulo 1: …", "resumen": [{"caja": [{"datos": [["4", "semanas"]]}]}]},
   {"numero": 2, "nombre": "Pruebas", "visible": false}
  ],
  "recursos": [
   {"tipo": "forum", "seccion": 0, "nombre": "Foro de dudas", "opciones": {"type": "general"},
    "intro": [{"parrafos": ["…"]}]}
  ],
  "eliminar": [],
  "mover": [{"nombre": "Algo viejo", "seccion": 2}],
  "orden": {"1": ["Actividad 0: Bienvenida", "…"]}
 }
}
```

| Campo | Para qué |
|---|---|
| `plantilla` | Carpeta de `plantillas/` que usan todas las actividades |
| `actividades[]` | Actividades H5P: `id` (nombre del archivo generado), `script`, `nombre_moodle` y `seccion` |
| `libros[]` | Actividades como libro de Moodle (ver 5.5) |
| `moodle.shortname` | Identifica el curso en el Moodle local: si existe se actualiza, si no se crea |
| `moodle.secciones[]` | Número, nombre, `resumen` (bloques) y `visible`. La 0 es la página de inicio. |
| `moodle.recursos[]` | Recursos nativos: `page`, `forum`, `label`, `assign`, `url`… Se crean solo si no existen con ese nombre. `opciones` pasa campos propios del módulo (por ejemplo `{"teamsubmission": 1}` en una tarea). |
| `moodle.eliminar` | Nombres de actividades a borrar (por ejemplo, un aviso que ya fue reemplazado) |
| `moodle.mover` | Llevar actividades a otra sección (por ejemplo, la sección Pruebas) |
| `moodle.orden` | Orden final de las actividades en cada sección |

Los **bloques** de `resumen`, `intro` y `contenido` se convierten en HTML con los colores de la plantilla:

| Bloque | Resultado |
|---|---|
| `{"titulo_curso": "…"}` | Título del curso, con el color principal |
| `{"titulo": "…"}` | Encabezado de sección |
| `{"parrafos": ["…", "…"]}` | Párrafos |
| `{"datos": [["16", "semanas"], …]}` | Fichas de datos (semanas, créditos…) |
| `{"caja": [bloques]}` | Recuadro con borde principal y fondo suave |
| `{"lista": ["…", {"pendiente": "…"}]}` | Lista con viñetas |
| `{"pendiente": "…"}` | Marca PENDIENTE |
| `{"nota": "…"}` | Nota en cursiva |
| `{"html": "…"}` | HTML tal cual (último recurso) |

## 5.3 Script de actividad (slides H5P)

`ph5p.py construir` ejecuta el script con tres variables ya definidas: `PLANTILLA`, `COLORES` y `CURSO_DIR`. El script debe definir `TITULO` y `SLIDES`.

```python
from h5pkit import Slide, titulo, parrafos, destacado, pendiente, BLANCO

T = PLANTILLA  # noqa: F821

SLIDES = [
    Slide(T.slide(2), 2).menu("Inicio")
    .texto(3, f'<p><span style="font-size:1.625em;color:{BLANCO};">Actividad 1</span></p>')
    .texto(4, f'<h2><span style="font-size:1.5em;color:{BLANCO};">Nombre de la actividad</span></h2>')
    .cerrar(),
    # …
]
TITULO = "Actividad 1"
```

Flujo para escribir cada slide:

1. En la maqueta, identifica el componente (intro, meta, fuente, preguntas…).
2. En `FICHA.md` (y en `plantilla.json` → `disenos`), elige el slide de la plantilla que mejor le queda.
3. Reemplaza cada texto con el tamaño que indica la ficha; quita lo que no se usa; marca lo que falta con `pendiente(...)` o `imagen_pendiente(...)`.
4. Construye y revisa en la vista previa (5.6).

Funciones disponibles: [docs/07-referencia.md](07-referencia.md#h5pkit).

**Navegación entre slides**: dale una clave a un slide con `.clave("paso2")` y crea una zona clicable con `.ir_a("paso2", x, y, ancho, alto)`. ph5p la traduce al número de slide al construir.

## 5.4 Construir y revisar

```bash
python -I ph5p.py construir mi-curso
```
```bash
python -I ph5p.py vista-previa
```

La vista previa muestra los `.h5p` sin Moodle, en `http://127.0.0.1:8765/preview/index.html?h=trabajo/salida/mi-curso/<id>`. Revisa:

- que ningún texto se salga de su caja (ver [Problemas conocidos](08-problemas-conocidos.md#texto-cortado));
- las imágenes pendientes;
- la navegación y las preguntas.

## 5.5 Script de libro (actividad como contenido de Moodle)

Debe definir `DATOS`:

```python
DATOS = {
    "subseccion": "Actividad 1 (prueba): versión como contenido Moodle",  # nombre de la subsección
    "seccion": 1,                                     # sección donde se crea
    "despues_de": "Actividad 1: …",                   # (opcional) actividad tras la cual se ubica
    "libro": {
        "nombre": "Actividad 1 (libro)",
        "intro": "<p>…</p>",
        "capitulos": [
            {"titulo": "Ruta", "html": "<p>…<a href=\"{{capitulo:Paso 1: …}}\">Paso 1</a></p>", "sub": False},
            {"titulo": "Fuente del paso 1", "html": "…", "sub": True},   # subcapítulo
        ],
    },
    "cuestionario": {                                 # (opcional) cuestionario nativo de opción única
        "nombre": "Paso 1: Analiza y responde",
        "retro": "PENDIENTE: retroalimentación del profesor.",
        "preguntas": [{"texto": "¿…?", "correcta": "…", "incorrectas": ["…", "…"]}],
    },
}
```

Enlaces internos que se resuelven al publicar:

- `{{capitulo:<título exacto>}}` → URL de ese capítulo.
- `{{actividad:<nombre exacto>}}` → URL de una actividad del curso (por ejemplo, la tarea de entrega).

Los colores están en `COLORES["principal"]`, `COLORES["acento"]`, etc.

## 5.6 Publicar en el Moodle local

```bash
python -I ph5p.py moodle publicar mi-curso
```

Ver [docs/03-moodle-local.md](03-moodle-local.md#37-publica-y-abre-el-curso). Puedes publicar las veces que quieras.
