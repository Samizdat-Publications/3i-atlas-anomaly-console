# The Two-Instrument Problem

**Why the "2026 fireball surge" can't be settled with the data that exists — and why
that's a measurable fact about the instruments, not a rhetorical dodge.**

Compiled 2026-08-23. Every number here is reproducible from the two public sources
listed at the end.

---

## The claim

Through 2026 a widely-repeated argument holds that fireball activity has surged, and
that the surge is not merely an artifact of more people looking up. The sharpest
version of it — the one worth engaging, because it already anticipates the obvious
objection — runs roughly:

> In the first quarter alone, events with 50 or more reports more than doubled the
> recent average, and events with 100-plus reports also roughly doubled. The signal
> wasn't just more people looking up — the larger, brighter events themselves increased.

That is a specific, checkable proposition. It checks out as stated, and it still
cannot be used to conclude what it's used to conclude. Both halves of that sentence
matter.

---

## The two instruments

Only two datasets cover this question at global scale, and they are built on
completely different physics.

| | **AMS / IMO** | **NASA JPL CNEOS** |
|---|---|---|
| What it records | Human eyewitness reports filed to a website | US Government sensor detections |
| Unit of measurement | *number of people who reported it* | radiated energy (J) and total impact energy (kt TNT) |
| Sensitive to audience size | **Yes, structurally** | **No** |
| Detects small events | Yes — anything bright enough to notice | **No — hard floor around 0.05 kt** |
| Coverage | Where people and phones are | Global, day and night, ocean included |
| Published uncertainties | n/a | **None. CNEOS publishes no error bars at all.** |

Neither is a census. AMS is a record of *attention*. CNEOS is a record of *detections
the sensors made and the agency chose to release* — its own documentation says "not
all fireballs are reported" and that the data "should be used with appropriate caution."

---

## What AMS shows

Events per report-count bin, Q1 2026 against the 2021–2025 Q1 mean:

| Report bin | 2026 Q1 | 5-yr mean | ratio |
|---|---|---|---|
| 1 report only | 1602 | 1283.0 | ×1.25 |
| 2–10 | 658 | 552.8 | ×1.19 |
| 11–25 | 63 | 65.4 | **×0.96** |
| 26–50 | 27 | 22.4 | ×1.21 |
| 51–99 | 25 | 11.8 | **×2.12** |
| 100+ | 16 | 8.8 | **×1.82** |

The quoted claim is **accurate**. Events with 50+ reports did roughly double; 100+
did too. Anyone checking the top two rows will find exactly what was described.

At first glance this also looks like it beats the reporting-bias objection: if the
cause were simply more people filing reports, you would expect every bin to rise
together — and the 11–25 bin is *flat*. A growing audience, the argument goes,
doesn't skip the middle.

**That reasoning is wrong, and the data shows why.**

---

## The redistribution test

A growing audience does two things at once. It surfaces more events *and* it gives
each individual event more reports — which pushes events **upward through the bins**.
An event that would have drawn 20 reports in 2022 draws 45 in 2026 and moves from the
11–25 bin into 26–50. The middle bin is simultaneously refilled from below and drained
from above, and can easily come out flat while the top bins swell.

So the diagnostic is not "did the top bins rise" — it's **did the population of
substantially-reported events grow faster than the population as a whole.**

| Window | All events | Events with ≥11 reports |
|---|---|---|
| Q1 2026 vs 2021–25 | **×1.23** | **×1.21** |
| Jan–Aug 2026 vs 2021–25 | **×1.43** | **×1.45** |

They match, in both windows, to within noise. The number of well-witnessed events grew
at *exactly* the rate the whole dataset grew.

And inside that population, the distribution slid upward — which is the signature of
more reports per event:

| Share of the ≥11-report population | 2021–25 | 2026 Q1 |
|---|---|---|
| 11–25 reports | 60.3% | **48.1%** |
| 26–50 reports | 20.7% | 20.6% |
| 51–99 reports | 10.9% | **19.1%** |
| 100+ reports | 8.1% | **12.2%** |

