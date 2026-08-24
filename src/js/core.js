/* ============================================================
   CORE — state, time engine, ERA-AWARE ephemeris access, audio
   window.CX is the app namespace. Load order: core, charts,
   scene3d, ui, main.
   Eras: '3i' (ATLAS 2025-26) / '1i' ('Oumuamua 2017-18) / '2i'
   (Borisov 2019-20). Each era has its own target + planet
   ephemerides and its own timeline window.
   ============================================================ */
(function () {
  'use strict';
  const CX = (window.CX = {});

  // ---------- data handles ----------
  const EPH = window.ATLAS_EPHEM || { eras: {} };
  const CONTENT = window.ATLAS_CONTENT || { meta: { objects: {} }, anomalies: [], timeline: [], quotes: [], compare: [] };
  CX.EPH = EPH; CX.CONTENT = CONTENT;

  CX.ERA_META = {
    '3i': { key: '3i', label: '3I/ATLAS', sub: 'C/2025 N1', color: '#ffb347', colorHex: 0xffb347,
            discovery: '2025-07-01', designation: '3I/ATLAS · C/2025 N1' },
    '1i': { key: '1i', label: "1I/'OUMUAMUA", sub: '1I/2017 U1', color: '#d9b8ff', colorHex: 0xd9b8ff,
            discovery: '2017-10-19', designation: "1I/'OUMUAMUA · 1I/2017 U1" },
    '2i': { key: '2i', label: '2I/BORISOV', sub: 'C/2019 Q4', color: '#9fd9ff', colorHex: 0x9fd9ff,
            discovery: '2019-08-30', designation: '2I/BORISOV · C/2019 Q4' },
    // Not an era: the fireball register has no ephemeris and never becomes S.era.
    // It is here so cross-object case search can badge and colour its two cases.
    'fb': { key: 'fb', label: 'CNEOS FIREBALLS', sub: 'ATMOSPHERIC IMPACTS', color: '#ff8a5e', colorHex: 0xff8a5e,
            discovery: '2014-01-08', designation: 'CNEOS FIREBALL REGISTER' },
  };
  CX.ERA_ORDER = ['3i', '1i', '2i'];

  const DAY = 86400000;
  const MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
  CX.MONTHS = MONTHS;

  // ---------- state ----------
  const S = (CX.S = {
    era: '3i',
    mode: 'track',
    t: 0,
    playing: false,
    speed: 3,
    booted: false,
    selAnomaly: null,
    selEvent: null,
    selDoc: 0,
    camPreset: 'free',
    audio: true,
    crt: true,
    labels: true,
    orbits: true,
    grid: false,
    viz: { antiTail: false, ecliptic: false, dispatch: false },
  });

  // ---------- era plumbing ----------
  CX.eraData = function () { return EPH.eras[S.era] || { objects: {}, close_approaches: {} }; };
  CX.CA = function () { return CX.eraData().close_approaches || {}; };

  function utcOfIsoDate(iso) {
    return Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10));
  }

  CX.EPOCH = 0; CX.N = 1; CX.NOW_T = null;

  CX.applyEraClock = function () {
    const e = CX.eraData();
    const tgt = e.objects.target || { n: 2, step_days: 1, start: '2025-05-15' };
    CX.EPOCH = utcOfIsoDate(tgt.start);
    CX.N = Math.round((tgt.n - 1) * tgt.step_days) + 1;
    const nowT = (Date.now() - CX.EPOCH) / DAY;
    CX.NOW_T = (nowT >= 0 && nowT <= CX.N - 1) ? nowT : null;
  };

  CX.setEra = function (k, silent) {
    if (!EPH.eras[k]) return;
    S.era = k;
    CX.applyEraClock();
    S.viz.antiTail = false; S.viz.ecliptic = false; S.viz.dispatch = false;
    S.selAnomaly = null; S.selEvent = null;
    CX.setT(CX.tOfIso(CX.ERA_META[k].discovery), true);
    if (!silent) { CX.emit('era'); CX.emit('time'); }
  };

  // ---------- time model ----------
  CX.dateOf = function (t) { return new Date(CX.EPOCH + t * DAY); };
  CX.isoOf = function (t) { return CX.dateOf(t).toISOString().slice(0, 10); };
  CX.tOfIso = function (iso) { return (utcOfIsoDate(iso) - CX.EPOCH) / DAY; };
  CX.fmtDate = function (t) {
    const d = CX.dateOf(t);
    return d.getUTCFullYear() + ' ' + MONTHS[d.getUTCMonth()] + ' ' + String(d.getUTCDate()).padStart(2, '0');
  };

  // ---------- ephemeris interpolation (era-aware) ----------
  // key: 'target' or a planet name; t is fractional days from era epoch.
  CX.pos = function (key, t) {
    const o = CX.eraData().objects[key];
    if (!o) return [0, 0, 0];
    let i = t / o.step_days;
    if (i <= 0) i = 0;
    if (i >= o.n - 1) i = o.n - 1.000001;
    const i0 = Math.floor(i), f = i - i0;
    const a = o.pos[i0], b = o.pos[Math.min(i0 + 1, o.n - 1)];
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
  };
  CX.eraTargetPath = function (eraKey) {
    const e = EPH.eras[eraKey];
    return e && e.objects.target ? e.objects.target : null;
  };
  CX.dist = function (p, q) {
    const dx = p[0] - q[0], dy = p[1] - q[1], dz = p[2] - q[2];
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  };
  CX.rSun = function (key, t) { return CX.dist(CX.pos(key, t), [0, 0, 0]); };
  CX.range = function (a, b, t) { return CX.dist(CX.pos(a, t), CX.pos(b, t)); };
  CX.targetSpeed = function (t) {
    const o = CX.eraData().objects.target;
    const s = o && o.speed_kms;
    if (!s) return 0;
    let i = t / o.step_days;
    i = Math.max(0, Math.min(s.length - 1.000001, i));
    const i0 = Math.floor(i), f = i - i0;
    return s[i0] + (s[Math.min(i0 + 1, s.length - 1)] - s[i0]) * f;
  };
  CX.AU_KM = 149597870.7;

  // ---------- content scoping ----------
  CX.eraMetaContent = function () {
    return (CONTENT.meta && CONTENT.meta.objects && CONTENT.meta.objects[S.era]) || {};
  };
  CX.eraAnomalies = function () {
    return (CONTENT.anomalies || []).filter(function (a) { return (a.object || '3i') === S.era; });
  };
  CX.eraTimeline = function () {
    return (CONTENT.timeline || []).filter(function (e) { return (e.object || '3i') === S.era; });
  };
  // Timeline entries are addressable by id (E-YYYYMMDD), the same way case files
  // are, so they can be deep-linked and walked.
  CX.eventById = function (id) {
    const want = String(id || '').toLowerCase();
    return (CONTENT.timeline || []).find(function (e) {
      return String(e.id || '').toLowerCase() === want;
    }) || null;
  };

  // ---------- tiny event bus ----------
  const subs = {};
  CX.on = function (ev, fn) { (subs[ev] = subs[ev] || []).push(fn); };
  CX.emit = function (ev, arg) { (subs[ev] || []).forEach(function (fn) { fn(arg); }); };

  // ---------- audio engine (all synthesized, no assets) ----------
  const AU = (CX.audio = { ctx: null, master: null, humOn: false });

  AU.init = function () {
    if (AU.ctx) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    AU.ctx = new Ctx();
    AU.master = AU.ctx.createGain();
    AU.master.gain.value = S.audio ? 1 : 0;
    AU.master.connect(AU.ctx.destination);
    AU.startHum();
    AU.bleepLoop();
  };
  AU.setMuted = function (m) {
    if (!AU.master) return;
    AU.master.gain.linearRampToValueAtTime(m ? 0 : 1, AU.ctx.currentTime + 0.15);
  };
  AU.startHum = function () {
    if (AU.humOn || !AU.ctx) return;
    AU.humOn = true;
    const g = AU.ctx.createGain(); g.gain.value = 0.0; g.connect(AU.master);
    g.gain.linearRampToValueAtTime(0.016, AU.ctx.currentTime + 2.5);
    [[55, 'sine', 1], [41.2, 'sine', 0.6], [110.3, 'triangle', 0.18]].forEach(function (cfg) {
      const o = AU.ctx.createOscillator(), og = AU.ctx.createGain();
      o.type = cfg[1]; o.frequency.value = cfg[0]; og.gain.value = cfg[2];
      o.connect(og); og.connect(g); o.start();
    });
    const len = AU.ctx.sampleRate * 2, buf = AU.ctx.createBuffer(1, len, AU.ctx.sampleRate);
    const ch = buf.getChannelData(0); let last = 0;
    for (let i = 0; i < len; i++) { const w = Math.random() * 2 - 1; last = (last + 0.02 * w) / 1.02; ch[i] = last * 3; }
    const src = AU.ctx.createBufferSource(); src.buffer = buf; src.loop = true;
    const f = AU.ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 240;
    const ng = AU.ctx.createGain(); ng.gain.value = 0.35;
    src.connect(f); f.connect(ng); ng.connect(g); src.start();
  };
  function tone(freq, dur, gain, type, when) {
    if (!AU.ctx) return;
    const t0 = AU.ctx.currentTime + (when || 0);
    const o = AU.ctx.createOscillator(), g = AU.ctx.createGain();
    o.type = type || 'sine'; o.frequency.value = freq;
    g.gain.setValueAtTime(0, t0);
    g.gain.linearRampToValueAtTime(gain, t0 + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0004, t0 + dur);
    o.connect(g); g.connect(AU.master);
    o.start(t0); o.stop(t0 + dur + 0.05);
  }
  AU.tone = tone;
  AU.bleepLoop = function () {
    if (!AU.ctx) return;
    const delay = 3200 + Math.random() * 5200;
    setTimeout(function () {
      if (S.audio && !document.hidden) {
        const f = 820 + Math.random() * 900;
        tone(f, 0.05, 0.018, 'sine');
        if (Math.random() < 0.35) tone(f * 1.34, 0.045, 0.013, 'sine', 0.09);
      }
      AU.bleepLoop();
    }, delay);
  };
  AU.ui = function () { tone(2100, 0.03, 0.02, 'square'); };
  AU.uiLow = function () { tone(1100, 0.04, 0.02, 'square'); };
  AU.boot = function (i) { tone(500 + (i % 5) * 160, 0.03, 0.016, 'square'); };
  AU.missionEvent = function () { tone(880, 0.1, 0.05); tone(1320, 0.14, 0.035, 'sine', 0.11); };
  AU.anomalyAlert = function () {
    tone(660, 0.13, 0.055, 'triangle'); tone(494, 0.16, 0.05, 'triangle', 0.15);
    tone(660, 0.13, 0.04, 'triangle', 0.34); tone(494, 0.2, 0.038, 'triangle', 0.49);
  };
  AU.auth = function () {
    tone(392, 0.1, 0.05); tone(523, 0.1, 0.05, 'sine', 0.11);
    tone(659, 0.12, 0.05, 'sine', 0.22); tone(1046, 0.35, 0.045, 'sine', 0.34);
  };
  AU.eraSwitch = function () {
    tone(523, 0.07, 0.04, 'square'); tone(784, 0.09, 0.035, 'square', 0.09);
    tone(1046, 0.16, 0.03, 'sine', 0.19);
  };

  // ---------- events (era-scoped mission + anomaly markers) ----------
  CX.allEvents = function () {
    const evs = [];
    CX.eraTimeline().forEach(function (e) {
      evs.push({ t: CX.tOfIso(e.date), kind: e.kind || 'observation', title: e.title, desc: e.description, cls: 'mission', src: e });
    });
    CX.eraAnomalies().forEach(function (a) {
      evs.push({ t: CX.tOfIso(a.date), kind: 'anomaly', title: a.id + ' — ' + a.title, desc: a.observation, cls: 'anomaly', src: a });
    });
    evs.sort(function (a, b) { return a.t - b.t; });
    return evs;
  };

  // ---------- sim clock tick ----------
  let lastFrame = null;
  CX.tick = function (now) {
    if (lastFrame == null) lastFrame = now;
    const dt = Math.min(0.1, (now - lastFrame) / 1000);
    lastFrame = now;
    if (S.playing) {
      const prev = S.t;
      S.t += S.speed * dt;
      if (S.t >= CX.N - 1) { S.t = CX.N - 1; S.playing = false; CX.emit('playstate'); }
      CX.checkEventCrossings(prev, S.t);
      CX.emit('time');
    }
  };
  CX.setT = function (t, silent) {
    S.t = Math.max(0, Math.min(CX.N - 1, t));
    if (!silent) CX.emit('time');
  };
  CX.checkEventCrossings = function (t0, t1) {
    if (t1 <= t0) return;
    const evs = CX.allEvents();
    for (let i = 0; i < evs.length; i++) {
      if (evs[i].t > t0 && evs[i].t <= t1) { CX.emit('eventCross', evs[i]); }
    }
  };

  // boot-time clock init (era 3i)
  CX.applyEraClock();
})();
