# 3I/ATLAS Anomaly Review Console — Source Dossier

**Purpose of this file:** a self-contained primary-source description of the project's
datasets, schemas, methods and findings, written for ingestion into a research notebook
(NotebookLM / Gemini). Generated 2026-08-23 against commit `5cc4511`, app version 2.14.

**Repository:** <https://github.com/Samizdat-Publications/3i-atlas-anomaly-console>
**Branch:** `main` (single active branch; all releases merge here)
**Live build:** <https://3i-atlas-anomaly-console.pages.dev>
**Licence/status:** public repository, unofficial and educational project.

---

## 0. Fields this dataset does NOT contain

Stated first so a notebook does not go looking for them or hallucinate them.

| Requested field | Status |
|---|---|
| FOIA request identifiers | **None.** No FOIA material is used anywhere in this project. |
| Wayback Machine first-capture dates | **None.** Sources are cited by live URL only; no archival snapshot IDs are recorded. |
| Per-record "credibility score" (numeric) | **None.** Verification is categorical, not scored — see §2.4. |
| Per-record "severity score" | **None.** The Loeb Scale (§2.5) is an OBJECT-level rank assigned by a third party, not a per-record severity. |
| Witness//personal identifiers | **None.** No personal data is stored. |
| Cross-referenced entity tags | **None as a structured field.** Cross-references exist only as (a) `sources` URL arrays, (b) briefing→case link arrays, (c) the `tag` slot in fireball rows, used solely for `IM1`/`IM2`. |
| Video transcripts | **Not in this repository.** See §3.6 — they are third-party content held in a separate PRIVATE repo and are unreachable to an external ingester. |

---

## 1. Project Overview & Scope

### 1.1 Definition
A single-file, framework-free browser application ("NASA terminal" dashboard) that
documents claims of anomalous behaviour by interstellar objects — principally
**3I/ATLAS (C/2025 N1)** — and presents each claim beside its mainstream counter-reading,
with primary-source citations and a per-record verification verdict.

### 1.2 Objective
To let a non-specialist evaluate contested claims against real data. The design rule,
set by the project owner, is explicit and constrains the content:

> Not a debunk console. Speculation grounded in real data, leaning toward taking the UAP
> phenomenon seriously — not a scoreboard against the people making the claims. Test claims
> as their proponents actually make them, credit accurate figures, and state the limits that
> cut against your own conclusion.

### 1.3 Core research hypotheses under test
| ID | Proposition | Status in dataset |
|---|---|---|
| H1 | 3I/ATLAS exhibits measurable properties outside the range of known comets | Supported for several specific measurements; see §3.1. 47 case files. |
| H2 | Those properties collectively indicate artificial origin | Not established. Anomalies are non-independent; a single unifying cause propagates into many. |
| H3 | Meteor/fireball rates rose materially in 2026 | Observation confirmed in eyewitness-report data; **not** confirmed by either instrument that measures brightness or energy. §5.1. |
| H4 | Fireballs preferentially fall near volcanoes | **Tested and not supported.** Monte Carlo, no association at any radius. §5.2. |
| H5 | Fireball events cluster in repeat locations | **Tested and not supported.** §5.2. |
| H6 | Two CNEOS bolides (IM1, IM2) were interstellar | Unresolved; rests on one un-audited catalog with no published uncertainties. §3.4. |

### 1.4 Dataset origin and collection methods
All datasets are machine-pulled from named public sources by scripts in `tools/`.
None are hand-transcribed. Hand-authored analytical text is stored separately from
fetched data so a refresh can never overwrite prose, and vice versa.

