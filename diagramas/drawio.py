# -*- coding: utf-8 -*-
"""Utilidades mínimas para escribir diagramas .drawio (XML sin comprimir) desde Python.

Sin dependencias externas. Cada diagrama es una lista de celdas mxCell con
geometría absoluta; los iconos de AWS usan la librería oficial mxgraph.aws4
de diagrams.net y los de Google Cloud la librería mxgraph.gcp2.
"""
from xml.sax.saxutils import escape, quoteattr

# Paleta oficial de categorías de AWS (fill de los iconos de recurso)
AWS = {
    "compute": "#ED7100",
    "container": "#ED7100",
    "db": "#C925D1",
    "storage": "#7AA116",
    "net": "#8C4FFF",
    "sec": "#DD344C",
    "mgmt": "#E7157B",
    "dev": "#C925D1",
    "integration": "#E7157B",
    "ml": "#01A88D",
    "cost": "#7AA116",
    "general": "#232F3E",
}

INK = "#232F3E"
MUTED = "#5B6B7F"

# Escala de fuentes: los diagramas se ven reducidos dentro de la página, así que el texto
# se genera un 40 % más grande que el tamaño nominal de cada llamada.
ESCALA = 1.4


def fs(size):
    return int(round(size * ESCALA))

GROUPS = {
    "cloud": "grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fontColor=#232F3E;dashed=0;",
    "account": "grIcon=mxgraph.aws4.group_account;strokeColor=#CD2264;fontColor=#CD2264;dashed=0;",
    "region": "grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fontColor=#147EBA;dashed=1;",
    "vpc": "grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fontColor=#8C4FFF;dashed=0;",
    "sg": "grIcon=mxgraph.aws4.group_security_group;grStroke=1;strokeColor=#DD3522;fontColor=#DD3522;dashed=1;",
    "asg": "grIcon=mxgraph.aws4.group_auto_scaling_group;strokeColor=#ED7100;fontColor=#ED7100;dashed=1;",
    "ec2": "grIcon=mxgraph.aws4.group_ec2_instance_contents;strokeColor=#ED7100;fontColor=#C2410C;dashed=0;",
    "onprem": "grIcon=mxgraph.aws4.group_corporate_data_center;strokeColor=#7D8998;fontColor=#7D8998;dashed=0;",
}


