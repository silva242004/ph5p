<?php
// Sube un solo .h5p al Moodle LOCAL (útil para probar una actividad sin publicar todo el curso).
// Uso: php subir_h5p.php <ruta/moodle/config.php> <archivo.h5p> <nombre corto del curso> <sección> "<nombre>"

define('CLI_SCRIPT', true);
if ($argc < 6) {
    fwrite(STDERR, "Uso: php subir_h5p.php <config.php> <archivo.h5p> <curso> <sección> \"<nombre>\"\n");
    exit(1);
}
require($argv[1]);
require_once(__DIR__ . '/lib_ph5p.php');
\core\session\manager::set_user(get_admin());
$course = $DB->get_record('course', ['shortname' => $argv[3]], '*', MUST_EXIST);
$cm = ph5p_subir_h5p($course, realpath($argv[2]), (int) $argv[4], $argv[5]);
echo "Validación OK. Actividad: {$cm->url->out(false)}\n";