Same number of events relative to baseline, shifted rightward. That is what an audience
effect looks like. It is *also* what a genuine increase in brightness would look like.
**AMS cannot tell these apart, because its unit of measurement is people, not photons.**

This does not make the claim false. It makes it **undetermined by this dataset**.

---

## What CNEOS shows

CNEOS measures energy directly, so audience size is irrelevant to it. Like-for-like,
1 January to 15 August each year:

| Year | events | ≥1 kt |
|---|---|---|
| 2016 | 24 | 4 |
| 2017 | 18 | 3 |
| 2018 | 23 | 3 |
| 2019 | 23 | 4 |
| 2020 | 26 | 0 |
| 2021 | 19 | 1 |
| 2022 | 31 | 6 |
| 2023 | 23 | 5 |
| 2024 | 18 | 3 |
| 2025 | 24 | 3 |
| **2026** | **18** | **1** |

2026 sits at the bottom of an ordinary range. No surge. If anything it is a quiet year
at the top end.

**But this is where it stops being an answer.**

---

## The floor

The CNEOS catalog contains 1,069 rows spanning 1988-04-15 to 2026-08-15. Its energy
distribution has a hard bottom:

- **minimum energy in the entire catalog: 0.048 kt**
- 5th percentile: 0.078 kt
- median: 0.200 kt
- **only 6 rows out of 1,069 fall below 0.073 kt**

For scale: 0.05 kt is 50 tons of TNT equivalent. Essentially every event driving the
AMS excess is *far* below that. The August 2026 Pacific Northwest bolide — one of the
most-reported events of the year, 250+ AMS reports, security-camera footage,
infrasound picked up by Cascade volcano sensors — is **0.13 kt**, and that is one of
the *larger* ones. Most spectacular eyewitness fireballs never come close.

So CNEOS showing nothing unusual in 2026 is not evidence that nothing happened. **The
sensors are structurally blind to the size class under discussion.** Asking CNEOS about
a 0.01 kt fireball wave is like asking a seismograph about footsteps.

---

## What each side can and cannot honestly claim

**A skeptic cannot say:** "The government sensors see no increase, so there isn't one."
The sensors cannot see the events in question at all. Their silence carries no
information about that size range.

**A proponent cannot say:** "The data confirms a real surge in bright events." The one
instrument that measures absolute energy shows nothing unusual, and the instrument that
does show a rise measures human attention — which demonstrably rose at the same rate.

**Both of these are load-bearing.** The argument is not "we don't know, so anything
goes," and it is not "absence of evidence settles it." It is that the question falls
into a **measurement gap between two instruments**, and that gap is quantifiable:
roughly 0.001 kt to 0.05 kt, where eyewitnesses see everything and sensors see nothing.

The honest position is that the 2026 excess in AMS data is **real as an observation and
unresolved as a physical claim.**

---

## What settles it — and the answer

A third instrument that measures brightness objectively and doesn't depend on
anyone filing a report. The **Global Meteor Network** is exactly that: an open
camera network publishing trajectories with **absolute magnitudes**, no human in
the loop deciding what counts.

**This has now been run.** 92 months, 2019–2026, streamed and aggregated
(`tools/fetch_gmn.py`, `data/gmn-monthly.json`).

GMN carries its own severe bias — the network grew from 73 stations to 1,327, so
raw counts are meaningless across years. The bias-resistant statistic is the
**bright-meteor fraction**: meteors at absolute magnitude ≤ −4 as a share of all
detections. More cameras multiply faint and bright detections together, so the
ratio holds; a real excess of bright meteors moves it.

| Year (Jan–Aug) | meteors | mag ≤ −4 | **bright fraction** | stations |
|---|---|---|---|---|
| 2021 | 95,687 | 419 | 0.438% | 341 |
| 2022 | 172,637 | 987 | 0.572% | 571 |
| 2023 | 227,045 | 922 | 0.406% | 899 |
| 2024 | 406,629 | 1,654 | 0.407% | 1,023 |
| 2025 | 566,412 | 1,856 | 0.328% | 1,327 |
| **2026** | **540,305** | **2,372** | **0.439%** | 1,251 |

