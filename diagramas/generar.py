# -*- coding: utf-8 -*-
"""Genera los diagramas .drawio del portafolio.

Uso, desde la raíz del sitio:  python diagramas/generar.py
Cada módulo d_*.py dibuja un diagrama y lo escribe junto a este script. Los
diagramas se abren y editan en https://app.diagrams.net y se embeben en las
páginas con el visor oficial de diagrams.net.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.dont_write_bytecode = True  # no deja __pycache__ dentro del sitio publicado

import d_finops  # noqa: E402
import d_langfuse  # noqa: E402
import d_landing  # noqa: E402
import d_celda  # noqa: E402
import d_observabilidad  # noqa: E402

if __name__ == "__main__":
    solo = sys.argv[1:]
    for nombre, mod in (("finops", d_finops), ("langfuse", d_langfuse), ("landing", d_landing),
                        ("celda", d_celda), ("observabilidad", d_observabilidad)):
        if not solo or nombre in solo:
            mod.generar(AQUI)
    print("listo")
