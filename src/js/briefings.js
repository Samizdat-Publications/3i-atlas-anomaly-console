/* BRIEFINGS — question-led entry points into the register.
 *
 * The console is organised by object and case, which is how the DATA is shaped,
 * not how anyone arrives. People come with a question ("are fireballs actually
 * increasing?"), and 46 dossiers is a wall rather than a door. A briefing states
 * the question, answers it in a few hundred words, shows the one chart that
 * carries the argument, and then hands off to the case files that do the work.
 *
 * Deep-linkable at #brief/<id> so a single finding can be sent to someone on its
 * own — which is the main way this material actually travels.
 */
(function () {
  'use strict';
  const CX = window.CX = window.CX || {};
  const B = CX.briefings = {};
  function $(id) { return document.getElementById(id); }
  function setH(node, html) { node.textContent = ''; node.insertAdjacentHTML('beforeend', html); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  let current = null;

  function all() {
    return (window.ATLAS_CONTENT && window.ATLAS_CONTENT.briefings) || [];
  }
  B.all = all;
  B.get = function (id) {
    return all().filter(function (b) { return b.id === id; })[0] || null;
  };
  B.current = function () { return current; };

  function caseLabel(ref) {
    const parts = String(ref).split('/');
    const list = (window.ATLAS_CONTENT || {}).anomalies || [];
    for (let i = 0; i < list.length; i++) {
      if (list[i].object === parts[0] && list[i].id === parts[1]) return list[i];
    }
    return null;
  }

  const OBJ_LABEL = { '3i': '3I', '1i': '1I', '2i': '2I', fb: 'FIREBALL' };

  function cardHTML(b, active) {
    return '<button class="cx-brief-card' + (active ? ' cx-on' : '') +
      '" data-act="brief" data-brief="' + esc(b.id) + '">' +
      '<div class="cx-brief-card-tag">' + esc(b.tag || b.id) + '</div>' +
      '<div class="cx-brief-card-q">' + esc(b.question) + '</div>' +
      '</button>';
  }

  /* The reading pane. Long-form on purpose: this is the one surface in the
   * console meant to be read start to finish rather than skimmed. */
  function paneHTML(b) {
    let h = '<article class="cx-brief">' +
      '<div class="cx-brief-head">' +
      '<div class="cx-brief-id">' + esc(b.id) + ' · ' + esc(b.tag || '') + '</div>' +
      '<h2 class="cx-brief-q">' + esc(b.question) + '</h2>' +
      '<p class="cx-brief-short">' + esc(b.short) + '</p>' +
      '</div>';

    if (b.chart) {
      h += '<figure class="cx-brief-fig"><canvas id="cx-brief-canvas"></canvas></figure>';
    }

    (b.sections || []).forEach(function (s) {
      h += '<section class="cx-brief-sec"><h3>' + esc(s.h) + '</h3><p>' + esc(s.p) + '</p></section>';
    });

    const cases = (b.cases || []).map(caseLabel).filter(Boolean);
    if (cases.length) {
      h += '<div class="cx-brief-cases"><div class="cx-brief-caseshead">THE CASE FILES BEHIND THIS</div>';
      cases.forEach(function (c) {
        h += '<button class="cx-brief-case" data-act="brief-case" data-obj="' + esc(c.object) +
          '" data-case="' + esc(c.id) + '">' +
          '<span class="cx-brief-case-id">' + esc(OBJ_LABEL[c.object] || c.object) + ' ' + esc(c.id) + '</span>' +
          '<span class="cx-brief-case-t">' + esc(c.title) + '</span></button>';
      });
      h += '</div>';
    }

    if ((b.sources || []).length) {
      h += '<div class="cx-brief-src"><span>SOURCES</span> ' +
        b.sources.map(function (u) {
          let host = u;
          try { host = new URL(u).hostname.replace(/^www\./, ''); } catch (e) { /* keep raw */ }
          return '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' + esc(host) + '</a>';
        }).join(' ') + '</div>';
    }

    h += '<div class="cx-brief-foot">Unofficial and educational. Where a claim is contested, ' +
      'both readings are given — including the limits that cut against the conclusion here.</div>';
    return h + '</article>';
  }

  function drawChart(b) {
    const cv = $('cx-brief-canvas');
    if (!cv || !b.chart || !CX.charts || !CX.charts.dossier) return;
    // The pane is still laying out on the frame the markup lands; measuring the
    // canvas before that gives a zero-width chart that never repaints.
    requestAnimationFrame(function () {
      try { CX.charts.dossier(b.chart, cv); } catch (e) { /* a missing chart is not fatal */ }
    });
  }

  B.open = function (id) {
    const list = all();
    if (!list.length) return;
    const b = B.get(id) || list[0];
    current = b.id;
    const rail = $('cx-brief-rail');
    if (rail) {
      setH(rail, '<div class="cx-brief-railhead">BRIEFINGS</div>' +
        list.map(function (x) { return cardHTML(x, x.id === b.id); }).join(''));
    }
    const pane = $('cx-brief-pane');
    if (pane) { setH(pane, paneHTML(b)); pane.scrollTop = 0; }
    drawChart(b);
    if (CX.ui && CX.ui.syncHash) CX.ui.syncHash();
  };

  B.refresh = function () {
    if (!current) { B.open((all()[0] || {}).id); return; }
    const b = B.get(current);
    if (b) drawChart(b);
  };

  window.addEventListener('resize', function () {
    if (window.CX && CX.S && CX.S.mode === 'briefings') B.refresh();
  });
})();
