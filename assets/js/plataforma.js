/* Proyecto Plataforma: mapa de capacidades (HTML) y árbol de la organización (ECharts). */
(function () {
  "use strict";

  const CAPACIDADES = [
    { d: "Gobierno", k: "gobierno", items: ["Landing zone con Control Tower", "OUs por función y SCP propias",
      "Baseline de AWS Config por OU", "Budgets, anomalías y tag policies", "Vending de cuentas desde Terraform"] },
    { d: "Identidad", k: "seguridad", items: ["Identity Center con MFA", "CI federado por OIDC", "IRSA por service account",
      "Root centralizado y break-glass", "Revisión de acceso por script"] },
    { d: "Seguridad", k: "cumplimiento", items: ["GuardDuty", "Security Hub CIS + FSBP", "Access Analyzer",
      "Object Lock del estado", "Alarmas de cambios críticos y de entrega"] },
    { d: "Red", k: "red", items: ["VPC multi-AZ", "Direccionamiento sin TGW", "Subredes de pods enrutables", "VPC Flow Logs"] },
    { d: "Cómputo", k: "computo", items: ["Amazon EKS", "Karpenter spot y on-demand", "Chart base de servicio", "cert-manager con DNS01"] },
    { d: "Datos", k: "datos", items: ["PostgreSQL 18 + pgvector", "Valkey 9 por clase de carga", "PgBouncer con presupuesto de conexiones"] },
    { d: "Observabilidad", k: "observabilidad", items: ["Colector OTel con redacción", "Presidio con fail-close", "Mimir, Tempo y Loki",
      "Grafana y Alertmanager"] },
    { d: "Entrega", k: "entrega", items: ["Pipeline build, scan, sign", "Firma con Cosign y KMS", "CI de Terraform y Helm"] },
    { d: "Portabilidad", k: "ia", items: ["Interfaz agnóstica por capacidad", "Regla propia de TFLint", "Tamaños genéricos por proveedor"] },
  ];

  /* ---- Mapa de capacidades en HTML: el estado se lee como texto, no solo por color ---- */
  const mapa = document.getElementById("mapa-capacidades");
  if (mapa) {
    mapa.innerHTML = CAPACIDADES.map((g) =>
      '<section class="card cap-grupo domain-card" data-domain="' + g.k + '">' +
        "<h3>" + g.d + "</h3><ul>" +
        g.items.map((n) => "<li>" + n + "</li>").join("") +
      "</ul></section>"
    ).join("");
  }

  /* ---- Árbol de la organización ------------------------------------------- */
  const P = window.Portafolio;
  if (!P) return;

  const ORG = {
    name: "Raíz",
    tip: "All Features: requisito de Control Tower y de las SCP. En la raíz, SCP de protección de la organización, higiene de root y límite del identity store. La denegación de regiones se aplica por OU con un control de Control Tower.",
    children: [
      { name: "Cuenta de gestión", tip: "Fuera del alcance de las SCP: se protege con mínimo privilegio, inmutabilidad del estado y detección de cambios." },
      { name: "OU Security", tip: "Administrada por Control Tower.", children: [
        { name: "Log Archive", tip: "Trail organizacional con Object Lock GOVERNANCE." },
        { name: "Audit", tip: "Administrador delegado de GuardDuty, Security Hub y Access Analyzer." },
      ]},
      { name: "OU Alianzas", tip: "Cuentas sin cargas de trabajo; una SCP lo impone." },
      { name: "OU Comercial", tip: "Las cuentas nacen en cuarentena hasta unirse a los controles." },
      { name: "OU Pruebas de políticas", tip: "Para validar SCP antes de aplicarlas al resto." },
      { name: "OU Suspendidas", tip: "SCP que deniega todo: destino de las cuentas retiradas." },
    ],
  };

  P.Charts.register("#chart-organizacion", (p) => {
    const narrow = window.innerWidth < 600;
    const paint = (n, depth) => {
      const c = depth === 0 ? p.d.gobierno : depth === 1 ? (n.name.startsWith("OU") ? p.d.cumplimiento : p.d.gobierno) : p.d.red;
      return Object.assign({}, n, {
        itemStyle: { color: c, borderColor: c },
        children: n.children ? n.children.map((ch) => paint(ch, depth + 1)) : undefined,
      });
    };
    return {
      tooltip: {
        trigger: "item", backgroundColor: p.surface, borderColor: p.border,
        textStyle: { color: p.text, fontFamily: p.font, fontSize: 12 },
        extraCssText: "max-width:260px;white-space:normal;",
        formatter: (i) => "<strong>" + i.name + "</strong><br>" + (i.data.tip || ""),
      },
      series: [{
        type: "tree", data: [paint(ORG, 0)], orient: "LR",
        top: 20, bottom: 20, left: narrow ? 60 : 80, right: narrow ? 120 : 160,
        symbol: "circle", symbolSize: 12, expandAndCollapse: false, initialTreeDepth: -1,
        lineStyle: { color: p.border, width: 1.5, curveness: 0.5 },
        label: { position: "left", verticalAlign: "middle", align: "right", color: p.text, fontFamily: p.font, fontSize: narrow ? 10 : 12 },
        leaves: { label: { position: "right", verticalAlign: "middle", align: "left", color: p.text2 } },
        emphasis: { focus: "descendant" },
      }],
    };
  });
})();
