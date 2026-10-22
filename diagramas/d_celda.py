# -*- coding: utf-8 -*-
"""Diagrama: topología de una celda en AWS."""
import os

from drawio import Diagram, INK, MUTED  # noqa: F401
from comun import C_FLUJO, C_API, C_FALLA, C_OK, GCP_BIGQUERY  # noqa: F401


def _etiqueta(d, x=None, dy=None):
    """Ajusta la etiqueta de la última flecha: x en [-1, 1] a lo largo del trazo
    (0 = punto medio) y dy como desplazamiento vertical en píxeles."""
    c = d.cells[-1]
    if x is not None:
        c = c.replace('<mxGeometry relative="1"', '<mxGeometry x="%.2f" relative="1"' % x, 1)
    if dy is not None:
        c = c.replace("</mxGeometry>", '<mxPoint x="0" y="%d" as="offset"/></mxGeometry>' % dy, 1)
    d.cells[-1] = c


def _servicio(d, x, y, icono, cat, rotulo, detalle):
    """Icono de servicio con el rótulo a la derecha (para la franja de servicios regionales)."""
    d.aws(x + 24, y, icono, cat, size=48)
    d.text(x + 64, y + 6, 280, 40, "<b>%s</b><br><font color='%s'>%s</font>" % (rotulo, MUTED, detalle), size=11)


