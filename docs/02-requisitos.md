# 2. Requisitos

| Qué | Versión | Para qué |
|---|---|---|
| Windows | 10 u 11 | Los comandos de Moodle local están probados en Windows. En Linux o macOS el motor de Python funciona igual. |
| Python | **3.12 o superior** | Motor y CLI. No usa paquetes externos (`pip install` no hace falta). |
| Git | cualquiera reciente | Clonar este repo e instalar mod_hvp en el Moodle local |
| Navegador | Chrome, Edge o Firefox | Vista previa y Moodle local |
| Disco | ~2 GB libres | Moodle local (~1 GB descomprimido) y paquetes generados |
| Puertos libres | 80 (Apache) y 3306 (MariaDB) | Moodle local |

Comprueba la versión de Python:

```bash
python --version
```

## Por qué `python -I`

Todos los comandos se ejecutan como `python -I ph5p.py …`. El modo aislado (`-I`) evita que Python cargue código de la carpeta actual o de variables de entorno. Es más seguro cuando trabajas con plantillas descargadas.

## Lo que **no** necesitas

- Cuenta en el Moodle institucional para construir o probar: todo se prueba en local.
- PHP instalado aparte: el paquete de Moodle para Windows trae el suyo, y ph5p lo usa.
- Docker o WSL: el paquete de Moodle para Windows no los necesita.
