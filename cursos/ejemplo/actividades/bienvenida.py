"""Actividad de ejemplo: 4 slides clonados de la plantilla fiuao-6-215.

Contrato de un script de actividad (lo ejecuta ph5p.py construir <curso>):
  - Recibe PLANTILLA (la plantilla de curso.json ya descomprimida), COLORES y CURSO_DIR.
  - Debe definir TITULO (título del paquete) y SLIDES (lista de slides ya cerrados con .cerrar()).

Los números de slide y de elemento salen de plantillas/fiuao-6-215/FICHA.md.
Si usas otra plantilla, cambia los números según su ficha.
"""
from h5pkit import Slide, titulo, parrafos, destacado, pendiente, BLANCO

T = PLANTILLA  # noqa: F821

SLIDES = [
    # Slide 2 de la plantilla: portada. Elemento 3 = etiqueta, 4 = título.
    Slide(T.slide(2), 2).menu("Inicio")
    .texto(3, f'<p><span style="font-size:1.625em;color:{BLANCO};">Actividad de ejemplo</span></p>')
    .texto(4, f'<h2><span style="font-size:1.5em;color:{BLANCO};">Mi primera actividad con ph5p</span></h2>')
    .cerrar(),

    # Slide 19: título grande (8), texto (2), recuadro destacado (0 forma, 7 texto), imagen a la derecha (1).
    Slide(T.slide(19), 19).menu("¿Qué aprenderás?")
    .texto(8, titulo("¿Qué ", "aprenderás?", tam="2.25em", tag="p"))
    .texto(2, parrafos("Este texto lo escribe el profesor en la maqueta. ph5p solo lo monta en la plantilla."))
    .texto(7, destacado("Meta: entender cómo se arma una actividad con ph5p."))
    .imagen_pendiente(1, "Imagen con licencia que se elige al montar.")
    .quitar(4, 5, 6)            # botón "Referencias": este slide no cita fuentes
    .cerrar(),

    # Slide 25: Analiza y responde (SingleChoiceSet en el elemento 3). La primera respuesta es la correcta.
    Slide(T.slide(25), 25).menu("Analiza y responde")
    .texto(0, titulo("Analiza y ", "responde", tam="1.375em"))
    .texto(1, parrafos("Selecciona la respuesta correcta."))
    .preguntas_unica(3, [
        ("¿Qué formato tiene un archivo .h5p?", ["Un ZIP con h5p.json y content/", "Un PDF", "Una imagen"]),
    ], retro="PENDIENTE: retroalimentación del profesor.")
    .cerrar(),

    # Slide 31: cierre. Elemento 5 = texto, 3 = frase final.
    Slide(T.slide(31), 31).menu("Cierre")
    .texto(5, pendiente("mensaje de cierre del profesor."))
    .cerrar(),
]
TITULO = "Actividad de ejemplo"