class Diagram:
    def __init__(self, name, width=1600, height=1000):
        self.name = name
        self.width = width
        self.height = height
        self.cells = []
        self._n = 1

    # ------------------------------------------------------------------ ids
    def nid(self):
        self._n += 1
        return "c%d" % self._n

    def _vertex(self, value, style, x, y, w, h, parent="1"):
        i = self.nid()
        self.cells.append(
            '<mxCell id="%s" value=%s style=%s vertex="1" parent="%s">'
            '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
            % (i, quoteattr(value), quoteattr(style), parent, x, y, w, h)
        )
        return i

    # --------------------------------------------------------------- formas
    def text(self, x, y, w, h, value, size=12, bold=False, color=INK, align="left", html=True):
        style = (
            "text;html=1;whiteSpace=wrap;fillColor=none;strokeColor=none;verticalAlign=top;"
            "align=%s;fontSize=%d;fontColor=%s;fontStyle=%d;spacing=0;" % (align, fs(size), color, 1 if bold else 0)
        )
        return self._vertex(value, style, x, y, w, h)

    def title(self, x, y, w, value, subtitle=None):
        self.text(x, y, w, 30, value, size=20, bold=True)
        if subtitle:
            self.text(x, y + 32, w, 22, subtitle, size=12, color=MUTED)

    def box(self, x, y, w, h, value, fill="#FFFFFF", stroke="#5B6B7F", color=INK, size=11,
            bold=False, rounded=True, dashed=False, align="center", valign="middle", extra=""):
        style = (
            "rounded=%d;arcSize=10;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontColor=%s;"
            "fontSize=%d;fontStyle=%d;align=%s;verticalAlign=%s;spacing=8;dashed=%d;%s"
            % (1 if rounded else 0, fill, stroke, color, fs(size), 1 if bold else 0, align, valign,
               1 if dashed else 0, extra)
        )
        return self._vertex(value, style, x, y, w, h)

    def zone(self, x, y, w, h, label, fill="#F7F9FC", stroke="#9AA7B8", color=INK, size=12, dashed=False, align="left"):
        """Recuadro contenedor genérico con rótulo arriba (a la izquierda por defecto)."""
        style = (
            "rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontColor=%s;"
            "fontSize=%d;fontStyle=1;align=%s;verticalAlign=top;spacingLeft=12;spacingRight=12;spacingTop=6;"
            "dashed=%d;container=0;" % (fill, stroke, color, fs(size), align, 1 if dashed else 0)
        )
        return self._vertex(label, style, x, y, w, h)

    def group(self, kind, x, y, w, h, label, size=12, valign="top"):
        style = (
            "sketch=0;outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fillColor=none;"
            "shape=mxgraph.aws4.group;verticalAlign=%s;align=left;grIconSize=32;spacingLeft=40;"
            "spacingTop=4;spacingBottom=4;fontSize=%d;fontStyle=1;container=0;%s" % (valign, fs(size), GROUPS[kind])
        )
        return self._vertex(label, style, x, y, w, h)

    def subnet(self, x, y, w, h, label, public=False, size=11):
        fill, stroke = ("#E6F2F8", "#147EBA") if public else ("#E9F3E6", "#248814")
        return self.box(x, y, w, h, label, fill=fill, stroke=stroke, color=stroke, size=size, bold=True,
                        rounded=False, align="left", valign="top", extra="spacingLeft=10;spacingTop=4;")

    def aws(self, cx, y, icon, cat, label="", detail="", size=56, lw=170, lh=44, pend=False):
        """Icono de recurso AWS centrado en cx con su rótulo debajo. Devuelve el id del icono.
        pend=True lo dibuja atenuado: diseñado, aún no implementado."""
        fill = AWS[cat]
        lh = int(lh * ESCALA)
        style = ("opacity=40;" if pend else "") + (
            "sketch=0;outlineConnect=0;fontColor=%s;gradientColor=none;fillColor=%s;strokeColor=#ffffff;"
            "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;"
            "fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.%s;"
            % (INK, fill, icon)
        )
        i = self._vertex("", style, cx - size // 2, y, size, size)
        if label:
            v = "<b>%s</b>" % escape(label) + ("<br><font color='%s'>%s</font>" % (MUTED, escape(detail)) if detail else "")
            self.text(cx - lw // 2, y + size + 4, lw, lh, v, size=11, align="center")
        return i

    def res(self, cx, y, name, cat, label="", detail="", w=48, h=48, lw=170, lh=44, pend=False):
        """Forma de recurso de AWS (contorno, p. ej. nat_gateway, users, s3_express_one_zone).
        pend=True la dibuja atenuada: diseñada, aún no implementada."""
        lh = int(lh * ESCALA)
        style = ("opacity=40;" if pend else "") + (
            "sketch=0;outlineConnect=0;fontColor=%s;gradientColor=none;fillColor=%s;strokeColor=none;dashed=0;"
            "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=11;fontStyle=0;"
            "aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.%s;" % (INK, AWS[cat], name)
        )
        i = self._vertex("", style, cx - w // 2, y, w, h)
        if label:
            v = "<b>%s</b>" % escape(label) + ("<br><font color='%s'>%s</font>" % (MUTED, escape(detail)) if detail else "")
            self.text(cx - lw // 2, y + h + 4, lw, lh, v, size=11, align="center")
        return i

    def shape(self, cx, y, shape_style, label="", detail="", w=56, h=56, lw=170, lh=44):
        """Forma arbitraria de otra librería (por ejemplo mxgraph.gcp2.*) con rótulo debajo."""
        lh = int(lh * ESCALA)
        i = self._vertex("", "html=1;aspect=fixed;" + shape_style, cx - w // 2, y, w, h)
        if label:
            v = "<b>%s</b>" % escape(label) + ("<br><font color='%s'>%s</font>" % (MUTED, escape(detail)) if detail else "")
            self.text(cx - lw // 2, y + h + 4, lw, lh, v, size=11, align="center")
        return i

    def badge(self, x, y, value, fill="#0E7490", color="#FFFFFF", w=26, h=26, size=12):
        style = (
            "ellipse;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontColor=%s;fontSize=%d;"
            "fontStyle=1;align=center;verticalAlign=middle;" % (fill, color, fs(size))
        )
        return self._vertex(value, style, x, y, w, h)

    def edge(self, src, dst, label="", color="#232F3E", width=2, dashed=False, size=10,
             orthogonal=True, end="blockThin", start="none", points=None, extra=""):
        """Conector entre dos celdas. points: lista opcional de (x, y) como puntos de paso."""
        i = self.nid()
        style = (
            "%shtml=1;rounded=1;fontSize=%d;strokeColor=%s;strokeWidth=%d;endArrow=%s;endFill=1;"
            "startArrow=%s;startFill=1;labelBackgroundColor=#FFFFFF;fontColor=%s;dashed=%d;%s"
            % ("edgeStyle=orthogonalEdgeStyle;" if orthogonal else "", fs(size), color, width, end, start,
               color, 1 if dashed else 0, extra)
        )
        pts = ""
        if points:
            pts = '<Array as="points">%s</Array>' % "".join('<mxPoint x="%d" y="%d"/>' % p for p in points)
        self.cells.append(
            '<mxCell id="%s" value=%s style=%s edge="1" parent="1" source="%s" target="%s">'
            '<mxGeometry relative="1" as="geometry">%s</mxGeometry></mxCell>'
            % (i, quoteattr(label), quoteattr(style), src, dst, pts)
        )
        return i

    def line(self, x1, y1, x2, y2, color="#232F3E", width=2, dashed=False, end="blockThin"):
        """Línea libre entre dos puntos (sin celdas de origen ni destino)."""
        i = self.nid()
        style = ("html=1;endArrow=%s;endFill=1;strokeColor=%s;strokeWidth=%d;dashed=%d;"
                 % (end, color, width, 1 if dashed else 0))
        self.cells.append(
            '<mxCell id="%s" value="" style=%s edge="1" parent="1">'
            '<mxGeometry relative="1" as="geometry">'
            '<mxPoint x="%d" y="%d" as="sourcePoint"/><mxPoint x="%d" y="%d" as="targetPoint"/>'
            "</mxGeometry></mxCell>" % (i, quoteattr(style), x1, y1, x2, y2)
        )
        return i

    def legend(self, x, y, items, w=280):
        """items: lista de (color, texto, discontinuo)."""
        self.text(x, y, w, 20, "Convenciones", size=11, bold=True)
        yy = y + 24
        for color, label, dashed in items:
            self.line(x, yy + 8, x + 44, yy + 8, color=color, dashed=dashed)
            self.text(x + 54, yy, w - 54, 18, label, size=10, color=MUTED)
            yy += 22

    # ---------------------------------------------------------------- salida
    def xml(self):
        body = "".join(self.cells)
        return (
            '<mxfile host="portafolio-generar.py" agent="python" version="24.0.0">'
            '<diagram id="%s" name=%s>'
            '<mxGraphModel dx="%d" dy="%d" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" '
            'arrows="1" fold="1" page="0" pageScale="1" pageWidth="%d" pageHeight="%d" '
            'background="#FFFFFF" math="0" shadow="0">'
            '<root><mxCell id="0"/><mxCell id="1" parent="0"/>%s</root>'
            "</mxGraphModel></diagram></mxfile>\n"
            % (self.name.replace(" ", "-")[:40], quoteattr(self.name), self.width, self.height,
               self.width, self.height, body)
        )

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.xml().encode("utf-8"))
