"""Convierte los bloques de curso.json en HTML para Moodle (resúmenes de sección, intros, páginas).

Bloques soportados (lista de dicts):
  {"titulo": "Texto"}                          encabezado con el color principal
  {"parrafos": ["...", "..."]}                 párrafos
  {"datos": [["16", "semanas"], ...]}          fichas de datos con el color de acento
  {"pendiente": "qué falta"}                   marca PENDIENTE visible
  {"lista": ["...", {"pendiente": "..."}]}     lista con viñetas (items texto o pendiente)
  {"nota": "texto"}                            nota en cursiva
  {"caja": [bloques...]}                       recuadro con borde del color principal y fondo suave
  {"html": "<p>...</p>"}                       HTML tal cual (último recurso)
"""
import html


def _e(t):
    return html.escape(t, quote=False)


class Estilo:
    def __init__(self, colores):
        self.principal = colores.get("principal", "#8A1428")
        self.acento = colores.get("acento", "#0099E6")
        self.fondo = colores.get("fondo_suave", "#E0F3FA")
        self.pendiente = colores.get("pendiente", "#FE9800")

    def pend(self, t):
        return (f'<span style="color:{self.pendiente};font-weight:bold;">PENDIENTE:</span> '
                f'<span style="color:{self.pendiente};">{_e(t)}</span>')

    def bloque(self, b):
        if "titulo" in b:
            return f'<h4 style="color:{self.principal};margin:12px 0 6px;">{_e(b["titulo"])}</h4>'
        if "titulo_curso" in b:
            return f'<h3 style="color:{self.principal};margin-top:0;">{_e(b["titulo_curso"])}</h3>'
        if "parrafos" in b:
            return "".join(f"<p>{_e(p)}</p>" for p in b["parrafos"])
        if "datos" in b:
            return "<p>" + "".join(
                f'<span style="display:inline-block;margin:2px 6px 2px 0;padding:4px 12px;border:1px solid '
                f'{self.acento};border-radius:14px;background:#fff;"><strong style="color:{self.acento};">'
                f'{_e(str(v))}</strong> {_e(et)}</span>' for v, et in b["datos"]) + "</p>"
        if "pendiente" in b:
            return f"<p>{self.pend(b['pendiente'])}</p>"
        if "lista" in b:
            items = "".join(f"<li>{self.pend(i['pendiente']) if isinstance(i, dict) else _e(i)}</li>" for i in b["lista"])
            return f"<ul>{items}</ul>"
        if "nota" in b:
            return f"<p><em>{_e(b['nota'])}</em></p>"
        if "caja" in b:
            return (f'<div style="border-left:6px solid {self.principal};background:{self.fondo};padding:12px 16px;'
                    f'border-radius:4px;margin-bottom:12px;">{self.html(b["caja"])}</div>')
        if "html" in b:
            return b["html"]
        raise ValueError(f"bloque desconocido: {b}")

    def html(self, bloques):
        if isinstance(bloques, str):
            return bloques
        return "".join(self.bloque(b) for b in bloques or [])
