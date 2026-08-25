"""Bake a compact three-instrument summary -> src/data-instruments.js.

The console cannot ship the raw AMS and GMN datasets — GMN alone is gigabytes
upstream. What the chart in case F-03 needs is one small table: for each year, the
BIAS-RESISTANT statistic from each instrument, plus the raw count beside it so the
divergence between the two is visible rather than asserted.

    python tools/bake_instruments.py

Run after fetch_ams.py / fetch_gmn.py / fetch_fireballs.py, before build.py.
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data-instruments.js")
BASE = range(2021, 2026)
MONTHS = 3          # Q1 — complete for every year, and the window the claim is about


def load(name):
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        sys.exit("Missing data/%s — run the matching fetcher first." % name)
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ams, gmn, fb = load("ams-reports.json"), load("gmn-monthly.json"), load("fireballs.json")
    M = {k: v for k, v in gmn["months"].items() if v}
    ALL = [b["key"] for b in ams["bins"]]
    GE51 = ["51_99", "100_plus"]

    def ams_y(y):
        yr = ams["years"].get(str(y))
        if not yr:
            return None
        tot = sum(sum((yr.get(k) or [0] * 12)[:MONTHS]) for k in ALL)
        big = sum(sum((yr.get(k) or [0] * 12)[:MONTHS]) for k in GE51)
        return (tot, big, 100.0 * big / tot) if tot else None

    def gmn_y(y):
        ms = [v for k, v in M.items() if k[:4] == str(y) and int(k[4:]) <= MONTHS]
        n = sum(v["n"] for v in ms)
        if not n or len(ms) < MONTHS:
            return None
        return (n, sum(v["counts"]["m4"] for v in ms),
                100.0 * sum(v["counts"]["m4"] for v in ms) / n,
                max(v["stations"] for v in ms))

    def cneos_y(y):
        rows = [e for e in fb["events"]
                if e[0][:4] == str(y) and int(e[0][5:7]) <= MONTHS]
        return (len(rows), sum(1 for e in rows if (e[2] or 0) >= 1))

    years = []
    for y in range(2019, 2027):
        a, g, c = ams_y(y), gmn_y(y), cneos_y(y)
        years.append({
            "y": y,
            "amsAll": a and a[0], "ams51": a and a[1], "amsShare": a and round(a[2], 4),
            "gmnAll": g and g[0], "gmnBright": g and g[1],
            "gmnFrac": g and round(g[2], 4), "gmnStations": g and g[3],
            "cneosAll": c[0], "cneos1kt": c[1],
        })

    def mean(key):
        vals = [r[key] for r in years if r["y"] in BASE and r[key] is not None]
        return sum(vals) / len(vals) if vals else None

    # Spatial test result, if it has been run. Only the summary and the
    # histogram travel into the bundle; the Monte Carlo itself takes minutes and
    # is not something a build step should be doing.
    def spatial_of(fname):
        sp = os.path.join(ROOT, "data", fname)
        if not os.path.exists(sp):
            return None
        with io.open(sp, encoding="utf-8") as f:
            t = json.load(f)
        out = {
            "events": t["events"], "targets": t["volcanoes"], "trials": t["trials"],
            "label": t.get("target_label", "volcano"),
            "radii": t["radii"], "median": t["median"], "histogram": t["histogram"],
        }
        # Event-to-event clustering is target-independent and only computed once.
        if t.get("cluster"):
            out["cluster"] = t["cluster"]
        return out

    spatial = spatial_of("spatial-test.json")
    spatial_nuclear = spatial_of("spatial-test-nuclear.json")
    # The console's existing chart reads .volcanoes; keep the old key alive.
    if spatial:
        spatial["volcanoes"] = spatial["targets"]

    # NUFORC sighting archive, if it has been pulled. Case F-06 argues from the
    # MONTHLY series and from one number that is not in it — the share the claim
    # compares against — so both travel, along with the rolling baseline that is
    # the whole point of the chart.
    # GLM — the daylight-capable instrument. Only the yearly window aggregates and
    # the day/night split travel; the case argues from those.
    gpath = os.path.join(ROOT, "data", "glm-bolides.json")
    glm = None
    if os.path.exists(gpath):
        with io.open(gpath, encoding="utf-8") as f:
            g = json.load(f)
        def sh(a):
            return round(100.0 * a["bright"] / a["n"], 4) if a["n"] else None
        glm = {
            "count": g["count"], "first": g["first"], "last": g["last"],
            "window_end": g["window_end"], "regime_change": g["regime_change"],
            "day_pct": g["daytime"]["day_pct"],
            "years": [{
                "y": y["year"], "n": y["window"]["n"], "bright": y["window"]["bright"],
                "share": sh(y["window"]),
                "humanShare": (round(100.0 * y["window"]["human_bright"] / y["window"]["human"], 4)
                               if y["window"]["human"] else None),
                "day": y["window"]["day"], "night": y["window"]["night"],
            # 2017-2020 are pipeline ramp-up: the bright share runs 4.7-100% there
            # purely because the detector was still learning to see faint events.
            # They are not comparable to the baseline and charting them would
            # squash the years that are.
            } for y in g["years"] if y["year"] >= 2021 and y["window"]["n"] >= 100],
        }

    npath = os.path.join(ROOT, "data", "nuforc.json")
    nuforc = None
    if os.path.exists(npath):
        with io.open(npath, encoding="utf-8") as f:
            nf = json.load(f)
        ms = nf["months"]
        nuforc = {
            "start": ms[0]["m"], "end": ms[-1]["m"],
            "n": [m["n"] for m in ms],
            "fb": [m["fb"] for m in ms],
            "baseline": nf["fireball"]["share"],
            "rank": nf["fireball"]["rank"],
            "shapes": nf["fireball"]["shapes"],
            "claim": nf["claim"]["month"],
            "last_sighting": nf["last_sighting"],
        }

    payload = {
        "spatial": spatial,
        "spatialNuclear": spatial_nuclear,
        "nuforc": nuforc,
        "glm": glm,
        "window": "Q1 (January-March), whole months only",
        "baseline": "%d-%d" % (min(BASE), max(BASE)),
        "note": ("Raw counts measure the instruments; the shares and rates measure the sky. "
                 "Each series is plotted against its own baseline mean so they can be "
                 "compared on one axis."),
        "means": {k: mean(k) for k in
                  ("amsAll", "ams51", "amsShare", "gmnAll", "gmnFrac", "gmnStations", "cneos1kt")},
        "years": years,
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write("/* GENERATED by tools/bake_instruments.py. Do not hand-edit. */\n")
        f.write("window.ATLAS_INSTRUMENTS = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    if glm:
        print("  GLM included: %d detections %s-%s, %d%% daytime, %d comparable years"
              % (glm["count"], glm["first"], glm["last"], glm["day_pct"], len(glm["years"])))
    if nuforc:
        print("  NUFORC series included: %d months %s-%s, all-time fireball share %.2f%%"
              % (len(nuforc["n"]), nuforc["start"], nuforc["end"], nuforc["baseline"]))
    for tag, sp in (("volcano", spatial), ("nuclear", spatial_nuclear)):
        if sp:
            print("  spatial test (%s) included: %d events vs %d targets, %d trials"
                  % (tag, sp["events"], sp["targets"], sp["trials"]))
    print("Wrote %s (%d bytes), %d years, baseline %s"
          % (OUT, os.path.getsize(OUT), len(years), payload["baseline"]))
    for r in years:
        print("  %d  AMS share %-7s  GMN frac %-7s  CNEOS >=1kt %s"
              % (r["y"], r["amsShare"], r["gmnFrac"], r["cneos1kt"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
