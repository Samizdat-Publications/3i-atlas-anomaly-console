/* ============================================================
   CHARTS — minimal canvas plotting for telemetry + dossiers
   Era-aware: telemetry arrays rebuild when the active era changes.
   ============================================================ */
(function () {
  'use strict';
  const CX = window.CX, S = CX.S;
  const CH = (CX.charts = {});

  const COL = {
    grid: 'rgba(14,58,79,.55)', axis: 'rgba(111,147,168,.8)', txt: '#6f93a8',
    cyan: '#34e1ff', green: '#46ffa1', amber: '#ffb347', red: '#ff4a5e',
    dim: '#1d6d8c', ghost: 'rgba(52,225,255,.25)',
  };

  function fit(cv) {
    const r = cv.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(10, Math.round(r.width * dpr)), h = Math.max(10, Math.round(r.height * dpr));
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    const g = cv.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { g: g, w: r.width, h: r.height };
  }

  function plot(cv, cfg) {
    const f = fit(cv), g = f.g, W = f.w, H = f.h;
    const padL = cfg.padL != null ? cfg.padL : 34, padR = 6, padT = 6, padB = cfg.padB != null ? cfg.padB : 14;
    const iw = W - padL - padR, ih = H - padT - padB;
    g.clearRect(0, 0, W, H);
    g.font = '9px ShareTechMono, Consolas, monospace';

    const x0 = cfg.xMin, x1 = cfg.xMax;
    let y0 = cfg.yMin, y1 = cfg.yMax;
    if (y0 == null || y1 == null) {
      y0 = Infinity; y1 = -Infinity;
      cfg.series.forEach(function (s) {
        for (let i = 0; i < s.ys.length; i++) {
          const v = s.ys[i];
          if (v == null || !isFinite(v)) continue;
          if (v < y0) y0 = v; if (v > y1) y1 = v;
        }
      });
      const pad = (y1 - y0) * 0.08 || 1;
      y0 -= pad; y1 += pad;
    }
    if (cfg.invertY) { const tmp = y0; y0 = y1; y1 = tmp; }
    const X = function (x) { return padL + (x - x0) / (x1 - x0) * iw; };
    const Y = function (y) { return padT + (1 - (y - y0) / (y1 - y0)) * ih; };

    g.strokeStyle = COL.grid; g.lineWidth = 1; g.fillStyle = COL.txt;
    (cfg.xTicks || []).forEach(function (tk) {
      const x = X(tk.x);
      g.globalAlpha = 0.7; g.beginPath(); g.moveTo(x, padT); g.lineTo(x, padT + ih); g.stroke(); g.globalAlpha = 1;
      if (tk.label) g.fillText(tk.label, x - 9, H - 3);
    });
    const yt = cfg.yTicks || 3;
    for (let i = 0; i <= yt; i++) {
      const v = y0 + (y1 - y0) * (i / yt);
      const y = Y(v);
      g.globalAlpha = 0.45; g.beginPath(); g.moveTo(padL, y); g.lineTo(padL + iw, y); g.stroke(); g.globalAlpha = 1;
      g.fillText(cfg.yFmt ? cfg.yFmt(v) : v.toFixed(1), 2, y + 3);
    }

    (cfg.markers || []).forEach(function (m) {
      const x = X(m.x);
      g.strokeStyle = m.color || COL.amber;
      g.setLineDash([3, 3]);
      g.beginPath(); g.moveTo(x, padT); g.lineTo(x, padT + ih); g.stroke();
      g.setLineDash([]);
      if (m.label) { g.fillStyle = m.color || COL.amber; g.fillText(m.label, Math.min(x + 3, W - 60), padT + 9); g.fillStyle = COL.txt; }
    });

    cfg.series.forEach(function (s) {
      g.strokeStyle = s.color; g.lineWidth = s.w || 1.4;
      if (s.dash) g.setLineDash(s.dash);
      g.beginPath();
      let started = false;
      for (let i = 0; i < s.xs.length; i++) {
        const vx = s.xs[i], vy = s.ys[i];
        if (vy == null || !isFinite(vy)) { started = false; continue; }
        const px = X(vx), py = Y(vy);
        if (!started) { g.moveTo(px, py); started = true; } else g.lineTo(px, py);
      }
      g.stroke();
      g.setLineDash([]);
      if (s.label) {
        g.fillStyle = s.color;
        g.fillText(s.label, s.labelX != null ? X(s.labelX) : padL + 4, s.labelY != null ? Y(s.labelY) : padT + 10);
        g.fillStyle = COL.txt;
      }
    });

    if (cfg.cursor != null && cfg.cursor >= x0 && cfg.cursor <= x1) {
      const x = X(cfg.cursor);
      g.strokeStyle = COL.green; g.globalAlpha = 0.9;
      g.beginPath(); g.moveTo(x, padT); g.lineTo(x, padT + ih); g.stroke();
      g.globalAlpha = 1;
    }
    return { X: X, Y: Y };
  }
  CH.plot = plot;

  // ---------- era-scoped telemetry data (real ephemeris) ----------
  let builtEra = null;
  let dayXs = [], rSunYs = [], speedYs = [], magYs = [];
  let rangeSeries = {};
  const RANGE_KEYS = [
    { key: 'mars', color: '#d3603f' }, { key: 'earth', color: '#5f9fe8' },
    { key: 'venus', color: '#e8c88a' }, { key: 'jupiter', color: '#d8a76f' },
  ];
  function buildData() {
    if (builtEra === S.era) return;
    builtEra = S.era;
    dayXs = []; rSunYs = []; speedYs = []; magYs = []; rangeSeries = {};
    const step = Math.max(1, Math.round((CX.N - 1) / 320));
    for (let t = 0; t < CX.N; t += step) {
      dayXs.push(t);
      const r = CX.rSun('target', t);
      rSunYs.push(r);
      speedYs.push(CX.targetSpeed(t));
      const d = CX.range('target', 'earth', t);
      magYs.push(6.2 + 5 * Math.log10(Math.max(0.1, d)) + 7.6 * Math.log10(Math.max(0.25, r)));
      RANGE_KEYS.forEach(function (rk) {
        (rangeSeries[rk.key] = rangeSeries[rk.key] || []).push(CX.range('target', rk.key, t));
      });
    }
  }
  CH.invalidate = function () { builtEra = null; };

  function monthTicks() {
    const tks = [];
    const d = new Date(CX.EPOCH);
    d.setUTCDate(1);
    for (let i = 0; i < 40; i++) {
      d.setUTCMonth(d.getUTCMonth() + 1);
      const t = (d.getTime() - CX.EPOCH) / 86400000;
      if (t >= CX.N) break;
      if (t > 0 && d.getUTCMonth() % 3 === 0) {
        tks.push({ x: t, label: CX.MONTHS[d.getUTCMonth()].slice(0, 1) + (d.getUTCMonth() === 0 ? String(d.getUTCFullYear()).slice(2) : '') });
      }
    }
    return tks;
  }

  CH.renderRail = function () {
    buildData();
    const cur = S.t;
    const ca = CX.CA();
    const periT = ca.sun ? CX.tOfIso(ca.sun.date) : null;
    const cvR = document.getElementById('cx-ch-rsun');
    const cvP = document.getElementById('cx-ch-ranges');
    const cvV = document.getElementById('cx-ch-speed');
    const periMarkers = periT != null ? [{ x: periT, color: COL.amber, label: 'PERI' }] : [];
    if (cvR) plot(cvR, {
      xMin: 0, xMax: CX.N - 1, series: [{ xs: dayXs, ys: rSunYs, color: COL.cyan, w: 1.5 }],
      xTicks: monthTicks(), cursor: cur, yFmt: function (v) { return v.toFixed(0); },
      markers: periMarkers,
    });
    if (cvP) plot(cvP, {
      xMin: 0, xMax: CX.N - 1,
      series: RANGE_KEYS.map(function (rk) {
        return { xs: dayXs, ys: rangeSeries[rk.key], color: rk.color, w: 1.2 };
      }),
      xTicks: monthTicks(), cursor: cur, yMin: 0, yMax: 7, yFmt: function (v) { return v.toFixed(0); },
    });
    if (cvV) plot(cvV, {
      xMin: 0, xMax: CX.N - 1, series: [{ xs: dayXs, ys: speedYs, color: COL.green, w: 1.5 }],
      xTicks: monthTicks(), cursor: cur, yFmt: function (v) { return v.toFixed(0); },
      markers: periT != null ? [{ x: periT, color: COL.amber }] : [],
    });
  };

  // ---------- dossier charts (stylized illustrations of published results) ----------
  // ---------- CNEOS speed distribution (REAL data, not a stylized illustration) ----------
  // Every catalog row that reports a pre-entry speed, binned. IM1 and IM2 are marked,
  // together with the 10-15 km/s uncertainty band Brown & Borovicka (2023) measured for
  // USG velocities at high speed — the band is the whole argument, so it is drawn.
  CH.speedDist = function (cv) {
    const D = window.ATLAS_FIREBALLS || { events: [] };
    const f = fit(cv), g = f.g, W = f.w, H = f.h;
    g.clearRect(0, 0, W, H);
    g.font = '9px ShareTechMono, Consolas, monospace';
    const V0 = 10, V1 = 76, STEP = 2;
    const nb = Math.ceil((V1 - V0) / STEP);
    const bins = new Array(nb).fill(0);
    let n = 0;
    const marks = [];
    D.events.forEach(function (e) {
      const v = e[6];
      if (v == null) return;
      n++;
      const b = Math.floor((v - V0) / STEP);
      if (b >= 0 && b < nb) bins[b]++;
      if (e[7]) marks.push({ v: v, tag: e[7] });
    });
    const peak = Math.max(1, Math.max.apply(null, bins));
    const padL = 26, padR = 8, padT = 16, padB = 16;
    const iw = W - padL - padR, ih = H - padT - padB;
    const X = function (v) { return padL + (v - V0) / (V1 - V0) * iw; };
    const Y = function (c) { return padT + ih - (c / peak) * ih; };

    // Brown & Borovicka uncertainty band around the IM1 reading
    const im1 = marks.find(function (m) { return m.tag === 'IM1'; });
    if (im1) {
      g.fillStyle = 'rgba(255,74,94,.10)';
      g.fillRect(X(Math.max(V0, im1.v - 15)), padT, X(im1.v) - X(Math.max(V0, im1.v - 15)), ih);
    }
    g.strokeStyle = COL.grid;
    for (let v = 20; v <= 70; v += 10) {
      const x = X(v);
      g.globalAlpha = 0.6; g.beginPath(); g.moveTo(x, padT); g.lineTo(x, padT + ih); g.stroke(); g.globalAlpha = 1;
      g.fillStyle = COL.txt; g.fillText(String(v), x - 6, H - 4);
    }
    g.fillStyle = COL.txt; g.fillText('km/s', W - 26, H - 4);
    for (let i = 0; i < nb; i++) {
      if (!bins[i]) continue;
      const x = X(V0 + i * STEP), w = Math.max(1.5, X(V0 + STEP) - X(V0) - 1);
      g.fillStyle = 'rgba(52,225,255,.42)';
      g.fillRect(x, Y(bins[i]), w, padT + ih - Y(bins[i]));
    }
    g.strokeStyle = COL.axis; g.globalAlpha = 0.7;
    g.beginPath(); g.moveTo(padL, padT + ih); g.lineTo(padL + iw, padT + ih); g.stroke(); g.globalAlpha = 1;
    marks.forEach(function (m) {
      const x = X(m.v);
      g.strokeStyle = COL.amber; g.setLineDash([3, 3]);
      g.beginPath(); g.moveTo(x, padT); g.lineTo(x, padT + ih); g.stroke(); g.setLineDash([]);
      g.fillStyle = COL.amber;
      g.fillText(m.tag + ' ' + m.v.toFixed(1), Math.min(x + 3, W - 50), padT + (m.tag === 'IM1' ? 9 : 22));
    });
    if (im1) {
      g.fillStyle = 'rgba(255,74,94,.8)';
      g.fillText('▮ 10-15 km/s USG VELOCITY ERROR', padL, 9);
    }
  };

  // ---------- CNEOS detections per year (REAL data) ----------
  // Built to answer one recurring question — "are fireballs increasing?" — from
  // the shipped catalog rather than from impression. Two things make the honest
  // answer visible: the >=1 kt subset is drawn INSIDE each bar (a detection-rate
  // change inflates faint events far more than bright ones, so a flat bright
  // subset under a rising total means reporting, not flux), and the years before
  // the satellite record begins are shaded rather than silently plotted as zero.
  const RATE_FROM = 1988, RATE_SPARSE_TO = 1993, RATE_BASE_FROM = 2000;
  CH.fireballRate = function (cv, big) {
    const D = window.ATLAS_FIREBALLS || { events: [], meta: {} };
    const f = fit(cv), g = f.g, W = f.w, H = f.h;
    g.clearRect(0, 0, W, H);
    g.font = (big ? '10px ' : '9px ') + 'ShareTechMono, Consolas, monospace';

    const last = String((D.meta && D.meta.last) || '').slice(0, 10);
    const lastYear = +last.slice(0, 4) || RATE_FROM;
    const years = [];
    for (let y = RATE_FROM; y <= lastYear; y++) years.push(y);
    const all = {}, kt1 = {};
    years.forEach(function (y) { all[y] = 0; kt1[y] = 0; });
    D.events.forEach(function (e) {
      const y = +e[0].slice(0, 4);
      if (all[y] == null) return;
      all[y]++;
      if ((e[2] || 0) >= 1) kt1[y]++;
    });
    // the final year is only partial — say so rather than letting it read as a fall
    const doy = last ? (Date.UTC(lastYear, +last.slice(5, 7) - 1, +last.slice(8, 10)) -
                        Date.UTC(lastYear, 0, 1)) / 86400000 + 1 : 365;
    const partial = doy < 350;

    const peak = Math.max.apply(null, years.map(function (y) { return all[y]; })) || 1;
    const padL = big ? 30 : 22, padR = 6, padT = big ? 26 : 20, padB = big ? 20 : 14;
    const iw = W - padL - padR, ih = H - padT - padB;
    const bw = iw / years.length;
    const X = function (y) { return padL + (y - RATE_FROM) * bw; };
    const Y = function (n) { return padT + ih - (n / peak) * ih; };

    // the years before the satellite record begins
    g.fillStyle = 'rgba(255,74,94,.07)';
    g.fillRect(X(RATE_FROM), padT, bw * (RATE_SPARSE_TO - RATE_FROM + 1), ih);

    g.strokeStyle = COL.grid;
    for (let n = 10; n <= peak; n += 10) {
      const y = Y(n);
      g.globalAlpha = 0.5; g.beginPath(); g.moveTo(padL, y); g.lineTo(padL + iw, y); g.stroke(); g.globalAlpha = 1;
      g.fillStyle = COL.txt; g.fillText(String(n), 2, y + 3);
    }

    years.forEach(function (y) {
      const x = X(y), w = Math.max(1.5, bw - 1.4);
      const isPartial = partial && y === lastYear;
      g.fillStyle = isPartial ? 'rgba(52,225,255,.20)' : 'rgba(52,225,255,.38)';
      g.fillRect(x, Y(all[y]), w, padT + ih - Y(all[y]));
      if (kt1[y]) {                       // the bias-resistant subset, inside the bar
        g.fillStyle = isPartial ? 'rgba(255,179,71,.45)' : COL.amber;
        g.fillRect(x, Y(kt1[y]), w, padT + ih - Y(kt1[y]));
      }
      if (isPartial) {
        g.strokeStyle = 'rgba(52,225,255,.5)'; g.setLineDash([2, 2]);
        g.strokeRect(x, Y(all[y]), w, padT + ih - Y(all[y])); g.setLineDash([]);
      }
    });

    // mean of the settled era, drawn across it only
    let sum = 0, n = 0;
    years.forEach(function (y) {
      if (y >= RATE_BASE_FROM && !(partial && y === lastYear)) { sum += all[y]; n++; }
    });
    const mean = n ? sum / n : 0;
    g.strokeStyle = COL.green; g.setLineDash([4, 3]);
    g.beginPath(); g.moveTo(X(RATE_BASE_FROM), Y(mean)); g.lineTo(padL + iw, Y(mean)); g.stroke();
    g.setLineDash([]);
    g.fillStyle = COL.green;
    g.fillText(mean.toFixed(1) + '/yr', Math.min(padL + iw - 34, X(RATE_BASE_FROM) + 4), Y(mean) - 3);

    g.strokeStyle = COL.axis; g.globalAlpha = 0.7;
    g.beginPath(); g.moveTo(padL, padT + ih); g.lineTo(padL + iw, padT + ih); g.stroke(); g.globalAlpha = 1;
    g.fillStyle = COL.txt;
    [1990, 2000, 2010, 2020].forEach(function (y) {
      if (y <= lastYear) g.fillText(String(y), X(y) - 8, H - 3);
    });

    g.fillStyle = 'rgba(52,225,255,.75)';
    g.fillText('■ ALL EVENTS', padL, 9);
    g.fillStyle = COL.amber;
    g.fillText('■ ≥ 1 kt', padL + (big ? 108 : 84), 9);
    g.fillStyle = 'rgba(255,74,94,.75)';
    g.fillText('■ PRE-RECORD', padL + (big ? 178 : 138), 9);
    if (big) {
      g.fillStyle = COL.txt;
      g.fillText('CNEOS DETECTIONS PER YEAR — THE BRIGHT SUBSET IS THE ONE A DETECTION-RATE CHANGE CANNOT INFLATE', padL, 21);
    }
  };

  CH.dossier = function (kind, cv) {
    if (kind === 'speed-dist') { CH.speedDist(cv); return; }
    if (kind === 'fireball-rate') { CH.fireballRate(cv, true); return; }
    buildData();
    if (kind === 'spectrum') {
      const xs = [], ys = [];
      for (let wl = 336; wl <= 364; wl += 0.14) {
        let v = 0.06 + Math.random() * 0.035;
        [[341.48, 0.55], [344.63, 0.7], [345.85, 0.95], [349.30, 0.8], [352.45, 0.6], [356.64, 0.5]].forEach(function (ln) {
          v += ln[1] * Math.exp(-Math.pow((wl - ln[0]) / 0.16, 2));
        });
        xs.push(wl); ys.push(v);
      }
      plot(cv, {
        xMin: 336, xMax: 364, yMin: 0, yMax: 1.15, padB: 16,
        series: [
          { xs: xs, ys: ys, color: COL.amber, w: 1.3, label: 'Ni I EMISSION', labelX: 337, labelY: 1.05 },
        ],
        xTicks: [{ x: 340, label: '340' }, { x: 350, label: '350nm' }, { x: 360, label: '360' }],
        markers: [
          { x: 344.06, color: 'rgba(52,225,255,.5)', label: '' }, { x: 358.12, color: 'rgba(52,225,255,.5)', label: 'Fe I — NOT DETECTED' },
        ],
        yFmt: function (v) { return v.toFixed(1); },
      });
    } else if (kind === 'polarization') {
      const xs = [], normal = [], atlas = [];
      for (let a = 0; a <= 40; a += 0.5) {
        xs.push(a);
        normal.push(-1.8 * Math.sin(Math.PI * Math.min(1, a / 22)) * Math.exp(-a / 30) * 2.2 + a * 0.09);
        atlas.push(-8.5 * Math.exp(-Math.pow((a - 6.5) / 6, 2)) + Math.max(0, a - 20) * 0.12);
      }
      plot(cv, {
        xMin: 0, xMax: 40, yMin: -10, yMax: 4, padB: 16,
        series: [
          { xs: xs, ys: normal, color: COL.dim, w: 1.2, dash: [4, 3], label: 'TYPICAL COMETS', labelX: 16, labelY: 2.8 },
          { xs: xs, ys: atlas, color: COL.amber, w: 1.6, label: 'MEASURED', labelX: 6, labelY: -9 },
        ],
        xTicks: [{ x: 10, label: '10°' }, { x: 20, label: '20°' }, { x: 30, label: '30°' }],
        yFmt: function (v) { return v.toFixed(0) + '%'; },
      });
    } else if (kind === 'acceleration') {
      const xs = [], grav = [], resid = [];
      for (let d = -60; d <= 70; d += 1) {
        xs.push(d);
        grav.push(0);
        resid.push(d < -5 ? (Math.random() - 0.5) * 0.15 : (1 - Math.exp(-(d + 5) / 22)) * 2.6 + (Math.random() - 0.5) * 0.18);
      }
      plot(cv, {
        xMin: -60, xMax: 70, yMin: -0.8, yMax: 3.2, padB: 16,
        series: [
          { xs: xs, ys: grav, color: COL.dim, w: 1, dash: [4, 3], label: 'GRAVITY-ONLY FIT', labelX: -58, labelY: 0.35 },
          { xs: xs, ys: resid, color: COL.amber, w: 1.5, label: 'ASTROMETRIC RESIDUAL', labelX: -20, labelY: 2.9 },
        ],
        xTicks: [{ x: -30, label: '-30d' }, { x: 0, label: 'PERIHELION' }, { x: 30, label: '+30d' }, { x: 60, label: '+60d' }],
        yFmt: function (v) { return v.toFixed(1); },
      });
    } else if (kind === 'lightcurve') {
      const ca = CX.CA();
      const markers = [];
      if (ca.sun) markers.push({ x: CX.tOfIso(ca.sun.date), color: COL.amber, label: 'PERIHELION' });
      if (ca.earth) markers.push({ x: CX.tOfIso(ca.earth.date), color: 'rgba(95,159,232,.7)', label: 'EARTH C/A' });
      plot(cv, {
        xMin: 0, xMax: CX.N - 1, invertY: true, padB: 16,
        series: [{ xs: dayXs, ys: magYs, color: COL.cyan, w: 1.5, label: 'APPARENT MAG (MODEL ON REAL GEOMETRY)', labelX: 30, labelY: null }],
        xTicks: monthTicks(),
        markers: markers,
        cursor: S.t,
        yFmt: function (v) { return v.toFixed(0); },
      });
    } else if (kind === 'trajectory' || kind === 'timing') {
      const xs = [], ys = [], exs = [], eys = [];
      const tgt = CX.eraData().objects.target;
      let xmax = 7;
      if (tgt) {
        for (let i = 0; i < tgt.n; i += 4) {
          const p = tgt.pos[i];
          const xr = Math.sqrt(p[0] * p[0] + p[1] * p[1]) * (p[0] < 0 ? -1 : 1);
          xs.push(xr); ys.push(p[2]);
          if (Math.abs(xr) > xmax) xmax = Math.abs(xr);
        }
      }
      xmax = Math.min(9, xmax);
      for (let x = -xmax; x <= xmax; x += 0.5) { exs.push(x); eys.push(0); }
      plot(cv, {
        xMin: -xmax, xMax: xmax, yMin: -Math.max(2.2, xmax * 0.35), yMax: Math.max(2.2, xmax * 0.35), padB: 16,
        series: [
          { xs: exs, ys: eys, color: COL.dim, w: 1.2, dash: [5, 4], label: 'ECLIPTIC PLANE (EDGE-ON)', labelX: -xmax + 0.4, labelY: Math.max(2.2, xmax * 0.35) * 0.2 },
          { xs: xs, ys: ys, color: COL.amber, w: 1.6, label: 'TARGET PATH VS PLANE', labelX: -xmax + 0.4, labelY: -Math.max(2.2, xmax * 0.35) * 0.82 },
        ],
        xTicks: [{ x: -5, label: '-5AU' }, { x: 0, label: 'SUN' }, { x: 5, label: '5AU' }],
        yFmt: function (v) { return v.toFixed(0); },
      });
    } else if (kind === 'size') {
      const f = fit(cv), g = f.g;
      g.clearRect(0, 0, f.w, f.h);
      g.font = '10px ShareTechMono, Consolas, monospace';
      const items = [
        { name: "1I/'OUMUAMUA ~0.2 km", r: 3, color: '#d9b8ff' },
        { name: '2I/BORISOV ~0.5 km', r: 6, color: '#9fd9ff' },
        { name: '3I/ATLAS ≤ 5.6 km (HST limit)', r: 30, color: COL.amber },
      ];
      let x = 40;
      items.forEach(function (it) {
        const y = f.h - 24;
        g.strokeStyle = it.color; g.fillStyle = it.color;
        g.globalAlpha = 0.22; g.beginPath(); g.arc(x + it.r, y - it.r, it.r, 0, 7); g.fill();
        g.globalAlpha = 1; g.beginPath(); g.arc(x + it.r, y - it.r, it.r, 0, 7); g.stroke();
        g.save(); g.translate(x + it.r, y + 12); g.fillText(it.name, -g.measureText(it.name).width / 2, 0); g.restore();
        x += it.r * 2 + 92;
      });
      g.fillStyle = COL.txt;
      g.fillText('NUCLEUS SIZE COMPARISON — THE THREE KNOWN INTERSTELLAR OBJECTS', 12, 16);
    } else {
      CH.dossier('lightcurve', cv);
    }
  };
})();
