# Portafolio · Ricardo Villalobos

Portafolio de Platform Engineering con tres proyectos contados a nivel de arquitectura: una plataforma
multicuenta en AWS para un SaaS multi-tenant, observabilidad de LLM autoalojada en Amazon EKS y una
práctica FinOps multinube.

## Cómo está hecho

HTML, CSS y JavaScript sin paso de build. Gráficos con Apache ECharts. Diagramas draw.io generados con
Python y mostrados con el visor oficial de diagrams.net. Tema claro y oscuro, diseño responsive.

La paleta parte de los colores de AWS: Squid Ink, Smile Orange y el azul de la consola. Cada dominio usa el
color de su categoría en los íconos de arquitectura de AWS. El orden de los dominios en el gráfico radial y
el de las porciones del gráfico de costos separan colores que se confunden con daltonismo.

## Estructura

```
index.html                    Inicio: perfil, proyectos, enfoque, tecnologías y trayectoria
proyectos/plataforma-aws.html Plataforma multicuenta en AWS para un SaaS multi-tenant
proyectos/langfuse.html       Observabilidad de LLM autoalojada en Amazon EKS
proyectos/finops.html         Práctica FinOps multinube
assets/css/styles.css         Sistema de diseño (tema claro y oscuro, responsive)
assets/js/main.js             Comportamiento común y datos de contacto (PERFIL)
assets/js/*.js                Gráficos y contenido dinámico de cada página
assets/img/                   favicon.svg y og.png (vista previa al compartir)
diagramas/*.drawio            Diagramas que se embeben con el visor de diagrams.net
diagramas/generar.py          Genera los .drawio (Python, sin dependencias)
diagramas/d_*.py              Un módulo por diagrama
diagramas/drawio.py           Utilidades para escribir .drawio
diagramas/comun.py            Colores compartidos por los diagramas
404.html                      Página 404 para sitio de usuario o de proyecto
.nojekyll                     Publica los archivos tal cual, sin Jekyll
.gitignore                    Excluye cachés de Python, PDF y archivos del sistema
```

## Ejecutar en local

El visor de diagramas no funciona con `file://`. Desde la carpeta del sitio:

```
python -m http.server 8000
```

Y abre http://localhost:8000.

## Regenerar los diagramas

```
python diagramas/generar.py
```

Cada `.drawio` también se puede abrir y editar en https://app.diagrams.net.

## Datos de contacto

Se editan en el objeto `PERFIL` al inicio de `assets/js/main.js`. Un valor vacío oculta su botón, y si no
queda ningún canal, la sección de contacto se oculta. El CV no se publica en este repositorio.

## Publicar en GitHub Pages

1. Crea un repositorio público. Si se llama `<usuario>.github.io`, el sitio queda en
   `https://<usuario>.github.io/`; con otro nombre, en `https://<usuario>.github.io/<repo>/`. Las rutas
   son relativas y funcionan en los dos casos.
2. Sube el contenido de esta carpeta a la rama `main`.
3. En *Settings > Pages*, elige *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
4. Las etiquetas `og:url`, `og:image` y `canonical` apuntan a `https://ricardovillalobos0990.github.io/`.
   Si publicas con otro nombre de repositorio, actualízalas en las cuatro páginas.
