# Changelog — 3I/ATLAS Anomaly Console

## v2.22 docs - 2026-11-04 (now tracking: the newest video and post, at the top of every page)

- **A "Now tracking" block** at the top of the README, the about page and the landing page names
  the newest Angry Astronaut video and Avi Loeb post built into the console, each a clickable
  link to the original, with links to the briefing and cases it went into. It is written from
  `data/tracking.json` by the new `tools/update_tracking.py`, which refuses a video whose
  transcript is not in the repo; CI fails if any page falls out of step.
- **README brought current:** the briefings and the v2.22 camera changes are described, the
  acceleration chart is no longer called an illustration (it has plotted real Horizons output
  since v2.19), refreshes are described as run by hand, the new tools are listed, counts are
  updated (77 timeline records, 9 briefings), and the em dashes are gone.
- **The transcript index** (`data/transcripts/README.md`) now lists all 119 videos to
  2026-11-01; it had stopped at 114 and 2026-08-23.

## v2.22 - 2026-11-04 (every camera takes the mouse, and a first-visit intro)

- **Drag and zoom work in every camera view.** CHASE, FROM MARS and FROM SUN used to lock the
  mouse out entirely, and CHASE is the view the console opens in, so a first visitor could not
  move anything and had no hint that the other views existed. Now a drag or a wheel in any of
  them hands the framing to the viewer: the camera keeps their angle and distance and carries it
  along with the object, re-centring on it so the drag orbits the object itself. Picking a camera
  again restores its scripted framing. A drag also ends a camera flight in progress instead of
  fighting it, and the scene shows a grab cursor.
- **The camera buttons now light the view you are actually in.** The page opened in CHASE with
  FREE highlighted. The highlight now follows the camera whoever moved it (boot, a case file, the
  tour, a target switch).
- **A one-card intro on a first visit**, along the lower third of the 3D view: what the replay
  shows, what the amber and cyan markers mean, and four ways in (drag and scroll, the cameras, the
  timeline, BRIEFINGS), with buttons for the 90-second tour, the full controls, or straight in.
  The replay keeps running behind it. It is remembered per browser, never shown over a shared
  deep link, closes with Esc, and on a phone sits between the overlay row and the camera row.

## v2.21 - 2026-11-02 (data refresh: five new fireballs, every figure re-derived)

Every upstream dataset pulled fresh, by hand, and every figure the case files quote re-derived
from it. No conclusion changed. Several numbers did, and the case text now says so.

- **CNEOS: 1,069 rows to 1,074**, latest 2026-10-04. One of the five new rows, 0.67 kt over
  northern Manitoba on 2026-09-11, falls in the regions F-04 discusses, so F-04 now counts FIVE
  rows there, not four. It is listed, not argued: it has not been matched to a public sighting.
  F-03's CNEOS line now runs 1 January to 4 October: 23 events against a 2016-2025 range of
  19 to 35.
- **GLM: 11,611 detections**, through 2026-10-06. The 2026 bright share is now x1.09 against
  the 2021-2025 mean (x1.13 on human-reviewed events only), against GMN's x1.07. F-03 used to
  say the two instruments agreed "to two decimal places"; they now land within two hundredths of
  each other, and the sentence says that instead.
- **GMN:** August re-pulled in full and September and October added. Q1 and January-to-July
  figures unchanged (x1.08, x1.07).
- **AMS:** the stats pages returned 503 again (the fourth time since October) while the rest of
  the AMS site was up. This release ships the 2026-09-01 AMS pull that the stranded automatic
  refresh made, the newest real AMS data that exists. F-03's Q1 share moves from 1.715% to 1.714%.
- **Spatial tests re-run on 888 located events.** Volcanoes: 23 vs 33.0 within 100 km, median
  844 vs 856 km, still no association; clustering 349 vs 356 km. Power reactors: 200 km excess
  now 34 vs 24.2, a 41% excess, p=0.033 scatter / 0.068 rotation, still a non-result. Wider
  nuclear set: 12 vs 6.0 within 100 km, p=0.008 and 0.015, slightly stronger. Its subsets were
  recomputed: the weapons complex alone is 3 vs 0.8, p=0.042 under rotation but 0.057 under
  scatter, so no single kind of site clears both nulls. F-07 and BR-08 still call it a weak
  signal. Their "one time in four" sentence now says what it means: with six tests, at least one
  clears p=0.05 by chance about one time in four.
- **Horizons:** ephemeris and counterfactual re-run; no close approach moved. The gap between
  3I's real path and its gravity-only twin is 126,661 km on 2026-11-02.
- **Layout, found while capturing the landing page:** at ordinary desktop widths the overlay
  toggles (five since GRAVITY-ONLY) ran over the camera buttons; each row now gets half the scene
  and wraps. The overlay banners sat on the disclaimer and now clear it. On narrow screens the
  camera row and the disclaimer collided; the disclaimer now has its own full-width strip at the
  bottom, with the camera row and the banners stacked above it. Checked at 1280, 884 and 412 px.
- **Tooling:** `fireball_rate_check.py --needles` prints every figure the check looks for, so a
  refresh can map old figures to new ones mechanically. `about.html` reads its fireball count
  from the data. The showcase landing page is current: nine briefings, 77 timeline records,
  1,074 fireballs, the changing-course release, Wikidata credited, and the refresh described as
  it now runs (by hand, as a pull request).

## v2.20 - 2026-11-01 (quality pass: correctness, phones, keyboards, speed, CI)

A review of the whole console turned up bugs that had been there since the early releases. None
of them changes a number; all of them change how it feels to use.

- **Correctness.** The boot could start the app twice (a double-click, or a key then a click
  inside the fade): two renderers, two frame loops, doubled audio. It now starts once. The replay
  no longer keeps running, with alert tones, behind a briefing, the fireball map, the archive or a
  shared link, and Space no longer starts it from a page you are reading. Lists that re-render on a
  timer (the next-event panel, the case log) no longer swallow clicks. Closing a case opened from a
  briefing returns to the briefing. Play at the end of the tape rewinds. L and G keep their buttons
  in step. LOCATE ON IMPACT MAP only appears where there is a catalog row to locate. The SYS clock
  keeps time while paused. DISPATCH reads its dates and distances from the computed close
  approaches instead of hard-coding them.
- **Phones.** The timeline decides tap versus drag when the finger lifts, not when it lands; at
  phone width the marker hit zones covered most of the track, so nearly every drag opened a record.
  Slide-over rails close on a selection or a tap outside them, and a case sheet now sits above
  them. The disclaimer stays visible at every width.
