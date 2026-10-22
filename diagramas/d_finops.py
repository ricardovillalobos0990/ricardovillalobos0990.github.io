# -*- coding: utf-8 -*-
"""Diagrama: captura automatizada de costos (FinOps)."""
import os

from drawio import Diagram, INK, MUTED  # noqa: F401
from comun import C_FLUJO, C_API, C_FALLA, C_OK, GCP_BIGQUERY  # noqa: F401


def _etiqueta(d, eid, pos=0.0, perp=0, dx=0, dy=0):
    """Ubica la etiqueta de una arista ya creada.
    pos: posición a lo largo del trazo (-1 = origen, 0 = centro, 1 = destino);
    perp: desplazamiento perpendicular; dx/dy: desplazamiento absoluto en px."""
    viejo = '<mxGeometry relative="1" as="geometry">'
    nuevo = '<mxGeometry x="%.3f" y="%d" relative="1" as="geometry">' % (pos, perp)
    if dx or dy:
        nuevo += '<mxPoint x="%d" y="%d" as="offset"/>' % (dx, dy)
    for k, c in enumerate(d.cells):
        if c.startswith('<mxCell id="%s" ' % eid):
            d.cells[k] = c.replace(viejo, nuevo, 1)
            return
    raise KeyError(eid)


def _lados(sx, sy, tx, ty):
    """Restricciones de salida y entrada (fracciones del ancho y alto de cada celda)."""
    return ("exitX=%s;exitY=%s;exitDx=0;exitDy=0;entryX=%s;entryY=%s;entryDx=0;entryDy=0;"
            % (sx, sy, tx, ty))


