# 8. Problemas conocidos

## Imagen negra

Un `H5P.Image` sin archivo no queda invisible: se dibuja como un **recuadro negro**. Usa `imagen_pendiente(i, …)` o `quitar(i)`. `verificar` detiene la construcción si queda alguna.

## Texto cortado

Las cajas tienen posición y tamaño en % del slide; si el texto no cabe, **se corta sin aviso**. Revisa en la vista previa y, en la consola del navegador, compara `scrollHeight` contra `clientHeight` de cada `.h5p-element`. Soluciones, en este orden: agrandar la caja (`caja`), mover lo que está debajo, dividir en dos slides o usar un botón emergente (`boton`). Si un `h2` de dos líneas se corta, dale más alto a la caja: los encabezados tienen márgenes propios.

## La flecha de la portada queda tapada

En `fiuao-6-215` la flecha de la portada está **dibujada en la imagen de fondo**, y el elemento "ir al siguiente" es solo una zona invisible encima (y ≈ 61 %). No muevas esa zona: el título debe terminar antes del 60 %.

## "Ampliar" (pantalla completa) muestra el contenido gigante y cortado

En el **navegador integrado de algunas apps** (por ejemplo, el panel de navegador de un editor), el botón de pantalla completa de H5P no logra entrar en pantalla completa: el iframe de mod_hvp queda en 150 px de alto y el contenido se dibuja a tamaño de pantalla. Pasa igual con la **plantilla original sin modificar**, así que no lo causa ph5p. Prueba la pantalla completa en Chrome, Edge o Firefox normales.

## "Can't find data record in database" al abrir un libro o un H5P

Cada `moodle publicar` **recrea** los H5P y los libros, que reciben otro `id`. Los enlaces guardados de antes ya no existen. Entra desde la página del curso.

## La interfaz de H5P sale en inglés

Los textos de interfaz ("Your result", "Retry") se guardan dentro del contenido con el idioma en que se creó la plantilla. `construir` los traduce. Si aparece uno nuevo en inglés, agrégalo a `TRADUCCION_MANUAL` en `nucleo/h5pkit.py`.

## Texto ilegible en celular

Un CoursePresentation escala el slide completo: con 375 px de ancho el texto de cuerpo queda en unos 5 px. Hay que pedir pantalla completa u orientación horizontal, poner poco texto por slide o usar la versión libro.

## Subsecciones desactivadas

En Moodle 4.5 `mod_subsection` viene desactivado. ph5p lo activa solo en el Moodle local; en producción hace falta un administrador.

## `Start Moodle.exe` no arranca los servicios

Usa `python -I ph5p.py moodle iniciar`.

## El nombre de la actividad H5P no es el que pedí

mod_hvp toma el nombre de `metadata->title`, no de `name`. `ph5p_subir_h5p` asigna los dos.

## El generador de preguntas de Moodle falla con `PHPUnit\Framework\TestCase`

`core_question`→`create_question` depende de PHPUnit. ph5p crea las preguntas con `question_bank::get_qtype(...)->save_question()`.

## Los cambios no se ven en Moodle

Moodle guarda caché. ph5p reconstruye la caché del curso al publicar; si aun así no ves los cambios, recarga con Ctrl+F5.