- **Keyboards and screen readers.** The console had no ARIA at all, and behind the boot
  screen it was still in the tab order. It is now inert until authentication, and every clickable
  row (case log, mission log, archive list, close approaches, redaction bars) is a focusable
  button that Enter or Space activates. Icon buttons are named, toggles report their state, the
  case sheet is a modal dialog that takes and returns focus, and toasts are announced. Faint text
  rises from 2.6:1 to 5:1 contrast. With reduced motion requested there is no autoplay, cameras
  cut instead of swooping, and transitions stop.
- **Speed.** The 3D scene no longer renders while it is covered (briefings, fireballs, archive) or
  in a hidden tab, and the audio suspends with the tab. Label placement reads the container size
  once per frame instead of fifteen times, the range line updates in place, the event list is
  built once per object, and the timeline canvas is only resized when its box changes.
- **Upkeep.** `build.py` writes the dev page's script list, which had fallen two files behind.
  Help and tour counts come from the data. Dead code removed. Em dashes swept from every piece of
  reader-facing text except verbatim quotations, and the build reports any that come back.
- **CI.** New `.github/workflows/check.yml` on every pull request and push: JavaScript parses,
  generated content matches its sources, the bundle rebuilds byte-identical, the offline file has
  zero external references, the fireball case text matches the data, and no spatial statistic is
  pinned at its cap.

## v2.19 - 2026-11-01 (is 3I/ATLAS changing course?)

A new paper, Krolikowska, Spada & Dones (arXiv:2610.38485, 28 Oct 2026), refits 3I's orbit from
observations made far from the Sun only, and the Angry Astronaut built a video on it the same week:
"3I Atlas changing course and speeding up!". This release answers the question in kilometres.

- **The push, computed rather than described.** New `tools/fetch_counterfactual.py` has JPL Horizons
  integrate 3I twice from its state on 2025-05-15: once with JPL's full-arc solution #54 and its
  non-gravitational push, once with the push switched off. Same planets, same Jupiter. On 2026-11-01
  the two are 126,306 km apart, 12.7 arcsec as seen from Earth (about fifty times the measurement
  noise), 18,400 km of it out of the orbital plane. The total velocity change is about 4.2 m/s, of
  which only 1.75 m/s is extra speed; the rest turned its direction. 97% of it was delivered by the
  Jupiter pass. By the end of July 2025 the gap was 824 km, below the noise, which is exactly why the
  paper finds the inbound data purely gravitational. The script refuses to run unless it first
  reproduces the shipped path (it does, to 8e-7 AU), and cross-checks against the paper's own
  gravity-only orbit.
- **3I is now pinned to JPL#54.** On 2026-10-21 Horizons switched C/2025 N1 to solution #55, a
  "temporary solution to support JWST Program 13145" fitted to 117 observations from October 2025 on,
  with the transverse term of the opposite sign. Re-running the old fetcher would have swapped the
  shipped path for it silently. `tools/jpl_solution.py` submits #54's own elements and push to
  Horizons as a user-defined object instead.
- **The acceleration chart was fake, and is now real.** It drew an "ASTROMETRIC RESIDUAL" ramp from
  `Math.random()`, different on every redraw, under A-10, A-24 and BR-01. It now plots the
  counterfactual, with perihelion, the Jupiter pass and the paper's two data arcs marked. A second
  new chart shows the activity laws the astrometry cannot tell apart.
- **GRAVITY-ONLY overlay in the tracker.** Draws the gravity-only twin, its gap exaggerated 2,000
  times so it can be seen at solar-system scale, and says so on the pod, the banner (with the true
  km and arcsec for the date on the clock) and the toast. VISUALIZE IN TRACKER on A-10 or A-24 turns
  it on. One shared reset also fixes the DISPATCH banner, which used to survive an era switch.
- **New briefing BR-09, "Is 3I/ATLAS changing course?"** The claim as made, credited where it is
  right (the push is real far from the Sun, partly out of plane, and its cause is unconstrained);
  where it stretches (the push did nearly all its work near the Sun; CO2 sublimates where water
  cannot; the video starts from JPL's first, superseded acceleration, about 37 times too large, and
  its force step slips by 1,000); the mass budget, which is tight but not broken; and "Where is Avi
  Loeb?", answered from all 56 of his posts in the window, including the test for steering he named
  on 17 October. A-10 and A-24 carry the paper.
- **Content current to 2026-11-01.** A research workflow covered 17 new 3I papers, Loeb's posts
  since August and five new videos, with an adversarial verifier per batch. 19 new timeline events,
  updates to 14 cases and F-07, 4 verbatim quotes, and 55 new claims mapped in `docs/claim-coverage.md`
  (no new case files). Full verified record: `data/research-2026q4.json`. The Loeb Scale stays at 3
  (his conditional March reduction), with the October paper's carried-forward 4 noted beside it.
- **F-07's wider nuclear target set.** New `tools/fetch_nuclear_wide.py`: 150 non-power sites from
  Wikidata (research reactors, waste stores, enrichment, reprocessing, test sites, and the weapons
  laboratories and missile bases the testimony names), behind a 150-site gate. Within 100 km: 12
  fireballs against 6.2 by chance, p=0.017 and 0.022, the register's first positional result to clear
  the bar under both nulls. Reported as a weak signal, not a finding: one of six tests, gone by
  200 km, and carried by no single kind of site.
- **Statistics fixes, each re-derived and checked.** `spatial_test.py`: the longitude shortcut was not
  a true lower bound at high latitude (now exact); the cap guard is saved to the JSON and fails the
  run only when it could move the median; empty target sets abort. The clustering statistic skipped
  every event that shared coordinates, which turned out to be hiding five CNEOS rows that appear
  twice (same position and clock time, days apart). Left in, they fake a cluster at p=0.006; removed,
  clustering is null (353 vs 357 km). F-03 to F-07 re-checked by `tools/fireball_rate_check.py`.
- **Content integrity.** `bake_content.py` ships every source (it kept four, dropping citations from
  23 cases), fails on unknown chart names and duplicate ids, and no longer rewrites research.json.
  Schematic charts are seeded and captioned as illustrations; cases that showed another object's
  picture show none.
- **Video Overview kit.** `dossier/briefings/BR-0n.md`: one source pack per briefing with a steering
  prompt. A briefing with a `video` link shows WATCH THE BRIEFING. Steps in `docs/NOTEBOOKLM-DOSSIER.md`.
