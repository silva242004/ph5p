# 3. Moodle local de pruebas

Sirve para ver el curso **como lo verá el estudiante** y para validar los `.h5p` con el mismo plugin que producción, sin tocar el Moodle institucional.

## 3.1 Averigua las versiones de producción

El Moodle local debe tener **la misma versión que producción**, no la más nueva. Puedes averiguarla sin ser administrador, con tu sesión iniciada en el Moodle institucional:

| Dato | Dónde verlo |
|---|---|
| Versión de Moodle | Abre `https://<moodle>/UPGRADING.md`: la primera sección `## 4.5.x` es la versión |
| Plugin H5P | Si las URL de las actividades H5P son `/mod/hvp/…`, es **mod_hvp** (no el H5P del núcleo) |
| Versión de mod_hvp | En una actividad H5P, el parámetro `?ver=AAAAMMDDNN` de `/mod/hvp/library/js/h5p.js` (código fuente de la página) |

La plantilla `fiuao-6-215` trae los datos de su Moodle en `plantilla.json` → `moodle_produccion` (Moodle 4.5, mod_hvp 1.28.3 = `2026081300`).

Para pasar del número `?ver=` a la etiqueta de mod_hvp, revisa `version.php` en las etiquetas de [h5p/h5p-moodle-plugin](https://github.com/h5p/h5p-moodle-plugin/tags). Por ejemplo, la etiqueta `1.28.3` tiene `$plugin->version = 2026081300`.

## 3.2 Descarga el paquete oficial para Windows

En [download.moodle.org/windows](https://download.moodle.org/windows/) elige la rama de producción (por ejemplo `MoodleWindowsInstaller-latest-405.zip` para 4.5, unos 241 MB). Trae Apache, MariaDB y PHP; no instala nada en el sistema. Moodle aclara que es solo para pruebas.

Descomprímelo en una carpeta **fuera de este repo**, por ejemplo `C:\Users\<tú>\moodle-local\`. La carpeta importante es `server\`.

## 3.3 Que solo responda en tu equipo

Por defecto Apache escucha en todas las interfaces y cualquiera en tu red podría entrar. Edita:

| Archivo (dentro de `server\`) | Cambio |
|---|---|
| `apache\conf\httpd.conf` | `Listen 80` → `Listen 127.0.0.1:80` |
| `apache\conf\extra\httpd-ssl.conf` | `Listen 443` → `Listen 127.0.0.1:443` |
| `mysql\bin\my.ini` | quita el `#` de `# bind-address="127.0.0.1"` |
| `php\php.ini` (al final del archivo hay un bloque que gana sobre lo de arriba) | `memory_limit = 512M` |

## 3.4 Arranca los servicios

En nuestras pruebas, `Start Moodle.exe` **no levantó** Apache ni MariaDB. Usa ph5p:

```bash
cd "C:/ruta/a/ph5p"
```
```bash
python -I ph5p.py moodle configurar "C:/Users/<tú>/moodle-local/server"
```
```bash
python -I ph5p.py moodle iniciar
```
```bash
python -I ph5p.py moodle estado
```

Los logs quedan en `trabajo/logs/`. Para apagar:

```bash
python -I ph5p.py moodle detener
```

## 3.5 Instala el sitio (una sola vez)

Inventa una contraseña de administrador **solo para este Moodle local** y guárdala fuera del repo, por ejemplo en `moodle-local\CREDENCIALES-LOCAL.txt`. Debe tener mayúscula, minúscula, número y símbolo.

```bash
cd "C:/Users/<tú>/moodle-local/server"
```
```bash
php/php.exe moodle/admin/cli/install.php --non-interactive --agree-license --lang=en --wwwroot=http://localhost --dataroot="C:/Users/<tú>/moodle-local/server/moodledata" --dbtype=mariadb --dbhost=127.0.0.1 --dbname=moodle --dbuser=root --dbpass= --fullname="Moodle local" --shortname=local --adminuser=admin --adminpass="<tu contraseña local>" --adminemail=admin@example.com
```

Referencia: [Administration via command line (Moodle 4.5)](https://docs.moodle.org/405/en/Administration_via_command_line#Installation).

## 3.6 Instala mod_hvp en la versión de producción

```bash
cd "C:/ruta/a/ph5p"
```
```bash
python -I ph5p.py moodle hvp --version 1.28.3
```

Clona el plugin oficial con sus submódulos (`library`, `editor`, `reporting`) en `server\moodle\mod\hvp` y ejecuta la actualización de Moodle.

## 3.7 Publica y abre el curso

```bash
python -I ph5p.py moodle publicar <curso>
```

Al final imprime **dónde se abre el curso**:

```
Curso listo: http://localhost/course/view.php?id=2
```

Entra en `http://localhost/login/index.php` con `admin` y tu contraseña local. También lo encuentras en **My courses** (el nombre sale de `curso.json` → `moodle.nombre`).

Las actividades se abren en `http://localhost/mod/hvp/view.php?id=…` (H5P) y `http://localhost/mod/book/view.php?id=…` (libros). **Cada vez que publicas, los H5P y los libros se recrean con otro `id`**: los enlaces viejos dan "Can't find data record in database". Entra siempre desde la página del curso.

## 3.8 Subsecciones

Los libros se colocan en una **subsección** (`mod_subsection`), que llegó a Moodle en 4.5 pero viene **desactivada**. ph5p la activa en el Moodle local la primera vez que publica un libro. En producción depende de que el administrador la active en *Administración del sitio > Extensiones > Módulos de actividad > Gestionar actividades*.

## 3.9 Pasar a producción

ph5p **no** sube nada al Moodle institucional. El `.h5p` validado está en `trabajo/salida/<curso>/<actividad>.h5p`, y quien tenga rol de edición lo sube desde *Agregar actividad > Contenido interactivo > Subir*.
