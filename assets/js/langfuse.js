/* Proyecto LLMOps: gráficos de modelo de costo, CPU, composición y precios públicos de S3. */
(function () {
  "use strict";
  const P = window.Portafolio;
  if (!P) return;

  const tooltip = (p, extra) => Object.assign({
    backgroundColor: p.surface, borderColor: p.border,
    textStyle: { color: p.text, fontFamily: p.font, fontSize: 12 },
    extraCssText: "max-width:280px;white-space:normal;",
  }, extra || {});
  const axisText = (p) => ({ color: p.muted, fontFamily: p.font, fontSize: 11 });

  /* ---- 1. Modelo de costo: ilustrativo ------------------------------------ */
  const xs = [], saas = [], propio = [];
  for (let i = 0; i <= 100; i++) {
    const x = i / 10;
    xs.push(x);
    saas.push(+(0.35 + 0.95 * x).toFixed(3));
    const escalon = x < 3.5 ? 3.2 : x < 7 ? 4.3 : 5.4;
    propio.push(+(escalon + 0.14 * x).toFixed(3));
  }
  P.Charts.register("#chart-modelo", (p) => ({
    grid: { left: 36, right: 16, top: 60, bottom: 36 },
    legend: { top: 0, left: 0, itemGap: 18, textStyle: { color: p.text2, fontFamily: p.font, fontSize: 12 } },
    tooltip: tooltip(p, { trigger: "axis", formatter: () => "Ilustrativo: compara la forma de las curvas, no valores." }),
    xAxis: {
      type: "category", data: xs, boundaryGap: false,
      name: "volumen instrumentado →", nameLocation: "end", nameGap: -2,
      nameTextStyle: { color: p.muted, fontFamily: p.font, fontSize: 11, align: "right", verticalAlign: "top", padding: [14, 0, 0, 0] },
      axisLabel: { show: false }, axisTick: { show: false }, axisLine: { lineStyle: { color: p.border } },
    },
    yAxis: {
      type: "value", name: "costo", nameLocation: "middle", nameRotate: 90, nameGap: 14, nameTextStyle: { color: p.muted, fontFamily: p.font, fontSize: 11 },
      axisLabel: { show: false }, splitLine: { show: false }, axisLine: { show: true, lineStyle: { color: p.border } },
    },
    series: [
      { name: "SaaS: paga por cada unidad", type: "line", data: saas, symbol: "none", lineStyle: { width: 3, color: p.accent2 }, itemStyle: { color: p.accent2 } },
      { name: "Autoalojado: escalones de infraestructura", type: "line", data: propio, symbol: "none", step: false, lineStyle: { width: 3, color: p.d.ia }, itemStyle: { color: p.d.ia },
        areaStyle: { color: p.d.ia, opacity: 0.08 } },
    ],
  }));

  /* ---- 2. CPU antes y después --------------------------------------------- */
  P.Charts.register("#chart-cpu", (p) => ({
    grid: { left: 12, right: 12, top: 40, bottom: 8, containLabel: true },
    legend: { top: 0, left: 0, textStyle: { color: p.text2, fontFamily: p.font, fontSize: 12 } },
    tooltip: tooltip(p, { trigger: "axis", axisPointer: { type: "shadow" } }),
    xAxis: { type: "category", data: ["CPU por evento (índice)", "Pico de CPU (%)"],
      axisLabel: Object.assign(axisText(p), { interval: 0, width: 150, overflow: "break" }), axisTick: { show: false }, axisLine: { lineStyle: { color: p.border } } },
    yAxis: { type: "value", max: 110, axisLabel: { show: false }, splitLine: { lineStyle: { color: p.border, opacity: 0.5 } } },
    series: [
      { name: "Antes", type: "bar", barMaxWidth: 46, data: [100, 78], itemStyle: { color: p.muted, borderRadius: [6, 6, 0, 0] },
        label: { show: true, position: "top", color: p.text2, fontFamily: p.mono, fontSize: 12 } },
      { name: "Después", type: "bar", barMaxWidth: 46, data: [32, 18], itemStyle: { color: p.d.ia, borderRadius: [6, 6, 0, 0] },
        label: { show: true, position: "top", color: p.text, fontFamily: p.mono, fontSize: 12, fontWeight: 700 } },
    ],
  }));

  /* ---- 3. Composición aproximada del costo -------------------------------- */
  const VALORES = { "S3: peticiones y almacenamiento": 53, "Cómputo EC2": 33, "Aurora PostgreSQL": 5, "EBS y otros": 5, "Valkey": 4 };
  P.Charts.register("#chart-composicion", (p) => {
    const narrow = document.getElementById("chart-composicion").clientWidth < 460;
    return {
    tooltip: tooltip(p, { trigger: "item", formatter: (i) => "<strong>" + i.name + "</strong><br>≈ " + i.value + " %" }),
    legend: narrow
      ? { orient: "vertical", left: "center", bottom: 6, itemWidth: 12, itemHeight: 12, itemGap: 6,
          data: Object.keys(VALORES), formatter: (n) => n + "  ≈" + VALORES[n] + " %",
          textStyle: { color: p.text2, fontFamily: p.font, fontSize: 12 } }
      : { orient: "vertical", right: 0, top: "middle", itemWidth: 12, itemHeight: 12,
          data: Object.keys(VALORES), formatter: (n) => n + "  ≈" + VALORES[n] + " %",
          textStyle: { color: p.text2, fontFamily: p.font, fontSize: 12 } },
    series: [{
      type: "pie", radius: narrow ? ["42%", "68%"] : ["48%", "78%"], center: narrow ? ["50%", "38%"] : ["30%", "52%"],
      avoidLabelOverlap: true, label: { show: false },
      labelLine: { length: 6, length2: 6 },
      itemStyle: { borderColor: p.surface, borderWidth: 2 },
      // El orden de las porciones separa verde y naranja, que se confunden con daltonismo; la leyenda va por valor.
      data: [
        { name: "S3: peticiones y almacenamiento", value: 53, itemStyle: { color: p.d.finops } },
        { name: "Aurora PostgreSQL", value: 5, itemStyle: { color: p.d.datos } },
        { name: "Cómputo EC2", value: 33, itemStyle: { color: p.d.computo } },
        { name: "Valkey", value: 4, itemStyle: { color: p.d.red } },
        { name: "EBS y otros", value: 5, itemStyle: { color: p.muted } },
      ],
    }],
    };
  });

  /* ---- 4. Precios públicos de S3, índice Standard = 100 -------------------- */
  P.Charts.register("#chart-s3", (p) => ({
    grid: { left: 12, right: 20, top: 40, bottom: 8, containLabel: true },
    legend: { top: 0, left: 0, textStyle: { color: p.text2, fontFamily: p.font, fontSize: 12 } },
    tooltip: tooltip(p, { trigger: "axis", axisPointer: { type: "shadow" },
      formatter: (items) => items[0].axisValue + "<br>" + items.map((i) => i.marker + i.seriesName + ": " + String(i.value).replace(".", ",")).join("<br>") }),
    xAxis: { type: "category", data: ["Escrituras y listados", "Lecturas", "Almacenamiento"],
      axisLabel: Object.assign(axisText(p), { interval: 0, width: 130, overflow: "break" }), axisTick: { show: false }, axisLine: { lineStyle: { color: p.border } } },
    yAxis: { type: "log", min: 1, max: 1000, logBase: 10, axisLabel: Object.assign(axisText(p), { formatter: (v) => String(v) }), splitLine: { lineStyle: { color: p.border, opacity: 0.5 } } },
    series: [
      { name: "S3 Standard", type: "bar", barMaxWidth: 46, data: [100, 100, 100], itemStyle: { color: p.muted, borderRadius: [6, 6, 0, 0] },
        label: { show: true, position: "top", color: p.text2, fontFamily: p.mono, fontSize: 11, formatter: (i) => String(i.value).replace(".", ",") } },
      { name: "S3 Express One Zone", type: "bar", barMaxWidth: 46, data: [22.6, 7.5, 478], itemStyle: { color: p.d.borde, borderRadius: [6, 6, 0, 0] },
        label: { show: true, position: "top", color: p.text, fontFamily: p.mono, fontSize: 11, fontWeight: 700, formatter: (i) => String(i.value).replace(".", ",") } },
    ],
  }));
})();