- **Also:** ephemeris extended to 2027-12-31 so NOW keeps working; five new transcripts (YouTube
  rate-limits captions, so `tools/import_transcript.py` imports them from a captions API, and the
  fetcher now merges into its index instead of replacing it); deploy runs wrangler from `public/`
  so the landing page's `functions/` stops riding along; build metadata, landing page and README
  take counts from the data; every dataset credited, including WRI's CC BY licence.

## v2.18.1 — 2026-08-24 (quote attribution)

- **Cases F-03 to F-07 were attributing their quotes to Avi Loeb.** The dossier prefixed every
  quote with "— A. LOEB ·" regardless of who said it, so the Angry Astronaut's sentences and
  Cheryl Costa's relayed figures both went out under his name. This is the same bug
  `claim_label` fixed for the section caption in v2.16 — the caption was closed and the quote
  line was not. The prefix now appears only where `claim_label` is the default LOEB ASSESSMENT,
  so his cases keep the attribution and the four that are not his no longer claim it.
- The first attempt at the fix was also wrong: it tested whether `claim_label` exists, but
  `bake_content.py` defaults it to `"LOEB ASSESSMENT"`, so the condition was always true and
  F-01 lost the Loeb attribution it should have had. Checking all four case types in a browser
  caught it. Putting a real person's name on somebody else's sentence is the one class of error
  this project can least afford.

## v2.18 — 2026-08-24 (the fourth instrument, and the one that sees daylight)

F-03 has always carried its own strongest objection: the Global Meteor Network is where the
weight of its evidence sits, and GMN is NIGHT-BLIND, while several of 2026's most-discussed
events were daytime. That limit is now answered rather than merely stated.

- **New `tools/fetch_glm.py`** pulls NASA's Geostationary Lightning Mapper bolide catalog —
  11410 published detections, 2017-07 to 2026-08 — from the Asteroid Threat Assessment Project's
  automated pipeline. Aggregates only; the raw payload is 29.5 MB of NASA's catalog.
- **Finding the endpoint took a detour worth recording.** The published `/service/event/all`
  path returns `{"success":false,"error":{}}`, as does every other `/service/*` path including
  ones that cannot exist — a catch-all handler, not a wrong guess. The real public route is
  **`/service/event/public`**, extracted from the site's own JS bundle.
- **It sees daylight, and that is the whole point.** Solar elevation computed per event from
  its time and position: **47.3% of GLM's detections are daytime** (5396 day against 5364 night) —
  roughly the half of the population a ground camera network never sees.
- **The result corroborates GMN almost exactly.** Over the like-for-like window of 1 January
  to 15 August, GLM's bright-category share runs **3.00% in 2026 against a 2021-2025 mean of
  2.80%**, a factor of **1.07**, against year-to-year scatter of 2.03% to 4.38%. GMN's figure
  for its comparable window was 1.07. Two instruments on different physics, one blind to half
  the clock, agreeing to two decimals.
- **A trap in the catalog was found and walked around, not into.** On **2025-03-06** the pipeline began
  auto-publishing detections that had previously required human review, so 2025-26 hold a class
  of record earlier years do not. The intuitive fix — restrict to high-confidence events — makes
  it worse, because review lags, so filtering on confidence really filters on how recent an event
  is; that cut alone would have shown a spurious x0.65 collapse. Running the statistic with and
  without the auto-published events is the fix that works: **the bright SHARE survives (x1.07
  full vs x1.08 human-published only); the bright COUNT does not (x1.12 vs x0.71)**, because the
  volume of human-published events fell once auto-publishing took over. The case quotes the
  share and never the count, and says why.
- **GLM drifts where GMN does not**, and the case says so: its faint-category share climbs from
  29.9% in 2019 to 71.4% in 2025 as the pipeline improved at dim events, which depresses the
  bright fraction for free. GMN's stable median magnitude is what let that confound be ruled out
  there. So GLM corroborates GMN rather than standing alone. Coverage is the GOES field of view,
  not global.
- **F-03 rewritten from three instruments to four**, BR-02 gains two sections, and
  `docs/two-instrument-problem.md` becomes the four-instrument problem with an update note
  saying plainly what changed and why.
- **New `CH.glmDaylight` chart** — bright share per year with the day/night split of every
  detection underneath, which is the picture no other instrument in the register can draw.
  Charts 2021 onward only: 2017-2020 are pipeline ramp-up, not comparable, and including them
  squashed the years that are.
- `tools/fireball_rate_check.py` now re-derives the GLM figures too, regime split included.
- 49 cases, 8 briefings.

## v2.17 — 2026-08-24 (chase on boot, a labelled toast, and the DISPATCH overlay)

Three requests from Stewart, plus two limits added to F-07 that he was right to push on.

- **The console now opens in the chase camera**, riding the target, instead of the free
  orbit view. Only when nothing was deep-linked: a case file's viz hint sets its own camera
  and overriding it would throw away the framing the link was shared for.
- **The event toast says what it is.** A record crossing the playhead now carries a kind
  chip — `▲ ANOMALY` or `◆ MISSION EVENT` — above the title. Previously an amber box just
  appeared with a chime and no statement of what kind of thing it was. UI toasts (link
  copied, target switched) pass no kind and get no chip, so the label always means a record.
- **New DISPATCH overlay**, off by default. Draws the claim that 3I/ATLAS released material
  at its three close approaches — the Mars pass (2025-10-03), perihelion (2025-10-29) and
  the Jupiter pass (2026-03-17, which came within a fraction of a percent of Jupiter's
  ~53.5 million km Hill radius, where material can enter Jovian orbit cheaply). Particles
  stream from the object toward the body each burst is claimed to have been aimed at,
  sunward at perihelion where the claim is about the anti-tail rather than a planet.
  **It is labelled as speculation in three places** — an amber pod, a dashed banner reading
  "ILLUSTRATION OF A CLAIM, NOT AN OBSERVATION. NOTHING HAS BEEN SEEN LEAVING THIS OBJECT",
  and a toast when it is switched on. An unlabelled particle burst in a console full of real
  Horizons geometry would read as a measurement, which it very much is not.
- **F-07 gains the two limits that matter most**, both raised by Stewart. The energy floor:
  the catalog's smallest row is 0.048 kt and only 195 of 1069 fall below 0.1 kt, energies
  that take a metre-scale rock at tens of km/s — while the objects in this testimony are
  routinely described at beach-ball or motorcycle scale, which cannot register here at any
  distance from anything. Most of the phenomenon is excluded before the geometry is even
  considered, and no better public dataset exists to switch to. And the target scope: the
  association as usually stated is with radiation and fissile material generally — research
  reactors, enrichment and reprocessing, waste storage, industrial and medical sources — not
  weapons specifically. Only civil power reactors have an openly licensed global position
  list, so that is what was tested, and the case now says so.
