# -*- coding: utf-8 -*-
"""Diagrama: pipeline de observabilidad con OpenTelemetry."""
import os

from drawio import Diagram, INK, MUTED  # noqa: F401
from comun import C_FLUJO, C_API, C_FALLA, C_OK, GCP_BIGQUERY  # noqa: F401


def _pos_rotulo(d, x):
    """Coloca el rótulo de la última flecha en la posición relativa x del trazo (-1 origen, 1 destino)."""
    d.cells[-1] = d.cells[-1].replace('<mxGeometry relative="1" as="geometry">',
                                      '<mxGeometry x="%s" relative="1" as="geometry">' % x, 1)


# =============================================================================
# Plataforma: pipeline de observabilidad con OpenTelemetry
# =============================================================================
def generar(aqui):
    d = Diagram("Pipeline de observabilidad", 1250, 1270)
    d.title(30, 20, 1190, "Pipeline de observabilidad con OpenTelemetry · olas 0 y 1",
            "Endpoint OTLP estable como contrato: los productores no se redespliegan entre olas. Redacción de datos personales que falla cerrada.")
    C_ROJO = "#C0392B"
    C_S3 = "#7AA116"

    # --- Productores (franja superior)
    d.zone(30, 96, 1190, 116, "Productores", fill="#F7F9FC", stroke="#9AA7B8")
    p2 = d.box(180, 132, 230, 62, "<b>Métricas del clúster</b><br>kubelet · kube-state", size=10)

    # --- Namespace de observabilidad
    d.zone(30, 248, 1190, 672, "Namespace de observabilidad · NetworkPolicy de denegación por defecto",
           fill="#F4FBF6", stroke="#16A34A", color="#15803D", align="right")
    svc = d.box(200, 315, 190, 90, "<b>Service OTLP estable</b><br>:4317 gRPC · :4318 HTTP<br><i>contrato inmutable</i>",
                fill="#E8F1FB", stroke="#147EBA", size=10)

    d.zone(440, 290, 760, 340, "OpenTelemetry Collector · ola 0", fill="#FFFFFF", stroke="#16A34A", color="#15803D", size=11)
    ml = d.box(460, 330, 180, 60, "memory_limiter", size=10)
    rt = d.box(730, 330, 180, 60, "<b>routing</b> por señal<br>valida atributos", size=10)
    cnt = d.box(1000, 330, 180, 60, "count connector<br>rechazos contados", fill="#F3F4F6", size=10)
    smp = d.box(460, 440, 180, 60, "Muestra de auditoría<br>por hash del trace_id", size=10)
    red = d.box(730, 440, 180, 60, "<b>Redacción</b><br>regex + transform", fill="#ECFDF3", stroke="#16A34A", size=10)
    pre = d.box(1000, 428, 180, 84, "<b>Presidio Analyzer</b><br>Deployment aparte<br>gate de readiness",
                fill="#FDECEA", stroke=C_ROJO, color="#7F1D1D", size=10)
    exp = d.box(730, 550, 180, 60, "Exportadores<br>header de tenant", fill="#E8F1FB", stroke="#147EBA", size=10)
    d.text(1000, 530, 185, 80, "Si Presidio no responde, el colector deja de estar Ready y salta una alerta.",
           size=10, color=C_ROJO)

    npg = d.group("ec2", 170, 670, 1030, 230, "NodePool on-demand con taint · ingesters y paneles · ola 1",
                  size=10, valign="bottom")
    gra = d.box(190, 712, 210, 66, "<b>Grafana</b><br>estado en base dedicada", size=10)
    am = d.box(190, 808, 210, 52, "<b>Alertmanager</b>", size=10)
    mim = d.box(460, 712, 180, 66, "<b>Grafana Mimir</b><br>métricas", fill="#FFF8F1", stroke="#ED7100", size=10)
    tem = d.box(730, 712, 180, 66, "<b>Grafana Tempo</b><br>trazas", fill="#FFF8F1", stroke="#ED7100", size=10)
    lok = d.box(1000, 712, 180, 66, "<b>Grafana Loki</b><br>logs", fill="#FFF8F1", stroke="#ED7100", size=10)

    # --- Almacenamiento regional (franja inferior)
    d.zone(30, 970, 1190, 160, "Almacenamiento regional", fill="#F6FAF2", stroke=C_S3, color="#4D7C0F", size=11)
    s3a = d.aws(300, 1010, "s3", "storage", "S3 de auditoría", "KMS · retención corta · solo PutObject", size=48, lw=300)
    d.aws(640, 1010, "key_management_service", "sec", "AWS KMS", "cifrado de todos los buckets", size=48, lw=300)
    s3b = d.aws(980, 1010, "s3", "storage", "S3 por backend", "acceso por IRSA · retención 30 días", size=48, lw=300)

    # --- Flechas
    d.edge(p2, svc, "", color=C_FLUJO,
           extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    d.edge(svc, ml, "OTLP", color=C_FLUJO)
    _pos_rotulo(d, -0.3)
    d.edge(ml, rt, "", color=C_FLUJO)
    d.edge(rt, cnt, "inválidos", color="#5B6B7F", width=2)
    d.edge(rt, red, "válidos", color=C_FLUJO)
    d.edge(rt, smp, "", color=C_FLUJO, width=1, points=[(766, 415), (550, 415)],
           extra="exitX=0.2;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    d.edge(pre, red, "", color=C_ROJO, dashed=True, width=2)
    d.edge(red, exp, "", color=C_FLUJO)
    d.edge(smp, s3a, "muestra antes de redactar", color=C_S3, dashed=True,
           points=[(100, 470), (100, 945), (300, 945)],
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    _pos_rotulo(d, -0.67)
    for b, cx in ((mim, 550), (tem, 820), (lok, 1090)):
        d.edge(exp, b, "", color=C_FLUJO, width=1, points=[(820, 650), (cx, 650)],
               extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    d.edge(npg, s3b, "bloques por IRSA", color=C_S3,
           extra="exitX=%.4f;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" % ((980 - 170) / 1030.0))
    _pos_rotulo(d, -0.25)
    d.edge(gra, am, "", color=C_FLUJO)

    d.box(30, 1160, 1190, 80,
          "<b>Promoción por gates</b>: canario de las tres señales consultable por tenant · soak de 72 horas · simulacro de rollback · runbook de recuperación con RPO y RTO.<br>"
          "<b>Guard de CI</b>: impide cambiar nombre, tipo o puertos del Service OTLP. <b>Versiones fijadas</b> en todos los charts, sin alias flotantes.",
          fill="#FFFFFF", stroke="#9AA7B8", size=11, align="left", extra="spacingLeft=16;")
    d.save(os.path.join(aqui, "plataforma-observabilidad.drawio"))
