# Changelog — 3I/ATLAS Anomaly Console

## v2.1 — 2026-07-24 (all three files verified)
- The iso-research fleet completed on second resume (23/23 agents, 0 errors). Provisional
  1I/2I case files replaced with adversarially verified versions:
  - 1I/'Oumuamua: 11 O-cases (10 CORRECTED, 1 CONFIRMED) — incl. the verified verbatim
    "buoy resting in the expanse of the universe" quote from Extraterrestrial (2021),
    Micheli's 4.92e-6 m/s^2 acceleration, Mamajek's 1-in-500 LSR statistic, Mashchenko's
    91% pancake fit, Bialy-Loeb 0.3-0.9 mm sail thickness.
  - 2I/Borisov: 5 B-cases (4 CORRECTED, 1 CONFIRMED).
  - Both era timelines swept and CORRECTED (16 + 14 events survive).
  - Loeb's actual retro-rank for 1I on his 2025 scale: 4 (replaces provisional 6).
- 15 new sourced quotes merged into the archive quote board (35 total).
- Every case file in every era now carries an individual fact-check verdict; every era's
  dataset-verify line is green. No provisional content remains anywhere.

## v2.0 — 2026-07-24 (three-object console)
- TARGET switcher (3I / 1I / 2I in the top bar): the whole console re-scopes per object —
  animated trajectory with era-correct planet positions (fresh Horizons fetch: 27 queries,
  planets for 2017-18 and 2019-20), timeline window, anomaly log, close approaches,
  telemetry charts, per-object Loeb-scale gauge.
- 1I/'Oumuamua: violet inert "tumbling cigar" rendering (no tail — that IS the anomaly),
  8 provisional O-cases (lightsail, impossible acceleration, 10:1 elongation, LSR rest,
  pancake fit, Spitzer non-detection, radio silence, population budget). Verified research
  workflow running; provisional entries are marked and will be replaced in v2.1.
- 2I/Borisov: ice-blue active comet, 4 control-case B-items (CO-rich, nickel-in-cold-coma
  context for 3I's A-07, outburst/fragmentation, most-pristine polarimetry).
- Verified per-era physics spot-checks: 1I perihelion 0.2567 AU @ 2017-09-09, Earth range
  0.220 AU on discovery day; 2I perihelion 2.0066 AU @ 2019-12-08 at 43.9 km/s.
- COMPARE mode now shows all three trajectories simultaneously; case register doc groups
  all three files; NOW button correctly refuses in historical eras.
- Timeline/quote data for 1I+2I from the research workflow's completed timeline agents
  (17 + 15 events); anomaly files provisional pending the resumed verify fleet.

## v1.2 — 2026-07-24 (fact-check complete)
- Timeline + comparison dataset-level verify sweeps completed (third resume; 31/31 agents,
  0 errors). Both returned CORRECTED with real catches folded in:
  - JUICE entry re-dated/re-framed: ESA's 2026-04-02 release covers Nov 2025 observations
    (~60M km, MAJIS measured ~2,000 kg/s water on 2025-11-02), not the Jupiter approach.
  - Methane result correctly attributed to Belyakov et al. ApJL (JWST/MIRI, CH4:H2O
    11.0±0.5% → 21.6±1.3%), separated from the June 2026 Cordiner Nature isotope paper
    (12C/13C = 147, 14N/15N = 343).
  - JWST CO2:H2O ratio updated to the published 7.6±0.3 (was preprint 8.0±1.0).
  - Hubble-era size/mass figures aligned to the actual NGA papers (~0.42 km radius).
  - 1I and 2I comparison rows fully confirmed against JPL SBDB/MPC.
- Loeb-scale panel now displays the dataset fact-check status line (bake derives it
  from the verifier verdicts).
- EVERYTHING in the console is now either real JPL Horizons geometry or
  adversarially fact-checked content. No open items remain.

## v1.1 — 2026-07-24
- A-24 (sideways non-gravitational acceleration) now adversarially fact-checked:
  date corrected 2026-02-05 → 2026-03-03 (Spada/Krolikowska/Dones arXiv submitted
  Feb 28 2026; Loeb's essay Mar 3 2026); one conflated source removed.
  All 25 anomaly cases now individually verified (21 CORRECTED, 4 CONFIRMED).
- Resume-protocol hardening: v1.0 archived to `_Archive (old versions)/`,
  resume rules added to CLAUDE.md.
- Still pending (hit usage limit twice): dataset-level verify sweeps for the
  timeline (24 events) and ISO comparison table. Resumable for ~free:
  `Workflow({scriptPath: <session workflows dir>/atlas-research-wf_79915c4d-948.js,
  resumeFromRunId: "wf_79915c4d-948"})` — 29/31 agents replay from cache.

## v1.0 — 2026-07-17 (initial release)
- Full NASA-terminal dashboard for 3I/ATLAS (C/2025 N1), single self-contained HTML (~1 MB).
- Real JPL Horizons ephemerides: 3I/ATLAS + 8 planets (daily, 2025-05-15 → 2026-12-31),
  1I/'Oumuamua, 2I/Borisov. Close approaches computed from data match published values.
- 3D tracking view (Three.js r128): starfield + Milky Way band, planets + orbit lines,
  hyperbolic trajectory with traveled/future path, ion + dust particle tails, anti-tail mode,
  camera presets (FREE / TOP-DOWN / CHASE / FROM MARS / FROM SUN), planet range line, HUD labels.
- Animated timeline 2025-05 → 2026-12: scrub/play (1-30 d/s), event markers, toasts + synth
  alert tones on crossings, TODAY marker + live "NOW" position.
- Anomaly register: 25 numbered case files from Avi Loeb's running list (final published
  tally 22), each with observation, Loeb's take (+ sourced quote), the official explanation,
  a per-case chart (spectrum / polarization / acceleration / lightcurve / size / trajectory),
  fact-check chip, and source links. "Visualize in tracker" applies the case to the 3D view.
- Loeb scale gauge with history (4 → held 4 → 3 after the quiet Jupiter pass).
- Compare mode: 1I vs 2I vs 3I trajectories in 3D + full stat table.
- Archive mode: styled "declassified" documents (charter memo, case register, DSN log,
  quote board of 20 verbatim sourced quotes) with click-to-reveal redactions.
- Boot sequence (auth = audio unlock), synthesized mission-control ambience, CRT toggle.
- Content produced by a 31-agent research workflow with per-anomaly adversarial fact-checks
  (20 CORRECTED, 4 CONFIRMED, 1 UNCHECKED — A-24's verifier hit a usage limit, as did the
  timeline/comparison dataset-level verifiers).
