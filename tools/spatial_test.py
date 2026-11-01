"""Do CNEOS fireballs fall closer to volcanoes — or to nuclear sites — than chance allows?

The fireball coverage keeps returning to position: another fireball, another
volcano; three in the same place; were these manufactured in the same place. That
is a testable claim, not just an arguable one, because the console already ships
883 located CNEOS events with coordinates and NOAA publishes 1,608 volcano
locations.

    python tools/spatial_test.py                     # volcanoes (the default)
    python tools/spatial_test.py --target nuclear    # nuclear power reactors
    python tools/spatial_test.py --trials 2000       # tighter p-values, slower
    python tools/spatial_test.py --json              # machine-readable

THE NUCLEAR TARGET ANSWERS A DIFFERENT AND OLDER CLAIM, and the instrument fits
it far less well. The association between unusual aerial phenomena and nuclear
installations rests on WITNESS TESTIMONY AT GUARDED SITES — LaPaz's 1948-51 green
fireballs over the New Mexico weapons complex, and the later missile-site reports
— not on satellite-detected bolides. CNEOS begins in 1988 and records airbursts,
so a null result here does NOT refute that testimony; the two are not describing
the same kind of event. What the test can establish is narrower and still worth
having: whether the population of objects large enough for satellites to see
shows any positional preference for nuclear sites. Say that, do not overclaim it.

WHY CNEOS IS THE RIGHT INSTRUMENT FOR THIS ONE. The visual evidence for the
volcano claim is webcam footage, and volcanoes are among the most continuously
camera-monitored places on Earth — an active volcano has cameras pointed at its
sky twenty-four hours a day, which is exactly the setup needed to catch a
fireball on video. That is a selection effect large enough to manufacture the
entire pattern. CNEOS does not have it: its detections come from satellite
sensors that do not care whether anyone is filming. So if the association is
physical it should appear here, and if it appears ONLY in webcam footage the
cameras are the more likely explanation.

THE NULL MODEL IS THE WHOLE TEST. Comparing against uniformly scattered random
points would be wrong: volcanoes sit on land and cluster in arcs, so any
land or latitude bias in the detections would fake an association. Two nulls are
used instead, both of which preserve the detections' own latitude distribution:

  ROTATION   one random longitude offset applied to every event at once. Keeps
             the event set's internal clustering perfectly intact and destroys
             only its alignment with volcano longitudes. The conservative null.
  SCATTER    each event keeps its latitude and draws a fresh uniform longitude.
             Destroys internal clustering too.

If the observed statistic is unremarkable against both, there is nothing here.
"""
import argparse, json, math, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R_EARTH = 6371.0088
RADII = (100.0, 200.0, 500.0)
BAND = 2.0                      # degrees of latitude per index bucket
SEED = 20260823                 # fixed: the same run twice must agree

# Each target names its dataset, the key its rows live under, and the subset used
# as the "was anyone watching / was it even there" control. Adding a target must
# never change the default one: F-05 quotes the volcano numbers verbatim.
TARGETS = {
    "volcanoes": {
        "file": "volcanoes.json", "key": "volcanoes", "label": "volcano",
        "provider": "NOAA", "out": "spatial-test.json",
        "control_label": "historically dated (i.e. watched) volcanoes only",
        "cluster": True,
        # 1,608 volcanoes are dense enough that almost nothing is 2,000 km from one.
        "cap": 2000.0, "trials": 1000, "hist_max": 2000, "hist_bin": 100,
    },
    "nuclear": {
        "file": "nuclear.json", "key": "sites", "label": "nuclear site",
        "provider": "WRI", "out": "spatial-test-nuclear.json",
        # A reactor commissioned after the events cannot have attracted them.
        "control_label": "reactors commissioned by 1990 only",
        "cluster": False,       # event-to-event clustering is target-independent;
                                # it is already answered under the volcano run.
        # THE CAP IS NOT COSMETIC. There are only 195 reactors on Earth and most
        # CNEOS events are thousands of km from the nearest one, so a 2,000 km
        # search cutoff pins the median AT the cutoff in every column and
        # manufactures a fake "observed 2000 vs chance 2000, p=1.000". That is a
        # broken statistic, not a null result. The cap has to clear the real
        # distances; the radius counts are unaffected either way. Fewer trials
        # because each query now scans every site.
        "cap": 20000.0, "trials": 600,
        # Reactor distances run to thousands of km, so volcano-sized bins would
        # drop most events off the end of the chart.
        "hist_max": 6000, "hist_bin": 300,
    },
    # Everything nuclear that is NOT a power station (tools/fetch_nuclear_wide.py):
    # research reactors, enrichment, reprocessing, waste, test sites, and the
    # weapons complex the testimony names. 150 sites, so the same sparse-target
    # rules as the reactor run: a cap that clears the real distances.
    "nuclear_wide": {
        "file": "nuclear-wide.json", "key": "sites", "label": "non-power nuclear site",
        "provider": "Wikidata", "out": "spatial-test-nuclear-wide.json",
        "control_label": "the weapons complex and test sites only (the places the testimony names)",
        "cluster": False,
        "cap": 20000.0, "trials": 600,
        "hist_max": 6000, "hist_bin": 300,
    },
}