- `tools/fireball_rate_check.py` checks the two new figures as well.

## v2.16 — 2026-08-24 (the nuclear-site test, and closing claim coverage)

The last untested positional claim in the fireball coverage is also the oldest one, and it
needed a different posture from the volcano test: the honest answer is mostly "this is the
wrong instrument", said before running anything rather than after.

- **New `tools/fetch_nuclear.py`** pulls 195 nuclear power reactor positions across 31
  countries from the WRI Global Power Plant Database (CC-BY 4.0). The IAEA's PRIS is the
  canonical register but publishes no machine-readable coordinates.
- **`tools/spatial_test.py` now takes `--target`.** The volcano path is unchanged and was
  regression-checked byte-for-byte against the shipped `spatial-test.json` after every
  edit — F-05 quotes those numbers verbatim and they could not be allowed to move.
- **The search cap is now per-target, and that was a real bug waiting to happen.** With
  only 195 reactors on Earth, most CNEOS events sit further than the old hard-coded 2,000 km
  cutoff, so the first nuclear run reported "median 2000 km observed vs 2000 km by chance,
  p=1.000" — a broken statistic dressed as a null result. Raised to 20,000 km for that
  target, and the report now warns when more than 2% of events sit at the cap. Histogram
  bins are per-target for the same reason.
- **The result: no proximity effect, with one honest exception that is reported rather than
  buried.** Within 100 km, 11 events against 8.8 expected. Within 500 km, 68 against 71.5 —
  below chance. Median distance 2682 km against 2687. But within 200 km there are 34 against
  24.8, a 37% excess reaching p=0.025 under the scatter null. It stays a non-result for two
  reasons: three radii were tested, and the SHAPE is wrong — absent at 100 km, present at
  200 km, gone at 500 km. A bump in the middle with nothing at the centre is not what an
  attraction looks like. Under the conservative rotation null it does not reach significance
  at all (p=0.070).
- **The selection effect turned up twice, independently.** F-05 explained the volcano footage
  by observatory sky-cameras; LaPaz was employed by the New Mexico installations and his
  observer network was their own staff, under standing orders to watch the sky. Same shape.
- **What the test explicitly does NOT do**, stated inside the case: CNEOS records airbursts,
  and the nuclear-connection testimony describes structured craft over silos. A null in a
  bolide catalog cannot refute Malmstrom, Rendlesham or the Hastings interviews. The catalog
  also begins in 1988, forty years after LaPaz's green fireballs, and civil power reactors
  are not the weapons complex he meant.
- **Case F-07, briefing BR-08**, and `CH.nuclearDist` — `CH.volcanoDist` generalised into a
  shared `CH.proximityDist` renderer rather than copied.
- **Claim coverage is closed.** Both remaining partials in `docs/claim-coverage.md` were
  resolved and they were different problems. Row 12 (Ni/CN) was a genuine gap INSIDE A-07 —
  the ratio was stated in the observation and argued in neither direction — now argued both
  ways, the counter-reading being that CN is the *denominator* and 3I is independently
  CO2-dominated with ~4% water, that Ni and CN are measured over different e-folding radii
  (593.7 vs 841 km), and that the extreme values live at 4.4-2.85 AU where Ni/Fe was also
  extreme before falling to normal. Row 17 (the ~20x water spike) was never a gap at all —
  A-20 carries it in both halves and the doc was stale. **No new case files for either**:
  splitting one set of spectra into extra cases is the tally inflation BR-01 warns about.
- **`tools/fireball_rate_check.py` now covers F-03 through F-07.** Verified it bites.
- 49 cases, 8 briefings.

## v2.15 — 2026-08-24 (the 2013 precedent)

The fireball coverage offers November 2013 as the historical rhyme for 2026: a wave of
fireball-shaped UFO reports, spotted by Cheryl Costa in the National UFO Reporting Center
database and written up in her New York Skies column. It is a checkable claim about a public
dataset, so it has been checked rather than repeated.

- **New `tools/fetch_nuforc.py`** pulls the NUFORC sighting archive and writes aggregates to
  `data/nuforc.json`. nuforc.org returns 403 to a datacenter address; the route that works is
  the planetsig/ufo-reports mirror, which geocoded and time-normalised the archive in 2014 and
  kept the SHAPE column — the field the claim is actually about. Aggregates only: the raw file
  is 14 MB of somebody else's report narrative, and what this needs is counts.
- **Costa's baseline figures check out almost exactly.** Fireball is 6,208 of 78,400
  shape-bearing reports — 7.92% — and ranks fourth of 29 shapes, against her remembered "about
  7%, fourth of roughly 30". The November elevation is real too: 33 fireballs in 226 US
  shape-bearing reports through the 11th, 14.6%, and her volume figure lands on the nose
  (227 US rows against "about 238").
- **What the month is measured against is where it comes apart, and the finding is bigger than
  the correction.** 7.92% is the average of a century-long archive. Annual fireball share ran
  4.85% in 2004 and 5.86% in 2009, then 8.56%, 10.72%, 14.54%, 13.97% across 2010-2013. Pool
  the twelve months before the one in question and the share is 14.33%; November 2013 came in
  at 14.37%. It was not a spike above the current baseline — it WAS the current baseline. It
  ranks 14th of all 172 complete months from January 2000 to April 2014; July 2012 holds the
  record at 22.26%.
- **The interesting thing is the tripling, and it is left standing.** The share of reports
  labelled fireball roughly tripled between 2009 and 2012 and stayed there. That is a large,
  real, unexplained change — exactly the kind of thing the column was reaching for. It found
  the right dataset and pointed at the wrong month, three years late. NUFORC cannot say whether
  the rise was the sky, the arrival of a camera in every pocket, or the word spreading through
  popular usage, and neither can this project.
- **Two limits are stated inside the case because they cut against the conclusion.** The
  archive is 81% United States: on 2013-02-15, the day of Chelyabinsk, it logged 11 reports,
  2 of them fireball, and February 2013 finished at 8.08% — among the quietest months of its
  year. The largest airburst since Tunguska is essentially absent from it. And the mirror
  stops on 2014-05-08, so the 2026 half of the parallel cannot be tested here at all.
- **The label does carry real signal**, which is worth saying plainly: fireball share peaks in
  July (10.94%) and December (10.11%) against 6.03% in April. That is the Perseids and the
  Geminids showing up in a database of public shape guesses.
