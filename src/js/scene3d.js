/* ============================================================
   SCENE3D — Three.js solar system + the active interstellar object
   Heliocentric ecliptic J2000 -> scene: x=X, y=Z, z=-Y, 1 AU = 10u
   Era-aware: the target body, its path and its look rebuild when
   the active era ('3i'/'1i'/'2i') changes.
   ============================================================ */
(function () {
  'use strict';
  const CX = window.CX, S = CX.S;
  const SC = (CX.scene3d = {});
  const AUu = 10;

  let renderer, scene, camera, controls, container, hud;
  let cometGroup, coreSprite, ionPts, dustPts, antiPts, trailFull, trailDone, periMarker;
  let sunLight, eclipticDisc, gridGroup, rangeLine, rangeTag;
  let compareGroup = null, compareLabels = {};
  let labelEls = {};
  let tween = null;
  let frameT = 0;
  let eraStep = 1;

  const v3 = function (p) { return new THREE.Vector3(p[0] * AUu, p[2] * AUu, -p[1] * AUu); };

  // per-era look of the target body
  const ERA_LOOK = {
    '3i': { core: 0xdffaff, coreScale: [1.35, 1.35], tails: true, actBase: 2.2, actMax: 3.2,
            trail: 0x49e8ff, full: 0x2a7d96,
            ion0: [0.34, 0.82, 1.0], ion1: [0.06, 0.24, 0.5], dust0: [1.0, 0.93, 0.74], dust1: [0.34, 0.27, 0.18] },
    '1i': { core: 0xe8d9ff, coreScale: [2.7, 0.6], tails: false,
            trail: 0xc9a8ff, full: 0x5d4a80 },
    '2i': { core: 0xe4f2ff, coreScale: [1.1, 1.1], tails: true, actBase: 2.9, actMax: 1.9,
            trail: 0x8fd0ff, full: 0x3a6a8f,
            ion0: [0.4, 0.75, 1.0], ion1: [0.08, 0.2, 0.45], dust0: [0.95, 0.97, 1.0], dust1: [0.3, 0.32, 0.36] },
  };

  const PLANETS = [
    { key: 'mercury', name: 'MERCURY', r: 0.055, color: 0x9c9488 },
    { key: 'venus',   name: 'VENUS',   r: 0.10,  color: 0xe8c88a },
    { key: 'earth',   name: 'EARTH',   r: 0.105, color: 0x5f9fe8 },
    { key: 'mars',    name: 'MARS',    r: 0.075, color: 0xd3603f },
    { key: 'jupiter', name: 'JUPITER', r: 0.34,  color: 0xd8a76f },
    { key: 'saturn',  name: 'SATURN',  r: 0.29,  color: 0xe6d3a3 },
    { key: 'uranus',  name: 'URANUS',  r: 0.20,  color: 0x9adfe3 },
    { key: 'neptune', name: 'NEPTUNE', r: 0.20,  color: 0x5f74e8 },
  ];
  const ELEMENTS = {
    mercury: [0.38710, 0.20563, 7.005, 48.331, 77.456],
    venus:   [0.72333, 0.00677, 3.395, 76.680, 131.564],
    earth:   [1.00000, 0.01671, 0.000, 0.000, 102.937],
    mars:    [1.52368, 0.09340, 1.850, 49.558, 336.041],
    jupiter: [5.20260, 0.04849, 1.303, 100.464, 14.331],
    saturn:  [9.55491, 0.05551, 2.489, 113.666, 93.057],
    uranus:  [19.21845, 0.04630, 0.773, 74.006, 173.005],
    neptune: [30.11039, 0.00899, 1.770, 131.784, 48.124],
  };
  const planetMeshes = {};

  // ---------- canvas textures ----------
  function glowTexture(inner, mid, size) {
    const c = document.createElement('canvas'); c.width = c.height = size || 128;
    const g = c.getContext('2d');
    const rad = c.width / 2;
    const grad = g.createRadialGradient(rad, rad, 0, rad, rad, rad);
    grad.addColorStop(0, inner);
    grad.addColorStop(0.25, mid);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = grad; g.fillRect(0, 0, c.width, c.height);
    return new THREE.CanvasTexture(c);
  }
  let dotTex = null;
  function dotTexture() {
    if (dotTex) return dotTex;
    const c = document.createElement('canvas'); c.width = c.height = 64;
    const g = c.getContext('2d');
    const grad = g.createRadialGradient(32, 32, 0, 32, 32, 30);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.4, 'rgba(255,255,255,.45)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
    dotTex = new THREE.CanvasTexture(c);
    return dotTex;
  }

  // ---------- starfield ----------
  function buildStars() {
    const dot = dotTexture();
    function starSystem(count, radius, size, bandPole, bandSigma, brightness) {
      const geo = new THREE.BufferGeometry();
      const pos = new Float32Array(count * 3), col = new Float32Array(count * 3);
      const pole = bandPole ? bandPole.clone().normalize() : null;
      let placed = 0, guard = 0;
      while (placed < count && guard < count * 40) {
        guard++;
        const u = Math.random() * 2 - 1, th = Math.random() * Math.PI * 2;
        const s = Math.sqrt(1 - u * u);
        const d = new THREE.Vector3(s * Math.cos(th), u, s * Math.sin(th));
        if (pole) {
          const lat = Math.abs(90 - THREE.MathUtils.radToDeg(d.angleTo(pole)));
          const p = Math.exp(-(lat * lat) / (2 * bandSigma * bandSigma));
          if (Math.random() > p) continue;
        }
        const r = radius * (0.92 + Math.random() * 0.16);
        pos[placed * 3] = d.x * r; pos[placed * 3 + 1] = d.y * r; pos[placed * 3 + 2] = d.z * r;
        const t = Math.random();
        let cr, cg, cb;
        if (t < 0.72) { cr = 0.75; cg = 0.85; cb = 1.0; }
        else if (t < 0.9) { cr = 1.0; cg = 0.97; cb = 0.9; }
        else { cr = 1.0; cg = 0.78; cb = 0.6; }
        const b = brightness * (0.35 + Math.random() * 0.65);
        col[placed * 3] = cr * b; col[placed * 3 + 1] = cg * b; col[placed * 3 + 2] = cb * b;
        placed++;
      }
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      const mat = new THREE.PointsMaterial({
        size: size, sizeAttenuation: false, map: dot, vertexColors: true,
        transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      });
      const pts = new THREE.Points(geo, mat);
      pts.frustumCulled = false;
      return pts;
    }
    scene.add(starSystem(3800, 1800, 1.7, null, 0, 0.75));
    scene.add(starSystem(240, 1750, 3.2, null, 0, 1.0));
    const bl = THREE.MathUtils.degToRad(180.0), bb = THREE.MathUtils.degToRad(29.81);
    const pole = new THREE.Vector3(
      Math.cos(bb) * Math.cos(bl),
      Math.sin(bb),
      -Math.cos(bb) * Math.sin(bl)
    );
    scene.add(starSystem(3200, 1850, 1.35, pole, 9, 0.5));
    scene.add(starSystem(500, 1830, 2.1, pole, 5, 0.7));
  }

  // ---------- orbits ----------
  function orbitLine(el, color, opacity) {
    const a = el[0], e = el[1];
    const inc = THREE.MathUtils.degToRad(el[2]);
    const raan = THREE.MathUtils.degToRad(el[3]);
    const argp = THREE.MathUtils.degToRad(el[4] - el[3]);
    const pts = [];
    for (let k = 0; k <= 256; k++) {
      const nu = (k / 256) * Math.PI * 2;
      const r = a * (1 - e * e) / (1 + e * Math.cos(nu));
      const xw = r * Math.cos(nu + argp), yw = r * Math.sin(nu + argp);
      const x = xw * Math.cos(raan) - yw * Math.cos(inc) * Math.sin(raan);
      const y = xw * Math.sin(raan) + yw * Math.cos(inc) * Math.cos(raan);
      const z = yw * Math.sin(inc);
      pts.push(v3([x, y, z]));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    return new THREE.Line(geo, new THREE.LineBasicMaterial({
      color: color, transparent: true, opacity: opacity, depthWrite: false,
    }));
  }

  function buildPlanets() {
    const glow = glowTexture('rgba(255,255,255,.9)', 'rgba(150,190,255,.25)');
    PLANETS.forEach(function (p) {
      const grp = new THREE.Group();
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(p.r, 24, 16),
        new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.85, metalness: 0.05,
          emissive: p.color, emissiveIntensity: 0.22 })
      );
      grp.add(mesh);
      const spr = new THREE.Sprite(new THREE.SpriteMaterial({
        map: glow, color: p.color, transparent: true, opacity: 0.5,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      spr.scale.setScalar(Math.max(0.9, p.r * 5));
      grp.add(spr);
      if (p.key === 'saturn') {
        const ring = new THREE.Mesh(
          new THREE.RingGeometry(p.r * 1.35, p.r * 2.2, 48),
          new THREE.MeshBasicMaterial({ color: 0xcbb98a, side: THREE.DoubleSide, transparent: true, opacity: 0.45 })
        );
        ring.rotation.x = Math.PI / 2 - 0.45;
        grp.add(ring);
      }
      scene.add(grp);
      planetMeshes[p.key] = grp;
      const ol = orbitLine(ELEMENTS[p.key], 0x1d6d8c, 0.35);
      ol.userData.orbit = true;
      scene.add(ol);
    });
  }

  // ---------- target body (comet / cigar) ----------
  const ION_N = 750, DUST_N = 520, ANTI_N = 260;
  let ionSeed, dustSeed, antiSeed;

  function particleSystem(count, size, tex) {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
    geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(count * 3), 3));
    const mat = new THREE.PointsMaterial({
      size: size, sizeAttenuation: true, map: tex, vertexColors: true,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const pts = new THREE.Points(geo, mat);
    pts.frustumCulled = false;
    return pts;
  }
  function seeds(n) {
    const arr = [];
    for (let i = 0; i < n; i++) {
      arr.push({
        u: Math.random(),
        j1: (Math.random() - 0.5), j2: (Math.random() - 0.5), j3: (Math.random() - 0.5),
        w: Math.random(),
      });
    }
    return arr;
  }

  function buildTarget() {
    cometGroup = new THREE.Group();
    const coreTex = glowTexture('rgba(235,255,255,1)', 'rgba(90,225,255,.35)');
    coreSprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: coreTex, color: 0xdffaff, transparent: true, opacity: 0.95,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    coreSprite.scale.set(1.35, 1.35, 1);
    cometGroup.add(coreSprite);
    scene.add(cometGroup);

    const dot = dotTexture();
    ionPts = particleSystem(ION_N, 0.55, dot);
    dustPts = particleSystem(DUST_N, 0.68, dot);
    antiPts = particleSystem(ANTI_N, 0.55, dot);
    antiPts.visible = false;
    scene.add(ionPts); scene.add(dustPts); scene.add(antiPts);
    ionSeed = seeds(ION_N); dustSeed = seeds(DUST_N); antiSeed = seeds(ANTI_N);

    trailFull = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineDashedMaterial({
      color: 0x2a7d96, transparent: true, opacity: 0.4, dashSize: 0.9, gapSize: 0.7, depthWrite: false,
    }));
    scene.add(trailFull);
    trailDone = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({
      color: 0x49e8ff, transparent: true, opacity: 0.85, depthWrite: false,
    }));
    scene.add(trailDone);

    periMarker = new THREE.Sprite(new THREE.SpriteMaterial({
      map: dot, color: 0xffb347, transparent: true, opacity: 0.9,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    periMarker.scale.setScalar(0.5);
    scene.add(periMarker);

    rebuildTargetPath();
  }

  function rebuildTargetPath() {
    const tgt = CX.eraData().objects.target;
    if (!tgt) return;
    const look = ERA_LOOK[S.era] || ERA_LOOK['3i'];
    eraStep = tgt.step_days;
    const pts = tgt.pos.map(v3);
    trailFull.geometry.dispose();
    trailFull.geometry = new THREE.BufferGeometry().setFromPoints(pts);
    trailFull.material.color.setHex(look.full);
    trailFull.computeLineDistances();
    trailDone.geometry.dispose();
    trailDone.geometry = new THREE.BufferGeometry().setFromPoints(pts);
    trailDone.material.color.setHex(look.trail);
    trailDone.geometry.setDrawRange(0, 1);

    coreSprite.material.color.setHex(look.core);
    coreSprite.scale.set(look.coreScale[0], look.coreScale[1], 1);

    const ca = CX.CA();
    if (ca.sun) periMarker.position.copy(v3(CX.pos('target', CX.tOfIso(ca.sun.date))));

    if (!look.tails) { ionPts.visible = false; dustPts.visible = false; antiPts.visible = false; }
  }

  function updateTailSystem(pts, seedArr, cometV, dirMain, spread, len, col0, col1, flow) {
    const pos = pts.geometry.attributes.position.array;
    const col = pts.geometry.attributes.color.array;
    const perpA = new THREE.Vector3();
    const perpB = new THREE.Vector3();
    perpA.crossVectors(dirMain, new THREE.Vector3(0, 1, 0));
    if (perpA.lengthSq() < 1e-6) perpA.set(1, 0, 0); else perpA.normalize();
    perpB.crossVectors(dirMain, perpA).normalize();
    const n = seedArr.length;
    for (let i = 0; i < n; i++) {
      const sd = seedArr[i];
      let u = (sd.u + frameT * flow) % 1;
      const d = Math.pow(u, 1.4) * len;
      const sp = spread * (0.15 + u * 1.1);
      const wob = Math.sin(u * 9 + sd.w * 6.28 + frameT * 0.8) * sp * 0.25;
      pos[i * 3] = cometV.x + dirMain.x * d + perpA.x * (sd.j1 * sp + wob) + perpB.x * sd.j2 * sp;
      pos[i * 3 + 1] = cometV.y + dirMain.y * d + perpA.y * (sd.j1 * sp + wob) + perpB.y * sd.j2 * sp;
      pos[i * 3 + 2] = cometV.z + dirMain.z * d + perpA.z * (sd.j1 * sp + wob) + perpB.z * sd.j2 * sp;
      const fade = Math.max(0, 1 - u) * (0.5 + sd.w * 0.5);
      col[i * 3] = (col0[0] + (col1[0] - col0[0]) * u) * fade;
      col[i * 3 + 1] = (col0[1] + (col1[1] - col0[1]) * u) * fade;
      col[i * 3 + 2] = (col0[2] + (col1[2] - col0[2]) * u) * fade;
    }
    pts.geometry.attributes.position.needsUpdate = true;
    pts.geometry.attributes.color.needsUpdate = true;
  }

  // ---------- compare mode: all three interstellar paths ----------
  function buildComparePaths() {
    compareGroup = new THREE.Group();
    CX.ERA_ORDER.forEach(function (k) {
      const tgt = CX.eraTargetPath(k);
      if (!tgt) return;
      const meta = CX.ERA_META[k];
      const pts = tgt.pos.map(v3);
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: meta.colorHex, transparent: true, opacity: 0.75, depthWrite: false })
      );
      line.userData.era = k;
      compareGroup.add(line);
      let best = 0, bd = 1e9;
      tgt.pos.forEach(function (p, i) {
        const dd = p[0] * p[0] + p[1] * p[1] + p[2] * p[2];
        if (dd < bd) { bd = dd; best = i; }
      });
      const spr = new THREE.Sprite(new THREE.SpriteMaterial({
        map: dotTexture(), color: meta.colorHex, transparent: true, opacity: 0.95,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      spr.scale.setScalar(0.55);
      spr.position.copy(v3(tgt.pos[best]));
      spr.userData.era = k;
      compareGroup.add(spr);
    });
    compareGroup.visible = false;
    scene.add(compareGroup);
  }

  // ---------- grid & ecliptic ----------
  function buildGrid() {
    gridGroup = new THREE.Group();
    [1, 2, 3, 5, 10, 20, 30].forEach(function (au) {
      const pts = [];
      for (let k = 0; k <= 128; k++) {
        const a = (k / 128) * Math.PI * 2;
        pts.push(new THREE.Vector3(Math.cos(a) * au * AUu, 0, Math.sin(a) * au * AUu));
      }
      const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: 0x0e3a4f, transparent: true, opacity: 0.5, depthWrite: false }));
      gridGroup.add(l);
    });
    for (let sp = 0; sp < 12; sp++) {
      const a = (sp / 12) * Math.PI * 2;
      const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(Math.cos(a) * AUu, 0, Math.sin(a) * AUu),
        new THREE.Vector3(Math.cos(a) * 30 * AUu, 0, Math.sin(a) * 30 * AUu),
      ]), new THREE.LineBasicMaterial({ color: 0x0e3a4f, transparent: true, opacity: 0.22, depthWrite: false }));
      gridGroup.add(l);
    }
    gridGroup.visible = S.grid;
    scene.add(gridGroup);

    eclipticDisc = new THREE.Mesh(
      new THREE.CircleGeometry(32 * AUu, 96),
      new THREE.MeshBasicMaterial({ color: 0x34e1ff, transparent: true, opacity: 0.05, side: THREE.DoubleSide, depthWrite: false })
    );
    eclipticDisc.rotation.x = -Math.PI / 2;
    eclipticDisc.visible = false;
    scene.add(eclipticDisc);
  }

  // ---------- labels ----------
  function makeLabel(key, name, target) {
    const d = document.createElement('div');
    d.className = 'cx-obj-label' + (target ? ' cx-lbl-target' : '');
    const nameSpan = document.createElement('span');
    nameSpan.textContent = name;
    d.appendChild(nameSpan);
    labelEls[key + '__name'] = nameSpan;
    if (target) {
      const sub = document.createElement('span');
      sub.className = 'cx-lbl-sub';
      d.appendChild(sub);
      labelEls[key + '__sub'] = sub;
    }
    hud.appendChild(d);
    labelEls[key] = d;
  }
  const projV = new THREE.Vector3();
  function placeLabel(key, worldV, subText) {
    const el = labelEls[key];
    if (!el) return;
    if (!S.labels) { el.style.display = 'none'; return; }
    projV.copy(worldV).project(camera);
    if (projV.z > 1 || projV.x < -1.05 || projV.x > 1.05 || projV.y < -1.05 || projV.y > 1.05) {
      el.style.display = 'none'; return;
    }
    el.style.display = 'block';
    el.style.left = ((projV.x + 1) / 2 * container.clientWidth) + 'px';
    el.style.top = ((-projV.y + 1) / 2 * container.clientHeight) + 'px';
    if (subText != null && labelEls[key + '__sub']) labelEls[key + '__sub'].textContent = subText;
  }
  function hideLabel(key) {
    if (labelEls[key]) labelEls[key].style.display = 'none';
  }

  // ---------- camera ----------
  const FREE_POS = new THREE.Vector3(26, 17, 30);
  function startTween(toPos, toTarget, dur) {
    tween = {
      p0: camera.position.clone(), p1: toPos.clone(),
      t0: controls.target.clone(), t1: toTarget.clone(),
      start: performance.now(), dur: dur || 1200,
    };
  }
  SC.applyPreset = function (name) {
    S.camPreset = name;
    const cp = v3(CX.pos('target', S.t));
    if (name === 'free') {
      controls.enabled = true;
      startTween(FREE_POS, new THREE.Vector3(0, 0, 0));
    } else if (name === 'top') {
      controls.enabled = true;
      startTween(new THREE.Vector3(0.01, 300, 0.01), new THREE.Vector3(0, 0, 0));
    } else {
      controls.enabled = false;
      tween = null;
      if (name === 'sun') startTween(new THREE.Vector3(0, 2.2, 0.1), cp, 900);
    }
    CX.emit('campreset');
  };

  function followCamera() {
    const cp = v3(CX.pos('target', S.t));
    const eps = 0.5;
    const cpN = v3(CX.pos('target', Math.min(CX.N - 1, S.t + eps)));
    const velDir = cpN.clone().sub(cp);
    if (velDir.lengthSq() < 1e-9) velDir.set(1, 0, 0); else velDir.normalize();
    let desiredPos, desiredTgt;
    if (S.camPreset === 'chase') {
      desiredPos = cp.clone().sub(velDir.clone().multiplyScalar(5.2)).add(new THREE.Vector3(0, 1.7, 0));
      desiredTgt = cp.clone().add(velDir.clone().multiplyScalar(8));
    } else if (S.camPreset === 'mars') {
      const mp = v3(CX.pos('mars', S.t));
      const up = mp.clone().normalize().multiplyScalar(0.7);
      desiredPos = mp.clone().add(new THREE.Vector3(0, 0.55, 0)).add(up);
      desiredTgt = cp;
    } else if (S.camPreset === 'sun') {
      desiredPos = cp.clone().normalize().multiplyScalar(2.6).add(new THREE.Vector3(0, 0.9, 0));
      desiredTgt = cp;
    } else return;
    camera.position.lerp(desiredPos, 0.055);
    controls.target.lerp(desiredTgt, 0.09);
    camera.lookAt(controls.target);
  }

  // ---------- era switch ----------
  SC.setEra = function () {
    rebuildTargetPath();
    if (labelEls.target__name) labelEls.target__name.textContent = '◆ ' + CX.ERA_META[S.era].label;
    if (labelEls.target) labelEls.target.style.color = CX.ERA_META[S.era].color;
    SC.applyPreset(S.camPreset === 'top' ? 'top' : 'free');
  };

  // ---------- init ----------
  SC.init = function (containerEl, hudEl) {
    container = containerEl; hud = hudEl;
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x010409, 1);
    renderer.domElement.id = 'cx-gl';
    container.insertBefore(renderer.domElement, container.firstChild);

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(52, container.clientWidth / container.clientHeight, 0.05, 6000);
    camera.position.copy(FREE_POS);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 0.6;
    controls.maxDistance = 1400;

    scene.add(new THREE.AmbientLight(0x2a3d52, 0.55));
    sunLight = new THREE.PointLight(0xfff2d8, 2.2, 0, 2);
    scene.add(sunLight);

    const sunSpr = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture('rgba(255,244,214,1)', 'rgba(255,180,80,.30)', 256),
      color: 0xffffff, transparent: true, opacity: 1,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    sunSpr.scale.setScalar(4.6);
    scene.add(sunSpr);
    const sunCore = new THREE.Mesh(new THREE.SphereGeometry(0.30, 24, 16),
      new THREE.MeshBasicMaterial({ color: 0xfff6dc }));
    scene.add(sunCore);

    buildStars();
    buildPlanets();
    buildTarget();
    buildComparePaths();
    buildGrid();

    rangeLine = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]),
      new THREE.LineBasicMaterial({ color: 0x46ffa1, transparent: true, opacity: 0.6, depthWrite: false })
    );
    rangeLine.visible = false;
    scene.add(rangeLine);
    rangeTag = document.createElement('div');
    rangeTag.className = 'cx-range-tag';
    rangeTag.style.display = 'none';
    hud.appendChild(rangeTag);

    makeLabel('sun', 'SUN');
    PLANETS.forEach(function (p) { makeLabel(p.key, p.name); });
    makeLabel('target', '◆ ' + CX.ERA_META[S.era].label, true);
    CX.ERA_ORDER.forEach(function (k) {
      makeLabel('cmp_' + k, CX.ERA_META[k].label);
      labelEls['cmp_' + k].style.color = CX.ERA_META[k].color;
    });

    CX.on('era', SC.setEra);
    window.addEventListener('resize', SC.resize);
    SC.resize();
  };

  SC.resize = function () {
    if (!renderer) return;
    const w = container.clientWidth, h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };

  SC.setCompare = function (on) {
    if (compareGroup) compareGroup.visible = on;
    if (on) {
      controls.enabled = true;
      startTween(new THREE.Vector3(38, 46, 42), new THREE.Vector3(0, 0, 0));
    }
  };

  // ---------- per-frame ----------
  const NEAR_KEYS = ['mercury', 'venus', 'earth', 'mars', 'jupiter', 'saturn'];
  SC.update = function (dtMs) {
    if (!renderer) return;
    frameT += dtMs * 0.001;
    const hudVisible = S.mode !== 'archive';
    if (hud.style.display !== (hudVisible ? '' : 'none')) hud.style.display = hudVisible ? '' : 'none';

    PLANETS.forEach(function (p) {
      planetMeshes[p.key].position.copy(v3(CX.pos(p.key, S.t)));
    });

    const look = ERA_LOOK[S.era] || ERA_LOOK['3i'];
    const cp = v3(CX.pos('target', S.t));
    cometGroup.position.copy(cp);
    const rS = CX.rSun('target', S.t);
    const compare = S.mode === 'compare';

    if (look.tails) {
      const activity = Math.min(look.actMax, Math.max(0.12, Math.pow(look.actBase / rS, 2)));
      coreSprite.scale.set(look.coreScale[0] * (0.65 + activity * 0.35), look.coreScale[1] * (0.65 + activity * 0.35), 1);
      const sunDir = cp.clone().normalize();
      if (!compare) {
        ionPts.visible = true; dustPts.visible = true;
        const nextV = v3(CX.pos('target', Math.min(CX.N - 1, S.t + 0.5)));
        const velDir = nextV.clone().sub(cp).normalize();
        const dustDir = sunDir.clone().multiplyScalar(0.72).add(velDir.clone().multiplyScalar(-0.28)).normalize();
        updateTailSystem(ionPts, ionSeed, cp, sunDir, 0.4, 6.2 * activity, look.ion0, look.ion1, 0.06);
        updateTailSystem(dustPts, dustSeed, cp, dustDir, 0.85, 4.4 * activity, look.dust0, look.dust1, 0.025);
        antiPts.visible = S.viz.antiTail;
        if (S.viz.antiTail) {
          updateTailSystem(antiPts, antiSeed, cp, sunDir.clone().negate(), 0.34, 2.8 * activity, [1.0, 0.74, 0.32], [0.42, 0.26, 0.09], 0.03);
        }
      } else { ionPts.visible = false; dustPts.visible = false; antiPts.visible = false; }
    } else {
      // inert body ('Oumuamua): slow tumble of the elongated glow, no tails
      ionPts.visible = false; dustPts.visible = false; antiPts.visible = false;
      const wob = 0.72 + 0.28 * Math.sin(frameT * 0.85);
      coreSprite.scale.set(look.coreScale[0] * wob + look.coreScale[1] * (1 - wob),
                           look.coreScale[1] * wob + look.coreScale[0] * (1 - wob) * 0.4, 1);
      coreSprite.material.rotation = frameT * 0.22;
    }
    trailDone.geometry.setDrawRange(0, Math.max(2, Math.floor(S.t / eraStep) + 1));

    eclipticDisc.visible = S.viz.ecliptic;
    gridGroup.visible = S.grid || S.viz.ecliptic;
    scene.traverse(function (o) { if (o.userData.orbit) o.visible = S.orbits; });

    let nearKey = null, nearD = 1e9;
    NEAR_KEYS.forEach(function (k) {
      const d = CX.range('target', k, S.t);
      if (d < nearD) { nearD = d; nearKey = k; }
    });
    if (!compare && nearD < 1.25) {
      rangeLine.visible = true;
      const pp = v3(CX.pos(nearKey, S.t));
      rangeLine.geometry.setFromPoints([cp, pp]);
      const mid = cp.clone().add(pp).multiplyScalar(0.5);
      projV.copy(mid).project(camera);
      if (projV.z < 1) {
        rangeTag.style.display = 'block';
        rangeTag.style.left = ((projV.x + 1) / 2 * container.clientWidth) + 'px';
        rangeTag.style.top = ((-projV.y + 1) / 2 * container.clientHeight) + 'px';
        rangeTag.textContent = nearKey.toUpperCase() + ' RANGE ' + nearD.toFixed(3) + ' AU';
      } else rangeTag.style.display = 'none';
    } else {
      rangeLine.visible = false;
      rangeTag.style.display = 'none';
    }

    if (tween) {
      const k = Math.min(1, (performance.now() - tween.start) / tween.dur);
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      camera.position.lerpVectors(tween.p0, tween.p1, e);
      controls.target.lerpVectors(tween.t0, tween.t1, e);
      if (k >= 1) tween = null;
    }
    if (!tween && (S.camPreset === 'chase' || S.camPreset === 'mars' || S.camPreset === 'sun')) {
      followCamera();
    }
    if (controls.enabled) controls.update();

    placeLabel('sun', new THREE.Vector3(0, 0, 0));
    PLANETS.forEach(function (p) { placeLabel(p.key, planetMeshes[p.key].position); });
    placeLabel('target', cp, rS.toFixed(2) + ' AU FROM SUN · ' + CX.targetSpeed(S.t).toFixed(1) + ' KM/S');
    CX.ERA_ORDER.forEach(function (k) {
      if (compare && k !== S.era) {
        const tgt = CX.eraTargetPath(k);
        if (tgt) placeLabel('cmp_' + k, v3(tgt.pos[0]));
      } else hideLabel('cmp_' + k);
    });

    renderer.render(scene, camera);
  };
})();