| Pipeline | Script | Upstream source |
|---|---|---|
| Orbital vectors | `tools/fetch_ephemeris.py` | JPL Horizons |
| Atmospheric impacts | `tools/fetch_fireballs.py` | NASA/JPL CNEOS Fireball API + Natural Earth 1:110m land |
| Eyewitness reports | `tools/fetch_ams.py` | American Meteor Society / IMO public statistics |
| Camera photometry | `tools/fetch_gmn.py` | Global Meteor Network trajectory summaries (CC BY) |
| Volcano positions | `tools/fetch_volcanoes.py` | NOAA NCEI volcano location service |
| Spatial hypothesis test | `tools/spatial_test.py` | derived from the two above |
| Content compilation | `tools/bake_content.py`, `tools/bake_instruments.py` | derived |
| Bundle build | `tools/build.py` | derived |

### 1.5 Pipeline architecture
```
upstream APIs ──► tools/fetch_*.py ──► data/*.json        (canonical, git-tracked)
hand-authored  ──────────────────────► data/research*.json
                                       data/fireball-cases.json
                                       data/briefings.json
                                              │
                                              ▼
                              tools/bake_content.py, bake_instruments.py
                                              │
                                              ▼
                                       src/data-*.js       (GENERATED, never hand-edited)
                                              │
                                              ▼
                                       tools/build.py ──► single-file HTML bundle
```
A scheduled GitHub Action (`.github/workflows/refresh-data.yml`) re-pulls upstream monthly
and opens a pull request **only if the upstream bytes changed**; it never pushes to `main`,
because a revised source row can invalidate analytical text that quotes it.

---

## 2. Data Schema & Classification Taxonomy

### 2.1 `data/fireballs.json` — CNEOS atmospheric impacts
Events are **positional arrays**, not objects. Field order is fixed and declared in the
file's own `fields` key:

| Index | Field | Type | Units / format | Notes |
|---|---|---|---|---|
| 0 | `date` | string | `YYYY-MM-DD HH:MM:SS` UTC | Second precision. Used for local-time matching. |
| 1 | `energy_1e10J` | number | 10¹⁰ joules | **Radiated** energy (light only). |
| 2 | `impact_e_kt` | number | kilotonnes TNT | **Total impact** energy. Distinct from index 1 — conflating them is a common error of an order of magnitude. |
| 3 | `lat` | number \| null | decimal degrees, +N | `null` where CNEOS reports no position. |
| 4 | `lon` | number \| null | decimal degrees, +E | |
| 5 | `alt_km` | number \| null | km | Altitude of peak brightness. |
| 6 | `vel_kms` | number \| null | km/s | Pre-entry speed. Present for a minority of rows. |
| 7 | `tag` | string \| null | `IM1` \| `IM2` \| null | Assigned **by date at fetch time**, never transcribed, so a catalog revision propagates. |

Top-level: `count` 1069, `located` 883, `first` 1988-04-15, `last` 2026-08-15.
**No uncertainties are published by CNEOS on any field.** This is the single most important
property of the dataset and the basis of most disputes about it (§4.4).

### 2.2 `data/ams-reports.json` — eyewitness report counts
Per-year, per-month counts binned by **how many people reported each event**. Unit of
measurement is people, not photons.

| Bin key | Definition |
|---|---|
| `one` | events with exactly 1 report |
| `2_10` | 1 < n ≤ 10 |
| `11_25` | 10 < n ≤ 25 |
| `26_50` | 25 < n ≤ 50 |
| `51_99` | 50 < n < 100 |
| `100_plus` | > 100 reports |

Structure: `years["YYYY"][bin_key]` → array of 12 integers (Jan–Dec).
Coverage 2006–2026, 21 years, 106,093 events total.

### 2.3 `data/gmn-monthly.json` — camera photometry
Monthly aggregates keyed `"YYYYMM"`, 92 months (2019-01 → 2026-08).

| Field | Meaning |
|---|---|
| `n` | meteors with a computed trajectory |
| `counts.m0/m2/m4/m6` | count at absolute magnitude ≤ 0 / −2 / −4 / −6 |
| `stations` | distinct contributing camera stations that month |
| `median_absmag` | median absolute magnitude (sensitivity-drift diagnostic) |
| `frac_m4` | `counts.m4 / n` — **the bias-resistant statistic** |
| `per_station` | `n / stations` |

