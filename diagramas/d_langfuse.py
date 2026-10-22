# -*- coding: utf-8 -*-
"""Diagrama: Langfuse autoalojado en Amazon EKS."""
import os

from drawio import Diagram, INK, MUTED  # noqa: F401
from comun import C_FLUJO, C_API, C_FALLA, C_OK, GCP_BIGQUERY  # noqa: F401


def _rotulo(d, eid, pos=0.0, dx=0, dy=0):
    """Mueve el rótulo de una flecha: pos de -1 (origen) a 1 (destino) y un desplazamiento en px."""
    for k, c in enumerate(d.cells):
        if c.startswith('<mxCell id="%s" ' % eid):
            c = c.replace('<mxGeometry relative="1" as="geometry">',
                          '<mxGeometry x="%.3f" relative="1" as="geometry">' % pos, 1)
            if dx or dy:
                c = c.replace("</mxGeometry>", '<mxPoint x="%d" y="%d" as="offset"/></mxGeometry>' % (dx, dy), 1)
            d.cells[k] = c
            return


def _icono_con_rotulo_lateral(d, cx, y, nombre, cat, rotulo, detalle, lado, w=48, recurso=True):
    """Icono AWS con el rótulo a un costado, para que la flecha pueda salir por abajo."""
    if recurso:
        i = d.res(cx, y, nombre, cat, "", "", w=w, h=w)
    else:
        i = d.aws(cx, y, nombre, cat, "", "", size=w)
    v = "<b>%s</b><br><font color='%s'>%s</font>" % (rotulo, MUTED, detalle)
    if lado == "izq":
        d.text(cx - w // 2 - 8 - 150, y + 4, 150, 44, v, size=11, align="right")
    else:
        d.text(cx + w // 2 + 8, y + 4, 170, 44, v, size=11, align="left")
    return i


# =============================================================================
# LLMOps: Langfuse autoalojado en Amazon EKS
# =============================================================================
def generar(aqui):
    d = Diagram("Langfuse autoalojado en Amazon EKS", 1240, 1716)
    d.title(30, 22, 1180, "Observabilidad de LLM autoalojada en Amazon EKS")
    d.text(30, 56, 1180, 46,
           "Tres planos: aplicación en EKS, datos analíticos en ClickHouse y metadatos y colas administradas.",
           size=12, color=MUTED)

    C_PEND = "#7D8998"
    C_DATOS = "#A21CAF"

    # ------------------------------------------------------ fuera de AWS
    d.legend(30, 118, [(C_FLUJO, "tráfico y datos", False), (C_PEND, "DNS", True), (C_DATOS, "replicación", True)], w=190)
    users = _icono_con_rotulo_lateral(d, 560, 118, "users", "general", "Personas", "navegador", "izq")
    cf = d.box(640, 118, 180, 60, "<b>Cloudflare DNS</b><br>registro hacia el ALB", fill="#FFF4E5", stroke="#F38020", size=10)
    r53 = _icono_con_rotulo_lateral(d, 900, 118, "route_53", "net", "Route 53", "subzona delegada", "der", recurso=False)

    # ---------------------------------------------------------- AWS
    d.group("cloud", 15, 262, 1210, 1440, "AWS · cuenta de producción")
    d.group("region", 32, 302, 1176, 1384, "Región")
    d.group("vpc", 49, 342, 1142, 1044, "VPC · aplicación y datos sin IP pública")

    # subredes públicas
    d.subnet(66, 384, 838, 140, "Subredes públicas", public=True)
    d.aws(220, 420, "certificate_manager_3", "sec", "ACM", "certificado propio", size=48, lw=150)
    alb = d.res(560, 420, "application_load_balancer", "net", "ALB", "IngressGroup propio", w=48, h=48, lw=150)
    d.res(780, 420, "nat_gateway", "net", "NAT gateway", "", w=48, h=48, lw=150)

    # clúster EKS
    CX, CY, CW, CH = 66, 540, 1108, 616
    cl = d.zone(CX, CY, CW, CH, "Clúster Amazon EKS · namespace dedicado", fill="#FFF8F1", stroke="#ED7100",
                color="#B45309", align="right")
    d.subnet(84, 580, 616, 562, "Zona A · subred privada")
    d.subnet(716, 580, 444, 562, "Zona B · subred privada")

    def nodo(x, y, w, nombre):
        d.box(x, y, w, 146, nombre, fill="#FFFFFF", stroke="#ED7100", size=10, bold=True, valign="top", extra="spacingTop=2;")
        ids = []
        for k, (txt, fill, stroke) in enumerate([("Langfuse web", "#E8F1FB", "#147EBA"),
                                                ("Langfuse worker", "#E8F1FB", "#147EBA"),
                                                ("ClickHouse Keeper", "#F5EBFF", "#8C4FFF")]):
            ids.append(d.box(x + 13, y + 30 + k * 36, w - 26, 30, txt, fill=fill, stroke=stroke, size=10))
        return ids

    d.zone(120, 616, 566, 194, "Node group de aplicación · taint", fill="none", stroke="#ED7100", color="#B45309",
           size=10, dashed=True, align="right")
    web1, _w1, _k1 = nodo(134, 650, 250, "Nodo 1")
    _web2, worker2, _k2 = nodo(394, 650, 250, "Nodo 2")
    d.zone(730, 616, 416, 194, "Node group de aplicación · taint", fill="none", stroke="#ED7100", color="#B45309",
           size=10, dashed=True, align="right")
    nodo(813, 650, 250, "Nodo 3")

    # un único node group de datos que cruza las dos zonas
    d.zone(120, 826, 1026, 142, "Node group de datos (abarca A y B) · taint", fill="none", stroke=C_DATOS,
           color=C_DATOS, size=10, dashed=True)
    cha = d.box(134, 862, 386, 90, "<b>ClickHouse · réplica completa A</b><br>EBS gp3 con CMK propia · caliente ~30 días",
                fill="#FDF2F8", stroke=C_DATOS, size=10)
    chb = d.box(744, 862, 388, 90, "<b>ClickHouse · réplica completa B</b><br>un solo shard: escala en vertical",
                fill="#FDF2F8", stroke=C_DATOS, size=10)

    orq = d.box(134, 986, 510, 60, "<b>Orquestador de agentes</b><br>emite trazas con el SDK de la generación anterior", size=10)
    svc = d.box(134, 1070, 510, 56, "<b>Service interno</b> de Langfuse web · la ingesta no sale de la VPC",
                fill="#E8F1FB", stroke="#147EBA", size=10)
    d.box(744, 986, 388, 140, "<b>Quórum de Keeper: 2 + 1</b><br>tolera la caída de cualquier nodo",
          fill="#FFF7E6", stroke="#D97706", size=10)

    # datos administrados (dentro de la VPC)
    d.zone(66, 1190, 1108, 180, "Datos administrados", fill="#FBF5FD", stroke=C_DATOS, color=C_DATOS, size=11)
    d.box(84, 1230, 216, 122, "<b>Acceso mínimo</b><br>un security group por puerto y por origen",
          fill="#FFFFFF", stroke="#C9B3D9", size=10)
    aur = d.aws(420, 1240, "aurora", "db", "Aurora PostgreSQL", "Serverless v2 · 2 zonas", size=48, lw=200)
    vk = d.res(660, 1240, "elasticache_for_valkey", "db", "ElastiCache Valkey", "noeviction · 2 zonas", w=48, h=48, lw=200)

    # servicios regionales (fuera de la VPC)
    d.zone(49, 1404, 1142, 266, "Servicios regionales", fill="#F6FAF2", stroke="#7AA116", color="#4D7C0F", size=11)
    d.aws(150, 1444, "key_management_service", "sec", "KMS", "CMK multirregión", size=44, lw=150)
    d.aws(330, 1444, "secrets_manager", "sec", "Secrets Manager", "solo ARN en outputs", size=44, lw=150)
    d.aws(150, 1560, "identity_and_access_management", "sec", "IRSA", "sin llaves estáticas", size=44, lw=150)
    d.aws(330, 1560, "simple_email_service", "sec", "SES", "correo transaccional", size=44, lw=150)
    s3e = d.aws(860, 1500, "s3", "storage", "S3 · eventos crudos", "SSE-KMS · ciclo de vida", size=48, lw=200)
    s3f = d.aws(1080, 1500, "s3", "storage", "S3 · capa fría", "partes vivas de las tablas", size=48, lw=200)

    # ------------------------------------------------------------ flujos
    e = d.edge(users, alb, "HTTPS", color=C_FLUJO,
               extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;")
    _rotulo(d, e, -0.6)
    d.edge(cf, alb, "", color=C_PEND, dashed=True, width=1, points=[(610, 148), (610, 434)],
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.29;entryDx=0;entryDy=0;")
    d.edge(r53, alb, "", color=C_PEND, dashed=True, width=1, points=[(900, 230), (630, 230), (630, 454)],
           extra="exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=1;entryY=0.71;entryDx=0;entryDy=0;")
    d.edge(alb, web1, "", color=C_FLUJO, points=[(350, 444)],
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0.906;entryY=0;entryDx=0;entryDy=0;")
    d.edge(orq, svc, "", color=C_FLUJO)
    d.edge(svc, web1, "", color=C_FLUJO, points=[(102, 1098), (102, 695)],
           extra="exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;")
    e = d.edge(worker2, cha, "inserta", color=C_FLUJO, points=[(665, 731), (665, 884)],
               extra="exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.244;entryDx=0;entryDy=0;")
    _rotulo(d, e, 0.56)
    d.edge(cha, chb, "replicación", color=C_DATOS, dashed=True, start="blockThin",
           extra="exitX=1;exitY=0.7;exitDx=0;exitDy=0;entryX=0;entryY=0.7;entryDx=0;entryDy=0;")

    def desde_cluster(dst, x, label, pos, color=C_FLUJO):
        e = d.edge(cl, dst, label, color=color,
                   extra="exitX=%.4f;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" % ((x - CX) / float(CW)))
        _rotulo(d, e, pos)

    desde_cluster(aur, 420, "metadatos · TLS", -0.6)
    desde_cluster(vk, 660, "cola de ingesta", -0.6)
    desde_cluster(s3e, 860, "eventos: PUT · LIST · GET", -0.9)
    desde_cluster(s3f, 1080, "capa fría por TTL", -0.9, color=C_DATOS)

    d.save(os.path.join(aqui, "langfuse-arquitectura.drawio"))
