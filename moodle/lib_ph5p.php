<?php
// Funciones de ph5p para un Moodle LOCAL de pruebas (4.5 + mod_hvp). No usar contra producción.
// Las incluye aplicar_plan.php y subir_h5p.php después de cargar config.php.

defined('MOODLE_INTERNAL') || die();
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->dirroot . '/mod/hvp/lib.php');
require_once($CFG->dirroot . '/mod/quiz/locallib.php');
require_once($CFG->dirroot . '/lib/phpunit/classes/util.php');   // generador de datos (funciona sin PHPUnit)

function ph5p_generador() {
    static $gen = null;
    return $gen ??= phpunit_util::get_data_generator();
}

function ph5p_buscar(int $courseid, string $nombre): ?cm_info {
    foreach (get_fast_modinfo($courseid)->get_cms() as $cm) {
        if ($cm->name === $nombre) {
            return $cm;
        }
    }
    return null;
}

function ph5p_seccion(int $courseid, int $num): stdClass {
    global $DB;
    return $DB->get_record('course_sections', ['course' => $courseid, 'section' => $num], '*', MUST_EXIST);
}

/** Crea el curso si no existe (por nombre corto) y asegura el número de secciones. */
function ph5p_curso(string $shortname, string $fullname, int $secciones): stdClass {
    global $DB;
    $course = $DB->get_record('course', ['shortname' => $shortname]);
    if (!$course) {
        $course = create_course((object) [
            'fullname' => $fullname, 'shortname' => $shortname, 'format' => 'topics', 'numsections' => $secciones,
            'category' => $DB->get_field_select('course_categories', 'MIN(id)', '1=1'),
        ]);
        echo "Curso creado: id={$course->id}\n";
    } else if ($course->fullname !== $fullname) {
        $DB->set_field('course', 'fullname', $fullname, ['id' => $course->id]);
    }
    course_create_sections_if_missing($course, range(0, $secciones));
    return get_course($course->id);
}

/** Valida un .h5p con el mismo validador del formulario de mod_hvp y lo sube (reemplaza si ya existe). */
function ph5p_subir_h5p(stdClass $course, string $archivo, int $seccion, string $nombre): cm_info {
    global $CFG, $DB;
    $interface = \mod_hvp\framework::instance('interface');
    $path = $CFG->tempdir . uniqid('/hvp-');
    $interface->getUploadedH5pFolderPath($path);
    $path .= '.h5p';
    $interface->getUploadedH5pPath($path);
    copy($archivo, $path);

    $validator = \mod_hvp\framework::instance('validator');
    if (!$validator->isValidPackage()) {
        $msgs = array_map(fn($m) => is_object($m) ? $m->message : $m, \mod_hvp\framework::messages('error'));
        throw new moodle_exception('generalexceptionmessage', 'error', '', "Paquete inválido $archivo: " . implode(' | ', $msgs));
    }
    foreach ($validator->h5pC->mainJsonData['preloadedDependencies'] as $dep) {
        if ($dep['machineName'] === $validator->h5pC->mainJsonData['mainLibrary'] && $validator->h5pF->libraryHasUpgrade($dep)) {
            throw new moodle_exception('generalexceptionmessage', 'error', '',
                'El sitio tiene una versión más nueva de la librería principal (olduploadoldcontent)');
        }
    }
    foreach (get_fast_modinfo($course->id)->get_instances_of('hvp') as $viejo) {
        if ($viejo->name === $nombre && (int) $viejo->sectionnum === $seccion) {
            course_delete_module($viejo->id);
        }
    }
    $core = \mod_hvp\framework::instance();
    $opciones = [H5PCore::DISPLAY_OPTION_FRAME => 1, H5PCore::DISPLAY_OPTION_DOWNLOAD => 1,
        H5PCore::DISPLAY_OPTION_EMBED => 1, H5PCore::DISPLAY_OPTION_COPYRIGHT => 1];
    $mi = add_moduleinfo((object) [
        'modulename' => 'hvp', 'module' => $DB->get_field('modules', 'id', ['name' => 'hvp']),
        'course' => $course->id, 'section' => $seccion, 'visible' => 1, 'h5paction' => 'upload',
        // El nombre de la actividad sale de metadata->title, no de name.
        'metadata' => (object) ['title' => $nombre], 'name' => $nombre,
        'introeditor' => ['text' => '', 'format' => FORMAT_HTML, 'itemid' => 0],
        'maximumgrade' => 10, 'grade' => 10,
        'disable' => $core->getStorableDisplayOptions($opciones, 0),
    ], $course);
    rebuild_course_cache($course->id, true);
    return ph5p_buscar($course->id, $nombre);
}

