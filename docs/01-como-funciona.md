# 1. Cómo funciona

## Qué es un `.h5p`

Un `.h5p` es un ZIP con tres cosas:

| Parte | Qué contiene |
|---|---|
| `h5p.json` | Título, librería principal (`H5P.CoursePresentation`) y dependencias con versión |
| `content/content.json` | **Todo el contenido**: slides, elementos, posiciones, textos HTML, preguntas y textos de interfaz |
| `content/images/…` | Imágenes y audios que usa el contenido |
| `H5P.Algo-x.y/` | Las librerías (código JS/CSS) en la versión exacta en que se exportó |

ph5p edita `content.json` con Python. Nunca toca las librerías: las copia tal cual de la plantilla, así que las versiones coinciden con las del Moodle de donde se descargó.

## Por qué clonar slides

Los slides de una plantilla institucional ya tienen el formato aprobado: colores, tamaños de letra, márgenes y formas decorativas. En vez de crear elementos desde cero, ph5p **copia un slide de la plantilla y cambia solo el texto** (y, si hace falta, la posición o el tamaño de una caja). Así el resultado hereda el formato y cumple la regla institucional de "conservar estructura, distribución y color".

```python
Slide(T.slide(19), 19)                       # copia del slide 19 de la plantilla
    .menu("¿Qué aprenderás?")                # título en el menú de navegación
    .texto(8, titulo("¿Qué ", "aprenderás?"))  # elemento 8 = título (ver FICHA.md)
    .texto(2, parrafos("Texto de la maqueta…"))
    .imagen_pendiente(1, "Imagen con licencia…")
    .quitar(4, 5, 6)                          # botón "Referencias" que no se usa
    .cerrar()
```

Los números (slide 19, elementos 8, 2, 1…) salen de la **ficha** de la plantilla (`plantillas/<nombre>/FICHA.md`), que ph5p genera automáticamente.

## Qué hace `construir`

Por cada actividad de `curso.json`:

1. Descomprime la plantilla en `trabajo/plantillas/<nombre>/` (una sola vez).
2. Carga los colores de `plantilla.json` y ejecuta el script de la actividad, que devuelve `TITULO` y `SLIDES`.
3. Resuelve los botones "ir a" por clave: `ir_a("paso2", …)` → número de slide.
4. Asigna un **`subContentId` nuevo** a cada elemento, porque al clonar slides se repiten, y las plantillas a veces ya traen duplicados. Si se repiten, Moodle mezcla los puntajes.
5. **Traduce la interfaz de H5P al español** ("Your result" → "Tu resultado"…) con los `language/es.json` y `es-mx.json` oficiales de cada librería. Lo que esos archivos no traducen se completa con `TRADUCCION_MANUAL`.
6. Copia solo las imágenes que se usan (el paquete pesa menos) y empaqueta `trabajo/salida/<curso>/<actividad>.h5p`.
7. **Verifica**: IDs únicos, botones "ir a" dentro de rango, que no haya imágenes vacías (se ven negras) y que cada slide tenga título de menú.

Los **libros** (actividad como contenido de Moodle, en lugar de slides) se generan como JSON en `trabajo/salida/<curso>/<id>.json`.

## Qué hace `moodle publicar`

1. Ejecuta `construir`.
2. Convierte los bloques de `curso.json` en HTML con los colores de la plantilla (`nucleo/moodle_html.py`).
3. Escribe `trabajo/salida/<curso>/plan_moodle.json` y lo aplica con `moodle/aplicar_plan.php`, que corre **dentro del Moodle local** con su propio PHP:
   - crea el curso (por nombre corto) y las secciones;
   - crea los recursos nativos (páginas, foros, etiquetas, tareas) si no existen;
   - **valida cada `.h5p` con el validador de mod_hvp** (el mismo del formulario web) y lo sube, reemplazando la versión anterior;
   - crea los libros en **subsecciones**, con capítulos, cuestionario y enlaces internos;
   - mueve y ordena las actividades.
4. Imprime la URL del curso: `http://localhost/course/view.php?id=N`.

Se puede ejecutar todas las veces que haga falta: no duplica recursos y reemplaza los H5P y los libros.

## Dos formatos para una actividad

| | Slides H5P (CoursePresentation) | Libro de Moodle + cuestionario |
|---|---|---|
| Formato institucional | Usa la plantilla tal cual | Solo los colores de la plantilla |
| Interactividad | Alta (botones, preguntas dentro del slide) | Lectura con enlaces; preguntas en un cuestionario nativo |
| Celular en vertical | Texto de unos **5 px** (el slide se encoge entero) | Texto de unos **15 px** |
| Calificación | Puntaje H5P vía xAPI | Cuestionario nativo de Moodle |

Las dos versiones pueden salir del mismo texto: pon el contenido en un módulo de Python, como `contenido_<actividad>.py`, y que lo importen el script de slides y el de libro.
