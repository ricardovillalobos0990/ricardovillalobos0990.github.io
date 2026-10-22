/* Proyecto FinOps: ciclo de la práctica y curva ilustrativa de suelo horario. */
(function () {
  "use strict";
  const P = window.Portafolio;
  if (!P) return;

  /* ---- Ciclo informar · optimizar · operar ------------------------------- */
  const FASES = [
    { id: "Informar", ang: -90, tip: "Captura automatizada, reconciliación con la factura y lectura con método.", acts: [
      ["Captura reconciliada", "AWS y GCP capturados dos veces por mes y cuadrados con la factura cuenta por cuenta."],
      ["Series comparables", "Sin cargas que cambiaron de factura y con cargos trimestrales prorrateados."],
      ["Atribución", "Por etiqueta, por tipo de uso y por instancia."],
    ]},
    { id: "Optimizar", ang: 30, tip: "Primero arquitectura, después compromisos sobre la base ya optimizada.", acts: [
      ["Logs", "Clase de menor costo, menos líneas por petición, flujos redundantes fuera."],
      ["Red", "Endpoints en lugar de NAT y tráfico interno por red privada."],
      ["arm64", "Graviton y dimensionamiento por la métrica que se agota primero."],
      ["Huérfanos", "Retiro de recursos sin uso, siempre con respaldo previo."],
      ["Compromisos", "Suelo horario cubierto y reservas específicas donde aplica."],
    ]},
    { id: "Operar", ang: 150, tip: "Revisión mensual y vigilancia de lo que vence o se desactualiza.", acts: [
      ["Revisión mensual", "Informe de variaciones contra el promedio de tres meses."],
      ["Vencimientos", "Compromisos escalonados para que nada vuelva solo a bajo demanda."],
      ["Versiones K8s", "Upgrades de Kubernetes planificados por fin de soporte estándar."],
    ]},
  ];

  const rad = (a) => (a * Math.PI) / 180;

  P.Charts.register("#chart-ciclo", (p) => {
    const el = document.getElementById("chart-ciclo");
    const narrow = el.clientWidth < 520;
    const nodes = [];
    const links = [];
    const R1 = 100, R2 = 225;
    FASES.forEach((f) => {
      nodes.push({
        name: f.id, tip: f.tip,
        x: Math.cos(rad(f.ang)) * R1, y: Math.sin(rad(f.ang)) * R1,
        symbolSize: narrow ? 74 : 82,
        itemStyle: { color: p.d.finops },
        label: { show: true, fontSize: narrow ? 12 : 13, fontWeight: 700, color: p.mode === "dark" ? "#0a0f1e" : "#ffffff" },
      });
      if (narrow) return;
      const spread = f.acts.length > 3 ? 22 : 26;
      f.acts.forEach(([name, tip], i) => {
        const a = f.ang + (i - (f.acts.length - 1) / 2) * spread;
        const x = Math.cos(rad(a)) * R2, y = Math.sin(rad(a)) * R2;
        nodes.push({
          name, tip, x, y,
          symbolSize: 13,
          itemStyle: { color: p.surface, borderColor: p.d.finops, borderWidth: 2 },
          label: {
            show: true, color: p.text2, fontSize: 11,
            position: Math.abs(x) < 40 ? (y < 0 ? "top" : "bottom") : (x > 0 ? "right" : "left"),
          },
        });
        links.push({ source: f.id, target: name, lineStyle: { color: p.border, width: 1.2, curveness: 0 }, symbol: ["none", "none"] });
      });
    });
    const ciclo = [
      { source: "Informar", target: "Optimizar" },
      { source: "Optimizar", target: "Operar" },
      { source: "Operar", target: "Informar" },
    ];
    ciclo.forEach((l) => { l.lineStyle = { color: p.d.finops, width: 2.5, curveness: 0.35 }; l.symbol = ["none", "arrow"]; l.symbolSize = 12; links.push(l); });
    const side = Math.max(160, Math.min(el.clientWidth - (narrow ? 60 : 260), el.clientHeight - 70));
    return {
      tooltip: {
        backgroundColor: p.surface, borderColor: p.border,
        textStyle: { color: p.text, fontFamily: p.font, fontSize: 12 },
        extraCssText: "max-width:260px;white-space:normal;",
        formatter: (i) => (i.dataType === "node" ? "<strong>" + i.name + "</strong><br>" + (i.data.tip || "") : ""),
      },
      series: [{
        type: "graph", layout: "none", roam: false,
        left: "center", top: "middle", width: side, height: side * (narrow ? 0.9 : 1),
        label: { fontFamily: p.font },
        edgeSymbol: ["none", "arrow"],
        data: nodes, links,
        emphasis: { focus: "adjacency", lineStyle: { width: 3 } },
      }],
    };
  });

  /* ---- Suelo horario (curva ilustrativa, sin datos reales) ---------------- */
  const DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
  const horas = [], consumo = [];
  for (let d = 0; d < 7; d++) {
    for (let h = 0; h < 24; h++) {
      const laboral = d < 5;
      const dia = Math.max(0, Math.sin(((h - 6) / 16) * Math.PI));
      const ruido = Math.sin(d * 7.3 + h * 1.7) * 2.2 + Math.cos(h * 0.9 + d) * 1.4;
      const v = 58 + (laboral ? 30 : 11) * dia + ruido;
      horas.push(DIAS[d] + " " + String(h).padStart(2, "0") + ":00");
      consumo.push(Math.round(v * 10) / 10);
    }
  }
  const suelo = Math.floor(Math.min(...consumo));
  const pico = Math.ceil(Math.max(...consumo));
  const cubierto = consumo.map((v) => Math.min(v, suelo));
  const demanda = consumo.map((v) => Math.round((v - suelo) * 10) / 10);

  P.Charts.register("#chart-suelo", (p) => ({
    grid: { left: 12, right: 12, top: document.getElementById("chart-suelo").clientWidth < 520 ? 92 : 44, bottom: 30, containLabel: false },
    legend: {
      top: 0, left: 0, itemWidth: 14, itemHeight: 10, itemGap: 22, icon: "roundRect",
      textStyle: { color: p.text2, fontFamily: p.font, fontSize: 12 },
      data: ["Cubierto por el compromiso", "A tarifa bajo demanda", "Compromiso al pico (ocioso en valles)"],
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: p.surface, borderColor: p.border,
      textStyle: { color: p.text, fontFamily: p.font, fontSize: 12 },
      formatter: (items) => items[0].axisValue,
    },
    xAxis: {
      type: "category", data: horas, boundaryGap: false,
      axisLine: { lineStyle: { color: p.border } },
      axisTick: { show: false },
      axisLabel: {
        color: p.muted, fontFamily: p.font, fontSize: 11,
        interval: (i) => i % 24 === 12,
        formatter: (v) => v.split(" ")[0],
      },
    },
    yAxis: {
      type: "value", min: 0, max: pico + 6,
      axisLabel: { show: false }, splitLine: { show: false },
    },
    series: [
      {
        name: "Cubierto por el compromiso", type: "line", stack: "c", symbol: "none",
        lineStyle: { width: 0 }, itemStyle: { color: p.d.finops }, areaStyle: { color: p.d.finops, opacity: 0.55 },
        data: cubierto,
      },
      {
        name: "A tarifa bajo demanda", type: "line", stack: "c", symbol: "none",
        lineStyle: { width: 1.5, color: p.accent2 }, itemStyle: { color: p.accent2 }, areaStyle: { color: p.accent2, opacity: 0.28 },
        data: demanda,
      },
      {
        name: "Compromiso al pico (ocioso en valles)", type: "line", symbol: "none",
        lineStyle: { type: "dashed", width: 1.5, color: p.muted },
        itemStyle: { color: p.muted },
        data: consumo.map(() => pico),
        markLine: {
          silent: true, symbol: "none",
          label: { formatter: "suelo horario", color: p.text2, fontFamily: p.font, position: "insideEndBottom" },
          lineStyle: { color: p.d.finops, width: 2 },
          data: [{ yAxis: suelo }],
        },
      },
    ],
  }));
})();