**Critical:** the network grew from 73 stations (2019) to 1,327 (2025). Raw counts are NOT
comparable across years. Only `frac_m4` is.

### 2.4 Verification taxonomy (categorical — there is no numeric score)

**Case files** — field `_verify` (in `research*.json`) / `verify` (in the built bundle):
| Value | Meaning |
|---|---|
| `CONFIRMED` | Every factual claim matched the cited primary source unchanged. |
| `CORRECTED` | Fact-check found an error; the record was amended before publication. |
| `UNCHECKED` | Default; not present in the current dataset. |
| `PROVISIONAL` | Hand-authored placeholder pending research. Not present in current data. |

Current distribution (3I set, n=26): `CORRECTED` 21, `CONFIRMED` 5.
Interpretation: `CORRECTED` is the *majority* state and denotes a record that was found
wrong and fixed — not a record of lower confidence than `CONFIRMED`.

**Quotations** — field `verify`:
| Value | Meaning |
|---|---|
| `VERBATIM` | Matched character-for-character against the primary source. |
| `CORRECTED` | Wording or date was wrong in circulation; corrected against source. |
| `PARAPHRASE` | Explicitly labelled as not a direct quotation. |
| `SECONDARY` | Primary text not publicly fetchable (paywall, print, translation). Labelled as such rather than presented as verified. |

Distribution across the 35 quotations: `SECONDARY` 23, `VERBATIM` 9, `CORRECTED` 2, `PARAPHRASE` 1.

### 2.5 Loeb Scale — object-level rank, third-party assigned
0–10 scale published by Avi Loeb for likelihood of technological origin.
Values in dataset: 3I/ATLAS = **3**; 1I/ʻOumuamua = **4** (retrospective); 2I/Borisov = **0**.
History for 3I/ATLAS: rank 4 (Jul 2025) → held 4 (Dec 2025) → **reduced to 3 (Mar 2026)**
after the Jupiter pass produced nothing unusual. This is not our score; it is a tracked claim.

### 2.6 Controlled vocabularies
| Vocabulary | Values |
|---|---|
| Object key | `3i`, `1i`, `2i`, `fb` (fireball register — has no ephemeris) |
| Timeline `kind` | `discovery`, `observation`, `close_approach`, `statement`, `status` |
| Quote `camp` | `loeb`, `official`, `media` |
| Case `viz_hint` | `acceleration`, `lightcurve`, `other`, `polarization`, `size`, `spectrum`, `tail`, `timing`, `trajectory`, `speed-dist`, `fireball-rate`, `fireball-instruments`, `volcano-dist` |
| Case ID prefix | `A-` 3I · `O-` 1I · `B-` 2I · `F-` fireball · `BR-` briefing |

### 2.7 Coordinate and temporal formats
- Positions: decimal degrees, +N / +E, WGS84-equivalent as published upstream.
- Fireball timestamps: `YYYY-MM-DD HH:MM:SS` **UTC**, second precision.
- Case/event/briefing dates: `YYYY-MM-DD`.
- Ephemeris: heliocentric ecliptic J2000, **AU**, daily samples.
- Timeline record IDs: `E-YYYYMMDD`, numerically suffixed on same-day collisions, so deep
  links survive insertion of earlier events.

---

## 3. Full Dataset & Case Records

Record counts as of commit `5cc4511`:

| Collection | Count | Location |
|---|---|---|
| Anomaly/case files | **47** (3I 26 · 1I 11 · 2I 5 · fireball 5) | `data/research.json`, `data/research-iso.json`, `data/fireball-cases.json` |
| Timeline events | **58** (3I 28 · 1I 16 · 2I 14) | `data/research.json`, `data/research-iso.json` |
| Sourced quotations | **35** (3I 20 · ISO 15) | same |
| Briefings (narrative syntheses) | **6** | `data/briefings.json` |
| CNEOS fireball rows | **1,069** (883 with position) | `data/fireballs.json` |
| AMS report-bin records | 21 years × 12 months × 6 bins | `data/ams-reports.json` |
| GMN monthly aggregates | **92** months | `data/gmn-monthly.json` |
| Volcano positions | **1,608** | `data/volcanoes.json` |
| Comparison profiles | 3 objects | `data/research.json` |