**2026 vs the 2021–2025 mean: ×1.02.** Flat.

Restricted to Q1, the quarter the claim is actually about: **0.286% against a
0.264% mean — ×1.08**, against year-to-year scatter running 0.131%–0.440%. Also
flat. At the very brightest level GMN records, magnitude ≤ −6, 2026 is *below* the
baseline median.

Set against the raw counts from the same window, the picture is unambiguous:

| | 2026 vs 5-yr mean |
|---|---|
| GMN meteors detected (raw) | ×1.84 |
| GMN stations reporting | ×1.58 |
| AMS events with ≥51 reports (raw) | ×1.71 |
| AMS events, all (raw) | ×1.43 |
| **AMS ≥51 as a share of all events** | **×1.19** |
| **GMN bright-meteor fraction** | **×1.02** |
| **CNEOS events ≥1 kt** | **×0.26** (1 event vs a mean of 3.8) |

Everything that grew is a count of instruments or of people. Every measure that
normalises for them is flat.

### The sensitivity-drift check

One way this could be wrong: if cameras improved, GMN would detect fainter
meteors, inflating the denominator and *masking* a real rise. Testable — the
median absolute magnitude would drift fainter.

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| +0.05 | −0.07 | −0.09 | −0.04 | −0.01 | −0.04 |

Stable to within a tenth of a magnitude across six years. The confound does not
apply, and the fractions are comparable.

### Where GMN cannot help

Three limits, stated because they cut toward the claim rather than against it:

1. **GMN is night-only.** Cameras see nothing in daylight. Several of the most
   prominent 2026 events were daytime — the Lake Erie bolide at 8:57 a.m. Eastern
   drew 222 reports across 16 states. GMN is structurally incapable of counting
   those, and no fraction computed from it says anything about them.
2. **Coverage is concentrated**, not global — heavily Europe and North America,
   with the network's footprint shifting year to year as stations join.
3. **The magnitude ≤ −6 counts are small and noisy** — 2022 is a six-fold outlier
   over its neighbours. Read the ≤ −4 line as the reliable one.

### Where that leaves the claim

The observation is real and correctly stated: AMS high-report events did roughly
double in Q1 2026. Three independent lines now say that this reflects **attention
rather than sky**: the well-reported population grew at exactly the rate of the
dataset as a whole, the CNEOS energy record shows a quiet year, and the one
instrument that measures brightness directly shows no excess at either brightness
threshold, with its own principal confound ruled out.

That is not proof of a negative, and the daytime blind spot is a real gap. But the
burden has moved: anyone maintaining that 2026 saw more bright meteors now has to
explain why the cameras that measure brightness did not record it.

## Sources

- **NASA JPL CNEOS Fireball data** — <https://cneos.jpl.nasa.gov/fireballs/>
  API documentation: <https://ssd-api.jpl.nasa.gov/doc/fireball.html>
- **AMS / IMO fireball statistics** (per-month counts by report bin, 2006–2026) —
  <https://fireball.amsmeteors.org/members/imo_fireball_stats/events_per_month_per_year>
- **Global Meteor Network** trajectory summaries —
  <https://globalmeteornetwork.org/data/traj_summary_data/>
- Brown, P. et al., "The flux of small near-Earth objects colliding with the Earth,"
  *Nature* **420**, 294–296 (2002) — measures the small-impactor flux from this same
  class of sensor data, and places the usable satellite record's start around 1994.

### Reproducing the numbers

The AMS figures are parsed from the `all_series[YEAR]` JavaScript arrays embedded in
the stats page above; the CNEOS figures come from the full API pull kept in
`data/fireballs.json` in this repository.

---

*Prepared as background for the 3I/ATLAS Anomaly Review Console
(<https://3i-atlas-anomaly-console.pages.dev>). Unofficial and educational. Where a
claim is contested, both readings are given.*
