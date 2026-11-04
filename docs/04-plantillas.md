# 4. Plantillas

Una plantilla es un `.h5p` de tipo **Course Presentation** con los diseños de slide aprobados por la institución o la facultad. ph5p no crea diseños: los **clona** de la plantilla.

## 4.1 Conseguir la plantilla correcta

- Descárgala **del mismo Moodle donde se va a entregar**, con el botón *Descargar* bajo la actividad H5P. Así las librerías del paquete tienen las mismas versiones que el servidor.
- Usa la versión **limpia**. Una copia que alguien ya empezó a llenar arrastra su texto.
- Debe ser `H5P.CoursePresentation`: `plantilla agregar` rechaza otros tipos.

## 4.2 Registrarla

```bash
cd "C:/ruta/a/ph5p"
```
```bash
python -I ph5p.py plantilla agregar "C:/Descargas/mi-plantilla.h5p" mi-facultad-v1
```

Crea `plantillas/mi-facultad-v1/` con:

| Archivo | Qué es |
|---|---|
| `plantilla.h5p` | Copia del archivo original |
| `FICHA.md` | Cada slide con sus elementos numerados (tipo, posición, texto, tamaño de letra) y la **paleta detectada**. Se regenera con `plantilla ficha`; no la edites a mano. |
| `plantilla.json` | Configuración que **completas tú**: colores, reglas y diseños |

## 4.3 Completar `plantilla.json`

```json
{
 "nombre": "Plantilla institucional de …",
 "descripcion": "De dónde se descargó y qué versión es.",
 "colores": {
  "texto": "hsl(0,0%,0%)",
  "texto_sobre_color": "hsl(0, 0%, 100%)",
  "acento": "hsl( 200, 100%, 45% )",
  "principal": "hsl( 350, 75%, 31% )",
  "fondo_suave": "rgb(224, 243, 250)",
  "pendiente": "#FE9800"
 },
 "reglas": ["Conserva la estructura…", "La página ¿Cómo navegar? solo va en la Actividad 0."],
 "disenos": {"2": "Portada…", "19": "Título grande, texto, recuadro…"}
}
```

| Rol de color | Dónde se usa |
|---|---|
| `texto` | Párrafos y parte negra de los títulos |
| `texto_sobre_color` | Texto sobre el color principal (portadas) |
| `acento` | Segunda palabra de los títulos de dos tonos, datos del curso |
| `principal` | Barras, encabezados de Moodle, bordes de recuadros |
| `fondo_suave` | Recuadros destacados y marcadores de imagen |
| `pendiente` | Marca **PENDIENTE**. No es institucional: desaparece cuando llega el contenido. |

**Cómo elegirlos:** en la tabla "Paleta detectada" de `FICHA.md`, los colores con más usos en "texto" y "relleno de forma" son los institucionales. Copia el valor **tal como aparece en la plantilla** (por ejemplo `hsl( 200, 100%, 45% )`), no una aproximación. Solo se permiten colores de esa tabla, más el naranja de PENDIENTE.

Ojo: la paleta no incluye los colores que vienen **dentro de las imágenes** de la plantilla.

## 4.4 Leer la ficha

```
### Slide 19: (sin título de menú)
| i | Tipo         | x | y  | ancho | alto | Contenido |
| 0 | Shape        | 5 | 54 | 58    | 33   | rectangle #E0F3FA |
| 1 | Image        | 71| 0  | 29    | 100  | **vacía: se ve como recuadro negro** |
| 2 | AdvancedText | 7 | 31 | 55    | 21   | Lorem ipsum… (0.875em) |
| 7 | AdvancedText | 8 | 56 | 52    | 30   | Excepteur sint… (0.875em) |
| 8 | AdvancedText | 7 | 14 | 34    | 12   | Lorem Ipsum (2.25em) |
```

- La columna `i` es el índice que usas en `Slide.texto(i, …)`, `Slide.caja(i, …)` o `Slide.quitar(i)`.
- El tamaño entre paréntesis (`0.875em`) es el que debes respetar al reemplazar el texto.
- **Imagen vacía**: si no la reemplazas con `imagen_pendiente(i, …)` o la quitas, se ve como un recuadro negro.
- `[botón emergente]`: texto que se abre al hacer clic (por ejemplo, "Referencias").
- `Ir a slide`: zona clicable. A veces la flecha que se ve está **dibujada en la imagen de fondo**; si mueves la zona, deja de coincidir con la flecha.

## 4.5 Plantillas incluidas

| Nombre | Institución | Notas |
|---|---|---|
| `fiuao-6-215` | Facultad de Ingeniería y Ciencias Básicas, UAO | 34 slides. La interfaz de H5P viene en inglés: ph5p la traduce. |
