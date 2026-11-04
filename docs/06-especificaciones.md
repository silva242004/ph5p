# 6. Especificaciones de montaje

Reglas que debe cumplir **todo curso** montado con ph5p. Salen de la experiencia montando cursos reales con la plantilla institucional; antes de entregar, repasa esta lista.

## Rol: montar, no redactar

1. **Quien monta no redacta contenido pedagógico.** El texto viene de la maqueta del profesor; otro equipo produce videos y slides conceptuales.
2. **No inventar.** Lo que la maqueta no trae se marca con `pendiente("…")` (texto naranja visible) o `imagen_pendiente(…)`. Ejemplos: retroalimentación de preguntas, textos de encuentros sincrónicos, nombres de módulos.
3. **Texto literal.** Solo se corrigen **erratas evidentes** (ortografía, siglas mal escritas, símbolos perdidos al copiar). Cada corrección se registra en el script (por ejemplo, en una lista `CAMBIOS_TEXTO`) para reportarla al profesor.
4. **Evaluar la maqueta antes de montar** y entregar al profesor la lista de lo que falta, lo que no cuadra (cifras, temas, enlaces vacíos) y las erratas.

## Formato institucional

5. **Conserva la estructura, la distribución y los colores de la plantilla.** Se puede mover, redimensionar y crear elementos, siempre siguiendo el formato.
6. **Solo colores de `plantilla.json`.** La única excepción es el naranja de PENDIENTE, que desaparece al completar el contenido.
7. **Respeta los tamaños de letra** de la ficha. En la plantilla `fiuao-6-215`: cuerpo `0.875em`, destacado `1em`, subtítulo `1.125em`, títulos `1.25–1.375em`, título grande `2.25em`.
8. **Portada en el formato oficial** de la plantilla. En `fiuao-6-215`: etiqueta blanca de `1.625em` y debajo el título en `h2` blanco de `1.5em`. Si el título es largo, se reduce el tamaño, pero **sin tapar la flecha** dibujada en el fondo.
9. **"¿Cómo navegar?" solo en la Actividad 0**, cuando la plantilla lo indica.
10. **Todo slide lleva título de menú** (`.menu("…")`). Usa el nombre que trae la maqueta; si no lo trae, el del componente ("Fuente", "Ruta").

## Calidad técnica

11. **Ningún texto puede desbordar su caja.** Revisa en la vista previa y en Moodle.
12. **Ninguna imagen vacía** (se ve negra): o una imagen con licencia, o `imagen_pendiente`.
13. **Imágenes con licencia** conocida. No uses imágenes de bancos sin licencia, ni con marca de agua o ID de stock.
14. **Interfaz de H5P en español** (lo hace `construir` automáticamente).
15. **IDs únicos** de subcontenido (lo hace `construir`; `verificar` lo comprueba).
16. **Respeta los límites de la maqueta**: título de actividad ≤ 80 caracteres, título de slide ≤ 35, retroalimentación ≤ 200, descripción de módulo ≤ 255. Si la maqueta los incumple, se reporta.
17. **Piensa en el celular.** Un CoursePresentation se encoge entero y su texto queda ilegible en vertical. Pon poco texto por slide, y para textos largos considera la versión libro.
18. **Valida en el Moodle local** con la misma versión de Moodle y de mod_hvp que producción antes de entregar.

## Seguridad y privacidad

19. **Nunca escribir en el Moodle institucional** desde ph5p. Ahí solo se mira (versiones, plantilla), y el `.h5p` final lo sube quien tenga el rol.
20. **Los cursos son privados**: no se versionan (`cursos/` está en `.gitignore`, salvo el ejemplo).
21. **Credenciales fuera del repo**: la contraseña del Moodle local va en un archivo aparte (por ejemplo `CREDENCIALES-LOCAL.txt` junto al Moodle) y nunca en `curso.json` ni en scripts.
22. **El Moodle local solo escucha en `127.0.0.1`** (ver [Moodle local](03-moodle-local.md#33-que-solo-responda-en-tu-equipo)).
