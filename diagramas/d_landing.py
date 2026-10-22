# -*- coding: utf-8 -*-
"""Diagrama: landing zone multicuenta."""
import os

from drawio import Diagram, INK, MUTED  # noqa: F401
from comun import C_FLUJO, C_API, C_FALLA, C_OK, GCP_BIGQUERY  # noqa: F401


# =============================================================================
# Plataforma: landing zone multicuenta
# =============================================================================
# Lienzo de 1250 px como máximo: se embebe con auto-fit en un marco de 865 px.
# Distribución en filas: raíz · (cuenta de gestión | OU Security) · OUs por
# función · controles detectivos (dos flujos) · CI y vending.
ANCHO = 1250
X0, X1 = 30, 1220          # margen útil del contenido
ICONO = 48


def _caja_junto_a_icono(y_icono, h, tam=ICONO):
    """y de una caja de alto h centrada verticalmente con un icono en y_icono."""
    return y_icono + tam // 2 - h // 2


def generar(aqui):
    d = Diagram("Landing zone multicuenta", ANCHO, 1375)
    d.text(X0, 24, X1 - X0, 34, "Landing zone multicuenta con controles preventivos, detectivos y de inmutabilidad",
           size=20, bold=True)
    d.text(X0, 62, X1 - X0, 46,
           "Organización en modo All Features gobernada con Control Tower.<br>"
           "Ninguna OU de gobierno aloja cargas de trabajo; el runtime vive en cuentas dedicadas fuera de ellas.",
           size=12, color=MUTED)
    C_SCP = "#DD344C"
    C_PEND = "#7D8998"

    # ---------------------------------------------------------------- raíz
    canal = 639  # x del canal libre entre la cuenta de gestión y la OU Security
    root = d.box(canal - 360, 126, 720, 64,
                 "<b>Raíz de la organización · All Features</b><br>SCP en la raíz: protección de la organización · higiene de root · límite del identity store",
                 fill="#FDF2F8", stroke="#E7157B", size=11)

    # ----------------------------------------------------- cuenta de gestión
    y2 = 232
    mg = d.zone(X0, y2, 594, 420, "Cuenta de gestión · fuera del alcance de las SCP", fill="#FFF5F5", stroke=C_SCP, color="#B91C1C")
    c1, c2, c3 = 134, 327, 520
    d.aws(c1, y2 + 50, "organizations", "mgmt", "Organizations", "OUs descubiertas por data source", size=ICONO, lw=170)
    d.aws(c2, y2 + 50, "control_tower", "mgmt", "Control Tower", "Account Factory desde Terraform", size=ICONO, lw=190)
    d.aws(c3, y2 + 50, "single_sign_on", "sec", "IAM Identity Center", "MFA · sesiones acotadas", size=ICONO, lw=190)
    d.aws(c1, y2 + 183, "s3", "storage", "Estado de Terraform", "Object Lock COMPLIANCE", size=ICONO, lw=190)
    d.aws(c2, y2 + 183, "key_management_service", "sec", "CMK del estado", "réplica en otra región", size=ICONO, lw=190)
    d.aws(c3, y2 + 183, "cloudwatch_2", "mgmt", "Alarmas", "uso de root · cambios críticos", size=ICONO, lw=190)
    d.box(X0 + 20, y2 + 314, 554, 86,
          "<b>Fuera del alcance de las SCP</b>: la defensa es mínimo privilegio,<br>"
          "inmutabilidad del estado y detección de cambios.",
          fill="#FFFFFF", stroke="#FCA5A5", size=10)

    # ----------------------------------------------------------- OU Security
    sec = d.zone(654, y2, X1 - 654, 420, "OU Security · administrada por Control Tower",
                 fill="#F7F5FF", stroke="#8C4FFF", color="#6D28D9")
    d.group("account", 674, y2 + 46, 210, 354, "Log Archive", size=11)
    d.aws(779, y2 + 112, "cloudtrail", "mgmt", "Trail organizacional", "todas las cuentas", size=ICONO, lw=200)
    d.aws(779, y2 + 262, "s3", "storage", "Logs centralizados", "Object Lock GOVERNANCE", size=ICONO, lw=200)
    d.group("account", 900, y2 + 46, 300, 354, "Audit · administrador delegado", size=11)
    a1, a2 = 975, 1125
    d.aws(a1, y2 + 112, "guardduty", "sec", "GuardDuty", "alta automática", size=44, lw=148)
    d.aws(a2, y2 + 112, "security_hub", "sec", "Security Hub", "CIS v3.0.0 · FSBP", size=44, lw=148)
    d.aws((a1 + a2) // 2, y2 + 262, "identity_and_access_management", "sec", "Access Analyzer", "acceso externo", size=44, lw=148)

    # ------------------------------------------------- OUs por función
    y3 = 692
    ous = d.zone(X0, y3, X1 - X0, 210, "OUs por función · sin cargas de trabajo",
                 fill="#FFF8F1", stroke="#ED7100", color="#B45309")
    tarjeta_w, hueco = 275, 20
    for k, (t, s, scp) in enumerate([("OU Alianzas", "cuentas sin cargas de trabajo", "SCP sin cargas"),
                                     ("OU Comercial", "las cuentas nacen en cuarentena", "SCP de cuarentena"),
                                     ("OU Pruebas de políticas", "SCP validadas antes de propagarlas", "SCP sin cargas"),
                                     ("OU Suspendidas", "destino de las cuentas retiradas", "SCP deniega todo")]):
        x = X0 + 20 + k * (tarjeta_w + hueco)
        y = y3 + 50
        d.group("account", x, y, tarjeta_w, 140, t, size=11)
        d.text(x + 16, y + 44, tarjeta_w - 32, 40, s, size=10, color=MUTED)
        d.box(x + 16, y + 92, tarjeta_w - 32, 34, scp, fill="#FDECEA", stroke=C_SCP, color="#7F1D1D", size=10, bold=True)

    # Árbol desde la raíz: a las dos zonas de la fila 2 y, por el canal libre
    # entre ellas, a las OUs por función.
    for z in (mg, sec):
        d.edge(root, z, "", color="#E7157B", width=2,
               extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    d.edge(root, ous, "", color="#E7157B", width=2,
           extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=%.4f;entryY=0;entryDx=0;entryDy=0;"
                 % ((canal - X0) / float(X1 - X0)))

    # --------------------------------------- detección, costo y notificación
    y4 = 942
    d.zone(X0, y4, X1 - X0, 305, "Controles detectivos, costo y notificación", fill="#F7F9FC", stroke="#9AA7B8")
    ya, yb = y4 + 52, y4 + 188           # fila de detección y fila de notificación
    cfg = d.aws(120, ya, "config", "mgmt", "AWS Config", "baseline por OU", size=ICONO, lw=170)
    sh = d.aws(380, ya, "security_hub", "sec", "Security Hub", "configuración central", size=ICONO, lw=190)
    hz = d.box(530, _caja_junto_a_icono(ya, 56), 220, 56, "<b>Hallazgos agregados</b><br>en la cuenta Audit", size=10)
    d.aws(1060, ya, "cost_management", "cost", "Budgets y anomalías", "guardarraíles de costo", size=ICONO, lw=220)
    d.edge(cfg, sh, "", color=C_FLUJO)
    d.edge(sh, hz, "", color=C_FLUJO)

    eb = d.aws(120, yb, "eventbridge", "integration", "EventBridge", "eventos de seguridad", size=ICONO, lw=170)
    sns = d.aws(380, yb, "sns", "integration", "SNS", "seguridad · costo · operación", size=ICONO, lw=230)
    out = d.box(530, _caja_junto_a_icono(yb, 56), 220, 56, "<b>Correo y chat</b>", size=10)
    al = d.aws(1060, yb, "cloudwatch_2", "mgmt", "Alarmas de entrega", "fallos de EventBridge y SNS", size=ICONO, lw=220)
    d.edge(eb, sns, "", color=C_FLUJO)
    d.edge(sns, out, "", color=C_FLUJO)
    d.edge(al, out, "", color=C_SCP, dashed=True,
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;")
    d.text(760, yb - 22, 266, 20, "si falla la entrega, escala a otro tópico", size=10, color=C_SCP, align="center")

    # ------------------------------------------------------- CI y vending
    y5 = 1275
    d.box(X0, y5, 560, 72, "<b>CI por OIDC de GitHub Actions</b> → rol de plan de solo lectura<br>apply con revisión humana previa",
          fill="#E8F1FB", stroke="#147EBA", size=10)
    d.box(X0 + 580, y5, X1 - X0 - 580, 72, "<b>Vending de cuentas en tres applies</b>: preparación · un plan con una sola creación ·<br>unión a los controles; guarda que verifica la SCP de la OU destino",
          fill="#FFFFFF", stroke="#9AA7B8", size=10)
    d.save(os.path.join(aqui, "plataforma-landing-zone.drawio"))