- **Case F-06 and briefing BR-07**, with a chart that is the whole argument in one picture:
  the monthly share, the rolling 12-month baseline climbing under it, the flat all-time 7.9%
  line far below, and November 2013 marked sitting on the rolling line rather than above it.
- **New `claim_label` field.** Cases F-03 to F-06 test claims made by people other than Avi
  Loeb, and the dossier was captioning all of them "LOEB ASSESSMENT" — attributing arguments to
  someone who did not make them. Those four now read "THE CLAIM AS MADE"; everything else is
  unchanged.
- **`tools/fireball_rate_check.py` now covers F-03 through F-06**, including F-05's Monte Carlo
  figures, which had been going unchecked. Verified it bites: perturbing three numbers in the
  case text fails the run.
- **New `dossier/15-nuforc-sightings.md`** from `tools/export_tables.py`, with the shape-label
  caveat stated before any number.
- 48 cases, 7 briefings.

## v2.14 — 2026-08-23 (the volcano test)
The most distinctive recurring claim in the fireball coverage is positional — another fireball,
another volcano; three in the same place — and it had never been tested, despite both halves
being public. It has been now.

- **New `tools/fetch_volcanoes.py`** pulls 1,608 volcano positions from NOAA's National Centers
  for Environmental Information. The Smithsonian GVP is the source the field usually cites but
  it returns 403 to anything that is not a browser; NOAA is a primary source in its own right.
- **New `tools/spatial_test.py`** — Monte Carlo, 1,000 trials per null. Choosing the null IS the
  test: scattering random points over the globe would be wrong, because volcanoes sit on land
  and cluster in arcs, so any land or latitude bias in the detections would fake an association.
  Two nulls are used, both preserving the events' own latitude distribution — a ROTATION null
  applying one random longitude offset to every event at once (keeping internal clustering
  perfectly intact), and a SCATTER null redrawing each longitude.
- **Result: no association at any distance, under either null.** Within 100 km: 23 observed
  against 32.8 by chance. Within 200 km: 78 against 82.3. Within 500 km: 260 against 250.5.
  Median nearest volcano 838 km against 854 km. The closest bin — the one the claim is about —
  sits BELOW chance. Clustering fails the same way: median nearest-event distance 353 km
  against 354 km. The rotation null is deliberately not offered for clustering, because
  rotating every event by the same offset leaves every event-to-event distance untouched.
- **Case F-05 and briefing BR-06**, with a chart putting the observed distance histogram
  against the chance curve — two lines lying on each other says more than a p-value.
- **The explanation is in the coverage itself**: "Five Vulks cameras are rolling." PHIVOLCS
  keeps cameras on Mayon's sky around the clock, because that is what a volcano observatory is
  for. Active volcanoes are among the very few places on Earth with fixed cameras aimed upward
  continuously. CNEOS has no such effect, which is why it is the right instrument here.
- **The limit is stated inside the case**: neither headline 2026 volcano event has a CNEOS row,
  because both are below the 0.048 kt floor. The nearest CNEOS row to Mayon in the whole record
  is 312 km away and from 2015.
- 47 cases, 6 briefings.

## v2.13 — 2026-08-23 (BRIEFINGS — a way in)
The console was organised by object and case, which is how the DATA is shaped, not how anyone
arrives. People come with a question; 46 dossiers is a wall rather than a door, and the most
original work in the register — the three-instrument analysis — was reachable only by knowing
to look inside case F-03.

- **New BRIEFINGS mode.** Five question-led entry points: is 3I/ATLAS a comet, are fireballs
  actually increasing, has anything interstellar hit Earth, why is only one of the three
  visitors contested, and what can these datasets actually settle. Each states the question,
  answers it in a few hundred words, shows the one chart that carries the argument, and hands
  off to the case files that do the detailed work.
- **Built for reading, not scanning.** Everything else in the console is a HUD; this is a page,
  so it gets a 68ch measure, real leading, and body text sized for a few hundred words rather
  than for glowing labels.
- **Deep-linkable at `#brief/<id>`**, which is the point: a single finding can be sent to
  someone on its own, and that is how this material actually travels.
- **Narrow screens turn the rail into a strip of question chips** above the reading pane —
  a 190px sidebar beside a text column leaves neither usable at phone width. Verified at
  360x780, 412x940 and 884x1104 with no horizontal scroll.
- **The tab is amber, not a peer of the other modes**, and the guided tour now ends by pointing
  at it.
- **bake_content.py refuses to build if a briefing links to a case that does not exist.** A dead
  link in the one surface built for reading is worse than no link.
- Briefings are `BR-01`..`BR-05`: 2I's cases already use `B-01`..`B-05`, and two things sharing
  an id in the same UI is a bug waiting to happen even when the hash namespaces differ.
- Fixed along the way: `syncHash` was never exported, so the briefings module's hash updates
  were silently a no-op; and entering a briefing left any open case sheet sitting on top of it.

## v2.12 — 2026-08-23 (A-26, the last uncovered anomaly)
Reading his enumerated 24-anomaly list against the register found exactly one observational
claim with no case file behind it. It has one now.
- **A-26 — extreme methanol enrichment (CH3OH/HCN), ALMA.** Verified against the primary
  source: Roth, Cordiner et al., ApJL doi:10.3847/2041-8213/ae433b (arXiv:2511.20845).
  CH3OH/HCN of 124 (+30/-34) on 12 Sep 2025 and 79 (+11/-14) on 15 Sep — among the most
  methanol-enriched values measured in any comet.
- His account of the study is **accurate**, including both ratios and the comparison object.
  The case says so, then makes the counterpoint the paper itself supplies: the single comet
  that beats 3I/ATLAS on this measure, C/2016 R2 (PanSTARRS), formed in OUR solar system —
  so the ratio cannot mark an object as foreign, let alone engineered. Also that the value is
  a RATIO and rises just as well on scarce HCN as on abundant methanol; that the two figures
  overlap inside their own error bars, so quoting "70 to 120" reports scatter as a span; and
  that the extended methanol source beyond 258 km is icy grains acting as miniature comets,
  which is why it is enhanced sunward where grains are hottest while nucleus-sourced HCN is
  depleted there.
- 46 cases now (3I 26, 1I 11, 2I 5, fireballs 4).

## v2.11 — 2026-08-23 (three instruments)
v2.10 answered the fireball-rate question from CNEOS alone. That was the wrong instrument for
the claim people actually make, and F-03 argued against a version of it nobody was defending.

