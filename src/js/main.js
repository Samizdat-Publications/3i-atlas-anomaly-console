/* ============================================================
   MAIN — boot flow + frame loop
   ============================================================ */
(function () {
  'use strict';
  window.APP_VERSION = '2.4';

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

      // honour a deep link (#3i/A-05, #1i/compare) before rolling the tape
      const deepLinked = CX.ui.applyHash();

      setTimeout(function () {
        S.playing = true;
        CX.emit('playstate');
        if (deepLinked) return;
        CX.ui.showToast({
          title: 'REPLAY ARMED — ' + CX.ERA_META[S.era].label + ' TRANSIT',
          t: S.t, cls: 'mission',
          desc: 'SPACE pauses · switch target with 3I / 1I / 2I · press T for the guided tour · ? for controls.',
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
