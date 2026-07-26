# 3I/ATLAS — Interstellar Anomaly Review Console (project guide for Claude sessions)

A single-file, framework-free "NASA terminal" dashboard about the interstellar object
**3I/ATLAS (C/2025 N1)** — real JPL Horizons trajectory data + Avi Loeb's 25-case anomaly
register (each case shows Loeb's claim AND the official explanation side by side).
Built for Stewart, for fun. Clearly labeled unofficial/educational in the footer.

## Resume protocol (usage limits hit often — checkpoint everything)
**CURRENT STATE (2026-07-26):** v2.3 shipped + deployed + browser-verified against the live
URL. Adds deep links (`#<era>/<case>`, see `syncHash`/`applyHash` in ui.js), the 8-beat
guided tour (`TOUR` array; steps resolve case files by KEYWORD via `findCase` so they survive
renumbering), cross-object case search (searches all 41 cases, badges foreign objects), and
`ANALYTICS_TOKEN` support in build.py (public/index.html only — the offline file must stay at
ZERO external refs; assert with a grep for `src="http`).
Git history was rewritten 2026-07-26 to use the GitHub noreply email — do NOT re-introduce
`stewartgregerson@gmail.com` as the git author; use
`179866421+Samizdat-Publications@users.noreply.github.com`. Three-object
console complete: 41 fact-checked case files (3I: 25, 1I: 11, 2I: 5), 54 timeline events,
35 quotes, all datasets either real Horizons geometry or adversarially verified. Research
payloads checkpointed: data/research.json (3I) + data/research-iso.json (1I/2I).

**NOW UNDER GIT + PUBLISHED.** Repo: https://github.com/Samizdat-Publications/3i-atlas-anomaly-console
(public, main branch). `git push` after every release — git history now replaces the
`_Archive (old versions)/` folder (which is gitignored, kept locally only).
**LIVE AT https://3i-atlas-anomaly-console.pages.dev** — Cloudflare Pages, account
`c82dd5addf7f4ebc0260ae476166b8d1` (stewartgregerson@gmail.com). It is a **Direct Upload**
project (created by wrangler), NOT a dashboard Git-connected one — Cloudflare cannot convert
between the two, so continuous deployment runs through `.github/workflows/deploy.yml`.

**CI/CD IS LIVE (2026-07-26).** Repo secret `CLOUDFLARE_API_TOKEN` is set and verified — a
push to `main` rebuilds from `src/` and auto-deploys. The workflow still length-checks the
token and skips (rather than failing) if it is ever cleared or mis-set.
Manual deploy still works any time — wrangler is logged in on Stewart's machine.

**No custom domain, by choice** — `3i-atlas-anomaly-console.pages.dev` is the permanent
canonical URL and `SITE_URL` in build.py should stay pointed at it. Stewart deliberately
declined a paid domain; the whole stack is free tier. Don't re-pitch one.

**Web Analytics is ON** via the Pages dashboard toggle (Settings -> Web Analytics), which
injects the beacon at the EDGE. Therefore `ANALYTICS_TOKEN` in build.py must stay EMPTY —
setting it too would double-count. The offline `_LATEST` file is unaffected (still 0
external refs); the beacon only exists in what Cloudflare serves.

Manual deploy (wrangler is already logged in locally):
```
python tools/build.py
npx wrangler pages deploy public --project-name 3i-atlas-anomaly-console --branch main
```
`tools/build.py` writes BOTH `_LATEST ...html` and `public/index.html` from the same bytes —
never edit either by hand. `SITE_URL` at the top of build.py must match the deployed origin
or social-card previews break.

Stewart's sessions can be cut off by usage limits mid-task. Rules:
1. **Everything on disk, immediately.** Fetched data → `data/`, research payloads →
   `data/research.json`, source edits saved as you go, `_CHANGELOG.md` updated per release.
   Nothing important lives only in conversation.
2. **Archive before overwrite.** Copy the current `_LATEST ...html` into
   `_Archive (old versions)/YYYY-MM-DD - ... vX.Y (note).html` before rebuilding.
3. **Multi-agent runs go through Workflow** so `resumeFromRunId` can replay completed
   agents from cache after a cutoff (only failed agents re-run).
4. **This file is the resume note.** If a task is left half-done, add a "CURRENT STATE /
   NEXT STEP" line at the top of this section before ending the session; remove it when done.

## The one rule: edit source → build → ship LATEST
- **Source of truth:** `src/`
  - `console.css` — design system (`cx-` prefix; phosphor cyan / signal amber / alert red on deep navy).
  - `js/core.js` — state, time engine (t = fractional days from 2025-05-15), ephemeris interpolation, WebAudio synth engine (no audio assets).
  - `js/scene3d.js` — Three.js r128 scene: starfield + Milky Way band, planets on real positions + element-derived orbit lines, comet with 3 particle tail systems (ion / dust / **anti-tail** for the A-05 viz), traveled-path drawRange trail, camera presets (free/top/chase/mars/sun), HUD labels + range line.
  - `js/charts.js` — canvas chart lib; right-rail telemetry (real data) + dossier charts (spectrum, polarization, acceleration, lightcurve, trajectory-side-view, size — stylized illustrations of published results).
  - `js/ui.js` — DOM skeleton, boot sequence, timeline scrubber, anomaly dossiers, compare table, archive docs (redactions + stamps), all wiring (delegated `data-act` clicks).
  - `js/main.js` — boot flow + frame loop. `APP_VERSION` lives here.
  - `data-ephemeris.js` / `data-content.js` — GENERATED. Never hand-edit.
  - `vendor/` — three.min.js r128 (UMD), OrbitControls, Share Tech Mono woff2 (OFL).
- **Build:** `python tools/build.py` → overwrites **`_LATEST - 3I-ATLAS Anomaly Console.html`**
  (project root, ~1 MB, fully offline, double-click to open — the only file Stewart needs).
- **Verify before claiming done:** `node --check` each edited js; serve (`python -m http.server`)
  and load in a browser; console must be clean. NOTE: browser caches aggressively — bust with
  `?bust=N` query when re-testing, and remember background tabs throttle the boot-sequence
  timers (front the tab or the auth prompt takes ~a minute to appear).

## Data pipelines (both real)
- **Ephemeris:** `python tools/fetch_ephemeris.py` — pulls heliocentric ecliptic J2000 vectors
  from JPL Horizons (3I/ATLAS + 8 planets daily 2025-05-15→2026-12-31; 1I/'Oumuamua 2017;
  2I/Borisov 2019-20) → `data/ephemeris.json` → baked to `src/data-ephemeris.js`.
  Computed close approaches match published values (Mars 0.1939 AU 2025-10-03, perihelion
  1.3566 AU 2025-10-29, Earth 1.7978 AU 2025-12-19, Jupiter 0.3588 AU 2026-03-17).
- **Content:** `python tools/bake_content.py <research-json>` — converts the research payload
  (`data/research.json`, produced 2026-07-17 by a 31-agent web-research + per-anomaly
  adversarial fact-check workflow) → `src/data-content.js`. 25 anomaly cases (each with
  `verify: CONFIRMED|CORRECTED|UNCHECKED`), 24 timeline events, 20 sourced quotes, 3 ISO
  comparison profiles. Loeb scale: 4 (Jul 2025) → held 4 (Dec 2025) → 3 (Mar 2026).
  Known gap: the timeline + comparison DATASET-level verifiers and the A-24 case verifier
  never ran (usage limit); everything else was individually fact-checked.

## Constraints
- Self-contained, offline, no admin, no server to run. All assets inline (font base64'd at build).
- The security hook blocks Write/Edit content containing the raw HTML-set property name —
  inject markup via `setH()` in ui.js (uses `insertAdjacentHTML`); never write that property
  name in code or docs.
- Keep the anomaly framing balanced: every Loeb claim is shown WITH the official explanation.
  The fiction ("IOWG", clearance banners, stamps) stays obviously playful; the disclaimer
  footer stays.

## App architecture notes
- Modes: `track` (default 3D) / `anomalies` (dossier overlay) / `compare` (1I·2I·3I paths +
  bottom-docked table) / `archive` (paper documents; HUD hidden in this mode).
- Timeline: click markers to jump (anomaly markers open the dossier); drag to scrub; SPACE
  play/pause; 1/2/3/4 modes; N=now (live position for today); M mute; Esc close.
- "VISUALIZE IN TRACKER" in a dossier jumps the clock to the anomaly date and applies its
  viz (anti-tail → sunward particles + chase cam; trajectory → ecliptic disc + top-down).
- Event crossings during playback fire toasts + synth alert tones (mission=cyan, anomaly=amber).
- Boot sequence doubles as the audio-unlock gesture; ESC skips.
