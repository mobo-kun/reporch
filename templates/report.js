/* Reporch page script: charts, TOC, progress, drawer, slides, image zoom. No network access. */
(function () {
  "use strict";
  var doc = document.documentElement;
  var rtl = doc.dir === "rtl";
  var lang = doc.lang || "en";
  var printing = /[?&]print\b/.test(location.search) || window.__REPORCH_PRINT__ === true;
  var calm = printing || (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  var css = getComputedStyle(doc);
  var palette = css.getPropertyValue("--chart").split(",").map(function (s) {
    var v = s.trim().replace(/^var\((--[\w-]+)\)$/, "$1");
    return v.indexOf("--") === 0 ? css.getPropertyValue(v).trim() : v;
  }).filter(Boolean);
  var ink = css.getPropertyValue("--ink").trim(), soft = css.getPropertyValue("--ink-soft").trim();
  var line = css.getPropertyValue("--line").trim();
  var font = css.getPropertyValue("--font").trim();

  var FA = "۰۱۲۳۴۵۶۷۸۹";
  function digits(s) {
    if (lang !== "fa" || typeof s !== "number") return String(s);   // codes such as "T1" keep Latin digits
    return String(s).replace(/\d/g, function (d) { return FA[d]; }).replace(/\./g, "٫");
  }
  function fmt(v, kind) {
    if (typeof v !== "number") return digits(v);
    if (kind === "percent") return digits(+(v * 100).toFixed(1)) + (lang === "fa" ? "٪" : "%");
    return digits(Math.abs(v) >= 100 ? Math.round(v) : +v.toFixed(2));
  }

  function build(spec) {
    var c = spec.chart, t = spec.table, cols = t.columns, rows = t.rows, f = t.format || {};
    var name = function (col) { return (t.labels && t.labels[col]) || col; };
    var col = function (name) { var i = cols.indexOf(name); return rows.map(function (r) { return r[i]; }); };
    var cats = col(c.x).map(digits);
    var series = c.series || [];
    var valueFmt = f[series[0]];
    var base = {
      color: palette, animation: !calm,
      textStyle: { fontFamily: font, color: ink },
      tooltip: { trigger: "item", valueFormatter: function (v) { return fmt(v, valueFmt); } },
      legend: series.length > 1 ? { bottom: 0, textStyle: { color: soft } } : undefined,
      grid: { left: 12, right: 12, top: 24, bottom: series.length > 1 ? 40 : 12, containLabel: true }
    };
    var valueAxis = { type: "value", splitLine: { lineStyle: { color: line } },
      axisLabel: { color: soft, formatter: function (v) { return fmt(v, valueFmt); } } };
    var catAxis = { type: "category", data: cats, inverse: rtl, axisLabel: { color: soft, interval: 0, width: 110, overflow: "break" },
      axisLine: { lineStyle: { color: line } } };
    var label = { show: true, color: ink, formatter: function (p) { return fmt(Array.isArray(p.value) ? p.value[1] : p.value, valueFmt); } };
    var k = c.kind;

    if (k === "bar" || k === "stackedBar" || k === "line" || k === "barHorizontal" || k === "rangeBar") {
      var horiz = k === "barHorizontal" || k === "rangeBar";
      if (horiz) { base.grid[rtl ? "left" : "right"] = 64; } else { base.grid.top = 32; }
      var o = Object.assign(base, horiz
        ? { xAxis: Object.assign({}, valueAxis, { inverse: rtl }), yAxis: Object.assign({}, catAxis, { inverse: true, position: rtl ? "right" : "left" }) }
        : { xAxis: catAxis, yAxis: Object.assign({}, valueAxis, { position: rtl ? "right" : "left" }) });
      o.tooltip.trigger = "axis";
      o.series = series.map(function (s) {
        return { name: name(s), type: k === "line" ? "line" : "bar", data: col(s), stack: k === "stackedBar" ? "all" : undefined,
          barMaxWidth: 36, label: k !== "rangeBar" && (series.length === 1 || k === "stackedBar") ? Object.assign({}, label, { position: k === "stackedBar" ? "inside" : (horiz ? (rtl ? "left" : "right") : "top") }) : undefined,
          itemStyle: { borderRadius: k === "stackedBar" ? 0 : 4 } };
      });
      if (k === "rangeBar" && c.range) {
        var lo = col(c.range[0]), hi = col(c.range[1]), vals0 = col(series[0]);
        o.series.push({ name: c.range.map(name).join("–"), type: "custom", z: 5,
          renderItem: function (params, api) {
            var y = api.value(0), a = api.coord([api.value(1), y]), b = api.coord([api.value(2), y]);
            var h = 10, st = { stroke: ink, lineWidth: 1.5 };
            var val = vals0[params.dataIndex], end = rtl ? Math.min(a[0], b[0]) - 6 : Math.max(a[0], b[0]) + 6;
            return { type: "group", children: [
              { type: "text", x: end, y: a[1], style: { text: fmt(val, valueFmt), fill: ink, font: "12px " + font,
                align: rtl ? "right" : "left", verticalAlign: "middle" } },
              { type: "line", shape: { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }, style: st },
              { type: "line", shape: { x1: a[0], y1: a[1] - h / 2, x2: a[0], y2: a[1] + h / 2 }, style: st },
              { type: "line", shape: { x1: b[0], y1: b[1] - h / 2, x2: b[0], y2: b[1] + h / 2 }, style: st }] };
          },
          encode: { x: [1, 2], y: 0 }, data: cats.map(function (_, i) { return [i, lo[i], hi[i]]; }),
          tooltip: { valueFormatter: function (v) { return fmt(v, valueFmt); } } });
      }
      return o;
    }
    if (k === "doughnut" || k === "funnel") {
      var vals = col(series[0]);
      base.legend = { bottom: 0, textStyle: { color: soft } };
      base.series = [{ type: k === "doughnut" ? "pie" : "funnel", radius: k === "doughnut" ? ["46%", "72%"] : undefined,
        sort: k === "funnel" ? "none" : undefined, left: "10%", width: k === "funnel" ? "80%" : undefined,
        label: { color: ink, formatter: function (p) { return p.name + "\n" + fmt(p.value, valueFmt); } },
        data: cats.map(function (n, i) { return { name: n, value: vals[i] }; }) }];
      return base;
    }
    if (k === "scatter") {
      base.xAxis = Object.assign({}, valueAxis, { name: name(c.x), inverse: rtl });
      base.yAxis = Object.assign({}, valueAxis, { name: name(series[0]), position: rtl ? "right" : "left" });
      var xs = col(c.x), ys = col(series[0]);
      base.series = [{ type: "scatter", symbolSize: 12, data: xs.map(function (x, i) { return [x, ys[i]]; }) }];
      return base;
    }
    if (k === "heatmap") {
      var ys2 = col(c.y), v2 = col(series[0]);
      var xc = Array.from(new Set(col(c.x))), yc = Array.from(new Set(ys2));
      var xsAll = col(c.x);
      base.xAxis = { type: "category", data: xc.map(digits), inverse: rtl, axisLabel: { color: soft } };
      base.yAxis = { type: "category", data: yc.map(digits), position: rtl ? "right" : "left", axisLabel: { color: soft } };
      base.visualMap = { min: Math.min.apply(null, v2), max: Math.max.apply(null, v2), orient: "horizontal", left: "center", bottom: 0,
        inRange: { color: [css.getPropertyValue("--primary-50").trim(), css.getPropertyValue("--primary-700").trim()] } };
      base.grid.bottom = 56;
      base.series = [{ type: "heatmap", label: { show: true, formatter: function (p) { return fmt(p.value[2], valueFmt); } },
        data: v2.map(function (v, i) { return [xc.indexOf(xsAll[i]), yc.indexOf(ys2[i]), v]; }) }];
      return base;
    }
    if (k === "radar") {
      var maxv = c.max || Math.max.apply(null, [].concat.apply([], series.map(col)));
      base.radar = { indicator: cats.map(function (n) { return { name: n, max: maxv }; }), axisName: { color: soft } };
      base.legend = { bottom: 0 };
      base.series = [{ type: "radar", data: series.map(function (s) { return { name: name(s), value: col(s) }; }) }];
      return base;
    }
    if (k === "box") {
      base.xAxis = catAxis; base.yAxis = Object.assign({}, valueAxis, { position: rtl ? "right" : "left" });
      var bx = c.box.map(col);
      base.series = [{ type: "boxplot", data: cats.map(function (_, i) { return bx.map(function (b) { return b[i]; }); }) }];
      return base;
    }
    if (k === "sankey") {
      var tg = col(c.target), vv = col(series[0]), src = col(c.x);
      var names = Array.from(new Set(src.concat(tg)));
      base.series = [{ type: "sankey", orient: "horizontal", nodeAlign: rtl ? "right" : "left",
        data: names.map(function (n) { return { name: digits(n) }; }),
        links: src.map(function (s, i) { return { source: digits(s), target: digits(tg[i]), value: vv[i] }; }),
        label: { color: ink }, lineStyle: { color: "gradient", opacity: .35 } }];
      return base;
    }
    return null;
  }

  var charts = [];
  function draw(el, attr) {
    if (!window.echarts) return null;
    var opt = build(JSON.parse(document.getElementById(el.getAttribute(attr)).textContent));
    if (!opt) return null;
    var ch = echarts.init(el, null, { renderer: "svg" });
    ch.setOption(opt);
    return ch;
  }
  document.querySelectorAll("[data-chart]").forEach(function (el) { var ch = draw(el, "data-chart"); if (ch) charts.push(ch); });
  window.__REPORCH_CHARTS_READY__ = true;
  var resize = function () { charts.forEach(function (c) { c.resize(); }); };
  window.addEventListener("resize", resize);
  window.addEventListener("beforeprint", resize);

  // Reading progress
  var bar = document.querySelector(".progress");
  if (bar) window.addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? scrollY / h * 100 : 0) + "%";
  }, { passive: true });

  // TOC active state
  var links = Array.prototype.slice.call(document.querySelectorAll(".toc nav a"));
  if ("IntersectionObserver" in window && links.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id); });
      });
    }, { rootMargin: "-10% 0px -70% 0px" });
    document.querySelectorAll("section.sec[id]").forEach(function (s) { io.observe(s); });
  }

  // Drawer (phones)
  var toc = document.querySelector(".toc"), scrim = document.querySelector(".scrim");
  function drawer(open) { if (toc) { toc.classList.toggle("open", open); scrim.classList.toggle("open", open); } }
  document.querySelectorAll("[data-open-toc]").forEach(function (b) { b.addEventListener("click", function () { drawer(true); }); });
  if (scrim) scrim.addEventListener("click", function () { drawer(false); });
  links.forEach(function (a) { a.addEventListener("click", function () { drawer(false); }); });

  // Slides: a 16:9 deck scaled to the window; deck charts are drawn when their slide is first shown
  var deck = document.querySelector(".deck");
  var slides = deck ? Array.prototype.slice.call(deck.querySelectorAll(".slide")) : [];
  var cur = 0, count = deck && deck.querySelector(".count"), prog = deck && deck.querySelector(".deck-progress span");
  function scale() { if (deck) deck.style.setProperty("--deck-scale", Math.min(innerWidth / 1280, (innerHeight - 52) / 720)); }
  function fit(s) {                       // shrink text until the slide fits its frame (never scroll)
    var f = 1; s.style.setProperty("--fit", 1);
    var body = s.querySelector(".s-body") || s;
    while (f > 0.6 && (s.scrollHeight > s.clientHeight + 1 || body.scrollHeight > body.clientHeight + 1)) {
      f -= 0.05; s.style.setProperty("--fit", f.toFixed(2));
    }
  }
  function show(i) {
    cur = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach(function (s, j) { s.classList.toggle("current", j === cur); });
    var s = slides[cur];
    s.querySelectorAll("[data-deck-chart]").forEach(function (el) {
      if (!el.__chart) el.__chart = draw(el, "data-deck-chart"); else el.__chart.resize();
    });
    fit(s);
    if (count) count.textContent = digits(cur + 1) + " / " + digits(slides.length);
    if (prog) prog.style.width = ((cur + 1) / slides.length * 100) + "%";
    if (history.replaceState) history.replaceState(null, "", "#slide-" + (cur + 1));
  }
  function slideMode(on) {
    document.body.classList.toggle("slides", on);
    if (deck) deck.setAttribute("aria-hidden", on ? "false" : "true");
    if (on) { scale(); show(cur); } else { if (history.replaceState) history.replaceState(null, "", location.pathname + location.search); resize(); }
  }
  window.addEventListener("resize", function () { if (document.body.classList.contains("slides")) { scale(); show(cur); } });
  document.querySelectorAll("[data-slides]").forEach(function (b) { b.addEventListener("click", function () { cur = 0; slideMode(true); }); });
  document.querySelectorAll("[data-exit-slides]").forEach(function (b) { b.addEventListener("click", function () { slideMode(false); }); });
  document.querySelectorAll("[data-next]").forEach(function (b) { b.addEventListener("click", function () { show(cur + 1); }); });
  document.querySelectorAll("[data-prev]").forEach(function (b) { b.addEventListener("click", function () { show(cur - 1); }); });
  if (deck) deck.querySelector(".stage").addEventListener("click", function (e) {
    if (e.target.closest("a, button, img, details")) return;
    var forward = rtl ? e.clientX < innerWidth / 2 : e.clientX > innerWidth / 2;
    show(cur + (forward ? 1 : -1));
  });
  document.addEventListener("keydown", function (e) {
    if (!document.body.classList.contains("slides")) return;
    var fwd = rtl ? "ArrowLeft" : "ArrowRight", back = rtl ? "ArrowRight" : "ArrowLeft";
    if (e.key === fwd || e.key === "PageDown" || e.key === " ") { e.preventDefault(); show(cur + 1); }
    if (e.key === back || e.key === "PageUp") { e.preventDefault(); show(cur - 1); }
    if (e.key === "Home") show(0);
    if (e.key === "End") show(slides.length - 1);
    if (e.key === "Escape") slideMode(false);
  });
  var m = /^#slide-(\d+)$/.exec(location.hash) || (/[?&]slides\b/.test(location.search) ? [0, "1"] : null);
  if (m && slides.length) { cur = +m[1] - 1; slideMode(true); }
  window.addEventListener("hashchange", function () {
    var h = /^#slide-(\d+)$/.exec(location.hash);
    if (h && slides.length && +h[1] - 1 !== cur) { cur = +h[1] - 1; slideMode(true); }
  });

  // Image zoom
  var lb = document.querySelector(".lightbox");
  document.querySelectorAll("main figure img").forEach(function (img) {
    img.addEventListener("click", function () { lb.querySelector("img").src = img.src; lb.querySelector("img").alt = img.alt; lb.classList.add("open"); });
  });
  if (lb) lb.addEventListener("click", function () { lb.classList.remove("open"); });
})();
