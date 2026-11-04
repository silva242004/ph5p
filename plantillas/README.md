# Plantillas

Plantillas H5P (Course Presentation) **institucionales o generales**. Cada carpeta tiene:

| Archivo | Qué es |
|---|---|
| `plantilla.h5p` | El paquete original, descargado del Moodle donde se va a entregar |
| `plantilla.json` | Colores por rol, reglas de uso, diseños y datos del Moodle de producción |
| `FICHA.md` | Generada: slides, elementos numerados y paleta. No editar a mano. |

Para agregar una: `python -I ph5p.py plantilla agregar <archivo.h5p> <nombre>`. Guía completa en [docs/04-plantillas.md](../docs/04-plantillas.md).

Aquí **no** van plantillas con contenido de un curso: usa siempre la versión limpia.