### 3.1 Case-file record structure
```json
{
  "id": "A-26",
  "title": "Extreme methanol enrichment (CH3OH/HCN) measured by ALMA",
  "date": "2025-09-15",
  "observation": "<what was measured, and by whom>",
  "loeb_take": "<the anomaly/technosignature reading>",
  "official_explanation": "<the mainstream counter-reading>",
  "loeb_quote": "<verbatim or labelled quotation>",
  "quote_source": "<citation for the quotation>",
  "loeb_scale": null,
  "viz_hint": "spectrum",
  "sources": ["<primary URL>", "..."],
  "_verify": "CONFIRMED",
  "_verifyNotes": "<what was checked against what>"
}
```
Every case carries **both** readings by construction. `sources` is capped at 4 URLs and
ordered primary-source-first.

### 3.2 The three interstellar objects — comparison anchors
| | 1I/ʻOumuamua | 2I/Borisov | 3I/ATLAS |
|---|---|---|---|
| Designation | 1I/2017 U1 | C/2019 Q4 | C/2025 N1 |
| Discovered | 2017-10-19 | 2019-08-30 | 2025-07-01 |
| Coma/tail | **none detected** | textbook comet | active, plus sunward anti-tail |
| Loeb Scale | 4 (retrospective) | **0** (control case) | 3 |
| Case files | 11 | 5 | 26 |
| Role | the original argument | the control | the contested case |

### 3.3 3I/ATLAS — measured trajectory milestones (JPL Horizons derived)
| Event | Date | Value |
|---|---|---|
| Mars closest approach | 2025-10-03 | 0.1939 AU |
| Perihelion | 2025-10-29 | 1.3566 AU |
| Earth closest approach | 2025-12-19 | 1.7978 AU |
| Jupiter closest approach | 2026-03-17 | 0.3588 AU |

### 3.4 Fireball register (object key `fb`) — 5 case files
| ID | Subject | Verify |
|---|---|---|
| F-01 | IM1 — 2014-01-08 bolide, 44.8 km/s, Bismarck Sea | CONFIRMED |
| F-02 | IM2 — 2017-03-09 bolide, 36.5 km/s, North Atlantic | CONFIRMED |
| F-03 | Are fireballs increasing? Three-instrument test | CONFIRMED |
| F-04 | The 2026 events with CNEOS rows | CONFIRMED |
| F-05 | Fireball/volcano proximity — Monte Carlo test | CONFIRMED |

### 3.5 Independently matched events (CNEOS row ↔ public reporting)
Matching rule: date **plus** location **plus** local-clock agreement. Date alone is not a
match — CNEOS logs 2–3 events monthly worldwide.

| Public description | CNEOS row (UTC) | Local conversion | Row values |
|---|---|---|---|
| "Daytime over Lake Erie at 8:57 a.m. Eastern, 222 reports across 16 states plus Ontario" | 2026-03-17 12:56:42 | 08:56:42 EDT (= 8:57 to the minute) | 41.2 N, 82.0 W · 0.37 kt · 45.0 km · 14.9 km/s |
| "Around 12:48 a.m. local, northern Oregon into British Columbia, 250+ reports" | 2026-08-14 07:48:36 | 00:48 PDT | 47.7 N, 119.4 W · 0.13 kt · 30.0 km · 12.2 km/s |

Across all of 2025–2026, only **four** CNEOS rows fall anywhere in the regions this body of
coverage discusses. Everything else discussed is below the detection floor (§4.4).