# =============================================================================
# Plataforma: topología de una celda en AWS
# =============================================================================
def generar(aqui):
    d = Diagram("Arquitectura de referencia de una celda en AWS", 1230, 1460)
    d.title(40, 24, 1150, "Arquitectura de referencia de una celda en AWS · red, cómputo y datos administrados",
            "Una VPC por ambiente sin Transit Gateway ni peering.")

    # --- Internet: fuera de la cuenta --------------------------------------------------------
    users = d.res(440, 118, "users", "general", "Usuarios", "", w=48, h=48, lw=120)
    edge_box = d.box(563, 100, 180, 100, "<b>Borde neutral</b><br>Cloudflare<br>DNS · TLS · CDN<br>WAF · DDoS",
                     fill="#FFF4E5", stroke="#F38020", size=10)
    ext = d.box(770, 100, 200, 100, "<b>Proveedores externos</b><br>APIs de modelos y SaaS<br>(solo egreso)",
                fill="#F3F4F6", stroke="#7D8998", size=10)

    d.group("cloud", 20, 235, 1190, 1203, "AWS · cuenta de la celda")
    d.group("region", 40, 275, 1150, 1143, "Región")
    d.group("vpc", 60, 315, 1110, 896, "VPC del ambiente · bloque propio de la supernet")

    # --- Subredes públicas -------------------------------------------------------------------
    PS = 355
    d.box(80, PS, 1070, 170, "Subredes públicas · una por zona", fill="#E6F2F8", stroke="#147EBA", color="#147EBA",
          size=11, bold=True, rounded=False, align="right", valign="top", extra="spacingRight=10;spacingTop=4;")
    IY = PS + 50
    nlb = d.res(202, IY, "network_load_balancer", "net", "NLB", "TCP/UDP tiempo real", w=44, h=44, lw=230)
    alb = d.res(438, IY, "application_load_balancer", "net", "ALB / Ingress", "APIs HTTPS", w=44, h=44, lw=180)
    igw = d.res(642, IY, "internet_gateway", "net", "Internet gateway", "", w=44, h=44, lw=160)
    nat = d.res(870, IY, "nat_gateway", "net", "NAT gateway", "solo saliente", w=44, h=44, lw=150)
    d.res(1068, IY, "endpoints", "net", "Endpoint S3", "gateway", w=44, h=44, lw=160)

    # --- Zonas: subredes privadas ------------------------------------------------------------
    Z = 545
    pods = []
    for k, z in enumerate(["Zona A", "Zona B"]):
        x = 80 + k * 543
        d.subnet(x, Z, 527, 508, "%s · subred privada" % z)
        g = Z + 38
        d.group("ec2", x + 15, g, 497, 140, "NodePool spot · sin estado", size=10)
        d.aws(x + 145, g + 48, "ec2", "compute", "Spot", "7 familias · reciclaje semanal", size=40, lw=240)
        pods.append(d.box(x + 285, g + 46, 212, 56, "Servicios sin estado", fill="#FFFFFF",
                          stroke="#ED7100", size=10))
        g = Z + 328
        d.group("ec2", x + 15, g, 497, 165, "NodePool on-demand · taint", size=10)
        d.aws(x + 145, g + 48, "ec2", "compute", "On-demand", "con estado", size=40, lw=180)
        d.text(x + 55, g + 132, 180, 20, "No desalojable", size=10, color=MUTED, align="center")
        d.box(x + 285, g + 44, 212, 44, "Ingesters y paneles", fill="#FFFFFF", stroke="#ED7100", size=10)
        d.box(x + 285, g + 98, 212, 54, "Medios en tiempo real", fill="#FFFFFF", stroke="#ED7100",
              size=10)
    DY = Z + 225
    rds = d.aws(471, DY, "rds", "db", "PostgreSQL 18", "primaria · pgvector", size=48, lw=180)
    d.res(225, DY, "elasticache_for_valkey", "db", "Valkey 9", "primaria", w=48, h=48, lw=170)
    rdsb = d.aws(768, DY, "rds", "db", "Standby Multi-AZ", "réplica síncrona", size=48, lw=180)
    d.res(1014, DY, "elasticache_for_valkey", "db", "Valkey 9", "réplica", w=48, h=48, lw=170)

    # --- Notas de la VPC y subredes de pods --------------------------------------------------
    NY = Z + 508 + 15
    d.box(80, NY, 527, 64, "<b>Security groups por capa</b>: clúster · nodos · PostgreSQL · caché.<br>"
          "Cada capa acepta solo su puerto y su origen.", fill="#FDECEA", stroke="#DD3522",
          color="#7F1D1D", size=10)
    d.box(623, NY, 527, 64, "<b>Tráfico entre zonas</b>: se cobra en ambos sentidos;<br>"
          "se decide caso a caso frente a la disponibilidad.", fill="#FFF7E6", stroke="#D97706", size=10)
    PB = NY + 64 + 15
    d.subnet(80, PB, 1070, 44, "Subredes de pods · CIDR secundario enrutable para VPC CNI custom networking")

    # --- Servicios regionales: franja bajo la VPC --------------------------------------------
    SY = 1226
    d.zone(60, SY, 1110, 176, "Servicios regionales", fill="#F6FAF2", stroke="#7AA116", color="#4D7C0F", size=11)
    servicios = [
        ("eks", "container", "Plano de control EKS", "access entries · IMDSv2"),
        ("s3", "storage", "Amazon S3", "bloques de observabilidad"),
        ("key_management_service", "sec", "AWS KMS", "S3 · EBS · RDS · secretos"),
        ("secrets_manager", "sec", "Secrets Manager", "credenciales maestras"),
        ("cloudwatch_2", "mgmt", "CloudWatch", "plano de control y flow logs"),
        ("cloudtrail", "mgmt", "CloudTrail", "auditoría"),
    ]
    for i, (icono, cat, rotulo, detalle) in enumerate(servicios):
        _servicio(d, 90 + (i % 3) * 365, SY + 44 + (i // 3) * 66, icono, cat, rotulo, detalle)

    # --- Flujos ------------------------------------------------------------------------------
    d.edge(users, edge_box, "", color=C_FLUJO,
           extra="exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.42;entryDx=0;entryDy=0;")
    d.edge(edge_box, igw, "HTTPS", color=C_FLUJO,
           extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.75;entryY=0;entryDx=0;entryDy=0;")
    _etiqueta(d, x=-0.07)
    d.edge(igw, alb, "", color=C_FLUJO,
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;")
    d.edge(igw, nlb, "", color=C_FLUJO, points=[(631, PS + 30), (202, PS + 30)],
           extra="exitX=0.25;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    d.edge(alb, pods[0], "", color=C_FLUJO, points=[(334, IY + 22), (334, Z - 10), (471, Z - 10)],
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    d.edge(pods[0], rds, "TLS", color=C_FLUJO,
           extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    _etiqueta(d, x=0.40)
    d.edge(nat, ext, "egreso", color=C_FLUJO,
           extra="exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;")
    _etiqueta(d, x=0.07)
    d.edge(rds, rdsb, "replicación<br>síncrona", color="#C925D1", dashed=True,
           extra="exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    _etiqueta(d, x=-0.55)
    d.save(os.path.join(aqui, "plataforma-celda.drawio"))
