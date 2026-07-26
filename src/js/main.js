/* ============================================================
   MAIN — boot flow + frame loop
   ============================================================ */
(function () {
  'use strict';
  window.APP_VERSION = '2.2';

  function start() {
    const CX = window.CX, S = CX.S;
    CX.ui.build();
    // start the clock at discovery
    CX.setT(CX.tOfIso('2025-07-01'), true);

    CX.ui.boot(function onAuth() {
      CX.audio.init();
      CX.audio.auth();
      S.booted = true;
      document.getElementById('cx-root').classList.add('cx-live');

      const center = document.getElementById('cx-center');
      const hud = document.getElementById('cx-hud');
      CX.scene3d.init(center, hud);

      CX.ui.renderClock();
      CX.ui.renderTimeline();
      CX.charts.renderRail();

      // roll the tape
      setTimeout(function () {
        S.playing = true;
        CX.emit('playstate');
        CX.ui.showToast({
          title: 'REPLAY ARMED — 3I/ATLAS TRANSIT · 2025-2026',
          t: S.t, cls: 'mission',
          desc: 'SPACE pauses · click markers for events · switch target with 3I / 1I / 2I · press ? for controls.',
        });
      }, 900);

      let last = performance.now();
      function frame(now) {
        const dt = now - last; last = now;
        CX.tick(now);
        CX.scene3d.update(dt);
        requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
