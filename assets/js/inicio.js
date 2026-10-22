/* Página de inicio: mapa de tecnologías (lista filtrable + gráfico radial). */
(function () {
  "use strict";

  const DOMINIOS = [
    { key: "gobierno", nombre: "Gobierno multicuenta", corto: "Gobierno", items: [
      ["AWS Organizations", "Estructura de cuentas y unidades organizativas con políticas heredadas"],
      ["AWS Control Tower", "Landing zone con controles preventivos y detectivos"],
      ["Service Control Policies", "Guardarraíles preventivos por unidad organizativa"],
      ["IAM Identity Center", "Acceso federado por conjuntos de permisos, sin usuarios IAM"],
      ["Service Catalog", "Aprovisionamiento estandarizado de cuentas y productos"],
      ["AWS Well-Architected", "Marco de revisión de las decisiones de arquitectura"],
      ["Google Cloud", "Segunda nube del entorno y destino de portabilidad"],
    ]},
    { key: "red", nombre: "Red y borde", corto: "Red", items: [
      ["Amazon VPC", "Redes privadas por cuenta y ambiente"],
      ["ALB · NLB", "Balanceo en capa 7 y capa 4"],
      ["Route 53", "DNS administrado"],
      ["ACM", "Certificados TLS administrados"],
      ["Cloudflare", "DNS, CDN y protección en el borde"],
      ["AWS Transfer Family", "SFTP administrado para integraciones"],
    ]},
    { key: "seguridad", nombre: "Seguridad y cumplimiento", corto: "Seguridad", items: [
      ["AWS IAM · IRSA", "Roles por servicio sin llaves estáticas"],
      ["Kubernetes RBAC", "Permisos mínimos dentro del clúster"],
      ["AWS Security Hub", "Postura de seguridad consolidada"],
      ["Amazon GuardDuty", "Detección de amenazas"],
      ["Amazon Inspector", "Escaneo de vulnerabilidades"],
      ["AWS Config", "Reglas de conformidad continuas"],
      ["AWS CloudTrail", "Auditoría centralizada de la organización"],
      ["AWS WAF", "Protección de aplicaciones web"],
      ["AWS KMS", "Cifrado con llaves administradas"],
      ["Secrets Manager", "Secretos rotables fuera del código"],
      ["OIDC · SAML", "Identidad de usuarios y SSO federado"],
      ["ISO 27001 · SOC 2", "Marcos de cumplimiento que guían los controles"],
    ]},
    { key: "observabilidad", nombre: "Observabilidad", corto: "Observab.", items: [
      ["OpenTelemetry", "Estándar neutral para métricas, trazas y logs"],
      ["Prometheus", "Métricas de clúster y servicios"],
      ["Alertmanager", "Enrutamiento y silenciamiento de alertas"],
      ["Grafana", "Tableros unificados sobre varias fuentes"],
      ["Mimir · Tempo · Loki", "Backends multi-tenant de métricas, trazas y logs"],
      ["Microsoft Presidio", "Detección de datos personales en la telemetría"],
      ["Amazon CloudWatch", "Métricas, logs y alarmas nativas de AWS"],
      ["Sentry", "Errores y rendimiento de aplicaciones"],
    ]},
    { key: "computo", nombre: "Cómputo y contenedores", corto: "Cómputo", items: [
      ["Amazon EKS", "Plataforma de ejecución de los microservicios"],
      ["Karpenter", "Aprovisionamiento de nodos justo a tiempo, con Spot diversificado y base on-demand"],
      ["Cluster Autoscaler", "Escalado de grupos de nodos administrados"],
      ["Helm", "Empaquetado de servicios y componentes de plataforma"],
      ["Linkerd", "Malla de servicios con mTLS y métricas por ruta"],
      ["Docker", "Imágenes de contenedor reproducibles"],
      ["AWS Lambda", "Funciones para integraciones y automatización"],
      ["AWS Fargate", "Contenedores sin administrar nodos"],
      ["Amazon EC2", "Cómputo dedicado y cargas con estado"],
      ["API Gateway", "Exposición de APIs administradas"],
      ["Amazon SQS · SNS", "Colas y notificaciones desacopladas"],
      ["Amazon MSK", "Kafka administrado para eventos"],
      ["RabbitMQ", "Mensajería entre servicios"],
    ]},
    { key: "ia", nombre: "IA y LLMOps", corto: "IA", items: [
      ["Langfuse", "Trazas, evaluaciones y costos de LLM, autoalojado"],
      ["Amazon Bedrock", "Modelos fundacionales administrados"],
      ["Claude · Gemini · Codex", "Asistentes de ingeniería en el día a día"],
      ["SDD", "Desarrollo guiado por especificaciones"],
    ]},
    { key: "datos", nombre: "Datos", corto: "Datos", items: [
      ["Aurora PostgreSQL", "Base relacional administrada con alta disponibilidad"],
      ["RDS PostgreSQL", "Bases relacionales por servicio"],
      ["ElastiCache (Valkey/Redis)", "Caché y colas en memoria"],
      ["OpenSearch · Elasticsearch", "Búsqueda y analítica de logs"],
      ["MongoDB Atlas", "Base documental administrada"],
      ["Amazon S3", "Almacenamiento de objetos con ciclo de vida y cifrado"],
      ["Amazon Athena", "Consultas SQL sobre datos en S3"],
      ["pgvector", "Búsqueda vectorial sobre PostgreSQL"],
      ["PgBouncer", "Pooler en modo transacción con presupuesto de conexiones"],
      ["ClickHouse", "Almacén analítico columnar para trazas de LLM"],
    ]},
    { key: "finops", nombre: "FinOps", corto: "FinOps", items: [
      ["Cost Explorer", "Análisis de gasto por cuenta, servicio y etiqueta"],
      ["Savings Plans", "Compromisos de uso de cómputo"],
      ["Reserved Instances", "Reservas para bases de datos y cachés"],
      ["Compute Optimizer", "Ajuste de tamaño basado en uso real"],
      ["S3 Lifecycle", "Retención y transición de almacenamiento"],
    ]},
    { key: "entrega", nombre: "IaC y entrega", corto: "IaC", items: [
      ["Terraform", "Infraestructura como código en módulos reutilizables"],
      ["Terragrunt", "Composición por ambiente y región sin duplicar código"],
      ["AWS CloudFormation", "Stacks nativos donde el servicio lo exige"],
      ["GitHub Actions", "Integración continua y pipeline de imágenes"],
      ["GitLab CI", "Pipelines de despliegue de servicios"],
      ["Python (boto3)", "Automatización y verificación sobre AWS"],
      ["Bash · PowerShell", "Scripts operativos idempotentes"],
      ["Cosign + KMS", "Firma de imágenes por digest con llave que nunca sale del HSM"],
      ["Snyk", "Escaneo de contenedores, IaC y dependencias que falla cerrado"],
      ["TFLint · tfsec · Checkov", "Análisis estático de IaC en cada pull request"],
    ]},
  ];

  /* Lista filtrable con un solo punto de tabulación (flechas para recorrerla) */
  const P = window.Portafolio;
  const list = document.getElementById("tech-list");
  const status = document.getElementById("tech-status");
  if (list) {
    const frag = document.createDocumentFragment();
    DOMINIOS.forEach((d) => d.items.forEach(([name, tip]) => {
      const li = document.createElement("li");
      li.className = "chip";
      li.dataset.domain = d.key;
      li.dataset.tip = tip;
      li.textContent = name;
      frag.appendChild(li);
    }));
    list.appendChild(frag);
    const chips = Array.from(list.querySelectorAll(".chip"));
    chips.forEach((c, i) => { c.tabIndex = i === 0 ? 0 : -1; if (P) P.bindTip(c, false); });
    list.addEventListener("keydown", (e) => {
      const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      const vis = chips.filter((c) => !c.hidden);
      const i = vis.indexOf(document.activeElement);
      if (!step || i < 0) return;
      e.preventDefault();
      const next = vis[(i + step + vis.length) % vis.length];
      vis[i].tabIndex = -1;
      next.tabIndex = 0;
      next.focus();
    });
    if (P) P.onFilter((target) => {
      if (target !== list) return;
      const vis = chips.filter((c) => !c.hidden);
      chips.forEach((c) => { c.tabIndex = -1; });
      if (vis[0]) vis[0].tabIndex = 0;
      if (status) status.textContent = "Mostrando " + vis.length + " tecnologías";
    });
  }

  /* Gráfico radial */
  if (!P) return;

  // Tinta de la etiqueta: blanca o casi negra, la que más contraste dé sobre el color del sector.
  const luminancia = (hex) => {
    const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const tinta = (hex) => (1.05 / (luminancia(hex) + 0.05) >= (luminancia(hex) + 0.05) / 0.0597 ? "#ffffff" : "#16191f");
  P.Charts.register("#chart-tecnologias", (p) => {
    const narrow = document.getElementById("chart-tecnologias").clientWidth < 460;
    return {
    tooltip: {
      trigger: "item",
      backgroundColor: p.surface,
      borderColor: p.border,
      textStyle: { color: p.text, fontFamily: p.font, fontSize: 12 },
      formatter: (info) => {
        const t = info.data && info.data.tip;
        return "<strong>" + info.name + "</strong>" + (t ? "<br><span style='opacity:.8'>" + t + "</span>" : "");
      },
      extraCssText: "max-width:260px;white-space:normal;",
    },
    series: [{
      type: "sunburst",
      radius: ["14%", "99%"],
      sort: null,
      nodeClick: "rootToNode",
      emphasis: { focus: "ancestor" },
      itemStyle: { borderColor: p.surface, borderWidth: 2, borderRadius: 4 },
      label: { fontFamily: p.font },
      levels: [
        {},
        { r0: "14%", r: "44%", label: { rotate: "radial", minAngle: 12, fontSize: narrow ? 9 : 11, fontWeight: 700, formatter: (i) => i.data.corto || i.name } },
        { r0: "44%", r: "99%", label: { show: !narrow, rotate: "radial", fontSize: 10, overflow: "truncate", width: 110 } },
      ],
      data: DOMINIOS.map((d) => ({
        name: d.nombre,
        corto: d.corto,
        itemStyle: { color: p.d[d.key] },
        label: { color: tinta(p.d[d.key]) },
        children: d.items.map(([name, tip]) => ({ name, value: 1, tip, itemStyle: { color: p.d[d.key] }, label: { color: tinta(p.d[d.key]) } })),
      })),
    }],
    };
  });
})();