- **The claim, as actually made, is tested — and its figures are confirmed.** The argument is
  built on American Meteor Society eyewitness reports, not CNEOS, and it already anticipates
  the reporting-bias objection. Checked against AMS itself the numbers hold: Q1 2026 logged 25
  events in the 51-99 report band against a 2021-2025 mean of 11.8, and 16 above 100 reports
  against 8.8. F-03 now says so plainly before going any further.
- **The test that separates the two readings.** A growing audience gives each event more
  reports and pushes events upward through the bins, so a flat middle bin is the bias rather
  than evidence against it. The diagnostic is whether well-witnessed events outgrew the
  dataset — x1.21 against x1.23, they did not.
- **A third instrument.** `tools/fetch_gmn.py` streams 92 months of Global Meteor Network
  trajectories (100+ MB each, aggregated in flight, never stored) for absolute magnitudes
  measured by camera with nobody deciding what to report. Bright meteors per detection run
  0.286% in Q1 2026 against a 0.264% mean — x1.08, inside scatter three times wider. The
  sensitivity confound is ruled out rather than assumed: median absolute magnitude holds
  between -0.09 and +0.05 across 2021-2026.
- **Three limits stated inside the case, because they cut the other way.** GMN is night-blind
  and several 2026 events were daytime; its coverage is regional; its brightest bin is noisy.
  The conclusion is that the observation stands and the burden has moved, not that the claim
  is refuted.
- **F-04 — the two events the sensors caught.** Both marquee 2026 US events are rows the
  console already shipped, matching the reported sighting to the minute: Lake Erie at
  12:56:42 UTC = 8:56:42 a.m. EDT against a reported 8:57, and the Pacific Northwest bolide
  at 07:48:36 UTC = 12:48 a.m. PDT against a reported 12:48. Both are slow — 14.9 and
  12.2 km/s against IM1's 44.8 — so the speed chart carries the case. It also untangles the
  radiated-versus-total energy confusion behind "10 tons" versus 0.13 kt.
- **New chart** `CH.instruments`: every series divided by its own 2021-2025 baseline, so raw
  counts and corrected rates share one axis. The dashed lines climbing while the solid lines
  stay flat is the whole argument, with no commentary.
- **New pipelines.** `fetch_ams.py` (21 years of report-bin counts), `fetch_gmn.py`,
  `bake_instruments.py` (a 1.6 KB per-year summary instead of gigabytes), `three_instruments.py`,
  `match_claims.py`.
- **`fireball_rate_check.py` rewritten** to re-derive every figure F-03 and F-04 quote across
  all three datasets. It caught two of my own errors before they shipped: a station count taken
  from a monthly minimum, and a fabricated timestamp. Windows are whole months throughout —
  comparing a partial current month against full earlier ones biases the current year low, and
  that mistake is invisible in the output.
- **Docs:** `docs/two-instrument-problem.md` and `docs/claim-coverage.md`.

## v2.10 — 2026-08-23 (is the fireball rate rising?)
A recurring claim — NASA's own fireball data shows impacts climbing — is answerable from the
catalog the console already ships, so the register now answers it instead of leaving the
question hanging over a map of dots.
- **DETECTIONS PER YEAR chart** in the fireball stats rail, clickable through to the case.
  Two design choices carry the argument: the **≥ 1 kt subset is drawn inside each bar**,
  because a change in detection and release inflates faint events far more than bright ones,
  so a flat bright subset under a rising total means reporting rather than flux; and the
  pre-1994 years are **shaded as pre-record** rather than plotted as honest zeroes. The final
  year is hatched as partial so it cannot read as a decline.
- **Case F-03 — "Are fireballs actually increasing? The catalog answers."** Steps, not a
  slope: 1988-1993 average about one event a year, 1994 jumps to 13, and from 2000 the rate
  sits at 34.4 / 35.4 / 36.0 per year across the three decades. The ≥ 1 kt rate over the same
  span is 4.1 / 4.1 / 3.7, and ≥ 5 kt is 1.00 / 1.00 / 0.83 — flat while the total was
  supposedly climbing. Monthly: 2.95 (2000-2023) against 2.70 (2024 to date), slightly lower.
  Sourced to CNEOS's own caveats and to Brown et al. (Nature 420, 294, 2002), whose 8.5-year
  flux study places the usable record's start right at the 1994 step.
- **`tools/fireball_rate_check.py`** re-derives every figure F-03 quotes and exits non-zero on
  drift. The monthly refresh workflow runs it and, if the numbers move, says so in the PR body
  — the one case file argued from computed numbers cannot silently go stale.
- F-03's claim block states the proposition rather than attributing it to a named person: the
  claim was tested as commonly stated, not any one person's version of it.

## v2.9 — 2026-08-22 (the timeline becomes readable)
Timeline entries were the only researched content in the console with no way to read them.
Clicking an **anomaly** marker had always opened its full case file; clicking a **mission**
marker flashed a toast with 110 characters of a description that averages 456, and
`bake_content.py` threw the citations away entirely. Roughly 26,000 characters of
fact-checked prose, and all 58 sets of sources, were shipped in the bundle and unreachable.
- **Timeline records.** A mission marker now opens the same sheet a case file does — cyan
  where the dossier is amber, with a kind chip (DISCOVERY / OBSERVATION / CLOSE APPROACH /
  STATEMENT / STATUS), the description in full, **clickable citations**, PREV/NEXT through
  the era, and COPY LINK.
- **Citations kept at bake.** `map_events` no longer strips `sources`, and gives every entry
  a date-derived id (`E-YYYYMMDD`) so a deep link survives events being inserted earlier —
  which happens every time the register is brought current. Same-day entries get a suffix.
  All 58 entries carry 1–4 sources. The anomaly dossier and the record share one citation row.
- **Deep links** extend to records: `#1i/E-20181026`.
- **MISSION LOG tab** in the left rail, beside CASE FILES. Not decoration: **24% of records
  fall outside their era's scrubber window** — 1I's story runs to 2026 while its ephemeris
  stops in 2018, stranding 9 of its 16 entries — so a marker is not a reliable way in. The
  tab shares the search box and searches all three objects, badging foreign hits.
- **Marker hit-testing is row-aware.** The two kinds are drawn in separate rows, above and
  below the baseline, but the hit test only ever compared X. At phone width, where markers
  sit ~10px apart, the rows competed for every tap and scrubbing by tap became impossible.
  The pointer's side of the baseline now decides which row it can hit. Settled model:
  **drag = time, tap = record.**
