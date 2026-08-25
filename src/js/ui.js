/* ============================================================
   UI — DOM skeleton, boot, timeline, dossiers, archive, wiring
   Markup is injected via setH() (insertAdjacentHTML) only.
   ============================================================ */
(function () {
  'use strict';
  const CX = window.CX, S = CX.S, C = CX.CONTENT;
  const UI = (CX.ui = {});

  function setH(node, html) { node.textContent = ''; node.insertAdjacentHTML('beforeend', html); }
  function el(tag, cls, html) {
    const d = document.createElement(tag);
    if (cls) d.className = cls;
    if (html != null) setH(d, html);
    return d;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function throttle(fn, ms) {
    let last = 0, timer = null;
    return function () {
      const now = Date.now();
      if (now - last >= ms) { last = now; fn(); }
      else if (!timer) { timer = setTimeout(function () { timer = null; last = Date.now(); fn(); }, ms - (now - last)); }
    };
  }
  UI.setH = setH; UI.el = el; UI.esc = esc;

  const $ = function (id) { return document.getElementById(id); };
  let tlCanvas, tlDragging = false;

  // The narrow-screen top bar wraps to as many rows as the device needs, so its
  // height is not knowable from CSS. Measure it and hand it to the stylesheet,
  // which uses it to place the slide-over rails.
  function syncChromeVars() {
    const top = document.querySelector('.cx-top');
    const bot = document.querySelector('.cx-bottom');
    const root = document.documentElement;
    if (top) root.style.setProperty('--topH', top.offsetHeight + 'px');
    if (bot) root.style.setProperty('--botH', bot.offsetHeight + 'px');
  }
  UI.syncChromeVars = syncChromeVars;

  // ============ BUILD ============
  UI.build = function () {
    const meta = C.meta || {};
    const root = el('div', 'cx-root'); root.id = 'cx-root';
    setH(root, [
      '<div class="cx-top">',
      '  <div class="cx-sigil">◈</div>',
      '  <div class="cx-title"><span id="cx-title-obj">3I/ATLAS</span> <small>' + esc(meta.tagline || 'INTERSTELLAR ANOMALY REVIEW CONSOLE') + '</small></div>',
      '  <div class="cx-tabs" style="margin-left:4px">',
      '    <button class="cx-tab cx-on" data-act="era" data-era="3i" title="3I/ATLAS · C/2025 N1">3I</button>',
      '    <button class="cx-tab" data-act="era" data-era="1i" title="1I/ʻOumuamua · 2017">1I</button>',
      '    <button class="cx-tab" data-act="era" data-era="2i" title="2I/Borisov · 2019">2I</button>',
      '  </div>',
      '  <div class="cx-tabs cx-tabs-mode">',
      '    <button class="cx-tab" data-act="tab" data-tab="briefings">BRIEFINGS</button>',
      '    <button class="cx-tab cx-on" data-act="tab" data-tab="track">TRACK</button>',
      '    <button class="cx-tab" data-act="tab" data-tab="anomalies">ANOMALIES</button>',
      '    <button class="cx-tab" data-act="tab" data-tab="compare">COMPARE<span class="cx-tab-long"> 1I·2I·3I</span></button>',
      '    <button class="cx-tab" data-act="tab" data-tab="fireballs">FIREBALLS</button>',
      '    <button class="cx-tab" data-act="tab" data-tab="archive">ARCHIVE</button>',
      '  </div>',
      '  <button class="cx-icobtn cx-railbtn" data-act="rail" data-side="left" title="anomaly log">◧</button>',
      '  <div class="cx-top-spacer"></div>',
      '  <div class="cx-alert-pill" id="cx-alert">LOEB SCALE ' + esc(meta.loebScale != null ? meta.loebScale : '—') + ' · REVIEW ACTIVE</div>',
      '  <div class="cx-clockbox"><div class="cx-simdate" id="cx-simdate">—</div><div class="cx-utc" id="cx-utc">—</div></div>',
      '  <button class="cx-icobtn cx-railbtn" data-act="rail" data-side="right" title="telemetry">◨</button>',
      '  <button class="cx-icobtn cx-on" id="cx-btn-audio" data-act="audio" title="sound">♪</button>',
      '  <button class="cx-icobtn cx-on" id="cx-btn-crt" data-act="crt" title="CRT effect">▦</button>',
      '  <button class="cx-icobtn" id="cx-btn-tour" data-act="tour-start" title="guided tour (T)">▶</button>',
      '  <button class="cx-icobtn" data-act="help" title="controls &amp; about (?)">?</button>',
      '</div>',
      '<div class="cx-left" id="cx-left"></div>',
      '<div class="cx-center" id="cx-center">',
      '  <div class="cx-hud" id="cx-hud"></div>',
      '  <div class="cx-crosshair"></div>',
      '  <div class="cx-campods" id="cx-campods">',
      '    <button class="cx-pod cx-on" data-act="cam" data-cam="free">FREE</button>',
      '    <button class="cx-pod" data-act="cam" data-cam="top">TOP-DOWN</button>',
      '    <button class="cx-pod" data-act="cam" data-cam="chase">CHASE</button>',
      '    <button class="cx-pod" data-act="cam" data-cam="mars">FROM MARS</button>',
      '    <button class="cx-pod" data-act="cam" data-cam="sun">FROM SUN</button>',
      '  </div>',
      '  <div class="cx-viewopts">',
      '    <button class="cx-pod cx-on" data-act="labels">LABELS</button>',
      '    <button class="cx-pod cx-on" data-act="orbits">ORBITS</button>',
      '    <button class="cx-pod" data-act="grid">GRID</button>',
      '    <button class="cx-pod cx-pod-spec" data-act="dispatch">DISPATCH</button>',
      '  </div>',
      '  <div class="cx-specnote" id="cx-specnote">DISPATCH \u2014 ILLUSTRATION OF A CLAIM, NOT AN OBSERVATION. NOTHING HAS BEEN SEEN LEAVING THIS OBJECT.</div>',
      '  <div class="cx-toast" id="cx-toast"></div>',
      '  <div class="cx-tour" id="cx-tour"><div class="cx-tour-inner">',
      '    <div class="cx-tour-step" id="cx-tour-step"></div>',
      '    <div class="cx-tour-title" id="cx-tour-title"></div>',
      '    <div class="cx-tour-text" id="cx-tour-text"></div>',
      '    <div class="cx-tour-bar"><div class="cx-tour-fill" id="cx-tour-fill"></div></div>',
      '    <div class="cx-tour-btns">',
      '      <button class="cx-btn cx-btn-ghost" data-act="tour-next">SKIP AHEAD ▶</button>',
      '      <span class="cx-spacer"></span>',
      '      <button class="cx-btn cx-btn-ghost" data-act="tour-stop">EXIT TOUR (ESC)</button>',
      '    </div>',
      '  </div></div>',
      '  <div class="cx-briefwrap" id="cx-briefwrap" style="display:none">',
      '    <div class="cx-brief-rail" id="cx-brief-rail"></div>',
      '    <div class="cx-brief-pane" id="cx-brief-pane"></div>',
      '  </div>',
      '  <div class="cx-comparewrap" id="cx-comparewrap" style="display:none"><div></div>',
      '    <div class="cx-cmp-table-wrap" id="cx-cmp-table"></div>',
      '  </div>',
      '  <div class="cx-fbwrap" id="cx-fbwrap" style="display:none">',
      '    <div class="cx-fb-main">',
      '      <div class="cx-fb-toolbar" id="cx-fb-toolbar"></div>',
      '      <div class="cx-fb-mapbox"><canvas id="cx-fb-map"></canvas></div>',
      '      <div class="cx-fb-readout" id="cx-fb-readout"></div>',
      '    </div>',
      '    <div class="cx-fb-side" id="cx-fb-side"></div>',
      '  </div>',
      '  <div class="cx-docwrap" id="cx-docwrap" style="display:none">',
      '    <div class="cx-doclist" id="cx-doclist"></div>',
      '    <div class="cx-docview" id="cx-docview"></div>',
      '  </div>',
      '  <div class="cx-overlay" id="cx-overlay"><div class="cx-sheet" id="cx-sheet"></div></div>',
      '</div>',
      '<div class="cx-right" id="cx-right"></div>',
      '<div class="cx-bottom">',
      '  <div class="cx-tl-track" id="cx-tl-track"><canvas id="cx-tl-canvas"></canvas></div>',
      '  <div class="cx-transport">',
      '    <button class="cx-tbtn" data-act="step" data-d="-7" title="back 7 days">⏮</button>',
      '    <button class="cx-tbtn" data-act="play" id="cx-btn-play" style="min-width:44px">▶</button>',
      '    <button class="cx-tbtn" data-act="step" data-d="7" title="fwd 7 days">⏭</button>',
      '    <span class="cx-speed-lbl">RATE</span>',
      '    <button class="cx-tbtn" data-act="speed" data-s="1">1d/s</button>',
      '    <button class="cx-tbtn cx-on" data-act="speed" data-s="3">3d/s</button>',
      '    <button class="cx-tbtn" data-act="speed" data-s="10">10d/s</button>',
      '    <button class="cx-tbtn" data-act="speed" data-s="30">30d/s</button>',
      '    <button class="cx-tbtn" data-act="now" title="jump to today">● NOW</button>',
      '    <span class="cx-tdate" id="cx-tdate"></span>',
      '  </div>',
      '</div>',
    ].join('\n'));
    document.body.appendChild(root);
    $('cx-center').appendChild(el('div', 'cx-disclaimer',
      'UNOFFICIAL SIMULATION FOR EDUCATION &amp; ENTERTAINMENT · NOT AFFILIATED WITH NASA/JPL · EPHEMERIS: JPL HORIZONS · ANOMALY NARRATIVE: A. LOEB (PUBLISHED CLAIMS) VS OFFICIAL ASSESSMENTS'));
    if (S.crt) document.body.classList.add('cx-crt');

    buildLeftRail();
    buildRightRail();
    tlCanvas = $('cx-tl-canvas');
    wire();
    CX.fireballs.wire();
    syncChromeVars();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(syncChromeVars).catch(function () {});
    setTimeout(syncChromeVars, 600);
    updateEraChrome();
    UI.renderClock();
    UI.renderTimeline();
  };

  // ============ LEFT RAIL ============
  function buildLeftRail() {
    const left = $('cx-left');
    const ca = CX.CA();
    const rows = [['sun', 'PERIHELION'], ['mars', 'MARS RANGE MIN'], ['venus', 'VENUS RANGE MIN'], ['earth', 'EARTH CLOSEST'], ['mercury', 'MERCURY RANGE MIN'], ['jupiter', 'JUPITER RANGE MIN']]
      .filter(function (r) { return ca[r[0]]; })
      .map(function (r) {
        const e = ca[r[0]];
        return '<div class="cx-row" data-act="approach" data-date="' + e.date + '">' +
          '<div class="cx-row-t">' + r[1] + ' <span style="color:var(--cyan)">' + e.au.toFixed(3) + ' AU</span></div>' +
          '<div class="cx-row-s">' + e.date + (e.km ? ' · ' + (e.km / 1e6).toFixed(1) + 'M KM' : '') + '</div></div>';
      }).join('');
    setH(left, [
      '<div class="cx-panel">',
      '  <div class="cx-panel-title"><span class="cx-tt-accent">◢</span> MISSION STATUS</div>',
      '  <div class="cx-readout-grid">',
      '    <div class="cx-readout"><div class="cx-ro-label">SUN RANGE</div><div class="cx-ro-value" id="cx-ro-rsun">—</div></div>',
      '    <div class="cx-readout"><div class="cx-ro-label">EARTH RANGE</div><div class="cx-ro-value" id="cx-ro-rearth">—</div></div>',
      '    <div class="cx-readout cx-ro-green"><div class="cx-ro-label">VELOCITY</div><div class="cx-ro-value" id="cx-ro-vel">—</div></div>',
      '    <div class="cx-readout cx-ro-amber"><div class="cx-ro-label">PHASE</div><div class="cx-ro-value" id="cx-ro-phase" style="font-size:13px">—</div></div>',
      '  </div>',
      '</div>',
      '<div class="cx-panel" style="padding:10px 0 0">',
      '  <div class="cx-logtabs">',
      '    <button class="cx-logtab' + (logTab === 'cases' ? ' cx-on' : '') + '" data-act="log-tab" data-tab="cases"><span style="color:var(--amber)">▲</span> CASE FILES</button>',
      '    <button class="cx-logtab' + (logTab === 'log' ? ' cx-on' : '') + '" data-act="log-tab" data-tab="log"><span style="color:var(--cyan)">◈</span> MISSION LOG</button>',
      '    <span class="cx-logcount" id="cx-alog-count"></span>',
      '  </div>',
      '  <div class="cx-search" id="cx-search">',
      '    <input id="cx-q" type="search" autocomplete="off" spellcheck="false" placeholder="search all 3 objects — try &quot;nickel&quot;">',
      '    <span class="cx-search-x" data-act="q-clear" title="clear">✕</span>',
      '  </div>',
      '  <div class="cx-alog" id="cx-alog"></div>',
      '</div>',
      '<div class="cx-panel" style="padding:10px 0 0">',
      '  <div class="cx-panel-title" style="padding:0 12px"><span class="cx-tt-accent">◎</span> CLOSE APPROACHES</div>',
      rows,
      '</div>',
    ].join('\n'));
    UI.renderAnomalyList();
    const qi = $('cx-q');            // rail is rebuilt on era switch — keep the query
    if (qi && query) qi.value = query;
    syncSearchPlaceholder();
  }

  // Case search runs across ALL three objects — searching "nickel" should surface
  // both 3I's anomaly and 2I's control-case result, which is half the point.
  let query = '';
  // Which list the rail is showing. The MISSION LOG tab exists because 24% of
  // timeline records sit outside their era's scrubber window — 1I's story runs to
  // 2026 while its ephemeris stops in 2018 — so a marker is not a reliable way in.
  let logTab = 'cases';
  function syncSearchPlaceholder() {
    const qi = $('cx-q');
    if (qi) qi.placeholder = logTab === 'log'
      ? 'search the mission log — try \u201cperihelion\u201d'
      : 'search all 3 objects — try \u201cnickel\u201d';
  }
  UI.setLogTab = function (t) {
    if (logTab === t) return;
    logTab = t;
    document.querySelectorAll('[data-act="log-tab"]').forEach(function (b) {
      b.classList.toggle('cx-on', b.getAttribute('data-tab') === t);
    });
    syncSearchPlaceholder();
    UI.renderAnomalyList();
  };

  function renderEventList() {
    const box = $('cx-alog');
    const q = query.trim().toLowerCase();
    const cnt = $('cx-alog-count');
    const wrap = $('cx-search');
    if (wrap) wrap.classList.toggle('cx-has-q', !!q);
    const all = C.timeline || [];
    let list;
    if (q) {
      list = all.filter(function (e) {
        return ((e.title || '') + ' ' + (e.description || '')).toLowerCase().indexOf(q) !== -1;
      });
      if (cnt) cnt.textContent = list.length + ' / ' + all.length + ' MATCH';
    } else {
      list = CX.eraTimeline();
      if (cnt) cnt.textContent = list.length + ' ENTRIES';
    }
    if (!list.length) {
      setH(box, '<div class="cx-nores">NO LOG ENTRY MATCHES &ldquo;' + esc(query.trim()) + '&rdquo;</div>');
      return;
    }
    setH(box, list.map(function (e) {
      const obj = e.object || '3i';
      const foreign = obj !== S.era;
      const em = CX.ERA_META[obj];
      const kind = EVENT_KIND[e.kind] || EVENT_KIND.observation;
      const future = !foreign && CX.tOfIso(e.date) > S.t;
      const badge = (q && foreign)
        ? '<span class="cx-obj-badge" style="color:' + em.color + ';border-color:' + em.color + '">' + obj.toUpperCase() + '</span>'
        : '';
      return '<div class="cx-acase cx-logrow' + (future ? ' cx-future' : '') +
        (S.selEvent === e.id ? ' cx-on' : '') + '" data-act="event" data-id="' + esc(e.id) + '">' +
        '<div class="cx-a-dot"' + (foreign ? ' style="background:' + em.color + ';box-shadow:none"' : '') + '></div>' +
        '<div class="cx-a-id" title="' + esc(kind[1]) + '">' + kind[0] + '</div>' +
        '<div class="cx-a-name">' + badge + esc(e.title) + '</div>' +
        '<div class="cx-a-date">' + esc((e.date || '').slice(2)) + '</div></div>';
    }).join(''));
  }

  UI.renderAnomalyList = function () {
    if (logTab === 'log') { renderEventList(); return; }
    return renderCaseList();
  };
  function renderCaseList() {
    const box = $('cx-alog');
    if (!box) return;
    const q = query.trim().toLowerCase();
    const cnt = $('cx-alog-count');
    const wrap = $('cx-search');
    if (wrap) wrap.classList.toggle('cx-has-q', !!q);

    let list;
    if (q) {
      list = (C.anomalies || []).filter(function (a) {
        return (a.id + ' ' + a.title + ' ' + a.observation + ' ' + a.loeb_take + ' ' +
                (a.loeb_quote || '') + ' ' + a.official_explanation).toLowerCase().indexOf(q) !== -1;
      });
      if (cnt) cnt.textContent = list.length + ' / ' + (C.anomalies || []).length + ' MATCH';
    } else {
      list = CX.eraAnomalies();
      if (cnt) cnt.textContent = list.length + ' CASES';
    }

    if (!list.length) {
      setH(box, '<div class="cx-nores">NO CASE MATCHES &ldquo;' + esc(query.trim()) + '&rdquo;</div>');
      return;
    }
    setH(box, list.map(function (a) {
      const obj = a.object || '3i';
      const foreign = obj !== S.era;
      const future = !foreign && CX.tOfIso(a.date) > S.t;
      const em = CX.ERA_META[obj];
      const badge = (q && foreign)
        ? '<span class="cx-obj-badge" style="color:' + em.color + ';border-color:' + em.color + '">' + obj.toUpperCase() + '</span>'
        : '';
      return '<div class="cx-acase' + (future ? ' cx-future' : '') + (S.selAnomaly === a.id ? ' cx-on' : '') +
        '" data-act="anomaly" data-id="' + esc(a.id) + '" data-obj="' + obj + '">' +
        '<div class="cx-a-dot"' + (foreign ? ' style="background:' + em.color + ';box-shadow:none"' : '') + '></div>' +
        '<div class="cx-a-id">' + esc(a.id) + '</div>' +
        '<div class="cx-a-name">' + badge + esc(a.title) + '</div>' +
        '<div class="cx-a-date">' + esc((a.date || '').slice(2)) + '</div></div>';
    }).join(''));
  };
  UI.setQuery = function (v) {
    query = v || '';
    UI.renderAnomalyList();
  };

  // ============ RIGHT RAIL ============
  function buildRightRail() {
    const right = $('cx-right');
    const pref = S.era.toUpperCase();
    const iso3 = (C.compare || []).find(function (o) { return (o.designation || '').indexOf(pref) === 0; }) || {};
    const meta = CX.eraMetaContent();
    setH(right, [
      '<div class="cx-chartbox"><div class="cx-chart-title"><span>HELIOCENTRIC DISTANCE</span><span>AU</span></div><canvas id="cx-ch-rsun"></canvas></div>',
      '<div class="cx-chartbox"><div class="cx-chart-title"><span>PLANET RANGES</span>',
      '<span><i style="color:#d3603f;font-style:normal">MARS</i> <i style="color:#5f9fe8;font-style:normal">EARTH</i> <i style="color:#e8c88a;font-style:normal">VENUS</i> <i style="color:#d8a76f;font-style:normal">JUP</i></span></div><canvas id="cx-ch-ranges"></canvas></div>',
      '<div class="cx-chartbox"><div class="cx-chart-title"><span>HELIOCENTRIC VELOCITY</span><span>KM/S</span></div><canvas id="cx-ch-speed"></canvas></div>',
      '<div class="cx-panel">',
      '  <div class="cx-panel-title"><span class="cx-tt-accent">◧</span> OBJECT DATA</div>',
      '  <div class="cx-readout-grid">',
      '    <div class="cx-readout"><div class="cx-ro-label">ECCENTRICITY</div><div class="cx-ro-value">' + esc(iso3.eccentricity != null ? iso3.eccentricity : '—') + '</div></div>',
      '    <div class="cx-readout"><div class="cx-ro-label">INCLINATION</div><div class="cx-ro-value">' + esc(iso3.inclination_deg != null ? iso3.inclination_deg : '—') + '°</div></div>',
      '    <div class="cx-readout"><div class="cx-ro-label">V-INFINITY</div><div class="cx-ro-value">' + esc(iso3.v_infinity_kms != null ? iso3.v_infinity_kms : '—') + '<small> KM/S</small></div></div>',
      '    <div class="cx-readout"><div class="cx-ro-label">PERIHELION</div><div class="cx-ro-value">' + esc(iso3.perihelion_au != null ? iso3.perihelion_au : '—') + '<small> AU</small></div></div>',
      '  </div>',
      '  <div style="margin-top:8px;color:var(--txt-dim);font-size:10.5px">NUCLEUS: ' + esc(iso3.size_estimate || '—') + '</div>',
      '</div>',
      '<div class="cx-panel">',
      '  <div class="cx-panel-title"><span style="color:var(--amber)">▲</span> LOEB SCALE</div>',
      '  <div class="cx-gauge"><div class="cx-gauge-track"><div class="cx-gauge-fill" style="width:' + Math.min(100, (meta.loebScale || 0) * 10) + '%"></div></div>',
      '  <div class="cx-gauge-num">' + esc(meta.loebScale != null ? meta.loebScale : '—') + ' / 10</div></div>',
      '  <div style="color:var(--txt-faint);font-size:10px;margin-top:2px">SELF-DECLARED ODDITY RATING PER A. LOEB — 0 NATURAL … 10 CONFIRMED TECH</div>',
      (meta.loebScaleHistory ? '  <div style="color:var(--amber-dim);font-size:9.5px;margin-top:4px;letter-spacing:.5px">' + esc(meta.loebScaleHistory) + '</div>' : ''),
      (meta.anomalyCountNote ? '  <div style="color:var(--txt-faint);font-size:9.5px;margin-top:4px">' + esc(meta.anomalyCountNote) + '</div>' : ''),
      (meta.datasetVerify ? '  <div style="color:var(--txt-faint);font-size:9.5px;margin-top:4px">FACT-CHECK: ' + esc(meta.datasetVerify) + '</div>' : ''),
      '</div>',
      '<div class="cx-panel" id="cx-nextevent-panel">',
      '  <div class="cx-panel-title"><span class="cx-tt-accent">▹</span> NEXT EVENT</div>',
      '  <div id="cx-nextevent" style="font-size:12px;color:var(--txt)">—</div>',
      '</div>',
    ].join('\n'));
  }

  // ============ CLOCK + READOUTS ============
  UI.renderClock = function () {
    const sd = $('cx-simdate'); if (!sd) return;
    sd.textContent = CX.fmtDate(S.t);
    $('cx-utc').textContent = 'SYS ' + new Date().toISOString().slice(0, 16).replace('T', ' ') + 'Z';
    const rs = CX.rSun('target', S.t), re = CX.range('target', 'earth', S.t);
    $('cx-ro-rsun').textContent = rs.toFixed(3);
    $('cx-ro-rearth').textContent = re.toFixed(3);
    $('cx-ro-vel').textContent = CX.targetSpeed(S.t).toFixed(1);
    const ca = CX.CA();
    const periT = ca.sun ? CX.tOfIso(ca.sun.date) : 0;
    const discT = CX.tOfIso(CX.ERA_META[S.era].discovery);
    $('cx-ro-phase').textContent = Math.abs(S.t - periT) < 2 ? 'PERIHELION' : (S.t < periT ? 'INBOUND' : 'OUTBOUND');
    const dd = Math.floor(S.t - discT);
    $('cx-tdate').textContent = '';
    setH($('cx-tdate'), 'T' + (dd >= 0 ? '+' : '−') + Math.abs(dd) + 'd FROM DISCOVERY · <b>' + CX.isoOf(S.t) + '</b>');
    // next event
    const evs = CX.allEvents();
    const nxt = evs.find(function (e) { return e.t > S.t; });
    const ne = $('cx-nextevent');
    if (ne) {
      if (nxt) {
        const isAnom = nxt.cls === 'anomaly';
        const id = nxt.src && nxt.src.id;
        const act = id ? ' data-act="' + (isAnom ? 'anomaly' : 'event') + '" data-id="' + esc(id) + '"' +
          (isAnom ? ' data-obj="' + esc(nxt.src.object || '3i') + '"' : '') : '';
        setH(ne, '<div class="cx-nextev"' + act + '>' +
          '<span style="color:var(--' + (isAnom ? 'amber' : 'cyan') + ')">' + esc(nxt.title) + '</span>' +
          '<div style="color:var(--txt-faint);font-size:10px">' + CX.fmtDate(nxt.t) + ' · IN ' +
          Math.ceil(nxt.t - S.t) + 'd' + (id ? ' · OPEN RECORD ▸' : '') + '</div></div>');
      } else setH(ne, '<span style="color:var(--txt-dim)">NO FURTHER SCHEDULED EVENTS — OUTBOUND CRUISE</span>');
    }
  };

  // ============ TIMELINE ============
  UI.renderTimeline = function () {
    if (!tlCanvas) return;
    const track = $('cx-tl-track');
    const r = track.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    tlCanvas.width = Math.round(r.width * dpr); tlCanvas.height = Math.round(r.height * dpr);
    const g = tlCanvas.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const W = r.width, H = r.height;
    g.clearRect(0, 0, W, H);
    const X = function (t) { return (t / (CX.N - 1)) * W; };
    g.font = '9px ShareTechMono, Consolas, monospace';

    // month grid
    const d = new Date(CX.EPOCH); d.setUTCDate(1);
    for (let i = 0; i < 40; i++) {
      d.setUTCMonth(d.getUTCMonth() + 1);
      const t = (d.getTime() - CX.EPOCH) / 86400000;
      if (t >= CX.N) break;
      if (t <= 0) continue;
      const x = X(t);
      g.strokeStyle = 'rgba(14,58,79,.7)';
      g.beginPath(); g.moveTo(x, 8); g.lineTo(x, H - 12); g.stroke();
      g.fillStyle = d.getUTCMonth() === 0 ? '#34e1ff' : '#3d5a6c';
      g.fillText(d.getUTCMonth() === 0 ? String(d.getUTCFullYear()) : CX.MONTHS[d.getUTCMonth()], x + 2, H - 3);
    }
    // baseline
    g.strokeStyle = 'rgba(29,109,140,.8)';
    g.beginPath(); g.moveTo(0, H / 2 + 2); g.lineTo(W, H / 2 + 2); g.stroke();
    // NOW tick (only when today falls inside the era window)
    if (CX.NOW_T != null) {
      const nx = X(CX.NOW_T);
      g.strokeStyle = 'rgba(70,255,161,.5)'; g.setLineDash([2, 3]);
      g.beginPath(); g.moveTo(nx, 4); g.lineTo(nx, H - 12); g.stroke(); g.setLineDash([]);
      g.fillStyle = 'rgba(70,255,161,.7)'; g.fillText('TODAY', nx - 14, 8);
    }

    // markers
    CX.allEvents().forEach(function (e) {
      const x = X(e.t), y = H / 2 + 2;
      if (e.cls === 'anomaly') {
        g.fillStyle = e.t <= S.t ? '#ffb347' : 'rgba(255,179,71,.35)';
        g.beginPath(); g.moveTo(x, y - 9); g.lineTo(x + 4.5, y - 1); g.lineTo(x - 4.5, y - 1); g.closePath(); g.fill();
      } else {
        g.fillStyle = e.t <= S.t ? '#34e1ff' : 'rgba(52,225,255,.35)';
        g.beginPath(); g.moveTo(x, y + 2); g.lineTo(x + 4, y + 7); g.lineTo(x, y + 12); g.lineTo(x - 4, y + 7); g.closePath(); g.fill();
      }
    });

    // playhead
    const px = X(S.t);
    g.strokeStyle = '#46ffa1'; g.lineWidth = 1.4;
    g.beginPath(); g.moveTo(px, 2); g.lineTo(px, H - 12); g.stroke();
    g.fillStyle = '#46ffa1';
    g.beginPath(); g.moveTo(px - 5, 0); g.lineTo(px + 5, 0); g.lineTo(px, 7); g.closePath(); g.fill();
    g.lineWidth = 1;
  };

  function tlScrub(ev) {
    const r = $('cx-tl-track').getBoundingClientRect();
    const frac = Math.max(0, Math.min(1, (ev.clientX - r.left) / r.width));
    CX.setT(frac * (CX.N - 1));
  }
  function tlClick(ev, tol) {
    // Marker hit test. The two kinds are drawn in separate rows — anomaly
    // triangles above the baseline, mission diamonds below — so the pointer's
    // side decides which row it can hit. Without that, the rows compete for
    // every tap and, at phone width where markers sit ~10px apart, scrubbing
    // by tapping became impossible.
    const r = $('cx-tl-track').getBoundingClientRect();
    const baseline = r.top + r.height / 2 + 2;
    const want = ev.clientY < baseline ? 'anomaly' : 'mission';
    const evs = CX.allEvents();
    let best = null, bd = tol || 6;
    evs.forEach(function (e) {
      if (e.cls !== want) return;
      const x = (e.t / (CX.N - 1)) * r.width + r.left;
      const d = Math.abs(x - ev.clientX);
      if (d < bd) { bd = d; best = e; }
    });
    if (best) {
      CX.audio.ui();
      if (best.cls === 'anomaly') { CX.setT(best.t + 0.01); openDossier(best.src.id); }
      else if (best.src && best.src.id) openEvent(best.src.id);
      else {
        CX.setT(best.t + 0.01);
        showToast(Object.assign({}, best, { kind: best.cls === 'anomaly' ? 'anomaly' : 'mission' }));
      }
      return true;
    }
    return false;
  }

  // ============ TOAST ============
  let toastTimer = null;
  // A toast raised by a RECORD crossing the playhead carries a kind chip, so it
  // reads as "this is an anomaly" rather than as an unexplained line of amber
  // text. UI toasts (link copied, target switched) pass no kind and get none.
  const TOAST_KIND = { anomaly: '\u25b2 ANOMALY', mission: '\u25c6 MISSION EVENT' };

  function showToast(e) {
    const t = $('cx-toast');
    const more = (e.desc && String(e.desc).length > 110) ? ' · MARKER OR MISSION LOG OPENS THE FULL RECORD' : '';
    const kind = e.kind ? TOAST_KIND[e.kind] : (e.cls === 'anomaly' ? TOAST_KIND.anomaly : '');
    setH(t, (kind ? '<span class="cx-toast-kind">' + esc(kind) + '</span>' : '') +
      esc(e.title) + '<span class="cx-toast-date">' + CX.fmtDate(e.t) +
      (e.desc ? ' — ' + esc(String(e.desc).slice(0, 110)) + '…' : '') + more + '</span>');
    t.className = 'cx-toast cx-show' + (e.cls === 'anomaly' ? ' cx-anom' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.className = 'cx-toast'; }, 4200);
  }
  UI.showToast = showToast;

  // ============ DOSSIER ============
  // Citation row, shared by case files and timeline records so both cite the
  // same way. Shows the domain; the full URL is the link target and the title.
  function refsRow(sources) {
    if (!sources || !sources.length) return '';
    return '<div class="cx-refs">REFS: ' + sources.map(function (u) {
      const dom = String(u).replace(/^https?:\/\//, '').split('/')[0];
      return '<a href="' + esc(u) + '" target="_blank" rel="noreferrer" title="' + esc(u) + '">' + esc(dom) + '</a>';
    }).join(' · ') + '</div>';
  }

  // ============ TIMELINE RECORD ============
  // Clicking an anomaly marker has always opened its full case file. Clicking a
  // mission marker only ever flashed a toast — 110 characters of a description
  // that averages 456, with its citations dropped at bake time. Same component,
  // cyan instead of amber, so the two read as siblings rather than clones.
  const EVENT_KIND = {
    discovery:      ['◆', 'DISCOVERY'],
    observation:    ['◈', 'OBSERVATION'],
    close_approach: ['◎', 'CLOSE APPROACH'],
    statement:      ['❝', 'STATEMENT'],
    status:         ['▪', 'STATUS'],
  };
  let eventIdx = -1, eventList = [];
  function openEvent(id) {
    const e = CX.eventById(id);
    if (!e) return;
    const obj = e.object || '3i';
    if (obj !== S.era) CX.setEra(obj);
    eventList = CX.eraTimeline();
    eventIdx = Math.max(0, eventList.findIndex(function (x) { return x.id === e.id; }));
    S.selEvent = e.id;
    S.selAnomaly = null;
    UI.renderAnomalyList();
    CX.setT(CX.tOfIso(e.date) + 0.01);
    const kind = EVENT_KIND[e.kind] || EVENT_KIND.observation;
    setH($('cx-sheet'), [
      '<div class="cx-sheet-head cx-sh-mission">',
      '  <div class="cx-sh-id">' + kind[0] + '</div>',
      '  <div class="cx-sh-title">' + esc(e.title) + ' <span class="cx-chip cx-c-kind">' + kind[1] + '</span></div>',
      '  <div class="cx-sh-date">' + esc(e.date) + '</div>',
      '  <button class="cx-x" data-act="close-overlay">✕</button>',
      '</div>',
      '<div class="cx-sheet-body">',
      '  <div class="cx-block"><div class="cx-block-label cx-bl-obs">MISSION LOG ENTRY</div>',
      '  <div class="cx-block-text">' + esc(e.description) + '</div></div>',
      refsRow(e.sources),
      '</div>',
      '<div class="cx-sheet-actions">',
      '  <button class="cx-btn cx-btn-ghost" data-act="event-nav" data-d="-1">◀ PREV</button>',
      '  <button class="cx-btn cx-btn-ghost" data-act="event-nav" data-d="1">NEXT ▶</button>',
      '  <button class="cx-btn cx-btn-ghost" data-act="copy-link" data-id="' + esc(e.id) + '" title="' + esc(recordUrl(e.id)) + '">⧉ COPY LINK</button>',
      '  <span style="flex:1"></span>',
      '  <span class="cx-sheet-count">ENTRY ' + (eventIdx + 1) + ' / ' + eventList.length + '</span>',
      '</div>',
    ].join('\n'));
    $('cx-overlay').classList.add('cx-show');
    syncHash();
  }
  UI.openEvent = openEvent;

  let dossierIdx = -1, dossierList = [];
  // Cases live under an object key: '3i'/'1i'/'2i' are eras with an ephemeris,
  // 'fb' is the CNEOS fireball register, which has none — so opening one of its
  // files switches MODE rather than era.
  function objCases(obj) {
    return obj === 'fb' ? CX.fireballs.cases()
      : (C.anomalies || []).filter(function (x) { return (x.object || '3i') === obj; });
  }
  function openDossier(id) {
    const a = (C.anomalies || []).find(function (x) { return x.id === id; });
    if (!a) return;
    const obj = a.object || '3i';
    if (obj === 'fb') { if (S.mode !== 'fireballs') setMode('fireballs'); }
    else if (obj !== S.era) CX.setEra(obj);
    dossierList = objCases(obj);
    dossierIdx = Math.max(0, dossierList.findIndex(function (x) { return x.id === a.id; }));
    S.selAnomaly = a.id;
    UI.renderAnomalyList();
    const sheet = $('cx-sheet');
    const chip = a.verify === 'CONFIRMED' ? '<span class="cx-chip cx-c-conf">FACTS VERIFIED</span>' :
      a.verify === 'CORRECTED' ? '<span class="cx-chip cx-c-corr">VERIFIED · CORRECTED</span>' :
      '<span class="cx-chip cx-c-unv">' + esc(a.verify || 'UNREVIEWED') + '</span>';
    const isFb = (a.object || '3i') === 'fb';
    setH(sheet, [
      '<div class="cx-sheet-head">',
      '  <div class="cx-sh-id">' + esc(a.id) + '</div>',
      '  <div class="cx-sh-title">' + esc(a.title) + ' ' + chip + '</div>',
      '  <div class="cx-sh-date">' + esc(a.date) + '</div>',
      '  <button class="cx-x" data-act="close-overlay">✕</button>',
      '</div>',
      '<div class="cx-sheet-body">',
      '  <div class="cx-block"><div class="cx-block-label cx-bl-obs">OBSERVATION</div><div class="cx-block-text">' + esc(a.observation) + '</div></div>',
      '  <div class="cx-block cx-b-loeb"><div class="cx-block-label cx-bl-loeb">' + esc(a.claim_label || 'LOEB ASSESSMENT') + '</div><div class="cx-block-text">' + esc(a.loeb_take) + '</div>' +
        (a.loeb_quote ? '<div class="cx-quote">“' + esc(a.loeb_quote) + '”<span class="cx-q-src">— ' + esc((a.claim_label === 'LOEB ASSESSMENT' ? 'A. LOEB · ' : '') + (a.quote_source || '')) + '</span></div>' : '') + '</div>',
      '  <div class="cx-block cx-b-off"><div class="cx-block-label cx-bl-off">OFFICIAL EXPLANATION</div><div class="cx-block-text">' + esc(a.official_explanation) + '</div></div>',
      '  <canvas class="cx-dchart" id="cx-dchart"></canvas>',
      refsRow(a.sources),
      '</div>',
      '<div class="cx-sheet-actions">',
      (isFb
        ? '  <button class="cx-btn cx-btn-amber" data-act="fb-visualize" data-id="' + esc(a.id) + '">◎ LOCATE ON IMPACT MAP</button>'
        : '  <button class="cx-btn cx-btn-amber" data-act="visualize" data-id="' + esc(a.id) + '">◈ VISUALIZE IN TRACKER</button>'),
      '  <button class="cx-btn cx-btn-ghost" data-act="dossier-nav" data-d="-1">◀ PREV</button>',
      '  <button class="cx-btn cx-btn-ghost" data-act="dossier-nav" data-d="1">NEXT ▶</button>',
      '  <button class="cx-btn cx-btn-ghost" data-act="copy-link" data-id="' + esc(a.id) + '" title="' + esc(caseUrl(a.id)) + '">⧉ COPY LINK</button>',
      '  <span style="flex:1"></span>',
      '  <span class="cx-sheet-count">CASE ' + (dossierIdx + 1) + ' / ' + dossierList.length + '</span>',
      '</div>',
    ].join('\n'));
    $('cx-overlay').classList.add('cx-show');
    syncHash();
    requestAnimationFrame(function () {
      const cv = $('cx-dchart');
      if (cv) CX.charts.dossier(a.viz_hint || 'lightcurve', cv);
    });
  }
  UI.openDossier = openDossier;
  function closeOverlay() {
    $('cx-overlay').classList.remove('cx-show');
    S.selAnomaly = null;
    S.selEvent = null;
    UI.renderAnomalyList();
    if (S.mode === 'anomalies') setMode('track');
    syncHash();
  }

  // The fireball equivalent of "visualize in tracker": close the file, put the
  // CNEOS row under a reticle on the map.
  function fbVisualize(id) {
    const row = CX.fireballs.rowOfCase(id);
    closeOverlay();
    setMode('fireballs');
    if (row && row[7]) CX.fireballs.focus(row[7]);
  }

  function visualize(id) {
    const a = CX.eraAnomalies().find(function (x) { return x.id === id; });
    if (!a) return;
    closeOverlay();
    setMode('track');
    CX.setT(CX.tOfIso(a.date));
    S.viz.antiTail = a.viz_hint === 'tail';
    S.viz.ecliptic = a.viz_hint === 'trajectory';
    if (a.viz_hint === 'trajectory') { CX.scene3d.applyPreset('top'); markCam('top'); }
    else if (a.viz_hint === 'tail') { CX.scene3d.applyPreset('chase'); markCam('chase'); }
    else { CX.scene3d.applyPreset('free'); markCam('free'); }
    showToast({ title: a.id + ' — ' + a.title, t: CX.tOfIso(a.date), cls: 'anomaly', desc: a.observation });
    CX.audio.anomalyAlert();
  }

  // ============ DEEP LINKS ============
  // #<era>[/<caseId>|/<mode>]  e.g. #3i/A-05, #1i/compare, #2i
  let hashLock = false;
  // Exported: briefings.js drives its own hash after opening a card.
  function syncHash() {
    if (hashLock || !S.booted) return;
    if (S.mode === 'briefings') {
      const bid = CX.briefings && CX.briefings.current();
      const bh = '#brief' + (bid ? '/' + bid : '');
      if (location.hash !== bh) {
        try { history.replaceState(null, '', bh); } catch (e) { /* file:// can refuse */ }
      }
      return;
    }
    const selCase = S.selAnomaly
      ? (C.anomalies || []).find(function (a) { return a.id === S.selAnomaly; }) : null;
    let h = '#' + ((selCase && selCase.object) || S.era);
    if (S.selAnomaly) h += '/' + S.selAnomaly;
    else if (S.selEvent) h += '/' + S.selEvent;
    else if (S.mode !== 'track') h += '/' + S.mode;
    if (location.hash !== h) {
      try { history.replaceState(null, '', h); } catch (e) { /* file:// can refuse */ }
    }
  }
  UI.syncHash = syncHash;

  const MODES = ['briefings', 'track', 'anomalies', 'compare', 'fireballs', 'archive'];
  function applyHash() {
    let raw = '';
    try { raw = decodeURIComponent(location.hash || ''); } catch (e) { raw = location.hash || ''; }
    raw = raw.replace(/^#/, '').trim();
    if (!raw) return false;
    const parts = raw.split('/');
    const era = (parts[0] || '').toLowerCase();
    const what = (parts[1] || '').toLowerCase();
    let applied = false;
    hashLock = true;
    try {
      if (era === 'brief') {
        closeOverlay();
        setMode('briefings');
        CX.briefings.open((parts[1] || '').toUpperCase());
        hashLock = false;
        return true;
      }
      if (CX.EPH.eras[era] && era !== S.era) { CX.setEra(era); applied = true; }
      if (what) {
        if (MODES.indexOf(what) !== -1) { setMode(what); applied = true; }
        else {
          const c = (C.anomalies || []).find(function (a) { return String(a.id).toLowerCase() === what; });
          if (c) {
            const obj = c.object || '3i';
            if (obj !== S.era) CX.setEra(obj);
            openDossier(c.id);
            applied = true;
          } else if (CX.eventById(what)) {
            openEvent(CX.eventById(what).id);
            applied = true;
          }
        }
      }
    } finally { hashLock = false; }
    syncHash();
    return applied;
  }
  UI.applyHash = applyHash;

  // Works for a case id (A-05) or a timeline record id (E-20260818).
  function recordUrl(id) {
    const rec = (C.anomalies || []).find(function (a) { return a.id === id; }) || CX.eventById(id) || {};
    return location.origin + location.pathname + '#' + (rec.object || S.era) + '/' + id;
  }
  const caseUrl = recordUrl;
  function copyCaseLink(id) {
    const url = recordUrl(id);
    const done = function (ok) {
      showToast({ title: ok ? 'LINK COPIED TO CLIPBOARD' : 'COPY FAILED — LINK IS IN THE ADDRESS BAR',
        t: S.t, cls: 'mission', desc: url });
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { done(true); }, function () { done(false); });
    } else done(false);
  }

  // ============ GUIDED TOUR ============
  function findCase(obj, kw) {
    const re = kw.toLowerCase();
    const c = (C.anomalies || []).filter(function (a) { return (a.object || '3i') === obj; })
      .find(function (a) { return ((a.title || '') + ' ' + (a.observation || '')).toLowerCase().indexOf(re) !== -1; });
    return c || null;
  }
  const TOUR = [
    { era: '3i', date: '2025-07-01', cam: 'top', ms: 11000, title: 'FIRST CONTACT — 1 JULY 2025',
      text: 'The ATLAS survey in Chile catches a fast mover. Within days the orbit solution comes back hyperbolic — an eccentricity above 6, the most extreme ever measured. This object is not bound to our Sun. It is passing through, once, and never returning.' },
    { era: '3i', date: '2025-10-03', cam: 'mars', ms: 11000, title: 'MARS FLYBY — 0.19 AU',
      text: 'It threads past Mars at 29 million km, close enough that orbiters there turned their cameras on it. Loeb noted the path also lines up with Venus and Jupiter, and argued that such an economical tour of the planets looks less like chance than like routing.' },
    { era: '3i', date: '2025-10-29', cam: 'sun', ms: 11000, title: 'PERIHELION — BEHIND THE SUN',
      text: 'Closest solar approach, 1.36 AU — and it happens while the object sits directly behind the Sun as seen from Earth. Anything it did here, it did unobserved. The official reading: an unremarkable consequence of orbital geometry.' },
    { era: '3i', caseKw: 'anti-tail', cam: 'chase', ms: 11000, title: 'THE TAIL POINTS THE WRONG WAY',
      text: 'A jet aimed sunward, into the light rather than away from it. Loeb logged it as an anomaly. The mainstream answer is a projection effect from large, slow dust grains — something ordinary comets do too.' },
    { era: '1i', date: '2017-10-19', cam: 'free', ms: 11000, title: "THE ORIGINAL — 1I/ʻOUMUAMUA, 2017",
      text: 'Switch targets and notice what is missing. No tail. No coma. Nothing at all. The first interstellar object we ever saw arrived completely inert — and then accelerated anyway.' },
    { era: '1i', caseKw: 'acceleration', cam: 'free', ms: 11000, title: 'PUSHED BY NOTHING',
      text: 'Astrometry showed a push falling off as 1/r², exactly like sunlight or outgassing. But no gas was ever detected. That gap between a real force and no visible cause is what launched the lightsail paper.' },
    { era: '2i', date: '2019-12-08', cam: 'chase', ms: 11000, title: 'THE CONTROL CASE — 2I/BORISOV',
      text: 'And this is what a normal visitor from another star looks like: a textbook comet, tail streaming dutifully away from the Sun, behaving exactly as physics says it should. Its case file is thin on purpose.' },
    { mode: 'briefings', brief: 'BR-02', ms: 13000, title: 'WHAT THE DATA CAN AND CANNOT SETTLE',
      text: 'The register is 46 cases deep, which is a lot to read. BRIEFINGS is the way in: five questions, each answered from the data with the counter-reading beside it. This one asks whether fireballs are really increasing, and gets three instruments to disagree with each other in a useful way.' },
    { mode: 'fireballs', fbFocus: 'IM1', ms: 12000, title: 'AND THE TWO THAT MAY HAVE LANDED',
      text: 'Every dot is a bolide US Government sensors logged since 1988. Two of them — IM1 off Papua New Guinea, IM2 in the Atlantic — are argued to have arrived from outside the solar system. The catalog that reports them publishes no error bars, which is exactly where the fight is.' },
    { mode: 'compare', cam: 'free', ms: 12000, title: 'THREE VISITORS, THREE STORIES',
      text: 'All three paths at once. Two of them ordinary enough; one still argued over. Every claim in this console sits beside its official rebuttal — go read them and decide for yourself.' },
  ];
  let tour = null;
  function tourStop(quiet) {
    if (tour && tour.timer) clearTimeout(tour.timer);
    tour = null;
    const box = $('cx-tour');
    if (box) box.classList.remove('cx-on');
    const b = $('cx-btn-tour');
    if (b) b.classList.remove('cx-on');
    if (!quiet) showToast({ title: 'TOUR ENDED — CONSOLE IS YOURS', t: S.t, cls: 'mission',
      desc: 'Press ? for controls, or search the case log on the left.' });
  }
  function tourStart() {
    if (tour) { tourStop(true); return; }
    closeOverlay();
    tour = { i: -1, timer: null };
    $('cx-tour').classList.add('cx-on');
    const b = $('cx-btn-tour');
    if (b) b.classList.add('cx-on');
    CX.audio.eraSwitch();
    tourNext();
  }
  function tourNext() {
    if (!tour) return;
    if (tour.timer) clearTimeout(tour.timer);
    tour.i++;
    if (tour.i >= TOUR.length) { tourStop(); return; }
    const st = TOUR[tour.i];

    if (st.era && st.era !== S.era) CX.setEra(st.era);
    if (st.mode) setMode(st.mode);
    else if (S.mode !== 'track') setMode('track');

    S.viz.antiTail = false; S.viz.ecliptic = false;
    let sub = '';
    if (st.caseKw) {
      const c = findCase(st.era, st.caseKw);
      if (c) {
        CX.setT(CX.tOfIso(c.date));
        if (c.viz_hint === 'tail') S.viz.antiTail = true;
        if (c.viz_hint === 'trajectory') S.viz.ecliptic = true;
        sub = ' · CASE ' + c.id;
      }
    } else if (st.date) {
      CX.setT(CX.tOfIso(st.date));
    }
    if (st.fbFocus) CX.fireballs.focus(st.fbFocus);
    if (st.brief) { CX.briefings.open(st.brief); sub = ' · ' + st.brief; }
    if (st.cam) { CX.scene3d.applyPreset(st.cam); markCam(st.cam); }
    S.playing = true; CX.emit('playstate');

    $('cx-tour-step').textContent = 'GUIDED TOUR · STEP ' + (tour.i + 1) + ' OF ' + TOUR.length + sub;
    $('cx-tour-title').textContent = st.title;
    $('cx-tour-text').textContent = st.text;
    CX.audio.missionEvent();

    const fill = $('cx-tour-fill');
    fill.style.transition = 'none';
    fill.style.width = '0%';
    void fill.offsetWidth;
    fill.style.transition = 'width ' + st.ms + 'ms linear';
    fill.style.width = '100%';

    tour.timer = setTimeout(tourNext, st.ms);
  }

  // ============ HELP / ABOUT ============
  function keyRow(cap, txt) {
    return '<div class="cx-keyrow"><b class="cx-keycap">' + esc(cap) + '</b><span>' + esc(txt) + '</span></div>';
  }
  function openHelp() {
    const sheet = $('cx-sheet');
    setH(sheet, [
      '<div class="cx-sheet-head">',
      '  <div class="cx-sh-id">?</div>',
      '  <div class="cx-sh-title">CONSOLE CONTROLS &amp; BRIEFING</div>',
      '  <div class="cx-sh-date">v' + esc(window.APP_VERSION || '') + '</div>',
      '  <button class="cx-x" data-act="close-overlay">✕</button>',
      '</div>',
      '<div class="cx-sheet-body">',
      '  <div class="cx-block"><div class="cx-block-text">',
      '    You are at a workstation of the (fictional) <b>Interstellar Object Working Group</b>, ',
      '    tracking the three confirmed visitors from outside our solar system. Trajectories, ',
      '    planet positions and close-approach distances are <b>real JPL Horizons data</b>. Each ',
      '    numbered case file states what was observed, <span style="color:var(--amber)">Avi Loeb\'s ',
      '    interpretation</span>, and the <span style="color:var(--green)">official explanation</span> ',
      '    side by side — so you can weigh both. Every case was individually fact-checked against ',
      '    primary sources; the chip beside each title shows its verdict.',
      '  </div></div>',
      '  <div class="cx-keys">',
      '    <div><h4>TARGET</h4>',
      keyRow('3I', 'ATLAS — the 2025-26 visitor, 25 cases'),
      keyRow('1I', "'Oumuamua — the 2017 original, 11 cases"),
      keyRow('2I', 'Borisov — the natural control case, 5 items'),
      keyRow('4', 'CNEOS fireballs — 2 disputed meteor cases'),
      '    </div>',
      '    <div><h4>TIME</h4>',
      keyRow('SPACE', 'play / pause the replay'),
      keyRow('← →', 'step one day (SHIFT = one week)'),
      keyRow('drag', 'scrub the timeline bar (drag = time)'),
      keyRow('click', 'open a marker\u2019s full record (tap = record)'),
      keyRow('N', "jump to today's real position (3I only)"),
      '    </div>',
      '    <div><h4>VIEW</h4>',
      keyRow('drag', 'orbit the camera (FREE / TOP-DOWN)'),
      keyRow('wheel', 'zoom in and out'),
      keyRow('L', 'labels on / off'),
      keyRow('G', 'distance grid on / off'),
      keyRow('M', 'mute the mission audio'),
      '    </div>',
      '    <div><h4>SECTIONS</h4>',
      keyRow('1', 'TRACK — the 3D tracking view'),
      keyRow('2', 'ANOMALIES — open the case files'),
      keyRow('3', 'COMPARE — all three paths at once'),
      keyRow('4', 'FIREBALLS — the CNEOS impact map'),
      keyRow('5', 'ARCHIVE — declassified documents'),
      keyRow('ESC', 'close any open panel'),
      '    </div>',
      '  </div>',
      '  <div class="cx-block" style="margin-top:14px"><div class="cx-block-label cx-bl-obs">START HERE</div>',
      '  <div class="cx-block-text">New to this? Take the <b style="color:var(--cyan)">guided tour</b> — about 90 seconds, ',
      '  flying all three objects through their highlights. Otherwise: open case <b>A-05</b> on 3I/ATLAS and press ',
      '  <b style="color:var(--amber)">VISUALIZE IN TRACKER</b> to watch its tail point the wrong way; ',
      '  search <b>&ldquo;nickel&rdquo;</b> in the case log to see the same measurement argued two ways on two ',
      '  different objects; click any <b style="color:var(--cyan)">timeline marker</b> to read that entry in full ',
      '  with its sources, or browse them all under <b style="color:var(--cyan)">MISSION LOG</b> in the left rail ',
      '  (some entries fall outside the scrubber window and have no marker); open ',
      '  <b style="color:var(--cyan)">FIREBALLS</b> for the CNEOS impact map and the two ',
      '  rows Loeb argues are interstellar meteors; and in <b>ARCHIVE</b>, the black redaction bars are clickable.</div>',
      '  <div class="cx-sheet-actions" style="padding:10px 0 0">',
      '    <button class="cx-btn" data-act="tour-start">▶ START GUIDED TOUR</button>',
      '    <button class="cx-btn cx-btn-ghost" data-act="close-overlay">CLOSE</button>',
      '  </div></div>',
      '  <div class="cx-block"><div class="cx-block-text" style="color:var(--txt-faint);font-size:11px">',
      '    Unofficial simulation built for education and entertainment. Not affiliated with, ',
      '    endorsed by, or produced by NASA, JPL, ESA or any government agency. The "IOWG" and its ',
      '    clearance banners are fiction; the ephemerides, measurements, quotes and citations are real.',
      '  </div></div>',
      '</div>',
    ].join('\n'));
    $('cx-overlay').classList.add('cx-show');
  }
  UI.openHelp = openHelp;

  // ============ COMPARE ============
  function renderCompare() {
    const box = $('cx-cmp-table');
    const objs = C.compare || [];
    const cls = ['cx-cmp-1i', 'cx-cmp-2i', 'cx-cmp-3i'];
    function row(label, fn) {
      return '<tr><td>' + label + '</td>' + objs.map(function (o, i) {
        return '<td class="' + cls[i] + '">' + fn(o) + '</td>';
      }).join('') + '</tr>';
    }
    setH(box, [
      '<table class="cx-cmp"><thead><tr><th>PARAMETER</th>',
      objs.map(function (o, i) { return '<th class="' + cls[i] + '">' + esc(o.designation) + ' “' + esc(o.name) + '”</th>'; }).join(''),
      '</tr></thead><tbody>',
      row('DISCOVERED', function (o) { return esc(o.discovered); }),
      row('V-INFINITY', function (o) { return o.v_infinity_kms != null ? o.v_infinity_kms + ' km/s' : '—'; }),
      row('ECCENTRICITY', function (o) { return o.eccentricity != null ? o.eccentricity : '—'; }),
      row('INCLINATION', function (o) { return o.inclination_deg != null ? o.inclination_deg + '°' : '—'; }),
      row('PERIHELION', function (o) { return (o.perihelion_au != null ? o.perihelion_au + ' AU' : '—') + ' · ' + esc(o.perihelion_date || ''); }),
      row('EARTH C/A', function (o) { return o.closest_earth_au != null ? o.closest_earth_au + ' AU' : '—'; }),
      row('SIZE', function (o) { return esc(o.size_estimate || '—'); }),
      row('NATURE', function (o) { return esc(o.nature || '—'); }),
      row('ODDITIES', function (o) { return (o.weird_notes || []).map(function (w) { return '▸ ' + esc(w); }).join('<br>') || '—'; }),
      row('LOEB POSITION', function (o) { return esc(o.loeb_position || '—'); }),
      '</tbody></table>',
    ].join(''));
  }

  // ============ ARCHIVE ============
  function redact(text, hint) {
    return '<span class="cx-redact" title="' + esc(hint || 'REDACTED — CLICK') + '" data-act="redact">' + esc(text) + '</span>';
  }
  function buildDocs() {
    const q = (C.quotes || []);
    const anomalies = C.anomalies || [];
    const meta = ((C.meta || {}).objects || {})['3i'] || {};
    const OBJ_NAMES = { '3i': '3I/ATLAS', '1i': "1I/'OUMUAMUA", '2i': '2I/BORISOV' };
    const docs = [];
    docs.push({
      title: 'IOWG CHARTER MEMORANDUM', sub: 'FICTIONAL FRAMING DOCUMENT',
      html: function () {
        return ['<div class="cx-doc">',
          '<div class="cx-stamp" style="top:18px;right:22px">SIMULATION</div>',
          '<div class="cx-stamp cx-stamp-green" style="bottom:26px;left:26px">DECLASSIFIED — FOR FUN</div>',
          '<div class="cx-doc-head"><div class="cx-doc-org">INTERSTELLAR OBJECT WORKING GROUP</div><div class="cx-doc-sub">INTERAGENCY · EYES ONLY (PRETEND)</div></div>',
          '<div class="cx-doc-meta">MEMO 001 · 2025-07-04 · SUBJECT: STANDING UP THE 3I DESK</div>',
          '<p>Following the 2017 passage of 1I/’Oumuamua and the unresolved questions catalogued thereafter, this working group is directed to maintain a running anomaly file on any subsequent interstellar visitor.</p>',
          '<p>On 1 July 2025 the ATLAS survey (Río Hurtado, Chile) detected a third such object, now designated <b>3I/ATLAS (C/2025 N1)</b>. Its heliocentric excess velocity of ' + redact('~58 km/s', '~58 km/s — fastest ISO recorded') + ' and orbital eccentricity of ' + redact('~6.1', 'e ≈ 6.14, most extreme ever measured') + ' make it the most unambiguous interstellar transit ever recorded.</p>',
          '<p>The desk will log each claimed anomaly alongside the official assessment, without prejudice. Current 3I tally: <b>' + anomalies.filter(function (a) { return (a.object || '3i') === '3i'; }).length + ' numbered cases</b> (see register for the 1I and 2I files). Loeb-scale standing: <b>' + (meta.loebScale != null ? meta.loebScale : '—') + ' / 10</b>.</p>',
          '<p>NOTE FOR FILE: this console is an unofficial visualization built for education and entertainment. It is not a NASA/JPL product. The trajectory data, however, is real — JPL Horizons ephemerides.</p>',
          '<div class="cx-doc-sig">AUTHORIZED: <span class="cx-hand">the desk</span></div>',
          '</div>'].join('');
      },
    });
    docs.push({
      title: 'ANOMALY SUMMARY BRIEF', sub: anomalies.length + ' NUMBERED CASES',
      html: function () {
        return ['<div class="cx-doc">',
          '<div class="cx-stamp" style="top:16px;right:20px">ANOMALOUS</div>',
          '<div class="cx-doc-head"><div class="cx-doc-org">ISO DESK — CASE REGISTER</div><div class="cx-doc-sub">SUMMARY OF CLAIMED DEPARTURES FROM NATURAL BEHAVIOR · ALL THREE VISITORS</div></div>',
          ['3i', '1i', '2i'].map(function (obj) {
            const cases = anomalies.filter(function (a) { return (a.object || '3i') === obj; });
            if (!cases.length) return '';
            return '<p style="letter-spacing:3px;border-bottom:1px solid #1d1a14;margin-top:14px"><b>' + OBJ_NAMES[obj] + ' — ' + cases.length + ' CASES</b></p>' +
              cases.map(function (a) {
                return '<p><b>' + esc(a.id) + '</b> · ' + esc(a.date) + ' — <b>' + esc(a.title) + '</b><br>' + esc(a.observation) + '<br><span style="color:#7a5a1e">' + esc((a.claim_label || 'LOEB ASSESSMENT').split(' ')[0]) + ':</span> ' + esc(String(a.loeb_take).slice(0, 180)) + '…<br><span style="color:#2c6a3f">OFFICIAL:</span> ' + esc(String(a.official_explanation).slice(0, 180)) + '…</p>';
              }).join('');
          }).join(''),
          '</div>'].join('');
      },
    });
    docs.push({
      title: 'DSN TRACKING LOG — PERIHELION', sub: 'SOLAR CONJUNCTION BLACKOUT',
      html: function () {
        const lines = [
          '2025-10-21 04:12Z GOLDSTONE  OPTICAL HANDOFF LOST — SOLAR ELONGATION < 15 DEG',
          '2025-10-24 11:03Z CANBERRA   TARGET IN CONJUNCTION. NO DIRECT OBSERVATION POSSIBLE.',
          '2025-10-29 11:47Z (COMPUTED) PERIHELION PASSAGE — 1.357 AU — ' + 'BEHIND SOLAR DISK AS SEEN FROM EARTH',
          '2025-10-29 11:47Z NOTE       ANY MANEUVER EXECUTED AT PERIHELION WOULD OCCUR PRECISELY WHILE UNOBSERVABLE (SEE CASE FILE)',
          '2025-11-08 02:30Z MADRID     REACQUISITION. OBJECT BRIGHTER THAN PRE-CONJUNCTION MODEL.',
          '2025-11-11 22:14Z SUMMARY    ASTROMETRY SHOWS RESIDUALS VS GRAVITY-ONLY SOLUTION. OUTGASSING FIT APPLIED.',
        ];
        return ['<div class="cx-doc" style="background:#0a1a14;color:#7fd6a8;box-shadow:0 6px 34px rgba(0,0,0,.75)">',
          '<div class="cx-doc-head" style="border-color:#2c6a3f"><div class="cx-doc-org" style="color:#9fe8c0">DEEP SPACE NETWORK — TRACKING EXCERPT</div><div class="cx-doc-sub" style="color:#4d8a66">REPRODUCED FOR REVIEW · STYLIZED</div></div>',
          lines.map(function (l) { return '<p style="margin-bottom:6px;font-size:11.5px">' + esc(l) + '</p>'; }).join(''),
          '</div>'].join('');
      },
    });
    if (q.length) {
      // Every case file carries a verification chip; the quote board used to
      // present all 35 statements identically whether or not anyone had checked
      // them against the source. Each now shows how far it was actually verified.
      const QV = { VERBATIM: ['✓ VERBATIM', '#2c6a3f'], CORRECTED: ['✎ CORRECTED', '#7a5a1e'],
                   PARAPHRASE: ['≈ PARAPHRASE', '#5a4a7a'], SECONDARY: ['· SECONDARY SOURCE', '#6b6257'] };
      const qmeta = (C.meta || {}).quotesVerify || {};
      const counts = qmeta.counts || {};
      docs.push({
        title: 'QUOTE BOARD — ON THE RECORD',
        sub: q.length + ' STATEMENTS · ' + (counts.VERBATIM || 0) + ' VERIFIED VERBATIM',
        html: function () {
          return ['<div class="cx-doc">',
            '<div class="cx-doc-head"><div class="cx-doc-org">WHAT THEY ACTUALLY SAID</div><div class="cx-doc-sub">LOEB CAMP VS OFFICIAL CHANNELS VS PRESS</div></div>',
            (qmeta.note ? '<p style="font-size:10.5px;color:#5a5346;border-bottom:1px solid #1d1a14;padding-bottom:9px">' + esc(qmeta.note) + '</p>' : ''),
            q.map(function (x) {
              const col = x.camp === 'loeb' ? '#7a5a1e' : x.camp === 'official' ? '#2c6a3f' : '#444';
              const v = QV[x.verify] || QV.SECONDARY;
              const chip = '<span style="color:' + v[1] + ';border:1px solid ' + v[1] +
                ';font-size:8.5px;letter-spacing:1px;padding:0 4px;margin-left:6px;white-space:nowrap">' + v[0] + '</span>';
              return '<p>“' + esc(x.text) + '”<br><span style="color:' + col + ';font-size:10.5px">— ' +
                esc(x.speaker) + ' · ' + esc(x.date) + (x.context ? ' · ' + esc(x.context) : '') + '</span>' + chip + '</p>';
            }).join(''),
            '</div>'].join('');
        },
      });
    }
    return docs;
  }
  let DOCS = null;
  function renderArchive() {
    if (!DOCS) DOCS = buildDocs();
    const list = $('cx-doclist');
    setH(list, DOCS.map(function (d, i) {
      return '<div class="cx-row' + (i === S.selDoc ? ' cx-on' : '') + '" data-act="doc" data-i="' + i + '"><div class="cx-row-t">▤ ' + esc(d.title) + '</div><div class="cx-row-s">' + esc(d.sub) + '</div></div>';
    }).join(''));
    setH($('cx-docview'), DOCS[S.selDoc] ? DOCS[S.selDoc].html() : '');
  }

  // ============ MODES ============
  function setMode(m) {
    S.mode = m;
    const rt = $('cx-root');
    if (rt) rt.setAttribute('data-mode', m);
    document.querySelectorAll('.cx-tab').forEach(function (t) {
      t.classList.toggle('cx-on', t.getAttribute('data-tab') === m);
    });
    $('cx-docwrap').style.display = m === 'archive' ? 'grid' : 'none';
    // '' not a value: the narrow-viewport rule collapses this to one scrolling
    // column, and an inline display would out-rank the media query.
    $('cx-briefwrap').style.display = m === 'briefings' ? '' : 'none';
    $('cx-comparewrap').style.display = m === 'compare' ? 'block' : 'none';
    // '' not 'grid': the narrow-viewport rule switches this pane to a single
    // scrolling column, and an inline display would out-rank the media query.
    $('cx-fbwrap').style.display = m === 'fireballs' ? '' : 'none';
    CX.scene3d.setCompare(m === 'compare');
    if (m === 'compare') renderCompare();
    if (m === 'archive') renderArchive();
    if (m === 'fireballs') requestAnimationFrame(function () { CX.fireballs.refresh(); });
    if (m === 'briefings') {
      closeOverlay();
      requestAnimationFrame(function () { CX.briefings.refresh(); });
    }
    if (m === 'anomalies') openDossier((CX.eraAnomalies()[0] || {}).id);
    syncHash();
  }
  UI.setMode = setMode;

  function markCam(name) {
    document.querySelectorAll('[data-act="cam"]').forEach(function (b) {
      b.classList.toggle('cx-on', b.getAttribute('data-cam') === name);
    });
  }

  // ============ ERA (target object) ============
  function updateEraChrome() {
    const em = CX.ERA_META[S.era], om = CX.eraMetaContent();
    const tl = $('cx-title-obj');
    if (tl) { tl.textContent = em.label; tl.style.color = em.color; tl.style.textShadow = '0 0 6px ' + em.color; }
    document.querySelectorAll('[data-act="era"]').forEach(function (b) {
      b.classList.toggle('cx-on', b.getAttribute('data-era') === S.era);
    });
    const pill = $('cx-alert');
    if (pill) pill.textContent = 'LOEB SCALE ' + (om.loebScale != null ? om.loebScale : '—') + ' · ' + (om.pillNote || 'REVIEW ACTIVE');
  }
  UI.updateEraChrome = updateEraChrome;

  function switchEra(k) {
    if (k === S.era || !CX.EPH.eras[k]) return;
    closeOverlay();
    if (S.mode !== 'track') setMode('track');
    CX.setEra(k);
    CX.audio.eraSwitch();
    syncHash();
  }

  // ============ WIRING ============
  function wire() {
    document.addEventListener('click', function (ev) {
      const btn = ev.target.closest('[data-act]');
      if (!btn) return;
      const act = btn.getAttribute('data-act');
      if (act !== 'redact') CX.audio.ui();
      if (act === 'tab') setMode(btn.getAttribute('data-tab'));
      else if (act === 'brief') CX.briefings.open(btn.getAttribute('data-brief'));
      else if (act === 'brief-case') {
        const obj = btn.getAttribute('data-obj');
        if (obj && obj !== S.era && CX.EPH.eras[obj]) CX.setEra(obj);
        setMode(obj === 'fb' ? 'fireballs' : 'anomalies');
        openDossier(btn.getAttribute('data-case'));
      }
      else if (act === 'era') switchEra(btn.getAttribute('data-era'));
      else if (act === 'cam') { CX.scene3d.applyPreset(btn.getAttribute('data-cam')); markCam(btn.getAttribute('data-cam')); }
      else if (act === 'play') togglePlay();
      else if (act === 'step') { CX.setT(S.t + Number(btn.getAttribute('data-d'))); }
      else if (act === 'speed') {
        S.speed = Number(btn.getAttribute('data-s'));
        document.querySelectorAll('[data-act="speed"]').forEach(function (b) { b.classList.toggle('cx-on', b === btn); });
      }
      else if (act === 'now') {
        if (CX.NOW_T != null) { CX.setT(CX.NOW_T); showToast({ title: 'CURRENT EPOCH — LIVE POSITION', t: CX.NOW_T, cls: 'mission', desc: 'Real position for today from JPL Horizons data.' }); }
        else { CX.audio.uiLow(); showToast({ title: 'HISTORICAL REPLAY — TARGET NOT IN CURRENT EPOCH', t: S.t, cls: 'mission', desc: 'This object transited in the past; today falls outside its tracked window.' }); }
      }
      else if (act === 'audio') { S.audio = !S.audio; CX.audio.setMuted(!S.audio); btn.classList.toggle('cx-on', S.audio); }
      else if (act === 'crt') { S.crt = !S.crt; document.body.classList.toggle('cx-crt', S.crt); btn.classList.toggle('cx-on', S.crt); }
      else if (act === 'labels') { S.labels = !S.labels; btn.classList.toggle('cx-on', S.labels); }
      else if (act === 'orbits') { S.orbits = !S.orbits; btn.classList.toggle('cx-on', S.orbits); }
      else if (act === 'grid') { S.grid = !S.grid; btn.classList.toggle('cx-on', S.grid); }
      else if (act === 'dispatch') {
        S.viz.dispatch = !S.viz.dispatch;
        btn.classList.toggle('cx-on', S.viz.dispatch);
        const n = $('cx-specnote');
        if (n) n.classList.toggle('cx-show', S.viz.dispatch);
        if (S.viz.dispatch) {
          showToast({ title: 'DISPATCH OVERLAY ON \u2014 SPECULATIVE', t: S.t, cls: 'anomaly',
            kind: 'anomaly',
            desc: 'Draws the claim that material was released at the Mars pass, perihelion and the Jupiter pass. No instrument has observed any such release. Scrub to 2025-10-03, 2025-10-29 or 2026-03-17 to see it.' });
        }
      }
      else if (act === 'anomaly') {
        const obj = btn.getAttribute('data-obj');
        if (obj && obj !== S.era) CX.setEra(obj);   // cross-object search result
        openDossier(btn.getAttribute('data-id'));
      }
      else if (act === 'log-tab') UI.setLogTab(btn.getAttribute('data-tab'));
      else if (act === 'q-clear') { UI.setQuery(''); const qi = $('cx-q'); if (qi) { qi.value = ''; qi.focus(); } }
      else if (act === 'tour-start') tourStart();
      else if (act === 'tour-next') tourNext();
      else if (act === 'tour-stop') tourStop();
      else if (act === 'copy-link') copyCaseLink(btn.getAttribute('data-id'));
      else if (act === 'approach') { CX.setT(CX.tOfIso(btn.getAttribute('data-date'))); }
      else if (act === 'doc') { S.selDoc = Number(btn.getAttribute('data-i')); renderArchive(); }
      else if (act === 'help') openHelp();
      else if (act === 'rail') {
        const side = btn.getAttribute('data-side');
        const cls = side === 'left' ? 'cx-show-left' : 'cx-show-right';
        const other = side === 'left' ? 'cx-show-right' : 'cx-show-left';
        document.body.classList.remove(other);
        document.body.classList.toggle(cls);
      }
      else if (act === 'close-overlay') closeOverlay();
      else if (act === 'visualize') visualize(btn.getAttribute('data-id'));
      else if (act === 'fb-visualize') fbVisualize(btn.getAttribute('data-id'));
      else if (act === 'fb-case') openDossier(btn.getAttribute('data-id'));
      else if (act === 'event') openEvent(btn.getAttribute('data-id'));
      else if (act === 'event-nav') {
        if (!eventList.length) return;
        const i = (eventIdx + Number(btn.getAttribute('data-d')) + eventList.length) % eventList.length;
        openEvent(eventList[i].id);
      }
      else if (act.indexOf('fb-') === 0) CX.fireballs.act(act, btn);
      else if (act === 'dossier-nav') {
        if (!dossierList.length) return;
        const i = (dossierIdx + Number(btn.getAttribute('data-d')) + dossierList.length) % dossierList.length;
        openDossier(dossierList[i].id);
      }
      else if (act === 'redact') {
        btn.style.color = '#efe8d0'; btn.style.background = '#3a3226';
        CX.audio.uiLow();
      }
    });
    $('cx-overlay').addEventListener('click', function (ev) {
      if (ev.target === $('cx-overlay')) closeOverlay();
    });

    // Delegated: the left rail (and the search box with it) is rebuilt on era switch.
    document.addEventListener('input', function (ev) {
      if (ev.target && ev.target.id === 'cx-q') UI.setQuery(ev.target.value);
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.target && ev.target.id === 'cx-q' && ev.key === 'Escape') {
        ev.stopPropagation();
        ev.target.value = ''; UI.setQuery(''); ev.target.blur();
      }
    });
    window.addEventListener('hashchange', function () { if (!hashLock) applyHash(); });

    // Pointer events, not mouse events: a finger drag never emits mousemove, so
    // the old handlers were dead on touch. Pointer capture keeps the drag alive
    // when the finger slides outside the track.
    const track = $('cx-tl-track');
    let tlPointer = null;
    track.addEventListener('pointerdown', function (ev) {
      if (ev.pointerType === 'mouse' && ev.button !== 0) return;
      if (tlClick(ev, ev.pointerType === 'mouse' ? 6 : 8)) return;
      tlPointer = ev.pointerId;
      tlDragging = true;
      try { track.setPointerCapture(ev.pointerId); } catch (e) { /* not fatal */ }
      tlScrub(ev);
      ev.preventDefault();
    });
    track.addEventListener('pointermove', function (ev) {
      if (!tlDragging || ev.pointerId !== tlPointer) return;
      tlScrub(ev);
      ev.preventDefault();
    });
    function tlRelease(ev) {
      if (ev && tlPointer != null && ev.pointerId !== tlPointer) return;
      tlDragging = false; tlPointer = null;
    }
    track.addEventListener('pointerup', tlRelease);
    track.addEventListener('pointercancel', tlRelease);

    window.addEventListener('keydown', function (ev) {
      if (!S.booted) return;
      if (ev.target && (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA')) return;
      const k = ev.key;
      if (k === ' ') { ev.preventDefault(); togglePlay(); }
      else if (k === 'ArrowRight') CX.setT(S.t + (ev.shiftKey ? 7 : 1));
      else if (k === 'ArrowLeft') CX.setT(S.t - (ev.shiftKey ? 7 : 1));
      else if (k === '1') setMode('track');
      else if (k === '2') setMode('anomalies');
      else if (k === '3') setMode('compare');
      else if (k === '4') setMode('fireballs');
      else if (k === '5') setMode('archive');
      else if (k === 'n' || k === 'N') { if (CX.NOW_T != null) CX.setT(CX.NOW_T); }
      else if (k === 'l' || k === 'L') { S.labels = !S.labels; }
      else if (k === 'g' || k === 'G') { S.grid = !S.grid; }
      else if (k === 'm' || k === 'M') { S.audio = !S.audio; CX.audio.setMuted(!S.audio); $('cx-btn-audio').classList.toggle('cx-on', S.audio); }
      else if (k === '?' || k === '/') { ev.preventDefault(); openHelp(); }
      else if (k === 't' || k === 'T') tourStart();
      else if (k === 'Escape') {
        document.body.classList.remove('cx-show-left', 'cx-show-right');
        if (tour) tourStop();
        else closeOverlay();
      }
    });

    window.addEventListener('resize', throttle(function () {
      syncChromeVars();
      UI.renderTimeline(); CX.charts.renderRail();
      if (S.mode === 'fireballs') CX.fireballs.refresh();
    }, 200));

    // reactive updates
    const slow = throttle(function () { UI.renderClock(); UI.renderTimeline(); CX.charts.renderRail(); }, 120);
    const anomalyDim = throttle(function () { UI.renderAnomalyList(); }, 900);
    CX.on('time', function () { slow(); anomalyDim(); });
    CX.on('eventCross', function (e) {
      showToast(Object.assign({}, e, { kind: e.cls === 'anomaly' ? 'anomaly' : 'mission' }));
      if (e.cls === 'anomaly') CX.audio.anomalyAlert(); else CX.audio.missionEvent();
    });
    CX.on('playstate', function () {
      $('cx-btn-play').textContent = S.playing ? '⏸' : '▶';
    });
    CX.on('era', function () {
      buildLeftRail();
      buildRightRail();
      updateEraChrome();
      UI.renderClock();
      UI.renderTimeline();
      CX.charts.renderRail();
      S.playing = true;
      CX.emit('playstate');
      const em = CX.ERA_META[S.era];
      showToast({ title: 'TARGET SWITCHED — ' + em.label + ' · ' + em.sub, t: S.t, cls: 'mission',
        desc: 'Replay armed from discovery. Timeline, anomaly log and telemetry now scoped to this object.' });
    });
  }
  function togglePlay() {
    S.playing = !S.playing;
    CX.emit('playstate');
  }

  // ============ BOOT ============
  UI.boot = function (onDone) {
    const boot = el('div', 'cx-boot');
    setH(boot, [
      '<div class="cx-boot-inner">',
      '  <div class="cx-boot-log" id="cx-boot-log"></div>',
      '  <div class="cx-boot-auth" id="cx-boot-auth">▮ TAP OR PRESS ANY KEY TO AUTHENTICATE ▮</div>',
      '</div>',
      '<div class="cx-boot-skip" id="cx-boot-skip">TAP HERE OR PRESS ESC — SKIP SEQUENCE</div>',
    ].join(''));
    document.body.appendChild(boot);
    const log = $('cx-boot-log');
    const lines = [
      ['cx-bl-head', 'IOWG SECURE WORKSTATION · NODE 3I-DESK-07'],
      ['cx-bl-dim', 'FIRMWARE 5.11.2 · CLEARANCE CHANNEL: TS//SAP-ATLAS (SIMULATED)'],
      ['', '&nbsp;'],
      ['', 'INITIALIZING SUBSYSTEMS'],
      ['bar', 'EPHEMERIS CORE ......... JPL HORIZONS BAKE 2026-07-17'],
      ['bar', 'RENDER PIPELINE ........ WEBGL / 3-BODY VISUAL STACK'],
      ['bar', 'ANOMALY REGISTER ....... CASE FILES MOUNTED'],
      ['bar', 'IMPACT REGISTER ........ CNEOS FIREBALL CATALOG'],
      ['bar', 'AUDIO TELEMETRY ........ SYNTH BUS ONLINE'],
      ['', '&nbsp;'],
      ['', 'ESTABLISHING DSN LINK'],
      ['cx-bl-ok', '  GOLDSTONE ............ LOCK'],
      ['cx-bl-ok', '  CANBERRA ............. LOCK'],
      ['cx-bl-ok', '  MADRID ............... LOCK'],
      ['', '&nbsp;'],
      ['cx-bl-warn', 'TARGET 3I/ATLAS · C/2025 N1 — INTERSTELLAR · OUTBOUND'],
      ['cx-bl-warn', 'ANOMALY REVIEW STATUS: ACTIVE'],
    ];
    let i = 0, done = false;
    function finish(skipAll) {
      if (done) return;
      done = true;
      const auth = $('cx-boot-auth');
      auth.classList.add('cx-ready');
      function go() {
        window.removeEventListener('keydown', keyGo, true);
        boot.style.transition = 'opacity .7s';
        boot.style.opacity = '0';
        setTimeout(function () { boot.remove(); }, 750);
        onDone();
      }
      function keyGo(ev) { ev.preventDefault(); ev.stopPropagation(); go(); }
      auth.addEventListener('click', go);
      window.addEventListener('keydown', keyGo, true);
    }
    function next() {
      if (done && i < lines.length) { /* fast-fill on skip */ }
      if (i >= lines.length) { finish(); return; }
      const ln = lines[i++];
      if (ln[0] === 'bar') {
        const row = el('div', '', esc(ln[1]) + ' <span class="cx-boot-bar"></span>');
        log.appendChild(row);
        const bar = row.querySelector('.cx-boot-bar');
        let b = 0;
        const iv = setInterval(function () {
          b += 2 + Math.floor(Math.random() * 4);
          if (b >= 24) { b = 24; clearInterval(iv); bar.textContent = ' [' + '■'.repeat(24) + '] OK'; setTimeout(next, 60); }
          else bar.textContent = ' [' + '■'.repeat(b) + '·'.repeat(24 - b) + ']';
        }, 26);
        CX.audio.boot && CX.audio.ctx && CX.audio.boot(i);
      } else {
        log.appendChild(el('div', ln[0], ln[1]));
        setTimeout(next, ln[1] === '&nbsp;' ? 90 : 150 + Math.random() * 160);
      }
    }
    function skipAll() {
      if (done) return;
      while (i < lines.length) { const ln = lines[i++]; log.appendChild(el('div', ln[0] === 'bar' ? '' : ln[0], ln[1] + (ln[0] === 'bar' ? ' [OK]' : ''))); }
      finish(true);
      window.removeEventListener('keydown', skip);
    }
    function skip(ev) { if (ev.key === 'Escape') skipAll(); }
    window.addEventListener('keydown', skip);
    const skipBtn = $('cx-boot-skip');
    if (skipBtn) skipBtn.addEventListener('click', skipAll);
    next();
  };
})();
