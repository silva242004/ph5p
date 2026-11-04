# 7. Referencia

## Comandos

Todos se ejecutan desde la carpeta del repo: `python -I ph5p.py <comando>`.

| Comando | Qué hace |
|---|---|
| `plantilla agregar <archivo.h5p> <nombre>` | Copia la plantilla a `plantillas/<nombre>/`, crea `plantilla.json` si no existe y genera `FICHA.md` |
| `plantilla ficha <nombre>` | Regenera `FICHA.md` |
| `plantilla lista` | Plantillas registradas y si tienen su `.h5p` |
| `curso nuevo <nombre> --plantilla <p>` | Crea `cursos/<nombre>/` a partir de `cursos/ejemplo/` |
| `construir <curso> [--actividad <id>]` | Genera `.h5p` y libros en `trabajo/salida/<curso>/` |
| `vista-previa [--puerto 8765]` | Sirve el repo en `127.0.0.1` y lista las URL de vista previa |
| `moodle configurar <carpeta server> [--url http://localhost]` | Guarda la ruta del Moodle local en `ph5p.local.json` |
| `moodle iniciar` / `detener` / `estado` | MariaDB y Apache del Moodle local |
| `moodle hvp [--version 1.28.3]` | Instala mod_hvp desde el repositorio oficial y actualiza Moodle |
| `moodle publicar <curso>` | `construir` + aplica el plan en el Moodle local e imprime la URL del curso |

Para subir un solo `.h5p` sin publicar todo el curso (útil para comparar con la plantilla original):

```bash
cd "C:/Users/<tú>/moodle-local/server"
```
```bash
php/php.exe "C:/ruta/a/ph5p/moodle/subir_h5p.php" moodle/config.php "<archivo.h5p>" <NOMBRE-CORTO-CURSO> <sección> "<nombre de la actividad>"
```

## h5pkit

Se importa en los scripts de actividad: `from h5pkit import …`.

### Plantilla y slides

| Función | Qué hace |
|---|---|
| `T.slide(n)` | Copia del slide `n` (1-based, como en el editor y en la ficha) |
| `Slide(datos, n)` | Envoltorio para editar un slide clonado; termina siempre con `.cerrar()` |
| `.menu("título")` | Título del slide en el menú de navegación |
| `.texto(i, html)` | Reemplaza el HTML del elemento de texto `i` |
| `.caja(i, x=, y=, w=, h=)` | Mueve o redimensiona el elemento `i` (en % del slide) |
| `.quitar(i, …)` | Quita elementos (por ejemplo, el botón "Referencias" si el slide no cita fuentes) |
| `.imagen_pendiente(i, "descripción")` | Cambia una imagen por un marcador visible "IMAGEN PENDIENTE" |
| `.agregar_texto(html, x, y, w, h)` | Agrega un texto nuevo |
| `.boton(i, "título", x, y, w, h)` | Convierte el texto `i` en botón emergente |
| `.clave("nombre")` | Nombre interno del slide para los botones "ir a" |
| `.ir_a("clave", x, y, w, h)` | Zona clicable invisible que salta al slide con esa clave |
| `.preguntas_unica(i, [(pregunta, [correcta, incorrecta…])], retro)` | Llena un SingleChoiceSet; **la primera respuesta es la correcta** |
| `.cerrar()` | Aplica los cambios y devuelve el slide listo para `SLIDES` |

### HTML con el formato de la plantilla

| Función | Resultado |
|---|---|
| `titulo("Parte negra ", "parte acento", tam="1.375em", tag="h2")` | Título de dos tonos |
| `parrafos("…", ("b", "en negrita"), tam="0.875em")` | Párrafos de cuerpo |
| `destacado("…")` | Texto de recuadro (cursiva + negrita, 1em) |
| `pendiente("qué falta")` | Marca PENDIENTE naranja |
| `lista(["…", "<span>html</span>"], tam=)` | Lista con viñetas |
| `enlace("texto", "https://…", tam=)` | Texto + URL clicable |
| `NEGRO`, `BLANCO`, `AZUL`, `GRANATE`, `FONDO`, `NARANJA` | Colores ya configurados con `plantilla.json` (roles `texto`, `texto_sobre_color`, `acento`, `principal`, `fondo_suave`, `pendiente`) |

### Ensamblado (lo usa el CLI)

| Función | Qué hace |
|---|---|
| `configurar_colores(dict)` | Aplica los colores de `plantilla.json` |
| `construir(plantilla, slides, titulo, carpeta, archivo_h5p)` | Resuelve "ir a", genera IDs nuevos, traduce la interfaz, copia imágenes y empaqueta |
| `verificar(content)` | Revisa IDs, "ir a", imágenes vacías y títulos de menú |
| `traducir_interfaz(content, carpeta_plantilla)` | Interfaz al español con `language/es.json` y `es-mx.json`, más `TRADUCCION_MANUAL` |

## Funciones PHP (`moodle/lib_ph5p.php`)

| Función | Qué hace |
|---|---|
| `ph5p_curso(shortname, nombre, secciones)` | Crea o actualiza el curso y asegura las secciones |
| `ph5p_subir_h5p(curso, archivo, sección, nombre)` | Valida con mod_hvp y sube (reemplaza si existe) |
| `ph5p_recurso(curso, recurso)` | Crea un recurso nativo con el generador de datos de Moodle |
| `ph5p_libro(curso, datos)` | Subsección + libro + cuestionario + enlaces internos |
| `ph5p_cuestionario(curso, sección, datos)` | Cuestionario de opción única con la API de tipos de pregunta |