/** Crea un recurso nativo (page, forum, label, assign, url...) si no existe uno con ese nombre. */
function ph5p_recurso(stdClass $course, array $r): void {
    if (ph5p_buscar($course->id, $r['nombre'])) {
        return;
    }
    $rec = ['course' => $course->id, 'section' => $r['seccion'], 'name' => $r['nombre'],
        'intro' => $r['intro'] ?? '', 'introformat' => FORMAT_HTML, 'visible' => !empty($r['visible']) || !isset($r['visible']) ? 1 : 0];
    if ($r['tipo'] === 'page') {
        $rec += ['content' => $r['contenido'] ?? '', 'contentformat' => FORMAT_HTML];
    }
    ph5p_generador()->create_module($r['tipo'], $rec + ($r['opciones'] ?? []));
    rebuild_course_cache($course->id, true);
    echo "  creado ({$r['tipo']}): {$r['nombre']}\n";
}

/**
 * Libro + cuestionario dentro de una subsección (mod_subsection, Moodle 4.5+).
 * $d: salida de un script de libro (ver docs/05-crear-un-curso.md). Se recrea desde cero cada vez.
 */
function ph5p_libro(stdClass $course, array $d): void {
    global $DB;
    $gen = ph5p_generador();
    if (!$DB->get_field('modules', 'visible', ['name' => 'subsection'])) {
        \core\plugininfo\mod::enable_plugin('subsection', 1);   // viene desactivado en 4.5
        echo "  subsecciones activadas (solo en este Moodle local)\n";
    }
    if ($vieja = ph5p_buscar($course->id, $d['subseccion'])) {
        course_delete_module($vieja->id);
        rebuild_course_cache($course->id, true);
    }
    $sub = $gen->create_module('subsection', ['course' => $course->id, 'section' => $d['seccion'] ?? 1, 'name' => $d['subseccion']]);
    $sec = $DB->get_record('course_sections', ['component' => 'mod_subsection', 'itemid' => $sub->id], '*', MUST_EXIST)->section;

    $l = $d['libro'];
    $libro = $gen->create_module('book', ['course' => $course->id, 'section' => $sec, 'name' => $l['nombre'],
        'intro' => $l['intro'] ?? '', 'introformat' => FORMAT_HTML, 'numbering' => 1, 'navstyle' => 2]);
    $caps = [];
    foreach ($l['capitulos'] as $i => $c) {
        $ch = $gen->get_plugin_generator('mod_book')->create_chapter(['bookid' => $libro->id, 'title' => $c['titulo'],
            'content' => $c['html'], 'contentformat' => FORMAT_HTML, 'pagenum' => $i + 1, 'subchapter' => $c['sub'] ? 1 : 0]);
        $caps[$c['titulo']] = $ch->id;
    }

    if (!empty($d['cuestionario'])) {
        ph5p_cuestionario($course, $sec, $d['cuestionario']);
    }

    // Enlaces internos: {{capitulo:<título>}} y {{actividad:<nombre>}}
    rebuild_course_cache($course->id, true);
    $cmlibro = get_coursemodule_from_instance('book', $libro->id, $course->id, false, MUST_EXIST);
    $resolver = function (array $m) use ($caps, $cmlibro, $course): string {
        if ($m[1] === 'capitulo') {
            $id = $caps[$m[2]] ?? throw new coding_exception("capítulo inexistente: {$m[2]}");
            return (new moodle_url('/mod/book/view.php', ['id' => $cmlibro->id, 'chapterid' => $id]))->out(false);
        }
        $cm = ph5p_buscar($course->id, $m[2]) ?? throw new coding_exception("actividad inexistente: {$m[2]}");
        return $cm->url->out(false);
    };
    foreach ($caps as $id) {
        $txt = $DB->get_field('book_chapters', 'content', ['id' => $id]);
        $nuevo = preg_replace_callback('/\{\{(capitulo|actividad):([^}]+)\}\}/u', $resolver, $txt);
        if ($nuevo !== $txt) {
            $DB->set_field('book_chapters', 'content', $nuevo, ['id' => $id]);
        }
    }
    if (!empty($d['despues_de']) && ($ref = ph5p_buscar($course->id, $d['despues_de']))) {
        // moveto_module($cm, $section, $beforeid): se ubica antes del siguiente al de referencia.
        $mods = array_values(get_fast_modinfo($course->id)->get_sections()[$ref->sectionnum] ?? []);
        $antes = $mods[array_search($ref->id, $mods) + 1] ?? null;
        $cmsub = ph5p_buscar($course->id, $d['subseccion']);
        if ($antes != $cmsub->id) {          // si ya está justo después, no se mueve
            moveto_module($cmsub, ph5p_seccion($course->id, $ref->sectionnum), $antes);
        }
    }
    rebuild_course_cache($course->id, true);
    echo "  libro: {$l['nombre']} (" . count($caps) . " capítulos) en la subsección «{$d['subseccion']}»\n";
}

