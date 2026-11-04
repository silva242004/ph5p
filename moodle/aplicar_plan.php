<?php
// Aplica en el Moodle LOCAL el plan que arma `python -I ph5p.py moodle publicar <curso>`:
// curso, secciones, recursos nativos, actividades H5P, libros en subsecciones, movimientos y orden.
// Se puede ejecutar muchas veces: no duplica recursos y reemplaza los H5P y libros.
//
// Uso: php aplicar_plan.php <ruta/moodle/config.php> <plan_moodle.json>

define('CLI_SCRIPT', true);
require($argv[1]);
require_once(__DIR__ . '/lib_ph5p.php');

$plan = json_decode(file_get_contents($argv[2]), true, 512, JSON_THROW_ON_ERROR);
\core\session\manager::set_user(get_admin());
$c = $plan['curso'];
$course = ph5p_curso($c['shortname'], $c['nombre'], $c['secciones']);

// 1) Secciones
foreach ($plan['secciones'] as $s) {
    course_update_section($course, ph5p_seccion($course->id, $s['numero']),
        ['name' => $s['nombre'], 'summary' => $s['resumen'], 'summaryformat' => FORMAT_HTML, 'visible' => $s['visible'] ? 1 : 0]);
}
echo "Secciones: " . count($plan['secciones']) . "\n";

// 2) Foro de avisos (lo crea Moodle) y recursos que ya no van
if (!empty($plan['renombrar_avisos']) && ($news = $DB->get_record('forum', ['course' => $course->id, 'type' => 'news']))) {
    $DB->set_field('forum', 'name', $plan['renombrar_avisos'], ['id' => $news->id]);
}
foreach ($plan['eliminar'] as $nombre) {
    if ($cm = ph5p_buscar($course->id, $nombre)) {
        course_delete_module($cm->id);
        echo "  eliminado: $nombre\n";
    }
}
rebuild_course_cache($course->id, true);

// 3) Recursos nativos
foreach ($plan['recursos'] as $r) {
    ph5p_recurso($course, $r);
}

// 4) Actividades H5P (se validan y se reemplazan)
foreach ($plan['h5p'] as $h) {
    $cm = ph5p_subir_h5p($course, $h['archivo'], $h['seccion'], $h['nombre']);
    echo "  H5P: {$h['nombre']} -> {$cm->url->out(false)}\n";
}

// 5) Libros en subsecciones
foreach ($plan['libros'] as $libro) {
    ph5p_libro($course, $libro);
}

// 6) Movimientos y orden
foreach ($plan['mover'] as $m) {
    if (($cm = ph5p_buscar($course->id, $m['nombre'])) && (int) $cm->sectionnum !== (int) $m['seccion']) {
        moveto_module($cm, ph5p_seccion($course->id, $m['seccion']));
        echo "  movido a la sección {$m['seccion']}: {$m['nombre']}\n";
    }
}
foreach ($plan['orden'] as $num => $nombres) {
    $sec = ph5p_seccion($course->id, (int) $num);
    foreach ($nombres as $nombre) {     // mover cada una al final, en orden, deja la sección ordenada
        if ($cm = ph5p_buscar($course->id, $nombre)) {
            moveto_module($cm, $sec);
            rebuild_course_cache($course->id, true);
        }
    }
}
rebuild_course_cache($course->id, true);
echo "\nCurso listo: {$CFG->wwwroot}/course/view.php?id={$course->id}\n";
