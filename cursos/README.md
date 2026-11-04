# Cursos

Cada curso es una carpeta `cursos/<nombre>/` con un `curso.json` y sus scripts (ver [docs/05-crear-un-curso.md](../docs/05-crear-un-curso.md)).

## Los cursos son privados

Git **ignora** todo lo que está en `cursos/`, salvo este README y `cursos/ejemplo/` (ver `.gitignore`). Tus cursos, maquetas, evaluaciones y textos de profesores quedan **solo en tu equipo** y no se suben al repositorio.

Para respaldar o compartir un curso con tu equipo, usa un repositorio **privado aparte** y clónalo dentro de `cursos/`:

```bash
cd "C:/ruta/a/ph5p/cursos"
```
```bash
git clone <url-de-tu-repo-privado> mi-curso
```

## `ejemplo/`

Curso mínimo con una actividad de 4 slides y una sección de Moodle. Sirve para probar que todo funciona y es la base de `python -I ph5p.py curso nuevo`.
