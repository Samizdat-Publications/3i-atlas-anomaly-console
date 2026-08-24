# 3I/ATLAS — Interstellar Anomaly Review Console (project guide for Claude sessions)

A single-file, framework-free "NASA terminal" dashboard about the interstellar object
**3I/ATLAS (C/2025 N1)** — real JPL Horizons trajectory data + Avi Loeb's 25-case anomaly
register (each case shows Loeb's claim AND the official explanation side by side).
Built for Stewart, for fun. Clearly labeled unofficial/educational in the footer.

## Resume protocol (usage limits hit often — checkpoint everything)
**CURRENT STATE (2026-08-24):** v2.15 merged + deployed (PR #11). v2.16 (nuclear-site test,
F-07 + BR-08, claim coverage closed) and v2.17 both shipped in PR #12. v2.17 adds: boot now
defaults to the CHASE camera unless a deep link set its own; the event toast carries a
`▲ ANOMALY` / `◆ MISSION EVENT` kind chip; and the **DISPATCH overlay** (off by default) draws
the claimed release of material at the Mars pass, perihelion and the Jupiter pass. DISPATCH is
labelled as speculation in three places on purpose — pod, dashed banner, and toast — because an
unlabelled particle burst inside real Horizons geometry reads as a measurement. If you touch it,
keep all three labels. Earlier: v2.11 shipped + deployed + verified live. The fireball
register now runs on THREE datasets, not one, because F-03 was answering the wrong question.
The "fireballs are increasing" argument is built on **AMS eyewitness reports**, not CNEOS —
and its figures are ACCURATE (Q1 2026: 25 events at 51-99 reports vs a 11.8 mean, 16 above
100 vs 8.8). F-03 now says so before arguing, then runs the test that separates the readings:
a bigger audience gives each event more reports and pushes events UP through the bins, so a
flat middle bin is the bias, not evidence against it. Diagnostic = did well-witnessed events
outgrow the dataset (x1.21 vs x1.23 — no). CNEOS can't arbitrate: floor ~0.048 kt, and only
**4 CNEOS rows in all of 2025-26 fall in the regions these videos discuss**. GMN settles it —
camera-measured absolute magnitudes, bright fraction x1.08 in Q1 2026, sensitivity drift ruled
out (median AbsMag stable -0.09..+0.05). **GMN IS NIGHT-BLIND** and several 2026 events were
daytime; that limit and two others are stated inside the case because they cut toward the claim.
F-04 is new: both marquee 2026 US events are rows we already shipped, matched TO THE MINUTE
(Lake Erie 12:56:42 UTC = 8:56:42 EDT vs "8:57"; Pacific NW 07:48:36 UTC = 12:48 PDT vs
"12:48"). Both slow (14.9/12.2 km/s vs IM1's 44.8) so speed-dist carries it.

**FRAMING RULE, from Stewart (see Constraints):** this is NOT a debunk console. Fun speculation
grounded in real data, leaning toward taking UAP seriously. F-03's old prosecutorial tone was
wrong. Test claims as their proponents actually make them, credit accurate figures, and state
the limits that cut against your own conclusion.

**CLAIM COVERAGE IS CLOSED (2026-08-24).** `docs/claim-coverage.md` maps his enumerated
24-anomaly list against our 26 3I cases and there are now ZERO gaps and ZERO partials.
The ALMA methanol gap was closed by **A-26** on 2026-08-23 — an earlier version of THIS
NOTE still called it open, which was wrong and cost a re-check. The last two partials were
resolved 2026-08-24 and they were not the same kind of problem: row 12 (Ni/CN) was a real
gap INSIDE A-07 — the ratio was stated in the observation and argued in neither direction —
and is now argued both ways (the counter-reading is that CN is the DENOMINATOR and 3I is
independently CO2-dominated with ~4% water, that Ni and CN are measured over different
e-folding radii of 593.7 vs 841 km, and that the extreme values live at 4.4-2.85 AU where
Ni/Fe was also extreme before falling to normal); row 17 (the ~20x water spike) was never a
gap at all — A-20 carries it in both halves and the doc was simply stale. NO new case files
were made for either: splitting one set of spectra into extra cases is the tally inflation
BR-01 explicitly warns about. **The volcano-proximity test is DONE (v2.14)** — `tools/fetch_volcanoes.py` (NOAA NCEI, 1,608
volcanoes; Smithsonian GVP still 403s a cloud IP) + `tools/spatial_test.py` (Monte Carlo, two
nulls, both preserving the events' latitude distribution). NO ASSOCIATION at any radius: 23
events within 100 km vs 32.8 by chance, 78 vs 82.3 at 200 km, median 838 vs 854 km. Clustering
also null (353 vs 354 km). Case F-05 + briefing BR-06. The explanation is the camera selection
effect — volcano observatories run fixed sky cameras 24/7, which is why the footage exists. Do
NOT offer a rotation null for the clustering statistic: rotating every event by one offset
leaves event-to-event distances unchanged and cannot test it.
**THE NUFORC CASE FILE IS DONE (v2.15).** `tools/fetch_nuforc.py` pulls the mirror
`planetsig/ufo-reports` (nuforc.org still 403s a cloud IP) and writes AGGREGATES ONLY to
`data/nuforc.json` — the raw CSV is 14 MB of someone else's report narrative. Case F-06 +
briefing BR-07 + chart `CH.nuforcShare`. The result: Costa's baseline figures are near-exact
(7.92%, 4th of 29 shapes) and the Nov 2013 elevation is real (14.6% US through the 11th), but
it is measured against the CENTURY-LONG average. The contemporary baseline — the pooled twelve
months before it — was 14.33%, and the month came in at 14.37%. It ranks 14th of all 172
complete months Jan 2000-Apr 2014; July 2012 holds the record at 22.26%. THE FINDING THAT
MATTERS is the one left standing: fireball share tripled from ~5% (2004-2009) to ~14.5%
(2012) and stayed there, unexplained — the column found the right dataset and pointed at the
wrong month, three years late. Limits stated inside the case: the archive is 81% US (Chelyabinsk
day = 11 reports, 2 fireball) and STOPS 2014-05-08, so the 2026 half of the parallel is
untestable here. Seasonality (July 10.94%, December 10.11%, April 6.03%) is evidence the
self-assigned label does track real meteor activity.
Also in v2.15: `claim_label` on a case overrides the dossier's "LOEB ASSESSMENT" caption —
F-03..F-06 now read "THE CLAIM AS MADE", because those claims are not Loeb's; and
`tools/fireball_rate_check.py` now re-derives F-05's and F-06's figures too, not just
F-03's and F-04's.

**THE NUCLEAR-SITE TEST IS DONE (v2.16).** `tools/fetch_nuclear.py` (WRI Global Power Plant
Database, 195 reactors, 31 countries) + `tools/spatial_test.py --target nuclear`. The claim is
LaPaz's 1948-51 green fireballs near Los Alamos/Sandia/Kirtland and its modern descendants
(Malmstrom 1967, Rendlesham, the Hastings interviews). RESULT: no proximity effect — 11 events
within 100 km vs 8.8 by chance, 68 within 500 km vs 71.5 (below chance), median 2682 vs 2687 km.
TWO LIMITS ADDED 2026-08-24 AT STEWART'S PROMPTING, and they are the most important part of the
case: (1) THE ENERGY FLOOR — 0.048 kt smallest row, only 195 of 1069 below 0.1 kt, which takes a
metre-scale rock; the objects in the testimony are beach-ball to motorcycle scale and cannot
register at all, so most of the phenomenon is excluded before geometry enters. No better public
dataset exists (GMN discards non-meteor tracks, imagery is too coarse, infrasound has the same
floor); only eyewitness databases and official UAP reporting see small slow objects, and neither
yields coordinates for a Monte Carlo. (2) THE CLAIM IS ABOUT RADIATION GENERALLY, not weapons —
research reactors, enrichment, reprocessing, waste storage, industrial and medical sources. Only
civil power reactors have an open global position list. A wider target set is real outstanding
work.
ONE EXCEPTION, reported not buried: 200 km gives 34 vs 24.8, a 37% excess at p=0.025 scatter /
p=0.070 rotation. It stays a non-result because three radii were tested AND the SHAPE is wrong —
absent at 100 km, present at 200, gone at 500. A bump in the middle with nothing at the centre is
not an attraction. **STATE UP FRONT WHAT THIS CANNOT DO:** CNEOS records airbursts; the nuclear
testimony describes craft over silos. A null here does NOT refute it. Catalog starts 1988, forty
years after LaPaz. Power reactors are not the weapons complex.
**A REAL BUG WAS FOUND AND FIXED:** `Index.nearest` had a hard-coded 2,000 km search cap. With only
195 reactors most events are beyond it, so the first run reported "median 2000 vs 2000, p=1.000" —
a broken statistic dressed as a null. Cap and histogram bins are now PER-TARGET, and the report
warns when >2% of events sit at the cap. If you add a third target, set its cap from the real
distance scale or you will ship a fake null.
The volcano path was regression-checked byte-for-byte against the shipped `spatial-test.json`
after every edit — F-05 quotes those figures verbatim. Do that again for any future change.

**NEXT STEP (open):** nothing large is queued. Candidates: a fourth instrument for the rate
question, per-briefing Video Overview assets (see the NotebookLM notes), or bringing content
current past 2026-08-18.

**TRANSCRIPTS ARE TRACKED IN THIS REPO (owner's decision, 2026-08-23).** 114 of them,
2025-06-28 to 2026-08-23, ~357k words, in `data/transcripts/` with attribution and a per-video
index in `data/transcripts/README.md`; `data/transcripts/notebook/` holds 3 consolidated files
for research-notebook ingestion. Stewart's position is that the channel's material may be used
freely. The private mirror `Samizdat-Publications/3i-atlas-transcripts` still exists and
`tools/push_transcripts.py` still works, but is no longer the only route. `tools/push_transcripts.py` copies and pushes; `tools/transcript_digest.py` is the
phone-friendly skim. Fetching still only works from Stewart's machine (YouTube blocks
datacenter IPs).

**Earlier (2026-08-23):** v2.10 shipped. Case F-03's first version answered the "fireballs are
increasing" claim from the CNEOS catalog alone: the record STEPS (1994, 2000) then is FLAT for
26 years. `CH.fireballRate()` draws it and still ships. Superseded as the argument by v2.11.

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
  - `js/briefings.js` — BRIEFINGS mode: the reading surface. Question, answer, one chart,
    links into the case files behind it. The only place in the console meant to be read
    start to finish, so it gets a text measure and real leading rather than HUD styling.
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
- **Eyewitness reports:** `python tools/fetch_ams.py` — AMS/IMO public stats, per-month counts
  binned by HOW MANY PEOPLE reported each event, 2006-present → `data/ams-reports.json`. The
  numbers ship inside the stats page as `all_series[YEAR]` JS arrays. Unit is PEOPLE, not photons.
- **Camera photometry:** `python tools/fetch_gmn.py` — Global Meteor Network monthly trajectory
  summaries streamed and aggregated in flight (100+ MB each, never stored) → `data/gmn-monthly.json`.
  Network grew 73 → 1,327 stations, so ONLY `frac_m4` is comparable across years.
- **Volcanoes:** `python tools/fetch_volcanoes.py` — NOAA NCEI, 1,608 positions → `data/volcanoes.json`.
- **UFO sightings:** `python tools/fetch_nuforc.py` — the NUFORC archive via the
  planetsig/ufo-reports mirror, AGGREGATES ONLY → `data/nuforc.json`. Frozen upstream (last
  sighting 2014-05-08), so it is not in the monthly refresh. `shape` is a WITNESS'S OWN WORD,
  not a measurement: its "fireball" is not the AMS or CNEOS quantity and must never be pooled
  with them.
- **Spatial test:** `python tools/spatial_test.py --save` — Monte Carlo, two nulls → `data/spatial-test.json`.
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

## Exports for outside tools (NotebookLM / Gemini)
`docs/NOTEBOOKLM-DOSSIER.md` is the self-contained source description: schemas, verification
taxonomy, method, findings, file manifest, ingestion order, and — deliberately first — a list of
fields this project does NOT have (no FOIA IDs, no Wayback captures, no numeric credibility
score), because a notebook told to expect them invents them.
- `python tools/export_dossier.py` → `dossier/00`-`11`: the corpus as Markdown + CSV (~39k words).
  Generates its own manifest so counts cannot go stale.
- `python tools/export_tables.py` → `dossier/12`-`14`: the three quantitative datasets as Markdown
  tables, because notebooks reject .csv URLs and lose column semantics when they do accept them.
- `python tools/export_transcripts.py` → `data/transcripts/notebook/`: 114 transcripts batched into
  3 files, since notebooks cap SOURCE COUNT far below 114 while allowing huge per-source word counts.
ALL of dossier/ is generated. Edit `data/`, never `dossier/`.

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

`tools/transcript_digest.py` is the bridge back to a cloud session: it reads the gitignored
transcripts locally and prints only the CLAIM-BEARING sentences — a subject noun plus
something checkable (a number, a trend word, a place correlation) — small enough to paste
from a phone. A sentence with a measured quantity but only a pronoun subject ("the energy on
this one was 1.2 kilotons") is kept anyway; it is usually the most checkable line in the
video. Its output also lands in `data/transcripts/digest.md`, inside the gitignored folder,
because a digest of his sentences is still his sentences.

The digest is the phone-friendly path; the FULL path is `tools/push_transcripts.py`, which
copies `data/transcripts/` into the separate PRIVATE repo `Samizdat-Publications/3i-atlas-transcripts`
and pushes. A cloud session attaches that repo and reads every transcript in full. Private, not
public: this repo is published and linked from the live site, and putting a creator's whole
caption archive in it is republishing his work rather than storing it. The GitHub app in a
cloud session CANNOT create repos (403), so the empty private repo has to be made by hand once
at https://github.com/new before that script will run.

## Stewart's machine — ALWAYS include the `cd`
Stewart is not a terminal user and works from a Windows laptop. This repo lives at
`C:\Users\stewa\OneDrive\Documents\Claude\3I ATLAS Anomaly Console` — note the SPACES in
the folder name, so the path must always be quoted or the command silently breaks at "3I".

**Every command block given to him must be copy-paste-runnable on its own**: start it with the
`cd`, use Windows path separators, and never assume he is already in the right folder or knows
how to get there. Prefer PowerShell. If `python` is not found, `py` is the Windows launcher.
One block = one paste = one working result; do not split a command across explanatory prose.

## Constraints
- Self-contained, offline, no admin, no server to run. All assets inline (font base64'd at build).
- The security hook blocks Write/Edit content containing the raw HTML-set property name —
  inject markup via `setH()` in ui.js (uses `insertAdjacentHTML`); never write that property
  name in code or docs.
- Keep the anomaly framing balanced: every Loeb claim is shown WITH the official explanation.
- **Not a debunk console** (Stewart, 2026-08-23). This is fun speculation grounded in real data,
  leaning toward taking the UAP phenomenon seriously — not hard science, and not a scoreboard
  against the people making the claims. Case F-03 as written argues like a prosecutor ("the
  shape is a step, not a slope"); every sentence is sourced, but the posture is wrong and it
  should be softened toward "here is what this catalog can and cannot settle". Detection-bias
  findings stay, because they are real and interesting. Positional/temporal claims (clusters,
  volcanoes, nuclear sites, 3I/ATLAS timing) are TESTABLE against the lat/lon and timestamps
  already shipped — test them honestly and show what is there. Where CNEOS cannot speak to a
  claim at all (sighting reports are not in it), say so plainly rather than implying a
  refutation the data has not earned.
  The fiction ("IOWG", clearance banners, stamps) stays obviously playful; the disclaimer
  footer stays.

## App architecture notes
- Modes: `briefings` (question-led entry points, the intended way in — `src/js/briefings.js`,
  content in `data/briefings.json`, deep-linked `#brief/BR-0n`; bake_content.py HARD-FAILS on a
  dead case link) / `track` (default 3D) / `anomalies` (dossier overlay) / `compare` (1I·2I·3I paths +
  bottom-docked table) / `fireballs` (CNEOS impact map; HUD hidden) / `archive` (paper documents;
  HUD hidden). `setMode` must set `display:''` — not `'grid'` — on `#cx-fbwrap`, or the inline
  style out-ranks the narrow-viewport rule that turns it into one scrolling column.
- Timeline: click markers to jump (anomaly markers open the dossier); drag to scrub; SPACE
  play/pause; 1-5 modes; N=now (live position for today); M mute; Esc close.
- "VISUALIZE IN TRACKER" in a dossier jumps the clock to the anomaly date and applies its
  viz (anti-tail → sunward particles + chase cam; trajectory → ecliptic disc + top-down).
- Event crossings during playback fire toasts + synth alert tones (mission=cyan, anomaly=amber).
- Boot sequence doubles as the audio-unlock gesture; ESC skips.