### 3.6 Transcript corpus — NOT INGESTIBLE FROM THIS REPOSITORY
114+ auto-caption transcripts (2025-06 → 2026-08) of a third-party YouTube channel are used
as the claim source. They are held in a **separate private repository**
(`Samizdat-Publications/3i-atlas-transcripts`) and `data/transcripts/` is gitignored here,
because the public repository must not republish a creator's caption archive.

**Consequence for a research notebook: these are unavailable.** What is public is the
*derived analysis* — claims are quoted only in short, attributed excerpts inside case files,
always labelled `TRANSCRIBED FROM AUTO-CAPTIONS, NOT A PUBLISHED TEXT`, because machine
transcription is not a verbatim record of a person's words.

---

## 4. Methodological Framework & Verification Protocols

### 4.1 Balance rule (structural, not editorial)
Every case file must carry the claim and the counter-reading in adjacent fields. A record
with only one side is malformed. Where a claim's figures are accurate, the record says so
explicitly before disagreeing with the *inference* drawn from them.

### 4.2 Source hierarchy
1. Refereed literature (DOI/arXiv) — preferred.
2. Primary data APIs (JPL, NOAA, AMS, GMN).
3. Institutional releases (NASA, ESO, NRAO).
4. Media reporting — permitted only for statements-of-record, marked `SECONDARY`.

Auto-caption transcripts are **claim sources**, never fact sources.

### 4.3 Anomaly-detection logic — the normalisation rule
Every instrument here grew over its own record: US sensor coverage, the eyewitness reporting
audience, and a camera network that went from 73 to 1,327 stations. Each produces a rising
raw count that has nothing to do with the sky. The invariant rule:

> Never compare raw counts across years. Divide by something that grew with the instrument.

| Instrument | Statistic used |
|---|---|
| AMS | high-report events as a **share** of all events |
| CNEOS | events at ≥1 kt (a detection-rate change cannot inflate the bright end) |
| GMN | meteors at absolute magnitude ≤ −4 as a **share** of all detections |

### 4.4 Detection-floor rule
CNEOS lists **no event below 0.048 kt**; only 6 of 1,069 rows fall below 0.073 kt.
Therefore:
- absence of a CNEOS row is **not** evidence an event did not occur;
- a claim about sub-0.05 kt events cannot be confirmed *or* refuted by CNEOS.

The measurement gap where eyewitnesses see everything and sensors see nothing is
approximately **0.001–0.05 kt**.

### 4.5 Temporal precedence and windowing
- **Whole months only.** Comparing a partial current month against full months in earlier
  years biases the current year downward. This error is invisible in output and changes
  conclusions; it was made and corrected during development.
- Like-for-like day-of-year cutoffs when comparing partial years.
- Baseline for all 2026 comparisons: **2021–2025 mean**.

### 4.6 Null models (negative controls)
For spatial tests, a uniform-random null is **wrong**: volcanoes sit on land and cluster in
arcs, so any land or latitude bias in the detections manufactures a false association.
Two nulls are used, both preserving the observed latitude distribution:

| Null | Construction | Tests |
|---|---|---|
| **Rotation** | one random longitude offset applied to *every* event at once | alignment with volcano longitudes, with the event set's internal clustering left perfectly intact |
| **Scatter** | each event keeps its latitude, redraws longitude uniformly | alignment *and* internal clustering |

**The rotation null is deliberately withheld from clustering statistics**, because rotating
every event by the same offset leaves every event-to-event distance unchanged and cannot
move the statistic. 1,000 trials per null; p-values use the +1 correction.

### 4.7 Contamination / debunk filters applied
- **Audience effect** — a growing reporting population both surfaces more events and gives
  each event more reports, pushing events *upward* through report bins. A flat middle bin is
  therefore a signature of the bias, not evidence against it. Diagnostic: did well-witnessed
  events outgrow the dataset as a whole?
- **Camera selection effect** — volcano observatories run fixed sky cameras continuously;
  this alone can generate an apparent fireball/volcano association in video evidence.
- **Sensitivity drift** — improving cameras would swell the faint end and mask a real rise
  in bright events. Diagnostic: median absolute magnitude over time.
