"""Do CNEOS fireballs fall closer to volcanoes than chance allows?

The fireball coverage keeps returning to position: another fireball, another
volcano; three in the same place; were these manufactured in the same place. That
is a testable claim, not just an arguable one, because the console already ships
883 located CNEOS events with coordinates and NOAA publishes 1,608 volcano
locations.

    python tools/spatial_test.py                 # the full test
    python tools/spatial_test.py --trials 2000   # tighter p-values, slower
    python tools/spatial_test.py --json          # machine-readable

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
    """Volcanoes bucketed by latitude band, so a query scans tens rather than
    1,608. Longitude cannot be bucketed the same way without wrap-around care,
    and the latitude cut alone is enough to make the Monte Carlo tractable."""

    def __init__(self, pts):
        self.bands = {}
        for lat, lon in pts:
            self.bands.setdefault(int(math.floor(lat / BAND)), []).append((lat, lon))
        self.n = len(pts)

    def nearest(self, lat, lon, cap=2000.0):
        span = int(math.ceil(cap / 111.0 / BAND)) + 1
        b0 = int(math.floor(lat / BAND))
        best = cap
        for b in range(b0 - span, b0 + span + 1):
            for vlat, vlon in self.bands.get(b, ()):
                if abs(vlat - lat) * 111.0 > best:
                    continue
                # cheap longitude gate before the trig
                dlon = abs(vlon - lon)
                if dlon > 180:
                    dlon = 360 - dlon
                if dlon * 111.0 * math.cos(math.radians(lat)) > best:
                    continue
                d = hav(lat, lon, vlat, vlon)
                if d < best:
                    best = d
        return best


def stats(events, idx):
    """Counts within each radius, plus the median nearest-volcano distance."""
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
    idx = Index(events)
    nn = []
    for la, lo in events:
        best = 20000.0
        span = int(math.ceil(1500.0 / 111.0 / BAND)) + 1
        b0 = int(math.floor(la / BAND))
        for b in range(b0 - span, b0 + span + 1):
            for ela, elo in idx.bands.get(b, ()):
                if ela == la and elo == lo:
                    continue                      # itself
                d = hav(la, lo, ela, elo)
                if d < best:
                    best = d
        nn.append(best)
    nn.sort()
    return {"median_nn": nn[len(nn) // 2],
            "pairs_100": sum(1 for d in nn if d <= 100),
            "pairs_50": sum(1 for d in nn if d <= 50)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trials", type=int, default=600)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--save", action="store_true",
                    help="also write data/spatial-test.json for the console to chart")
    args = ap.parse_args()

    fb, vo = load("fireballs.json"), load("volcanoes.json")
    events = [(e[3], e[4]) for e in fb["events"] if e[3] is not None and e[4] is not None]
    allv = [(v["lat"], v["lon"]) for v in vo["volcanoes"]]
    recent = [(v["lat"], v["lon"]) for v in vo["volcanoes"]
              if v.get("erupt") in set(vo.get("recent_codes") or [])]

    rng = random.Random(SEED)
    idx = Index(allv)
    obs, null = run(events, idx, args.trials, rng)

    out = {"events": len(events), "volcanoes": len(allv), "recent_volcanoes": len(recent),
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

    # Clustering: do events repeat in the same places more than chance?
    cobs = cluster_stats(events)
    ctr = max(60, args.trials // 6)               # heavier per trial; fewer of them
    cnull = {"median_nn": [], "pairs_100": [], "pairs_50": []}
    lats = [e[0] for e in events]
    for _ in range(ctr):
        sca = [(lats[i], rng.uniform(-180, 180)) for i in range(len(lats))]
        c = cluster_stats(sca)
        for k in cnull:
            cnull[k].append(c[k])
    out["cluster"] = {
        "trials": ctr,
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

    # Monitored-volcano control. A physical association should not care whether
    # anyone is watching; a camera artifact would concentrate on watched ones.
    idx_recent = Index(recent)
    nr = [idx_recent.nearest(la, lo) for la, lo in events]
    out["recent_only"] = {
        "within_200": sum(1 for d in nr if d <= 200),
        "median": sorted(nr)[len(nr) // 2],
    }

    # Histogram of distance-to-nearest-volcano, observed against the null, in
    # 100 km bins. This is the figure that makes the result readable: two curves
    # lying on top of each other says more than a p-value does.
    BINS = list(range(0, 2001, 100))
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
        "bin_km": 100, "bins": BINS[:-1],
        "observed": obs_h,
        "null_mean": [round(v / float(hruns), 2) for v in null_acc],
    }

    if args.save:
        sp = os.path.join(ROOT, "data", "spatial-test.json")
        with open(sp, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        print("Wrote %s" % sp)

    if args.json:
        json.dump(out, sys.stdout, indent=1)
        return 0

    print("CNEOS located events: %d    NOAA volcanoes: %d (%d historically dated)"
          % (len(events), len(allv), len(recent)))
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
    print("\n  median distance to the nearest volcano")
    print("    observed %.0f km | rotation null %.0f km p=%.3f | scatter null %.0f km p=%.3f"
          % (m["observed"], m["rotation_mean"], m["rotation_p"],
             m["scatter_mean"], m["scatter_p"]))
    print("\n  control — historically dated (i.e. watched) volcanoes only:")
    print("    %d events within 200 km, median %.0f km"
          % (out["recent_only"]["within_200"], out["recent_only"]["median"]))
    c = out["cluster"]
    print("\n  clustering — do events repeat in the same places? (%d trials, scatter null only:" % c["trials"])
    print("  a rotation leaves every event-to-event distance untouched and cannot test this)")
    print("    median nearest-event distance %.0f km vs null %.0f km  p=%.3f"
          % (c["median_nn"]["observed"], c["median_nn"]["null_mean"], c["median_nn"]["p"]))
    print("    events with another within 100 km: %d vs null %.1f  p=%.3f"
          % (c["pairs_100"]["observed"], c["pairs_100"]["null_mean"], c["pairs_100"]["p"]))
    print("    events with another within  50 km: %d vs null %.1f  p=%.3f"
          % (c["pairs_50"]["observed"], c["pairs_50"]["null_mean"], c["pairs_50"]["p"]))

    print("\n  A p above about 0.05 in BOTH null columns means the catalog shows no")
    print("  volcano association beyond what the geometry already implies.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
