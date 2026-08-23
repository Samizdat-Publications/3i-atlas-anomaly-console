# 3I/ATLAS — Interstellar Anomaly Review Console (project guide for Claude sessions)

A single-file, framework-free "NASA terminal" dashboard about the interstellar object
**3I/ATLAS (C/2025 N1)** — real JPL Horizons trajectory data + Avi Loeb's 25-case anomaly
register (each case shows Loeb's claim AND the official explanation side by side).
Built for Stewart, for fun. Clearly labeled unofficial/educational in the footer.

## Resume protocol (usage limits hit often — checkpoint everything)
**CURRENT STATE (2026-08-23):** v2.10 shipped. Case **F-03** answers the recurring "fireballs
are increasing" claim from the shipped catalog: the record STEPS (1994, 2000) then is FLAT for
26 years, and the >=1kt subset — which a detection-rate change cannot inflate — runs 4.1/4.1/3.7
per decade. `CH.fireballRate()` draws it (>=1kt sub-bar INSIDE each bar; pre-1994 shaded as
pre-record; final year hatched as partial). **F-03 is the only case file argued from computed
numbers**, so `tools/fireball_rate_check.py` re-derives every figure it quotes and the monthly
refresh workflow flags drift in the PR body. Its claim block deliberately does NOT name a
person — the transcript that prompted it could not be retrieved, so the proposition was tested
as commonly stated.

**Earlier (2026-08-22):** v2.9 shipped. Timeline entries are now first-class records:
a mission marker opens the same sheet a case file does, with the full description and
CLICKABLE SOURCES — `map_events` used to strip `sources` and no UI existed, so ~26k chars of
researched prose and all 58 citation sets shipped unreachable. Events get date-derived ids
(`E-YYYYMMDD`, suffixed on same-day collisions) so deep links survive insertion. The left
rail gained a MISSION LOG tab beside CASE FILES because **24% of records fall outside their
era's scrubber window** (1I runs to 2026, its ephemeris stops 2018 — 9 of 16 stranded), so a
marker is not a reliable way in. `tlClick` is now ROW-AWARE: anomaly triangles sit above the
baseline, mission diamonds below, and the pointer's side picks the row — without that, at
phone width the rows fought over every tap. Model: drag = time, tap = record. **v2.5 (fireball register) merged to main and
DEPLOYED** — the live URL now serves it. v2.6 adds touch support: the timeline scrubber and the
fireball map use Pointer Events (a finger never emits `mousemove`, so both were dead on a phone);
`.cx-root` on narrow screens uses `auto 1fr auto` rows and `ui.js` publishes measured
`--topH`/`--botH` so the slide-over rails follow a top bar that wraps to as many rows as the
device needs — it used to clip FIREBALLS/ARCHIVE/help off the right edge entirely. Touch targets
come from `@media (pointer: coarse)`. Verified under touch emulation at 412x940 and 884x1104.
All four approved phases are done: (1) v2.6 touch, (2) the monthly refresh workflow,
(3) v2.7 quote verification, (4) v2.8 content current to 2026-08-18. NOTE FOR NEXT SESSION:
two of the four phases were planned against STALE notes in this file — the fact-check "gap"
had already been closed, and the content was current to July not March. Check the repo state
before trusting a resume note here, including this one.

**Earlier (2026-08-22):** v2.5 built + browser-verified locally (Playwright against the
built `public/` bundle: 43 cases, 1,069 fireball rows, deep links, mobile layout, zero console
errors). Adds the **FIREBALLS** mode — the CNEOS atmospheric-impact map — plus case files F-01
(IM1) and F-02 (IM2). New pipeline `tools/fetch_fireballs.py` writes `data/fireballs.json` +
`data/world-land.json` and bakes `src/data-fireballs.js`; hand-authored case text lives in
`data/fireball-cases.json` and is merged by `bake_content.py` under object key `fb` (NOT an era —
it has no ephemeris, so `S.era` never becomes `fb`; opening one of its cases switches MODE).
Mode keys shifted: ARCHIVE is now `5`, FIREBALLS is `4`. Shipped on branch
`claude/fireball-dataset-3i-atlas-syop76`; not yet merged to main, so the live URL is still v2.4.

**Earlier (2026-07-26):** v2.3 shipped + deployed + browser-verified against the live
URL. Adds deep links (`#<era>/<case>`, see `syncHash`/`applyHash` in ui.js), the 8-beat
guided tour (`TOUR` array; steps resolve case files by KEYWORD via `findCase` so they survive
renumbering), cross-object case search (searches all 41 cases, badges foreign objects), and
`ANALYTICS_TOKEN` support in build.py (public/index.html only — the offline file must stay at
ZERO external refs; assert with a grep for `src="http`).
Git history was rewritten 2026-07-26 to use the GitHub noreply email — do NOT re-introduce
`stewartgregerson@gmail.com` as the git author; use
`179866421+Samizdat-Publications@users.noreply.github.com`. Three-object
console complete: 44 fact-checked case files (3I: 25, 1I: 11, 2I: 5, CNEOS fireballs: 3),
58 timeline events, 35 quotes, all datasets either real Horizons geometry, the live CNEOS
fireball table, or adversarially verified. Research
payloads checkpointed: data/research.json (3I) + data/research-iso.json (1I/2I).

**NOW UNDER GIT + PUBLISHED.** Repo: https://github.com/Samizdat-Publications/3i-atlas-anomaly-console
(public, main branch). `git push` after every release — git history now replaces the
`_Archive (old versions)/` folder (which is gitignored, kept locally only).
**LIVE AT https://3i-atlas-anomaly-console.pages.dev** — Cloudflare Pages, account
`c82dd5addf7f4ebc0260ae476166b8d1` (stewartgregerson@gmail.com). It is a **Direct Upload**
project (created by wrangler), NOT a dashboard Git-connected one — Cloudflare cannot convert
between the two, so continuous deployment runs through `.github/workflows/deploy.yml`.

**DATA REFRESH IS AUTOMATED (2026-08-22).** `.github/workflows/refresh-data.yml` re-pulls
CNEOS (and, on manual dispatch with the `ephemeris` input, Horizons) on the 1st of each
month, rebuilds, and opens a PR **only if the upstream bytes changed** — never pushes to
main, because a revised row can invalidate case-file text that quotes it.
`tools/refresh_report.py` generates the PR body (new / withdrawn / revised rows) and exits
1 when nothing changed, which is how the workflow decides whether to open anything. It
also shouts if the IM1 or IM2 row moves. `tools/fetch_fireballs.py` retries with backoff
since it now runs unattended.

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

## Landing page + screenshots (v2.4)
- `src/about.html` is the project landing page. build.py copies it to `public/about.html`,
  inlining the font and substituting `__SITE__` for SITE_URL. Pure HTML/CSS, no scripts.
- `public/shots/*.png` are the captured views, referenced by BOTH the README (relative path
  `public/shots/x.png`) and about.html (`shots/x.png`). Recapture with Playwright against the
  live URL; pin the clock first (`CX.S.playing=false` AFTER boot's 900 ms autoplay timer, or
  the replay runs to the end mid-capture) and palette-optimise with Pillow — keep the hero
  (`track.png`) at full colour, quantise the rest to 256.

## The one rule: edit source → build → ship LATEST
- **Source of truth:** `src/`
  - `console.css` — design system (`cx-` prefix; phosphor cyan / signal amber / alert red on deep navy).
  - `js/core.js` — state, time engine (t = fractional days from 2025-05-15), ephemeris interpolation, WebAudio synth engine (no audio assets).
  - `js/scene3d.js` — Three.js r128 scene: starfield + Milky Way band, planets on real positions + element-derived orbit lines, comet with 3 particle tail systems (ion / dust / **anti-tail** for the A-05 viz), traveled-path drawRange trail, camera presets (free/top/chase/mars/sun), HUD labels + range line.
  - `js/fireballs.js` — FIREBALLS mode: equirectangular CNEOS impact map (land rings, graticule,
    energy-tiered dots, IM1/IM2 reticles), filter pods, hover/click hit testing, stats rail.
    Reads `window.ATLAS_FIREBALLS`; event tuple layout is documented at the top of the file and
    must stay in sync with `tools/fetch_fireballs.py`.
  - `js/charts.js` — canvas chart lib; right-rail telemetry (real data) + dossier charts (spectrum, polarization, acceleration, lightcurve, trajectory-side-view, size — stylized illustrations of published results).
  - `js/ui.js` — DOM skeleton, boot sequence, timeline scrubber, anomaly dossiers + timeline
    records (both use the `cx-sheet` overlay and share `refsRow()`), the CASE FILES / MISSION
    LOG rail tabs, compare table, archive docs (redactions + stamps), all wiring (delegated
    `data-act` clicks).
  - `js/main.js` — boot flow + frame loop. `APP_VERSION` lives here.
  - `data-ephemeris.js` / `data-content.js` / `data-fireballs.js` — GENERATED. Never hand-edit.
  - `vendor/` — three.min.js r128 (UMD), OrbitControls, Share Tech Mono woff2 (OFL).
- **Build:** `python tools/build.py` → overwrites **`_LATEST - 3I-ATLAS Anomaly Console.html`**
  (project root, ~1 MB, fully offline, double-click to open — the only file Stewart needs).
- **Verify before claiming done:** `node --check` each edited js; serve (`python -m http.server`)
  and load in a browser; console must be clean. NOTE: browser caches aggressively — bust with
  `?bust=N` query when re-testing, and remember background tabs throttle the boot-sequence
  timers (front the tab or the auth prompt takes ~a minute to appear).

## Data pipelines (all real)
- **Ephemeris:** `python tools/fetch_ephemeris.py` — pulls heliocentric ecliptic J2000 vectors
  from JPL Horizons (3I/ATLAS + 8 planets daily 2025-05-15→2026-12-31; 1I/'Oumuamua 2017;
  2I/Borisov 2019-20) → `data/ephemeris.json` → baked to `src/data-ephemeris.js`.
  Computed close approaches match published values (Mars 0.1939 AU 2025-10-03, perihelion
  1.3566 AU 2025-10-29, Earth 1.7978 AU 2025-12-19, Jupiter 0.3588 AU 2026-03-17).
- **Fireballs:** `python tools/fetch_fireballs.py` — pulls the whole NASA/JPL CNEOS Fireball API
  table (1,069 rows since 1988-04-15, 883 located) plus Natural Earth 1:110m land (public domain,
  RDP-simplified to ~2,200 vertices) → `data/fireballs.json` + `data/world-land.json` → baked to
  `src/data-fireballs.js` (~94 KB). IM1/IM2 are tagged BY DATE from the live rows — never
  transcribed — so a CNEOS revision propagates. Their case text is `data/fireball-cases.json`.
- **Content:** `python tools/bake_content.py <research-json>` — converts the research payload
  (`data/research.json`, produced 2026-07-17 by a 31-agent web-research + per-anomaly
  adversarial fact-check workflow) → `src/data-content.js`. 25 anomaly cases (each with
  `verify: CONFIRMED|CORRECTED|UNCHECKED`), 24 timeline events, 20 sourced quotes, 3 ISO
  comparison profiles. Loeb scale: 4 (Jul 2025) → held 4 (Dec 2025) → 3 (Mar 2026).
  **The old "known gap" note here was WRONG and has been retired** (checked 2026-08-22):
  `timelineVerify`, `comparisonVerify` and A-24's `_verify` are all present in
  data/research.json with CORRECTED verdicts, and every one of the 25 cases carries a
  `_verify`. The real gap was one nobody had noticed: `quotesVerify` was absent from BOTH
  payloads — all 35 quotes shipped unverified. Closed in v2.7: 9 matched
  character-for-character against primary sources, 2 corrected, 1 is an explicit paraphrase,
  23 are SECONDARY (Medium/X/paywall/print/translation — primary text not publicly
  fetchable) and are labelled as such on the quote board rather than presented as verified.
  Per-quote `verify` now flows through bake_content.py into the bundle.

## Pulling claims from video (tools/fetch_transcripts.py)
Wraps yt-dlp to bulk-fetch a channel's captions. **Will not run from a cloud session** —
YouTube 429s datacenter IPs and demands "Sign in to confirm you're not a bot"; every
transcript route (timedtext, r.jina.ai, youtubetotranscript) is blocked the same way. Runs
fine from Stewart's machine, `--cookies-from-browser chrome` if it ever asks. The non-obvious
part is `vtt_to_text()`: YouTube auto-captions scroll, each cue repeating the previous cue's
tail, and one cue holds TWO lines of that window — so parse BY CUE, not by line, and append
only what a cue adds beyond the longest token overlap. Match on punctuation-stripped lowercase
tokens or "decade." fails to line up with "decade". `data/transcripts/` is gitignored: the repo
is public and those are someone else's words. Derived analysis goes in a case file; the
transcript does not.

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
  bottom-docked table) / `fireballs` (CNEOS impact map; HUD hidden) / `archive` (paper documents;
  HUD hidden). `setMode` must set `display:''` — not `'grid'` — on `#cx-fbwrap`, or the inline
  style out-ranks the narrow-viewport rule that turns it into one scrolling column.
- Timeline: click markers to jump (anomaly markers open the dossier); drag to scrub; SPACE
  play/pause; 1-5 modes; N=now (live position for today); M mute; Esc close.
- "VISUALIZE IN TRACKER" in a dossier jumps the clock to the anomaly date and applies its
  viz (anti-tail → sunward particles + chase cam; trajectory → ecliptic disc + top-down).
- Event crossings during playback fire toasts + synth alert tones (mission=cyan, anomaly=amber).
- Boot sequence doubles as the audio-unlock gesture; ESC skips.