- **Energy-type conflation** — radiated vs total impact energy differ by roughly an order of
  magnitude and are routinely quoted interchangeably in circulation.
- **Non-independence of anomalies** — one wrong assumption (e.g. nucleus size) propagates
  into many individually-listed anomalies, so a raw tally overstates the evidence. Noted as
  cutting both ways: a single mechanism explaining many observations is also what a correct
  explanation looks like.

### 4.8 Automated drift protection
`tools/fireball_rate_check.py` re-derives **every** figure quoted in cases F-03/F-04 from the
three datasets and exits non-zero on drift; the monthly refresh workflow fails loudly rather
than shipping a case that quotes a number the data no longer supports.
`tools/bake_content.py` hard-fails if a briefing links to a non-existent case.

---

## 5. Active Analytical Threads & Open Leads

### 5.1 Finding — the 2026 fireball rate: three instruments, three answers
Window: Q1 (whole months), 2026 vs 2021–2025 mean.

| Measure | 2026 | Baseline | Ratio |
|---|---|---|---|
| AMS events with ≥51 reports (raw) | 41 | 20.6 | ×1.99 |
| AMS all events (raw) | 2,391 | 1,944.2 | ×1.23 |
| AMS events with ≥11 reports | 131 | 108.4 | ×1.21 |
| AMS ≥51 as share of all | 1.715% | 1.067% | ×1.61 |
| CNEOS events ≥1 kt | 0 | 1.2 | — |
| **GMN bright-meteor share (mag ≤ −4)** | **0.286%** | **0.264%** | **×1.08** |

Sensitivity-drift control — GMN median absolute magnitude, 2021→2026:
`+0.05, −0.07, −0.09, −0.04, −0.01, −0.04` (stable; the confound does not apply).

**Reading.** The eyewitness observation is real and its published figures are accurate. The
well-witnessed population grew at the same rate as the dataset overall, which is the
signature of an audience effect. The instrument that measures brightness directly shows no
excess. **Stated limits that cut the other way:** GMN is night-blind and several prominent
2026 events were daytime; its coverage is regional; its brightest bin is noisy.
Conclusion recorded as *burden shifted*, not *claim refuted*.

### 5.2 Finding — fireball/volcano proximity: no association
883 located CNEOS events vs 1,608 NOAA volcanoes; 1,000 Monte Carlo trials per null.

| Within | Observed | Rotation null | p | Scatter null | p |
|---|---|---|---|---|---|
| 100 km | **23** | 32.8 | 0.963 | 32.7 | 0.968 |
| 200 km | 78 | 82.3 | 0.690 | 81.9 | 0.691 |
| 500 km | 260 | 250.5 | 0.301 | 250.6 | 0.253 |
| median nearest volcano | 838 km | 854 km | 0.295 | 853 km | 0.314 |

Clustering (scatter null only, 166 trials):
median nearest-event distance **353 km** vs 354 km (p=0.479); events with another within
100 km **55** vs 46.8 (p=0.228).

**Reading.** No association at any radius; the nearest bin sits *below* chance. Proposed
mechanism for the visual impression: volcano observatories operate continuous fixed sky
cameras. **Stated limit:** neither headline 2026 volcano event has a CNEOS row (both below
floor); nearest CNEOS row to Mayon volcano in the whole record is 312 km away, from 2015.

### 5.3 Finding — ALMA methanol enrichment (case A-26)
CH₃OH/HCN = **124 (+30/−34)** on 2025-09-12 and **79 (+11/−14)** on 2025-09-15; among the
most methanol-enriched values measured in any comet, **surpassed only by C/2016 R2
(PanSTARRS)** — an object that formed in our own solar system.
Source: Roth, Cordiner et al., ApJL, doi:10.3847/2041-8213/ae433b (arXiv:2511.20845).
Counter-reading: the quantity is a *ratio* and rises as readily on scarce HCN as on abundant
methanol; the two values overlap within their own error bars three days apart; the extended
source beyond 258 km is icy grains, which explains sunward enhancement while nucleus-sourced
HCN is depleted there.