- The "NEXT EVENT" panel in the right rail opens that record, and the toast says where the
  rest of the text lives.

## v2.8 — 2026-08-22 (content current to within four days)
The timeline stopped at 2026-07-17. An arXiv sweep found four papers published since, all
added as sourced timeline events — the register now runs to **2026-08-18**.
- **2026-06-30 — Kakharov & Loeb, panspermia** (arXiv:2607.00202). Natural panspermia
  plausible; **directed** panspermia ruled out on energy grounds — a 60 km/s impact releases
  1.8×10⁹ J/kg, hundreds of times the specific energy of TNT, destroying any capsule. Worth
  logging because it is Loeb publishing a negative result on a deliberate-technology scenario.
- **2026-07-02 — FAST radio search** (arXiv:2607.01666). No credible periodic artificial
  signal above 0.146 W. The second independent radio null after the Allen Telescope Array,
  and it covers a signal type the first did not.
- **2026-07-09 — JUICE/MAJIS, peer-reviewed** (arXiv:2607.08603). The April ESA press release
  arrives as a paper: H₂O fell 8→4×10²⁸ s⁻¹ across 2–25 Nov 2025, CO₂/H₂O steady near 10%,
  activity solar-heating controlled with CO₂ dominant, plus tentative aliphatic C–H organics
  at 3.2–3.6 µm.
- **2026-08-18 — Santana-Ros et al. inbound campaign** (arXiv:2608.18371). Carbon-chain
  depleted with CN the only prominent emission, and **a persistent sunward jet at PA ≈ 280°**
  attributed to a fixed high-latitude active region — independent confirmation that the
  feature behind case A-05 is real, long-lived, and mundane in origin.
- The 2026-07-17 entry no longer calls itself "current status"; the object's Loeb-scale panel
  now states the date the timeline runs to, so staleness is visible rather than implied.

## v2.7 — 2026-08-22 (the quotes get held to the same standard as the cases)
Went to close the three fact-check gaps CLAUDE.md had recorded and found **the note was
stale** — `timelineVerify`, `comparisonVerify` and A-24's verdict are all present and
CORRECTED, and all 25 cases carry a verdict. The real gap was one nobody had logged:
**`quotesVerify` was absent from both research payloads.** All 35 quotes — direct
statements attributed to named people and institutions, on a page headed ON THE RECORD —
had never been dataset-verified.
- **9 verified character-for-character** against the primary source: Bialy & Loeb
  (arXiv:1810.11490 full text), the ISSI *Natural History of 'Oumuamua* (arXiv:1907.01910),
  Hibberd/Crowl/Loeb (arXiv:2507.12213), ESO releases eso1737 and eso2106, and the
  University of Maryland ISSI release.
- **2 corrected.** The Bialy & Loeb lightsail line had quietly regularised the paper's own
  phrasing — the paper reads "as **a** debris from an advanced technological equipment".
  The Robert Weryk CBC quote was truncated five words early and closed with a period,
  dropping "and looking in that direction"; its date was also six days off (2018-11-06 →
  2018-11-12, the CBC publication date).
- **1 paraphrase**, already labelled, now formally marked.
- **23 SECONDARY** — Medium, X, paywalled news, a print book, a translated Russian
  interview. Their primary text is not publicly fetchable, so they are marked as such
  rather than presented as verified. Being honest about that is the point.
- The **quote board now shows a status chip on every statement**, the way every case file
  already did, plus a header line stating how many were matched to source. Per-quote
  `verify` flows through `bake_content.py` into the bundle.

## v2.6 — 2026-08-22 (touch)
The console was desktop-only in a way that was invisible from a desktop. Two of its
primary interactions listened for mouse events, and a finger never emits those.
- **Timeline scrubbing works on touch.** The scrubber moved from `mousedown`/`mousemove`/
  `mouseup` to Pointer Events with `setPointerCapture`, so a drag survives the finger
  sliding off the track. Marker tapping gets a 15px catch radius on touch versus 6px for a
  cursor. `touch-action: none` on the track stops the browser claiming the gesture.
- **The fireball map responds to taps.** `pointerdown` selects (mouse, finger or stylus);
  hover stays a mouse-and-stylus behaviour since a finger has none. Touch hit radius 20px.
  The handler deliberately does not `preventDefault`, so scrolling the page still works.
- **The narrow-screen top bar was clipping its own controls** — FIREBALLS, ARCHIVE, help,
  audio and the rail toggles all sat past the right edge and were simply unreachable on a
  phone. The bar now wraps, the five mode tabs get their own scrollable row, and the row
  count is whatever the device needs: `.cx-root` uses `auto 1fr auto` and ui.js publishes
  the measured heights as `--topH` / `--botH` so the slide-over rails land between them.
- **Touch targets under `@media (pointer: coarse)`**: tabs, pods, transport buttons, list
  rows and the close button all reach ~44px. Mouse layouts are untouched.
- The boot gate says "TAP OR PRESS ANY KEY" and its skip line is now tappable — it read
  "PRESS ESC" on a device with no ESC key.
- `COMPARE 1I·2I·3I` shortens to `COMPARE` on narrow screens; the CRT toggle is dropped
  there (decoration, and the width is worth more).
- Verified in Chromium under touch emulation at 412×940 and 884×1104 (Fold cover and inner):
  drag, tap, every control on-screen, no target under 32px, no console errors — plus a
  desktop pass confirming mouse drag, drag release and marker clicks are unchanged.

## v2.5 — 2026-08-22 (the fireball register)
- **New FIREBALLS mode** (tab, or key `4` — ARCHIVE moves to `5`): a world map of the NASA/JPL
  **CNEOS fireball catalog**. 1,069 rows since 1988-04-15, 883 with a reported position, plotted
  equirectangular with circle area scaling to impact energy — Chelyabinsk (441 kt) down to
  sub-kiloton flashes. Filter by energy tier or decade, restrict to rows that report a speed,
  hover any dot for its full row, click for a selection reticle.
- **Two new case files, F-01 and F-02**, for Loeb's interstellar-meteor candidates **IM1**
  (CNEOS 2014-01-08, off Manus Island) and **IM2** (2017-03-09, west of Portugal) — same
  both-sides format as the other 41: Siraj & Loeb's unbound reconstruction, the USSC memo and
  the material-strength argument, against Brown & Borovička's 10–15 km/s velocity uncertainties,
  Hajduková et al. on the missing error bars, the coal-ash reading of the spherules, the
  Fernando et al. seismometer/truck result and Loeb's reply, and Socas-Navarro's 94.1%.
  Fact-checked against primary sources on 2026-08-22.
