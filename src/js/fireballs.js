/* ============================================================
   FIREBALLS — the CNEOS atmospheric-impact register.
   A world map of every bolide US Government sensors have logged
   since 1988, plus the two rows Avi Loeb argues are interstellar
   meteors (IM1 2014-01-08, IM2 2017-03-09).
   Data is REAL: window.ATLAS_FIREBALLS, baked by
   tools/fetch_fireballs.py from the JPL CNEOS Fireball API, with
   Natural Earth 1:110m land for the coastlines.
   Markup goes in through UI.setH() only.
   ============================================================ */
(function () {
  'use strict';
  const CX = window.CX, S = CX.S;
  const FB = (CX.fireballs = {});
  const D = window.ATLAS_FIREBALLS || { meta: {}, events: [], land: { rings: [] } };
  const EV = D.events || [];
  const RINGS = (D.land && D.land.rings) || [];

  // event tuple layout — keep in sync with tools/fetch_fireballs.py
  const T_DATE = 0, T_ENERGY = 1, T_KT = 2, T_LAT = 3, T_LON = 4, T_ALT = 5, T_VEL = 6, T_TAG = 7;

  const ENERGY_STEPS = [
    { v: 0, label: 'ALL' },
    { v: 0.1, label: '≥ 0.1 kt' },
    { v: 1, label: '≥ 1 kt' },
    { v: 10, label: '≥ 10 kt' },
  ];
  const SPANS = [
    { key: 'all', label: 'ALL YEARS', from: 0, to: 9999 },
    { key: '80s', label: '1988-99', from: 1988, to: 1999 },
    { key: '00s', label: '2000-09', from: 2000, to: 2009 },
    { key: '10s', label: '2010-19', from: 2010, to: 2019 },
    { key: '20s', label: '2020-', from: 2020, to: 9999 },
  ];

  const F = (S.fb = { minKt: 0, span: 'all', speedOnly: false, sel: null, hover: null });

  function esc(s) { return CX.ui.esc(s); }
  function $(id) { return document.getElementById(id); }
  function span() { return SPANS.find(function (s2) { return s2.key === F.span; }) || SPANS[0]; }

  function located(e) { return e[T_LAT] != null && e[T_LON] != null; }
  function passes(e) {
    if (!located(e)) return false;
    if ((e[T_KT] || 0) < F.minKt) return false;
    if (F.speedOnly && e[T_VEL] == null) return false;
    const y = +e[T_DATE].slice(0, 4), sp = span();
    return y >= sp.from && y <= sp.to;
  }
  FB.shown = function () { return EV.filter(passes); };
  FB.cases = function () {
    return (CX.CONTENT.anomalies || []).filter(function (a) { return a.object === 'fb'; });
  };
  FB.byTag = function (tag) {
    return EV.find(function (e) { return e[T_TAG] === tag; }) || null;
  };
  // case id -> the catalog row it is about (F-01 is IM1, F-02 is IM2), matched on date
  FB.rowOfCase = function (id) {
    const c = FB.cases().find(function (a) { return a.id === id; });
    if (!c) return null;
    return EV.find(function (e) { return e[T_DATE].slice(0, 10) === c.date; }) || null;
  };

  // ---------- energy → colour / size ----------
  function tierColor(kt) {
    if (kt >= 10) return '#ff4a5e';
    if (kt >= 1) return '#ffb347';
    if (kt >= 0.1) return '#b97c26';
    return '#1899bd';
  }
  function radius(kt) {
    return 1.7 + 2.6 * Math.log10(1 + (kt || 0) * 12);
  }

  // ---------- map projection ----------
  let map = null;   // {cv,g,x0,y0,w,h} of the last frame, for hit testing
  function project(lon, lat, m) {
    return [m.x0 + (lon + 180) / 360 * m.w, m.y0 + (90 - lat) / 180 * m.h];
  }

  FB.render = function () {
    const cv = $('cx-fb-map');
    if (!cv || !cv.parentNode) return;
    const box = cv.parentNode.getBoundingClientRect();
    if (box.width < 10 || box.height < 10) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = Math.round(box.width), H = Math.round(box.height);
    if (cv.width !== W * dpr || cv.height !== H * dpr) { cv.width = W * dpr; cv.height = H * dpr; }
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
    const g = cv.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, W, H);

    // letterbox a 2:1 equirectangular frame inside the pane
    let w = W, h = w / 2;
    if (h > H) { h = H; w = h * 2; }
    const m = { x0: (W - w) / 2, y0: (H - h) / 2, w: w, h: h };
    map = m;

    g.fillStyle = '#020b13';
    g.fillRect(m.x0, m.y0, w, h);

    // land
    g.lineWidth = 1;
    g.strokeStyle = 'rgba(29,109,140,.75)';
    g.fillStyle = 'rgba(7,32,48,.62)';
    RINGS.forEach(function (r) {
      g.beginPath();
      for (let i = 0; i < r.length; i++) {
        const p = project(r[i][0], r[i][1], m);
        if (i === 0) g.moveTo(p[0], p[1]); else g.lineTo(p[0], p[1]);
      }
      g.closePath(); g.fill(); g.stroke();
    });

    // graticule
    g.strokeStyle = 'rgba(14,58,79,.7)';
    g.beginPath();
    for (let lon = -180; lon <= 180; lon += 30) {
      const p = project(lon, 90, m), q = project(lon, -90, m);
      g.moveTo(p[0], p[1]); g.lineTo(q[0], q[1]);
    }
    for (let lat = -60; lat <= 60; lat += 30) {
      const p = project(-180, lat, m), q = project(180, lat, m);
      g.moveTo(p[0], p[1]); g.lineTo(q[0], q[1]);
    }
    g.stroke();
    g.strokeStyle = 'rgba(52,225,255,.28)';
    g.beginPath();
    const eq0 = project(-180, 0, m), eq1 = project(180, 0, m);
    g.moveTo(eq0[0], eq0[1]); g.lineTo(eq1[0], eq1[1]);
    g.stroke();
    g.strokeStyle = 'rgba(29,109,140,.9)';
    g.strokeRect(m.x0, m.y0, w, h);

    // events, faintest first so the big ones read on top
    const list = FB.shown().slice().sort(function (a, b) { return (a[T_KT] || 0) - (b[T_KT] || 0); });
    list.forEach(function (e) {
      const p = project(e[T_LON], e[T_LAT], m);
      const r = radius(e[T_KT]);
      const col = tierColor(e[T_KT] || 0);
      g.fillStyle = col;
      g.globalAlpha = e[T_KT] >= 1 ? 0.85 : 0.55;
      g.beginPath(); g.arc(p[0], p[1], r, 0, 7); g.fill();
      g.globalAlpha = 1;
      if (e[T_KT] >= 10) {
        g.strokeStyle = col; g.globalAlpha = 0.5;
        g.beginPath(); g.arc(p[0], p[1], r + 4, 0, 7); g.stroke();
        g.globalAlpha = 1;
      }
    });

    // the two candidates get a reticle and a name
    EV.forEach(function (e) {
      if (!e[T_TAG] || !located(e)) return;
      const p = project(e[T_LON], e[T_LAT], m);
      g.strokeStyle = '#ffb347'; g.lineWidth = 1.2;
      g.beginPath(); g.arc(p[0], p[1], 9, 0, 7); g.stroke();
      g.beginPath();
      g.moveTo(p[0] - 14, p[1]); g.lineTo(p[0] - 5, p[1]);
      g.moveTo(p[0] + 5, p[1]); g.lineTo(p[0] + 14, p[1]);
      g.moveTo(p[0], p[1] - 14); g.lineTo(p[0], p[1] - 5);
      g.moveTo(p[0], p[1] + 5); g.lineTo(p[0], p[1] + 14);
      g.stroke();
      g.fillStyle = '#ffb347';
      g.font = '10px ShareTechMono, Consolas, monospace';
      g.fillText(e[T_TAG], p[0] + 12, p[1] - 10);
      g.lineWidth = 1;
    });

    // selection ring
    const sel = F.sel != null ? EV[F.sel] : null;
    if (sel && located(sel)) {
      const p = project(sel[T_LON], sel[T_LAT], m);
      g.strokeStyle = '#46ffa1'; g.lineWidth = 1.4;
      g.beginPath(); g.arc(p[0], p[1], radius(sel[T_KT]) + 6, 0, 7); g.stroke();
      g.lineWidth = 1;
    }

    // Caption above and legend below the frame when the pane leaves room for them
    // (a 2:1 map letterboxed in a taller pane usually does); inside it otherwise.
    g.font = '9px ShareTechMono, Consolas, monospace';
    const items = [[0.02, '< 0.1 kt'], [0.3, '0.1 - 1'], [3, '1 - 10'], [30, '≥ 10 kt']];
    const gap = 26;
    let total = 0;
    items.forEach(function (t) { total += 13 + g.measureText(t[1]).width + gap; });
    total -= gap;
    const below = m.y0 + h + 24 <= H;
    const ly = below ? m.y0 + h + 18 : m.y0 + h - 9;
    let lx = below ? m.x0 + (w - total) / 2 : m.x0 + 9;
    if (!below) {                       // sitting on the map — give it a backing
      g.fillStyle = 'rgba(2,11,19,.82)';
      g.fillRect(lx - 5, ly - 13, total + 10, 18);
    }
    items.forEach(function (t) {
      g.fillStyle = tierColor(t[0]);
      g.beginPath(); g.arc(lx + 5, ly - 3, radius(t[0]), 0, 7); g.fill();
      g.fillStyle = '#6f93a8';
      g.fillText(t[1], lx + 13, ly);
      lx += 13 + g.measureText(t[1]).width + gap;
    });
    if (m.y0 >= 18) {
      const cap = 'CNEOS ATMOSPHERIC IMPACTS · EQUIRECTANGULAR · CIRCLE AREA SCALES WITH IMPACT ENERGY';
      g.fillStyle = '#3d5a6c';
      g.fillText(cap, m.x0 + (w - g.measureText(cap).width) / 2, m.y0 - 9);
    }
  };

  // ---------- hit testing ----------
  function pick(clientX, clientY, coarse) {
    const cv = $('cx-fb-map');
    if (!cv || !map) return null;
    const r = cv.getBoundingClientRect();
    const px = clientX - r.left, py = clientY - r.top;
    let best = null, bd = coarse ? 20 : 12;
    EV.forEach(function (e, i) {
      if (!passes(e) && !e[T_TAG]) return;
      if (!located(e)) return;
      const p = project(e[T_LON], e[T_LAT], map);
      const d = Math.hypot(p[0] - px, p[1] - py);
      if (d < Math.max(bd, radius(e[T_KT]) + 3) && (best === null || d < bd)) { bd = d; best = i; }
    });
    return best;
  }

  function fmtRow(e) {
    if (!e) return '';
    const parts = [
      '<b>' + esc(e[T_DATE]) + ' UTC</b>',
      esc(Math.abs(e[T_LAT]).toFixed(1) + '°' + (e[T_LAT] < 0 ? 'S' : 'N') + ' ' +
          Math.abs(e[T_LON]).toFixed(1) + '°' + (e[T_LON] < 0 ? 'W' : 'E')),
      'IMPACT ENERGY <b style="color:' + tierColor(e[T_KT] || 0) + '">' + esc(e[T_KT] != null ? e[T_KT] + ' kt' : '—') + '</b>',
      'RADIATED ' + esc(e[T_ENERGY] != null ? e[T_ENERGY] + '×10¹⁰ J' : '—'),
      'ALT ' + esc(e[T_ALT] != null ? e[T_ALT] + ' km' : '—'),
      'SPEED ' + esc(e[T_VEL] != null ? e[T_VEL] + ' km/s' : 'NOT REPORTED'),
    ];
    if (e[T_TAG]) {
      const c = FB.cases().find(function (a) { return a.date === e[T_DATE].slice(0, 10); });
      parts.push('<span class="cx-fb-tag" data-act="fb-case" data-id="' + esc(c ? c.id : '') + '">▲ ' +
        esc(e[T_TAG]) + ' — OPEN CASE FILE</span>');
    }
    return parts.join('<span class="cx-fb-sep">·</span>');
  }

  function renderReadout() {
    const box = $('cx-fb-readout');
    if (!box) return;
    const e = F.hover != null ? EV[F.hover] : (F.sel != null ? EV[F.sel] : null);
    if (!e) {
      CX.ui.setH(box, '<span class="cx-fb-hint">HOVER OR CLICK AN IMPACT — ' +
        FB.shown().length + ' OF ' + (D.meta.located || 0) + ' LOCATED EVENTS SHOWN</span>');
      return;
    }
    CX.ui.setH(box, fmtRow(e));
  }

  // ---------- side panel ----------
  function stats() {
    const list = FB.shown();
    let kt = 0, big = null, fast = null;
    list.forEach(function (e) {
      kt += e[T_KT] || 0;
      if (!big || (e[T_KT] || 0) > (big[T_KT] || 0)) big = e;
      if (e[T_VEL] != null && (!fast || e[T_VEL] > fast[T_VEL])) fast = e;
    });
    return { n: list.length, kt: kt, big: big, fast: fast };
  }

  function renderSide() {
    const box = $('cx-fb-side');
    if (!box) return;
    const st = stats();
    const meta = D.meta || {};
    const cases = FB.cases();
    CX.ui.setH(box, [
      '<div class="cx-panel">',
      '  <div class="cx-panel-title"><span class="cx-tt-accent">◎</span> CATALOG</div>',
      '  <div class="cx-readout-grid">',
      '    <div class="cx-readout"><div class="cx-ro-label">EVENTS SHOWN</div><div class="cx-ro-value">' + st.n + '</div></div>',
      '    <div class="cx-readout"><div class="cx-ro-label">TOTAL ENERGY</div><div class="cx-ro-value">' + st.kt.toFixed(0) + '<small> KT</small></div></div>',
      '  </div>',
      '  <div class="cx-fb-note">' + esc(meta.count || 0) + ' ROWS SINCE ' + esc((meta.first || '').slice(0, 4)) +
        ' · ' + esc(meta.located || 0) + ' WITH A REPORTED POSITION · SOURCE ' + esc(String(meta.source || 'CNEOS').toUpperCase()) +
        ', PULLED ' + esc(meta.fetched || '—') + '. CNEOS PUBLISHES NO UNCERTAINTIES ON ANY FIELD.</div>',
      '</div>',
      '<div class="cx-panel">',
      '  <div class="cx-panel-title"><span class="cx-tt-accent">▲</span> EXTREMES IN VIEW</div>',
      st.big ? '  <div class="cx-row" data-act="fb-pick" data-date="' + esc(st.big[T_DATE]) + '">' +
        '<div class="cx-row-t">LARGEST <span style="color:var(--red)">' + esc(st.big[T_KT]) + ' KT</span></div>' +
        '<div class="cx-row-s">' + esc(st.big[T_DATE].slice(0, 10)) + '</div></div>' : '',
      st.fast ? '  <div class="cx-row" data-act="fb-pick" data-date="' + esc(st.fast[T_DATE]) + '">' +
        '<div class="cx-row-t">FASTEST <span style="color:var(--cyan)">' + esc(st.fast[T_VEL]) + ' KM/S</span></div>' +
        '<div class="cx-row-s">' + esc(st.fast[T_DATE].slice(0, 10)) + (st.fast[T_TAG] ? ' · ' + esc(st.fast[T_TAG]) : '') + '</div></div>' : '',
      '</div>',
      '<div class="cx-chartbox"><div class="cx-chart-title"><span>SPEED DISTRIBUTION</span><span>' +
        EV.filter(function (e) { return e[T_VEL] != null; }).length + ' ROWS</span></div><canvas id="cx-fb-speed"></canvas></div>',
      '<div class="cx-panel" style="padding:10px 0 0">',
      '  <div class="cx-panel-title" style="padding:0 12px"><span style="color:var(--amber)">▲</span> INTERSTELLAR CANDIDATES</div>',
      cases.map(function (a) {
        const row = FB.rowOfCase(a.id);
        return '<div class="cx-acase" data-act="fb-case" data-id="' + esc(a.id) + '">' +
          '<div class="cx-a-dot" style="background:var(--amber);box-shadow:none"></div>' +
          '<div class="cx-a-id">' + esc(a.id) + '</div>' +
          '<div class="cx-a-name">' + esc(a.title) + '</div>' +
          '<div class="cx-a-date">' + esc(row ? row[T_TAG] : a.date.slice(2)) + '</div></div>';
      }).join(''),
      '  <div class="cx-fb-note">BOTH ARE CATALOG ROWS, NOT TELESCOPE TARGETS. NEITHER HAS BEEN CONFIRMED INTERSTELLAR OUTSIDE THE CATALOG THAT REPORTED IT — OPEN A FILE FOR BOTH SIDES.</div>',
      '</div>',
    ].join('\n'));
    const cv = $('cx-fb-speed');
    if (cv) CX.charts.speedDist(cv);
  }

  // ---------- toolbar ----------
  function renderToolbar() {
    const box = $('cx-fb-toolbar');
    if (!box) return;
    CX.ui.setH(box, [
      ENERGY_STEPS.map(function (s2) {
        return '<button class="cx-pod' + (F.minKt === s2.v ? ' cx-on' : '') +
          '" data-act="fb-energy" data-v="' + s2.v + '">' + s2.label + '</button>';
      }).join(''),
      '<span class="cx-fb-gap"></span>',
      SPANS.map(function (s2) {
        return '<button class="cx-pod' + (F.span === s2.key ? ' cx-on' : '') +
          '" data-act="fb-span" data-k="' + s2.key + '">' + s2.label + '</button>';
      }).join(''),
      '<span class="cx-fb-gap"></span>',
      '<button class="cx-pod' + (F.speedOnly ? ' cx-on' : '') + '" data-act="fb-speedonly">SPEED REPORTED</button>',
      '<button class="cx-pod" data-act="fb-locate" data-tag="IM1">◎ IM1</button>',
      '<button class="cx-pod" data-act="fb-locate" data-tag="IM2">◎ IM2</button>',
    ].join(''));
  }

  FB.refresh = function () {
    renderToolbar();
    renderSide();
    renderReadout();
    FB.render();
  };

  // Pull a tagged row into view: select it and say what it is.
  FB.focus = function (tag) {
    const i = EV.findIndex(function (e) { return e[T_TAG] === tag; });
    if (i < 0) return;
    F.sel = i; F.hover = null;
    F.minKt = 0; F.span = 'all'; F.speedOnly = false;
    FB.refresh();
    const e = EV[i];
    CX.ui.showToast({
      title: tag + ' — CNEOS ' + e[T_DATE].slice(0, 10), t: S.t, cls: 'anomaly',
      desc: e[T_VEL] + ' km/s, ' + e[T_KT] + ' kt, ' + e[T_ALT] + ' km altitude. Claimed interstellar; disputed.',
    });
  };

  FB.selectByDate = function (dateStr) {
    const i = EV.findIndex(function (e) { return e[T_DATE] === dateStr; });
    if (i < 0) return;
    F.sel = i; F.hover = null;
    FB.refresh();
  };

  // ---------- wiring (called once, from ui.js) ----------
  FB.wire = function () {
    const cv = $('cx-fb-map');
    if (!cv) return;
    // Hover is a mouse/stylus idea — a finger has no hover state, so touch
    // selects on tap instead and the readout shows the selection.
    cv.addEventListener('pointermove', function (ev) {
      if (ev.pointerType === 'touch') return;
      const i = pick(ev.clientX, ev.clientY, false);
      if (i === F.hover) return;
      F.hover = i;
      cv.style.cursor = i == null ? 'crosshair' : 'pointer';
      renderReadout();
      FB.render();
    });
    cv.addEventListener('pointerleave', function () {
      if (F.hover == null) return;
      F.hover = null; renderReadout(); FB.render();
    });
    // pointerdown rather than click: fires for mouse, finger and stylus alike.
    // Deliberately does not preventDefault, so a scroll gesture still scrolls.
    cv.addEventListener('pointerdown', function (ev) {
      if (ev.pointerType === 'mouse' && ev.button !== 0) return;
      const i = pick(ev.clientX, ev.clientY, ev.pointerType !== 'mouse');
      if (i == null) return;
      F.sel = i;
      F.hover = null;
      CX.audio.ui();
      const e = EV[i];
      if (e[T_TAG]) {
        const c = FB.cases().find(function (a) { return a.date === e[T_DATE].slice(0, 10); });
        if (c) { CX.ui.openDossier(c.id); return; }
      }
      renderReadout();
      FB.render();
    });
  };

  // toolbar / side-panel actions, dispatched from ui.js's delegated click handler
  FB.act = function (act, btn) {
    if (act === 'fb-energy') { F.minKt = Number(btn.getAttribute('data-v')); F.sel = null; FB.refresh(); }
    else if (act === 'fb-span') { F.span = btn.getAttribute('data-k'); F.sel = null; FB.refresh(); }
    else if (act === 'fb-speedonly') { F.speedOnly = !F.speedOnly; FB.refresh(); }
    else if (act === 'fb-locate') { FB.focus(btn.getAttribute('data-tag')); }
    else if (act === 'fb-pick') { FB.selectByDate(btn.getAttribute('data-date')); }
    else return false;
    return true;
  };
})();