### 5.4 Claim-coverage status
An enumerated 24-anomaly list published by the primary claim source was mapped against the
register: **all 22 observational anomalies now have case files.** The remaining two items on
that list are *mechanisms* (deuterium-as-fusion-fuel, magnetohydrodynamic propulsion), not
observations, and are treated as hypotheses attached to existing measurements rather than as
independent anomalies.

### 5.5 Open leads — outstanding, blocked, or unbuilt
| Lead | Status | Blocker / next vector |
|---|---|---|
| Nuclear-site proximity claim | **Untested** | Needs an authoritative facility-coordinate dataset. Method would reuse `spatial_test.py` unchanged. |
| NUFORC 2013 sighting spike (Cheryl Costa claim: Nov 2013, ~238 reports, ~20% "fireball" category vs ~7% normal) | **Blocked** | nuforc.org returns Cloudflare 403 to datacenter IPs. Public CSV mirrors exist. |
| Ni/CN ratio | **Partial** | Currently folded into case A-07 though it is a separate measurement against a separate comparison population. |
| ~20× post-perihelion water spike | **Partial** | Case A-20 covers the icy-grain disappearance but not the spike. |
| GMN daytime blind spot | **Structural, unresolvable** | No camera network can see daytime bolides; a different instrument class would be required. |
| Smithsonian GVP volcano list | **Blocked** | 403 to non-browser clients; NOAA NCEI used instead. |

### 5.6 Cross-dataset queries a notebook could usefully run
1. For each CNEOS row 2025–2026, is there a matching AMS high-report event on the same date?
   (Tests whether the two instruments see the *same* events at the overlap of their ranges.)
2. Does the GMN bright-meteor share correlate with AMS high-report share month-by-month?
   (If the audience-effect reading is right, they should decouple.)
3. Do CNEOS velocity outliers (>40 km/s) cluster in time or position?
4. Does the 2026 AMS excess concentrate in specific countries — i.e. is it a *population*
   signal rather than a sky signal?

---

## 6. File Manifest & Ingestion

### 6.1 Raw file URL pattern
```
https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/<path>
```

### 6.2 Manifest

| # | Path | Format | Size | Records | Contents |
|---|---|---|---|---|---|
| **P1** | `data/research.json` | JSON | 144 KB | 26 cases · 28 events · 20 quotes · 3 profiles | **3I/ATLAS core corpus.** Case files with both readings, verification verdicts, citations. |
| **P2** | `data/research-iso.json` | JSON | 128 KB | 16 cases · 30 events · 15 quotes | 1I/ʻOumuamua and 2I/Borisov corpora. |
| **P3** | `data/fireball-cases.json` | JSON | 24 KB | 5 cases | Fireball register analyses incl. the three-instrument and volcano tests. |
| **P4** | `data/briefings.json` | JSON | 20 KB | 6 | Narrative syntheses; the interpretive layer over the case files. |
| **P5** | `data/fireballs.json` | JSON | 64 KB | 1,069 rows | CNEOS atmospheric impacts 1988–2026. Positional arrays — see §2.1. |
| **P6** | `data/ams-reports.json` | JSON | 16 KB | 21 years × 12 × 6 | Eyewitness report-count bins 2006–2026. |
| **P7** | `data/gmn-monthly.json` | JSON | 20 KB | 92 months | Camera photometry aggregates 2019–2026. |
| **P8** | `data/spatial-test.json` | JSON | 4 KB | 1 result set | Monte Carlo output: radii, p-values, clustering, distance histogram. |
| S1 | `data/volcanoes.json` | JSON | 188 KB | 1,608 | NOAA volcano positions (input to P8). |
| S2 | `data/ephemeris.json` | JSON | 384 KB | 3 eras | Heliocentric ecliptic J2000 daily vectors. Numeric; low text value. |
| S3 | `data/world-land.json` | JSON | 36 KB | 100 rings | Natural Earth coastline, map rendering only. **No analytical content.** |
| S4 | `data/provisional-iso-anomalies.json` | JSON | 12 KB | 12 | Superseded fallback drafts. **Do not ingest** — replaced by P2. |
| D1 | `docs/two-instrument-problem.md` | Markdown | ~14 KB | — | Methodological essay: instrument bias, detection floors, the three-instrument result. |
| D2 | `docs/claim-coverage.md` | Markdown | ~7 KB | — | 24-anomaly claim list mapped to case files. |
| D3 | `_CHANGELOG.md` | Markdown | ~30 KB | — | Full development and finding history, v2.5 → v2.14. |
| D4 | `CLAUDE.md` | Markdown | ~18 KB | — | Architecture, constraints, and the project's framing rules. |
| C1 | `tools/*.py` | Python | — | 14 scripts | Pipelines and tests. **Derivative — ingest only for method verification.** |
| C2 | `src/data-*.js` | JavaScript | 706 KB | — | **GENERATED. Do not ingest** — duplicates P1–P8 in compiled form. |