def control_subset(target, data):
    """The subset that a selection effect would concentrate on, if there is one."""
    if target == "volcanoes":
        codes = set(data.get("recent_codes") or [])
        return [(v["lat"], v["lon"]) for v in data["volcanoes"] if v.get("erupt") in codes]
    if target == "nuclear_wide":
        return [(v["lat"], v["lon"]) for v in data["sites"] if v["category"] in ("weapons", "test_site")]
    return [(v["lat"], v["lon"]) for v in data["sites"]
            if v.get("commissioned") and v["commissioned"] <= 1990]


def load(name):
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        sys.exit("Missing data/%s — run the matching fetcher first." % name)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(min(1.0, math.sqrt(a)))


class Index(object):
    """Targets bucketed by latitude band, so a query scans tens rather than all
    of them. Longitude cannot be bucketed the same way without wrap-around care,
    and the latitude cut alone is enough to make the Monte Carlo tractable."""

    def __init__(self, pts, cap=2000.0):
        self.cap = cap
        self.bands = {}
        for lat, lon in pts:
            self.bands.setdefault(int(math.floor(lat / BAND)), []).append((lat, lon))
        self.n = len(pts)

    def nearest(self, lat, lon, cap=None):
        cap = self.cap if cap is None else cap
        span = int(math.ceil(cap / 111.0 / BAND)) + 1
        b0 = int(math.floor(lat / BAND))
        best = cap
        for b in range(b0 - span, b0 + span + 1):
            for vlat, vlon in self.bands.get(b, ()):
                if abs(vlat - lat) * 111.0 > best:
                    continue
                # Cheap longitude gate before the full haversine. It must be a true
                # LOWER bound or it skips the real nearest site. From the haversine,
                # sin^2(d/2R) >= cos(lat1)cos(lat2)sin^2(dlon/2) >= (cos latmax * sin(dlon/2))^2.
                # (The old gate used dlon*111*cos(lat), the length along the
                # parallel, which is LONGER than the great circle at high latitude.)
                dlon = abs(vlon - lon)
                if dlon > 180:
                    dlon = 360 - dlon
                cmax = math.cos(math.radians(max(abs(lat), abs(vlat))))
                if cmax * math.sin(math.radians(dlon) / 2) > math.sin(min(best, math.pi * R_EARTH) / (2 * R_EARTH)):
                    continue
                d = hav(lat, lon, vlat, vlon)
                if d < best:
                    best = d
        return best