- **Real-data dossier chart** (`speed-dist`): the catalog's reported speeds binned, IM1 and IM2
  marked, with the USG velocity-error band drawn behind them — the claim and its rebuttal in one
  picture. Not a stylized illustration; it plots the shipped rows.
- **New pipeline** `tools/fetch_fireballs.py` → `data/fireballs.json`, `data/world-land.json`,
  baked to `src/data-fireballs.js` (94 KB). Coastlines are Natural Earth 1:110m land (public
  domain) simplified to ~2,200 vertices. The IM1/IM2 rows are tagged **by date**, never
  transcribed, so a CNEOS revision propagates on the next pull.
- `data/fireball-cases.json` is the hand-authored case source; `tools/bake_content.py` merges it
  in under object key `fb`. `src/data-content.js` stays generated.
- Cross-object search now also indexes `loeb_quote`, so searching *interstellar meteors* finds
  F-02 (the phrase lives in the quoted abstract).
- Deep links extend to the register: `#fb/F-01`, `#fb/F-02`, `#3i/fireballs`. The hash prefix now
  follows the open case's object rather than the active era.
- Guided tour gains a ninth beat on the impact map; help panel, boot sequence, README and the
  landing page updated. Offline `_LATEST` build verified at **zero external references**.

## v2.4 — 2026-07-26 (documentation + landing page)
- **Project landing page** at `/about` (`src/about.html` → `public/about.html` via build.py,
  font inlined, `__SITE__` resolved for absolute OG tags). Hero, stat strip, the premise,
  a captioned screenshot gallery, feature grid, and a data-provenance table.
- **README rewritten** as a proper front page: badges, hero screenshot, the three-object
  table, captioned screenshots of every key view, keyboard reference, deep-link examples,
  data provenance, and a source-tree map.
- **Seven captured screenshots** in `public/shots/` (1600×900, palette-optimised; hero kept
  at full colour). 2.5 MB → 1.2 MB. Lazy-loaded below the fold on the landing page.
- Three layout bugs the screenshots exposed, now fixed:
  - the footer disclaimer was `position:fixed` and spanned the full viewport, overlapping
    the right rail's text — it now lives inside the centre pane and is bounded by it;
  - camera/view pods bled through the document reader in ARCHIVE mode — the root now
    carries `data-mode` and they're hidden there;
  - the compare table and document reader were semi-transparent, letting the disclaimer
    ghost through — both are now opaque.

## v2.3 — 2026-07-26 (the four polish features)
- **Deep links.** URL hash `#<era>[/<case>|/<mode>]` — e.g. `#3i/A-05`, `#1i/compare`, `#2i`.
  Loading one jumps straight to that object and opens that case file; the hash updates as you
  navigate; back/forward work. Every dossier gains a **⧉ COPY LINK** button.
- **Guided tour** (`T`, the ▶ button, or from the help panel). Eight ~11-second beats across
  all three objects: discovery → Mars flyby → perihelion behind the Sun → the sunward
  anti-tail → 1I's tail-less arrival → its acceleration case → 2I as the control → all three
  paths in compare. Steps find their case files by keyword, so they survive case renumbering.
  Progress bar, SKIP AHEAD, and ESC to exit.
- **Cross-object case search.** The anomaly log gains a search box that queries all 41 cases
  across all three objects at once — searching "nickel" returns 3I's A-07 anomaly *and* 2I's
  B-02 control-case rebuttal, badged by object; clicking a foreign result switches target and
  opens it. Query survives era switches.
- **Analytics support.** `ANALYTICS_TOKEN` / `CF_ANALYTICS_TOKEN` in `tools/build.py` injects
  a cookieless Cloudflare Web Analytics beacon — into `public/index.html` **only**, so the
  offline `_LATEST` file keeps zero external references (verified: 0 in both files today).
- Help panel rewritten around the tour and search; first-run toast now points at `T` and `?`.
- **Cloudflare Web Analytics enabled** via the Pages dashboard toggle (edge-injected beacon,
  cookieless) — `ANALYTICS_TOKEN` stays empty so nothing double-counts.
- **CI/CD live**: `CLOUDFLARE_API_TOKEN` secret set; a push to `main` now rebuilds and
  auto-deploys. Verified end to end (workflow run 30188185642, Deploy → success).

## v2.2.1 — 2026-07-26 (published)
- **Live at https://3i-atlas-anomaly-console.pages.dev** (Cloudflare Pages, Direct Upload
  project deployed via wrangler). Verified against the live URL: v2.2 loads, 41 case files,
  three eras, security headers applied, og-image serving, zero console errors.
- **Source published** at https://github.com/Samizdat-Publications/3i-atlas-anomaly-console
  (public, MIT). git history now replaces `_Archive (old versions)/`, which is gitignored.
- `SITE_URL` in `tools/build.py` set to the deployed origin so OpenGraph/Twitter cards
  resolve an absolute image URL.
- `.github/workflows/deploy.yml` rebuilds from source, refuses to ship a stale bundle, and
  **skips the deploy step with a notice when `CLOUDFLARE_API_TOKEN` is absent or malformed**
  rather than failing the run — so the Actions tab stays green until the secret is added.
- Untracked `.wrangler/` local build cache (no credentials in it; token lives outside the repo).

## v2.2 — 2026-07-26 (publish pass)
- **In-app help** (`?` key or the top-bar button): full control legend, a plain-English
  briefing on how to read the case files, a "start here" tour, and the disclaimer.
  Public visitors had no way to discover the keyboard shortcuts before this.
- **Mobile/tablet layout**: below 900px the side rails become slide-over panels with
  top-bar toggles instead of vanishing; transport bar wraps; archive goes single-column.
  Verified at 375x812 with no horizontal overflow.
- **`prefers-reduced-motion`** honored — CRT flicker, pulsing alerts and panel transitions
  stop for visitors who ask for reduced motion.
- **Shareable on the open web**: description/OpenGraph/Twitter meta, theme-color, an inline
  SVG favicon, and `public/og-image.png` — a 1200x630 social card rendered from the real
  trajectory data by `tools/make_og_image.py`.
- **Build now emits `public/index.html`** (URL-friendly, Cloudflare Pages-ready) alongside
  the local `_LATEST ...html`.
- Repo scaffolding for publication: `README.md`, `LICENSE` (MIT + bundled-dependency and
  quoted-material notes), `.gitignore`; git history replaces the archive folder's role.

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