### 6.3 Direct links to primary sources
- P1 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/research.json>
- P2 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/research-iso.json>
- P3 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/fireball-cases.json>
- P4 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/briefings.json>
- P5 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/fireballs.json>
- P6 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/ams-reports.json>
- P7 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/gmn-monthly.json>
- P8 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/data/spatial-test.json>
- D1 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/docs/two-instrument-problem.md>
- D2 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/docs/claim-coverage.md>
- D4 <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/CLAUDE.md>
- This file <https://raw.githubusercontent.com/Samizdat-Publications/3i-atlas-anomaly-console/main/docs/NOTEBOOKLM-DOSSIER.md>

Whole-repository archive (all files, one download):
<https://github.com/Samizdat-Publications/3i-atlas-anomaly-console/archive/refs/heads/main.zip>

### 6.4 Recommended ingestion sequence
**Batch 1 — orientation (ingest first, in this order).**
`docs/NOTEBOOKLM-DOSSIER.md` (this file) → `D1` → `D2`.
Establishes vocabulary, method, and the detection-floor concept before any raw record is read.

**Batch 2 — interpretive layer.**
`P4` (briefings) → `P3` (fireball cases).
Six narrative syntheses and five analytical cases. Highest information density per token.

**Batch 3 — the case corpus.**
`P1` → `P2`. The 47 case files with citations and verification verdicts.

**Batch 4 — quantitative substrate.**
`P5` → `P6` → `P7` → `P8`. Ingest only after Batch 1, or the normalisation rules in §4.3
will not be applied and raw counts will be misread as trends.

**Optional.** `S1` (volcano positions), `D3` (changelog — useful for provenance of a
specific finding), `C1` (method verification).

**Do not ingest:** `C2` (generated duplicates), `S4` (superseded), `S3` (map geometry).

### 6.5 Known ingestion hazards
1. `data/fireballs.json` events are **positional arrays**, not keyed objects. Without §2.1
   an ingester will misread the columns; `impact_e_kt` (index 2) is the analytic field, not
   `energy_1e10J` (index 1).
2. Raw counts in `P6` and `P7` are **not comparable across years**. Use `frac_m4` and the
   AMS share. See §4.3.
3. `_verify: "CORRECTED"` is the majority state and denotes *corrected and now accurate*,
   not *doubtful*.
4. `loeb_scale` is a third party's claim being tracked, not this project's assessment.
5. Prose in case files deliberately contains **both** a claim and its rebuttal. Extracting a
   sentence without its adjacent field will invert the meaning.
6. The transcript corpus is absent by design (§3.6); quoted excerpts are auto-caption
   derived and labelled as such.

---

*Generated 2026-08-23 from commit `5cc4511`. Unofficial and educational. Where a claim is
contested, both readings are given, including limits that cut against the project's own
conclusions.*