def stats(events, idx):
    """Counts within each radius, plus the median nearest-target distance."""
    near = [idx.nearest(la, lo) for la, lo in events]
    near_sorted = sorted(near)
    return {
        "within": dict((int(r), sum(1 for d in near if d <= r)) for r in RADII),
        "median": near_sorted[len(near_sorted) // 2],
        "nearest": near,
    }


def pvalue(observed, draws, more_extreme_is):
    """Monte Carlo p, with the +1 correction — a p of exactly zero is not a
    thing a finite simulation can measure."""
    if more_extreme_is == "greater":
        k = sum(1 for d in draws if d >= observed)
    else:
        k = sum(1 for d in draws if d <= observed)
    return (k + 1.0) / (len(draws) + 1.0)


def run(events, idx, trials, rng):
    obs = stats(events, idx)
    lats = [e[0] for e in events]
    lons = [e[1] for e in events]

    null = {"rotation": {"within": dict((int(r), []) for r in RADII), "median": []},
            "scatter": {"within": dict((int(r), []) for r in RADII), "median": []}}

    for _ in range(trials):
        off = rng.uniform(-180, 180)
        rot = [(lats[i], ((lons[i] + off + 180) % 360) - 180) for i in range(len(lats))]
        s = stats(rot, idx)
        for r in RADII:
            null["rotation"]["within"][int(r)].append(s["within"][int(r)])
        null["rotation"]["median"].append(s["median"])

        sca = [(lats[i], rng.uniform(-180, 180)) for i in range(len(lats))]
        s = stats(sca, idx)
        for r in RADII:
            null["scatter"]["within"][int(r)].append(s["within"][int(r)])
        null["scatter"]["median"].append(s["median"])
    return obs, null


def cluster_stats(events):
    """How tightly do the events sit against each other? The "three in the same
    place" claim is about event-to-event distance, not event-to-volcano.

    Note the ROTATION null is useless here and is not offered: rotating every
    event by the same offset leaves every event-to-event distance exactly as it
    was, so the statistic cannot move. Only the scatter null says anything."""
    # Bucket by index so only the event ITSELF is skipped. Matching on
    # coordinates also skipped every other event reported at the same rounded
    # position, i.e. exactly the repeats this statistic exists to count.
    bands = {}
    for i, (la, lo) in enumerate(events):
        bands.setdefault(int(math.floor(la / BAND)), []).append((i, la, lo))
    nn = []
    for i, (la, lo) in enumerate(events):
        best = 20000.0
        span = int(math.ceil(1500.0 / 111.0 / BAND)) + 1
        b0 = int(math.floor(la / BAND))
        for b in range(b0 - span, b0 + span + 1):
            for j, ela, elo in bands.get(b, ()):
                if j == i:
                    continue                      # itself
                d = hav(la, lo, ela, elo)
                if d < best:
                    best = d
        nn.append(best)
    nn.sort()
    return {"median_nn": nn[len(nn) // 2],
            "pairs_100": sum(1 for d in nn if d <= 100),
            "pairs_50": sum(1 for d in nn if d <= 50)}


def catalog_duplicates(rows):
    """Indices of CNEOS rows that look like duplicated entries of an earlier row:
    identical coordinates AND the same time of day to within 2 s or the same
    energy. Found 2026-11-01: e.g. 2002-06-02 and 2002-06-06, both 04:28:20 UTC,
    8.8 kt, 34.0N 21.0E. Two airbursts do not share a position and a clock time
    days apart; a mistyped date does. They matter only to the clustering
    statistic, where each one is a fake "repeat at 0 km"."""
    def secs(t):
        h, m, x = t[11:19].split(":")
        return int(h) * 3600 + int(m) * 60 + int(x)
    seen, dup = {}, []
    for i, r in enumerate(rows):
        key = (r[3], r[4])
        for j in seen.get(key, ()):
            q = rows[j]
            if abs(secs(r[0]) - secs(q[0])) <= 2 or r[2] == q[2]:
                dup.append(i)
                break
        seen.setdefault(key, []).append(i)
    return dup


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", choices=sorted(TARGETS), default="volcanoes",
                    help="what to measure distance to (default: volcanoes)")
    ap.add_argument("--trials", type=int, default=None,
                    help="Monte Carlo trials per null (default: the target's own)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", action="store_true",
                    help="also write the target's spatial-test JSON for the console to chart")
    args = ap.parse_args()

    T = TARGETS[args.target]
    if args.trials is None:
        args.trials = T["trials"]
    fb, vo = load("fireballs.json"), load(T["file"])
    events = [(e[3], e[4]) for e in fb["events"] if e[3] is not None and e[4] is not None]
    allv = [(v["lat"], v["lon"]) for v in vo[T["key"]]]
    if not allv:
        sys.exit("ABORT: data/%s holds no %s positions. Every distance would equal the "
                 "cap and the test would report a fake null." % (T["file"], T["label"]))
    recent = control_subset(args.target, vo)

    rng = random.Random(SEED)
    idx = Index(allv, T["cap"])
    obs, null = run(events, idx, args.trials, rng)

    out = {"target": args.target, "target_label": T["label"], "cap_km": T["cap"],
           "events": len(events), "volcanoes": len(allv), "recent_volcanoes": len(recent),
           "trials": args.trials, "radii": {}, "median": {}}
    for r in RADII:
        k = int(r)
        o = obs["within"][k]
        rot = null["rotation"]["within"][k]
        sca = null["scatter"]["within"][k]
        out["radii"][k] = {
            "observed": o, "observed_pct": 100.0 * o / len(events),
            "rotation_mean": sum(rot) / len(rot), "rotation_p": pvalue(o, rot, "greater"),
            "scatter_mean": sum(sca) / len(sca), "scatter_p": pvalue(o, sca, "greater"),
        }
    out["median"] = {
        "observed": obs["median"],
        "rotation_mean": sum(null["rotation"]["median"]) / args.trials,
        "rotation_p": pvalue(obs["median"], null["rotation"]["median"], "less"),
        "scatter_mean": sum(null["scatter"]["median"]) / args.trials,
        "scatter_p": pvalue(obs["median"], null["scatter"]["median"], "less"),
    }

    # Clustering: do events repeat in the same places more than chance? This is
    # event-to-event and so identical whatever the target is — run it once, under
    # the default target, and do not pay for it again.
    if T["cluster"]:
      located = [e for e in fb["events"] if e[3] is not None and e[4] is not None]
      dups = set(catalog_duplicates(located))
      cevents = [(e[3], e[4]) for i, e in enumerate(located) if i not in dups]
      cobs = cluster_stats(cevents)
      cobs_raw = cluster_stats(events)
      ctr = max(60, args.trials // 6)             # heavier per trial; fewer of them
      cnull = {"median_nn": [], "pairs_100": [], "pairs_50": []}
      for _ in range(ctr):
        sca = [(e[0], rng.uniform(-180, 180)) for e in cevents]
        c = cluster_stats(sca)
        for k in cnull:
            cnull[k].append(c[k])
      out["cluster"] = {
        "trials": ctr,
        "duplicates_removed": len(dups),
        "duplicate_rows": [located[i][0] for i in sorted(dups)],
        "with_duplicates": {"pairs_50": cobs_raw["pairs_50"], "pairs_100": cobs_raw["pairs_100"],
                            "median_nn": cobs_raw["median_nn"]},
        "median_nn": {"observed": cobs["median_nn"],
                      "null_mean": sum(cnull["median_nn"]) / ctr,
                      "p": pvalue(cobs["median_nn"], cnull["median_nn"], "less")},
        "pairs_100": {"observed": cobs["pairs_100"],
                      "null_mean": sum(cnull["pairs_100"]) / ctr,
                      "p": pvalue(cobs["pairs_100"], cnull["pairs_100"], "greater")},
        "pairs_50": {"observed": cobs["pairs_50"],
                     "null_mean": sum(cnull["pairs_50"]) / ctr,
                     "p": pvalue(cobs["pairs_50"], cnull["pairs_50"], "greater")},
      }

    lats = [e[0] for e in events]

    # Control subset. A physical association should not care whether anyone is
    # watching, or whether the site had been built yet; a selection effect would
    # concentrate on the watched / already-existing ones.
    idx_recent = Index(recent, T["cap"])
    nr = [idx_recent.nearest(la, lo) for la, lo in events]
    out["recent_only"] = {
        "within_200": sum(1 for d in nr if d <= 200),
        "median": sorted(nr)[len(nr) // 2],
    }

    # Histogram of distance-to-nearest-target, observed against the null, in
    # 100 km bins. This is the figure that makes the result readable: two curves
    # lying on top of each other says more than a p-value does.
    BINS = list(range(0, T["hist_max"] + 1, T["hist_bin"]))
    def hist(vals):
        h = [0] * (len(BINS) - 1)
        for d in vals:
            for i in range(len(BINS) - 1):
                if BINS[i] <= d < BINS[i + 1]:
                    h[i] += 1
                    break
        return h
    obs_h = hist(obs["nearest"])
    null_acc = [0] * (len(BINS) - 1)
    hruns = min(args.trials, 200)
    hrng = random.Random(SEED + 1)
    for _ in range(hruns):
        sca = [(lats[i], hrng.uniform(-180, 180)) for i in range(len(lats))]
        h = hist([idx.nearest(la, lo) for la, lo in sca])
        null_acc = [a + b for a, b in zip(null_acc, h)]
    out["histogram"] = {
        "bin_km": T["hist_bin"], "bins": BINS[:-1],
        "observed": obs_h,
        "null_mean": [round(v / float(hruns), 2) for v in null_acc],
    }

    # Cap guard, BEFORE anything is saved or printed: an event with no target
    # inside the search cap reports the cap itself as its distance, and enough
    # of those turn the median into an artifact (the bug that once shipped a
    # "median 2000 vs 2000, p=1.000" null for nuclear sites).
    sat = sum(1 for d in obs["nearest"] if d >= T["cap"] - 1e-6)
    out["median"]["capped_out"] = sat
    sat_r = sum(1 for d in nr if d >= T["cap"] - 1e-6)
    out["recent_only"]["capped_out"] = sat_r
    # Only the share at or above HALF the events can move the median (the
    # statistic quoted); a few events beyond the cap are censored above it.
    capped = sat >= len(events) * 0.5

    if args.save:
        sp = os.path.join(ROOT, "data", T["out"])
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        print("Wrote %s" % sp)

    if args.json:
        json.dump(out, sys.stdout, indent=1)
        return 2 if capped else 0

    print("CNEOS located events: %d    %s %ss: %d (%d in the control subset)"
          % (len(events), T["provider"], T["label"], len(allv), len(recent)))
    print("Monte Carlo trials: %d per null model\n" % args.trials)
    print("  radius   observed        rotation null        scatter null")
    for r in RADII:
        k = int(r)
        d = out["radii"][k]
        print("  %4d km  %4d (%5.1f%%)   %7.1f  p=%.3f    %7.1f  p=%.3f"
              % (k, d["observed"], d["observed_pct"],
                 d["rotation_mean"], d["rotation_p"],
                 d["scatter_mean"], d["scatter_p"]))
    m = out["median"]
    print("\n  median distance to the nearest %s%s"
          % (T["label"],
             "   [note: %d of %d events have no %s within the %.0f km cap; censored ABOVE "
             "the median, so it is unaffected]" % (sat, len(events), T["label"], T["cap"])
             if sat else ""))
    print("    observed %.0f km | rotation null %.0f km p=%.3f | scatter null %.0f km p=%.3f"
          % (m["observed"], m["rotation_mean"], m["rotation_p"],
             m["scatter_mean"], m["scatter_p"]))
    print("\n  control — %s:" % T["control_label"])
    print("    %d events within 200 km, median %.0f km"
          % (out["recent_only"]["within_200"], out["recent_only"]["median"]))
    c = out.get("cluster")
    if c:
      print("\n  clustering — do events repeat in the same places? (%d trials, scatter null only:" % c["trials"])
      print("  a rotation leaves every event-to-event distance untouched and cannot test this)")
      print("    %d duplicated catalog rows removed first (same position, same clock time or energy)"
            % c["duplicates_removed"])
      print("    median nearest-event distance %.0f km vs null %.0f km  p=%.3f"
          % (c["median_nn"]["observed"], c["median_nn"]["null_mean"], c["median_nn"]["p"]))
      print("    events with another within 100 km: %d vs null %.1f  p=%.3f"
          % (c["pairs_100"]["observed"], c["pairs_100"]["null_mean"], c["pairs_100"]["p"]))
      print("    events with another within  50 km: %d vs null %.1f  p=%.3f"
          % (c["pairs_50"]["observed"], c["pairs_50"]["null_mean"], c["pairs_50"]["p"]))

    print("\n  A p above about 0.05 in BOTH null columns means the catalog shows no")
    print("  %s association beyond what the geometry already implies." % T["label"])
    if capped:
        print("\nFAIL: %d of %d events sit at the %.0f km cap. Raise this target's cap." % (sat, len(events), T["cap"]))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
