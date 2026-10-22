/* ==========================================================================
   Portafolio · comportamiento común
   - Datos de contacto (edita PERFIL: los enlaces vacíos no se muestran)
   - Tema claro/oscuro, menú móvil, aparición al hacer scroll
   - Índice lateral con resaltado, tooltips, filtro por dominio
   - Diagramas draw.io embebidos con el visor oficial de diagrams.net
   - Gráficos con Apache ECharts que siguen el tema
   ========================================================================== */

/* ---- 1. Datos de contacto -------------------------------------------------
   Llena solo lo que quieras publicar. Un valor vacío oculta su botón; si no
   queda ningún canal, la sección de contacto y su enlace del menú se ocultan.
   - email: solo un correo personal, nunca el de trabajo.
   - cv: no subas el PDF del CV a este repositorio (nombra al empleador y queda
     en el historial público). Déjalo vacío o usa una URL externa (https://…)
     a una versión sin el nombre del empleador.                               */
const PERFIL = {
  linkedin: "",        // ej. https://www.linkedin.com/in/tu-usuario
  email: "ricardovillalobos0990@gmail.com",
  cv: "",              // vacío, o una URL externa https://…
};

(function () {
  "use strict";

  const root = document.documentElement;
  root.classList.remove("no-js");
  const BASE = document.body.dataset.base || "./";

  /* ---- Contacto ---------------------------------------------------------- */
  document.querySelectorAll("[data-perfil]").forEach((el) => {
    const key = el.dataset.perfil;
    let value = key.split(".").reduce((o, k) => (o ? o[k] : undefined), PERFIL);
    if (!value) { el.hidden = true; return; }
    const externo = /^https?:/i.test(value);
    if (el.hasAttribute("data-perfil-texto")) el.textContent = value;
    if (key === "email") value = "mailto:" + value;
    else if (key === "cv" && !externo) value = BASE + value.replace(/^\.?\//, "");
    el.setAttribute("href", value);
    if (key === "cv" && !externo) el.setAttribute("download", "");
    else if (key !== "email") { el.target = "_blank"; el.rel = "noopener"; }
    el.hidden = false;
  });
  document.querySelectorAll("[data-perfil-group]").forEach((group) => {
    if (group.querySelectorAll("[data-perfil]:not([hidden])").length) return;
    group.hidden = true;
    const sec = group.closest("section[id]");
    if (!sec) return;
    sec.hidden = true;
    document.querySelectorAll('a[href$="#' + sec.id + '"]').forEach((a) => { a.hidden = true; });
  });

  /* ---- Tema ---------------------------------------------------------------- */
  const THEME_KEY = "portafolio-tema";
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const readStored = () => { try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; } };
  const store = (v) => { try { localStorage.setItem(THEME_KEY, v); } catch (e) { /* sin almacenamiento */ } };
  const currentTheme = () => root.dataset.theme || (media.matches ? "dark" : "light");
  const themeListeners = [];
  const onThemeChange = (fn) => themeListeners.push(fn);
  const syncThemeColor = () => {
    const bg = getComputedStyle(document.body).backgroundColor;
    document.querySelectorAll('meta[name="theme-color"]').forEach((m) => {
      if (root.dataset.theme) { m.removeAttribute("media"); m.setAttribute("content", bg); }
    });
  };
  const emitTheme = () => {
    syncThemeColor();
    themeListeners.forEach((fn) => { try { fn(currentTheme()); } catch (e) { console.error(e); } });
  };

  const stored = readStored();
  if (stored === "light" || stored === "dark") root.dataset.theme = stored;
  syncThemeColor();
  media.addEventListener?.("change", () => { if (!root.dataset.theme) emitTheme(); });

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    const sync = () => btn.setAttribute("aria-label", currentTheme() === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
    sync();
    btn.addEventListener("click", () => {
      const next = currentTheme() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      store(next);
      sync();
      emitTheme();
    });
  });

  /* ---- Menú móvil ---------------------------------------------------------- */
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navLinks = document.querySelector(".nav-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
    navLinks.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => {
      navLinks.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    }));
  }

  /* ---- Aparición ----------------------------------------------------------- */
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const reveals = document.querySelectorAll(".reveal");
  if (!reduceMotion && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("in"));
  }

  /* ---- Índice con resaltado ------------------------------------------------ */
  const tocLinks = Array.from(document.querySelectorAll(".toc a[href^='#']"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    const map = new Map();
    tocLinks.forEach((a) => { const s = document.getElementById(a.getAttribute("href").slice(1)); if (s) map.set(s, a); });
    const setActive = (a) => {
      tocLinks.forEach((l) => l.classList.toggle("active", l === a));
      if (a && window.matchMedia("(max-width: 960px)").matches) {
        const list = a.closest("ol");
        if (list) list.scrollTo({ left: a.offsetLeft - 16, behavior: reduceMotion ? "auto" : "smooth" });
      }
    };
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) setActive(map.get(e.target)); });
    }, { rootMargin: "-35% 0px -60% 0px" });
    map.forEach((_, s) => spy.observe(s));
  }

  /* ---- Tooltips ------------------------------------------------------------ */
  const tip = document.createElement("div");
  tip.className = "tooltip";
  tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);
  const showTip = (el) => {
    tip.textContent = el.dataset.tip;
    const r = el.getBoundingClientRect();
    tip.classList.add("show");
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    const left = Math.min(Math.max(8, r.left + r.width / 2 - tw / 2), window.innerWidth - tw - 8);
    let top = r.top - th - 8;
    if (top < 8) top = r.bottom + 8;
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  };
  const hideTip = () => tip.classList.remove("show");
  /** Activa el tooltip de un elemento con data-tip. focusable=false deja el tabindex a cargo de quien llama. */
  const bindTip = (el, focusable = true) => {
    if (focusable && !el.hasAttribute("tabindex")) el.setAttribute("tabindex", "0");
    el.setAttribute("aria-label", el.textContent.trim() + ": " + el.dataset.tip);
    el.addEventListener("mouseenter", () => showTip(el));
    el.addEventListener("mouseleave", hideTip);
    el.addEventListener("focus", () => showTip(el));
    el.addEventListener("blur", hideTip);
  };
  document.querySelectorAll("[data-tip]").forEach((el) => bindTip(el));
  window.addEventListener("scroll", hideTip, { passive: true });

  /* ---- Filtro por dominio -------------------------------------------------- */
  const filterListeners = [];
  document.querySelectorAll("[data-filter-group]").forEach((bar) => {
    const target = document.querySelector(bar.dataset.filterGroup);
    if (!target) return;
    const buttons = bar.querySelectorAll(".filter-btn");
    buttons.forEach((btn) => btn.addEventListener("click", () => {
      buttons.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      const d = btn.dataset.filter;
      target.querySelectorAll("[data-domain]").forEach((item) => {
        item.hidden = !(d === "todos" || item.dataset.domain === d);
      });
      filterListeners.forEach((fn) => fn(target, btn));
    }));
  });

  /* ---- Diagramas draw.io --------------------------------------------------- */
  // El script del visor de diagrams.net va fijado a una versión y con SRI. Las formas, estilos e
  // imágenes auxiliares las descarga el propio visor desde viewer.diagrams.net en tiempo de ejecución.
  const VIEWER_URL = "https://cdn.jsdelivr.net/gh/jgraph/drawio@v32.0.2/src/main/webapp/js/viewer-static.min.js";
  const VIEWER_SRI = "sha384-ieuF8OiNf95uXbw63j7ih5II3TzlQXmdV9s3eL8l63F59tJpTB3svI+2MfFvyod4";
  let viewerPromise = null;
  const loadViewer = () => {
    if (viewerPromise) return viewerPromise;
    viewerPromise = new Promise((resolve, reject) => {
      if (window.GraphViewer) { resolve(window.GraphViewer); return; }
      // Evita que el visor procese la página por su cuenta: se crea cada visor a mano.
      window.onDrawioViewerLoad = function () { resolve(window.GraphViewer); };
      const s = document.createElement("script");
      s.src = VIEWER_URL;
      s.integrity = VIEWER_SRI;
      s.crossOrigin = "anonymous";
      s.async = true;
      s.onload = () => { if (window.GraphViewer) resolve(window.GraphViewer); };
      s.onerror = () => reject(new Error("No se pudo cargar el visor de diagrams.net"));
      document.head.appendChild(s);
    });
    return viewerPromise;
  };

  const absUrl = (rel) => new URL(rel, document.baseURI).href;

  const renderDiagram = async (fig) => {
    if (fig.dataset.rendered) return;
    fig.dataset.rendered = "1";
    const src = fig.dataset.drawio;
    const frame = fig.querySelector(".diagram-frame");
    const fail = (msg) => {
      frame.innerHTML = "";
      const box = document.createElement("div");
      box.className = "diagram-error";
      box.innerHTML = msg + ' <a href="' + src + '" download>Descargar el diagrama</a>';
      frame.appendChild(box);
    };
    try {
      const [xml, GV] = await Promise.all([
        fetch(src, { cache: "no-cache" }).then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); }),
        loadViewer(),
      ]);
      const holder = document.createElement("div");
      holder.className = "mxgraph";
      holder.style.maxWidth = "100%";
      const config = {
        highlight: "#0e7490",
        nav: true,
        resize: true,
        center: true,
        "auto-fit": true,
        "toolbar-nohide": true,
        toolbar: "zoom layers lightbox",
        "toolbar-position": "top",
        lightbox: true,
        "dark-mode": "light",
        edit: null,
        xml: xml,
      };
      holder.setAttribute("data-mxgraph", JSON.stringify(config));
      frame.innerHTML = "";
      frame.appendChild(holder);
      GV.createViewerForElement(holder, (viewer) => {
        const zoom = fig.querySelector("[data-zoom]");
        if (zoom && viewer && typeof viewer.showLightbox === "function") {
          zoom.hidden = false;
          zoom.addEventListener("click", () => viewer.showLightbox());
        }
      });
    } catch (e) {
      console.error(e);
      fail("No se pudo mostrar el diagrama aquí.");
    }
  };

  const diagrams = document.querySelectorAll("figure.diagram[data-drawio]");
  diagrams.forEach((fig) => {
    const open = fig.querySelector("[data-open-drawio]");
    if (open) open.href = "https://app.diagrams.net/?lightbox=1&nav=1#U" + encodeURIComponent(absUrl(fig.dataset.drawio));
  });
  if (diagrams.length) {
    if ("IntersectionObserver" in window) {
      const dio = new IntersectionObserver((entries) => {
        entries.forEach((e) => { if (e.isIntersecting) { renderDiagram(e.target); dio.unobserve(e.target); } });
      }, { rootMargin: "300px 0px" });
      diagrams.forEach((d) => dio.observe(d));
    } else {
      diagrams.forEach(renderDiagram);
    }
  }

  /* ---- Gráficos ------------------------------------------------------------ */
  const css = (name) => getComputedStyle(root).getPropertyValue(name).trim();
  const palette = () => ({
    mode: currentTheme(),
    text: css("--text"),
    text2: css("--text-2"),
    muted: css("--muted"),
    border: css("--border"),
    surface: css("--surface"),
    surface2: css("--surface-2"),
    accent: css("--accent"),
    accent2: css("--accent-2"),
    font: "Inter, system-ui, sans-serif",
    mono: "JetBrains Mono, Consolas, monospace",
    d: {
      gobierno: css("--d-gobierno"), red: css("--d-red"), seguridad: css("--d-seguridad"),
      cumplimiento: css("--d-cumplimiento"), observabilidad: css("--d-observabilidad"),
      computo: css("--d-computo"), datos: css("--d-datos"), entrega: css("--d-entrega"),
      borde: css("--d-borde"), ia: css("--d-ia"), finops: css("--d-finops"),
    },
  });

  const registry = [];
  const Charts = {
    /** Registra un gráfico: build(p) devuelve la opción de ECharts para la paleta p. */
    register(selector, build) {
      const el = typeof selector === "string" ? document.querySelector(selector) : selector;
      if (!el) return;
      registry.push({ el, build, chart: null });
    },
    palette,
  };
  window.Portafolio = { Charts, onThemeChange, currentTheme, PERFIL, bindTip, onFilter: (fn) => filterListeners.push(fn) };

  const buildOption = (entry) => {
    const opt = entry.build(palette());
    opt.aria = Object.assign({ enabled: true }, opt.aria || {});
    return opt;
  };
  const initChart = (entry) => {
    if (entry.chart || !window.echarts) return;
    entry.chart = window.echarts.init(entry.el, null, { renderer: "svg" });
    entry.chart.setOption(buildOption(entry), true);
    if ("ResizeObserver" in window) new ResizeObserver(() => entry.chart && entry.chart.resize()).observe(entry.el);
    else window.addEventListener("resize", () => entry.chart.resize());
  };

  // DOMContentLoaded llega cuando ya corrieron los scripts de cada página (que registran sus gráficos)
  // y no espera a recursos lentos como el visor de diagramas. Los gráficos son livianos: se inician todos.
  document.addEventListener("DOMContentLoaded", () => {
    if (!registry.length) return;
    if (!window.echarts) {
      registry.forEach((r) => { r.el.innerHTML = '<p class="chart-note">El gráfico necesita JavaScript y conexión a jsDelivr.</p>'; });
      return;
    }
    registry.forEach((r) => { try { initChart(r); } catch (e) { console.error(e); } });
    // ECharts mide el texto al dibujar: cuando llegan las fuentes web, se vuelve a dibujar con las medidas reales.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => registry.forEach((r) => { if (r.chart) r.chart.setOption(buildOption(r), true); }));
    }
  });

  onThemeChange(() => {
    registry.forEach((r) => { if (r.chart) r.chart.setOption(buildOption(r), true); });
  });

  /* ---- Año en el pie ------------------------------------------------------- */
  document.querySelectorAll("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