/** Cuestionario de opción única con la API del tipo de pregunta (el generador de preguntas exige PHPUnit). */
function ph5p_cuestionario(stdClass $course, int $seccion, array $q): void {
    global $DB;
    $quiz = ph5p_generador()->create_module('quiz', ['course' => $course->id, 'section' => $seccion, 'name' => $q['nombre'],
        'intro' => $q['intro'] ?? '', 'introformat' => FORMAT_HTML, 'grade' => $q['nota'] ?? 10, 'questionsperpage' => 1]);
    $ctx = context_course::instance($course->id);
    $nombrecat = 'ph5p: ' . $q['nombre'];
    if ($cat = $DB->get_record('question_categories', ['contextid' => $ctx->id, 'name' => $nombrecat])) {
        $viejas = $DB->get_fieldset_sql('SELECT q.id FROM {question} q
            JOIN {question_versions} v ON v.questionid = q.id
            JOIN {question_bank_entries} e ON e.id = v.questionbankentryid
            WHERE e.questioncategoryid = ?', [$cat->id]);
        foreach ($viejas as $qid) {
            question_delete_question($qid);
        }
    } else {
        $cat = ph5p_generador()->get_plugin_generator('core_question')->create_question_category(
            ['contextid' => $ctx->id, 'name' => $nombrecat]);
    }
    $qtype = question_bank::get_qtype('multichoice');
    $vacio = ['text' => '', 'format' => FORMAT_HTML];
    foreach ($q['preguntas'] as $k => $p) {
        $op = array_merge([$p['correcta']], $p['incorrectas']);
        $form = (object) [
            'category' => "{$cat->id},{$ctx->id}", 'name' => $q['nombre'] . ' ' . ($k + 1),
            'questiontext' => ['text' => '<p>' . s($p['texto']) . '</p>', 'format' => FORMAT_HTML],
            'generalfeedback' => ['text' => '<p>' . s($q['retro'] ?? '') . '</p>', 'format' => FORMAT_HTML],
            'defaultmark' => 1, 'penalty' => 0.3333333, 'status' => 'ready', 'single' => 1, 'shuffleanswers' => 1,
            'answernumbering' => 'abc', 'showstandardinstruction' => 0, 'noanswers' => count($op),
            'answer' => array_map(fn($t) => ['text' => $t, 'format' => FORMAT_PLAIN], $op),
            'fraction' => array_merge(['1.0'], array_fill(0, count($op) - 1, '0.0')),
            'feedback' => array_fill(0, count($op), $vacio),
            'correctfeedback' => $vacio, 'partiallycorrectfeedback' => $vacio, 'incorrectfeedback' => $vacio,
            'shownumcorrect' => 0,
        ];
        $preg = $qtype->save_question((object) ['category' => $cat->id, 'qtype' => 'multichoice', 'contextid' => $ctx->id], $form);
        quiz_add_quiz_question($preg->id, $quiz, $k + 1);
    }
    \mod_quiz\quiz_settings::create($quiz->id)->get_grade_calculator()->recompute_quiz_sumgrades();
}