# =============================================================================
# FinOps: flujo de captura automatizada de costos
# =============================================================================
def generar(aqui):
    d = Diagram("Captura automatizada de costos", 1250, 1165)
    d.title(30, 24, 1190, "Captura automatizada de costos en AWS y Google Cloud",
            "Dos capturas por mes, escritura idempotente y falla cerrada: una captura rota deja la celda vacía, nunca un cero.")

    # Rejilla del orquestador: tres columnas de 240 px con canales de 40 px
    C1, C2, C3, CW = 380, 660, 940, 240
    M1, M2, M3 = C1 + CW // 2, C2 + CW // 2, C3 + CW // 2      # centros: 500, 780, 1060
    YA, HA = 380, 86       # fila AWS (Cost Explorer y su mapeo)
    YG, HG = 585, 86       # fila GCP (BigQuery y su mapeo)
    CA = YA + HA // 2      # centro de la fila AWS
    YQ = YG + 60           # altura de la consulta a BigQuery (debajo de la entrada del periodo)

    # ---------------------------------------------------------- fuentes
    d.group("cloud", 30, 110, 240, 400, "AWS · organización multicuenta")
    d.aws(150, 176, "organizations", "mgmt", "Cuenta de gestión", "facturación consolidada", size=52, lw=200)
    d.box(45, 288, 210, 76, "<b>Identidad dedicada</b><br>de solo lectura<br>de costos",
          fill="#FFF7E6", stroke="#D97706", size=10)
    ce = d.aws(150, CA - 26, "cost_explorer", "cost", "Cost Explorer API", "GetCostAndUsage", size=52, lw=200)

    d.zone(30, 548, 240, 302, "Google Cloud · proyecto de facturación", fill="#F3F7FE", stroke="#5184F3", color="#1A56DB")
    bq = d.shape(150, YQ - 26, GCP_BIGQUERY, "BigQuery", "export de facturación", w=60, h=52, lw=200)
    d.box(45, 732, 210, 96, "<b>Lectura a nivel de tabla</b><br>solo la tabla del export<br>y permiso para ejecutar<br>consultas acotadas",
          fill="#FFF7E6", stroke="#D97706", size=10)

    # ------------------------------------------------------- orquestador
    d.zone(345, 110, 875, 710, "Orquestador de flujos", fill="#F7F9FC", stroke="#9AA7B8")
    t1 = d.box(C1, 160, CW, 56, "<b>Programado diario</b><br>actúa solo el último día", fill="#FFFFFF", size=10)
    t2 = d.box(C2, 160, CW, 56, "<b>Programado día 3</b><br>captura el valor real", fill="#FFFFFF", size=10)
    t3 = d.box(C3, 160, CW, 56, "<b>Manual</b><br>pruebas y recuperación", fill="#FFFFFF", size=10, dashed=True)
    p = d.box(C2, 260, CW, 62, "<b>Periodo</b><br>mes y tipo de captura", fill="#E8F1FB", stroke="#147EBA", size=11)
    BAJA = _lados(0.5, 1, 0.5, 0)
    d.edge(t1, p, color=C_FLUJO, width=1, points=[(M1, 238), (M2, 238)], extra=BAJA)
    d.edge(t2, p, color=C_FLUJO, width=1, extra=BAJA)
    d.edge(t3, p, color=C_FLUJO, width=1, points=[(M3, 238), (M2, 238)], extra=BAJA)

    a = d.box(C1, YA, CW, HA, "<b>Cost Explorer</b><br>costo diario por cuenta vinculada<br>+ marketplace por servicio", size=10)
    ma = d.box(C2, YA, CW, HA, "<b>Mapeo AWS → filas</b><br>+ estimador de cierre<br>(mayor entre cargado<br>y promedio 7 días)", size=10)
    g = d.box(C1, YG, CW, HG, "<b>BigQuery</b><br>costo por proyecto y<br>mes de factura, neto de créditos", size=10)
    mg = d.box(C2, YG, CW, HG, "<b>Mapeo GCP → filas</b><br>cuentas sin mapa →<br>«no identificados»", size=10)
    YW = (CA + YG + HG // 2) // 2 - 40
    w = d.box(C3, YW, CW, 80, "<b>Escritura idempotente</b><br>por clave de fila y columna", fill="#ECFDF3", stroke=C_OK, size=10)
    f = d.box(C3, 632, CW, 72, "<b>Fuente sin datos</b><br>no se escribe nada:<br>celda vacía, nunca un cero",
              fill="#FDECEA", stroke=C_FALLA, color="#7F1D1D", size=10, dashed=True)
    v = d.box(C1, 718, C2 + CW - C1, 72, "<b>Informe de variaciones</b> · solo con el valor real<br>mes contra promedio de 3 meses, ajustado por días;<br>5 que más suben y 5 que más bajan",
              fill="#FFFFFF", size=10)

    # periodo → lecturas (la de GCP baja por el canal izquierdo del orquestador)
    d.edge(p, a, color=C_FLUJO, points=[(M2, 352), (M1, 352)], extra=BAJA)
    d.edge(p, g, color=C_FLUJO, points=[(M2, 352), (360, 352), (360, YG + 26)],
           extra=_lados(0.5, 1, 0, round(26 / HG, 3)))
    d.edge(a, ma, color=C_FLUJO, extra=_lados(1, 0.5, 0, 0.5))
    d.edge(g, mg, color=C_FLUJO, extra=_lados(1, 0.5, 0, 0.5))
    d.edge(ma, w, color=C_FLUJO, points=[(920, CA), (920, YW + 40)], extra=_lados(1, 0.5, 0, 0.5))
    d.edge(mg, w, color=C_FLUJO, points=[(920, YG + HG // 2), (920, YW + 40)], extra=_lados(1, 0.5, 0, 0.5))
    d.edge(w, f, "si la fuente falla", color=C_FALLA, dashed=True, extra=BAJA)
    d.edge(mg, v, color=C_FLUJO, width=1, dashed=True,
           extra=_lados(0.5, 1, round((M2 - C1) / (C2 + CW - C1), 3), 0))

    # llamadas de API a las fuentes (rectas, con la etiqueta en el canal entre fuentes y orquestador)
    e1 = d.edge(a, ce, "lectura", color=C_API, dashed=True, width=1, extra=_lados(0, 0.5, 1, 0.5))
    _etiqueta(d, e1, pos=-0.28)
    e2 = d.edge(g, bq, "consulta", color=C_API, dashed=True, width=1,
                extra=_lados(0, round((YQ - YG) / HG, 3), 1, 0.5))
    _etiqueta(d, e2, pos=-0.27)

    # ---------------------------------------------------------- destinos
    d.zone(920, 860, 295, 280, "Hojas de cálculo", fill="#F4FBF6", stroke="#34A853", color="#137333")
    hm = d.box(C3, 907, CW, 70, "<b>Hoja de máquina</b><br>solo la escribe el flujo", fill="#FFFFFF", stroke="#34A853", size=10)
    hf = d.box(C3, 1037, CW, 80, "<b>Hoja de finanzas</b><br>la editan personas e importa<br>la hoja de máquina por fórmula",
               fill="#FFFFFF", stroke="#34A853", size=10)
    d.edge(w, hm, color=C_FLUJO, points=[(1200, YW + 40), (1200, 942)], extra=_lados(1, 0.5, 1, 0.5))
    d.edge(hm, hf, "fórmula de importación", color="#137333", extra=BAJA)

    ch = d.box(520, 907, 240, 64, "<b>Canal del equipo</b><br>informe mensual de variaciones", fill="#FFFFFF", size=10)
    d.edge(v, ch, color=C_FLUJO, extra=BAJA)

    d.legend(30, 885, [(C_FLUJO, "flujo de datos", False), (C_API, "lectura de la fuente de costos", True),
                       (C_FALLA, "falla cerrada", True)], w=300)
    d.save(os.path.join(aqui, "finops-captura.drawio"))
