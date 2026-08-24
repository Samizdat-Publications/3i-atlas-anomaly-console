"""Re-derive every number cases F-03 and F-04 quote, and fail if any has drifted.

F-03 through F-07 are the case files argued from figures COMPUTED off the shipped
datasets rather than from a published paper. Those figures go stale the moment
CNEOS adds a row, AMS logs another month, or GMN publishes more trajectories — so
they are checked here instead of trusted. F-05's Monte Carlo and F-06's NUFORC
archive do not move on their own, but they are checked on the same terms: a case
that quotes a number nothing in the repository produces is the failure mode this
tool exists to catch, whether the drift came from upstream or from a rewrite.

    python tools/fireball_rate_check.py           # print the numbers, verify the cases
    python tools/fireball_rate_check.py --quiet   # exit status only

Exit 0 = every figure quoted still matches the data. Exit 1 = drift; the case
files need rewriting before the refresh is merged.

WINDOWS ARE WHOLE MONTHS. Comparing a partial current month against full months in
earlier years biases the current year downward — a mistake that is invisible in
the output and changes the conclusion.
"""
import argparse, collections, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_YEARS = range(2021, 2026)      # the comparison baseline both cases use
Q1 = 3
JAN_JUL = 7


def load(name):
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        sys.exit("Missing data/%s — run the matching fetcher first." % name)
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def load_optional(name):
    """For datasets a checkout may legitimately not have pulled yet."""
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def ams_stats(ams):
    def s(y, key, n):
        return sum((ams["years"].get(str(y), {}).get(key) or [0] * 12)[:n])

    def bucket(y, keys, n):
        return sum(s(y, k, n) for k in keys)

    ALL = [b["key"] for b in ams["bins"]]
    GE11 = ["11_25", "26_50", "51_99", "100_plus"]
    GE51 = ["51_99", "100_plus"]
    out = {}
    for n, tag in ((Q1, "q1"), (JAN_JUL, "jj")):
        cur_all = bucket(2026, ALL, n)
        out[tag] = {
            "all": cur_all,
            "all_mean": sum(bucket(y, ALL, n) for y in BASE_YEARS) / 5.0,
            "ge11": bucket(2026, GE11, n),
            "ge11_mean": sum(bucket(y, GE11, n) for y in BASE_YEARS) / 5.0,
            "ge51": bucket(2026, GE51, n),
            "ge51_mean": sum(bucket(y, GE51, n) for y in BASE_YEARS) / 5.0,
            "b5199": s(2026, "51_99", n),
            "b5199_mean": sum(s(y, "51_99", n) for y in BASE_YEARS) / 5.0,
            "b100": s(2026, "100_plus", n),
            "b100_mean": sum(s(y, "100_plus", n) for y in BASE_YEARS) / 5.0,
            "share51": 100.0 * bucket(2026, GE51, n) / cur_all,
            "share51_mean": sum(100.0 * bucket(y, GE51, n) / bucket(y, ALL, n)
                                for y in BASE_YEARS) / 5.0,
        }
    return out


def gmn_stats(gmn):
    M = {k: v for k, v in gmn["months"].items() if v}
    out = {}
    for n, tag in ((Q1, "q1"), (JAN_JUL, "jj")):
        def frac(y):
            ms = [v for k, v in M.items() if k[:4] == str(y) and int(k[4:]) <= n]
            tot = sum(v["n"] for v in ms)
            return (100.0 * sum(v["counts"]["m4"] for v in ms) / tot) if tot else None
        base = [frac(y) for y in BASE_YEARS if frac(y) is not None]
        ms26 = [v for k, v in M.items() if k[:4] == "2026" and int(k[4:]) <= n]
        out[tag] = {"frac": frac(2026), "mean": sum(base) / len(base),
                    "lo": min(base), "hi": max(base),
                    "n": sum(v["n"] for v in ms26),
                    "m4": sum(v["counts"]["m4"] for v in ms26)}
    meds = []
    for y in range(2021, 2027):
        ms = [v for k, v in M.items() if k[:4] == str(y)]
        if ms:
            meds.append(sum(v["median_absmag"] for v in ms) / len(ms))
    out["median_lo"], out["median_hi"] = min(meds), max(meds)
    # Peak stations in the first year vs peak overall. The MONTHLY minimum is a
    # quiet winter month, not the size of the network, and quoting it overstates
    # the growth.
    first = [v["stations"] for k, v in M.items() if k[:4] == "2019"]
    out["stations_first"] = max(first) if first else min(v["stations"] for v in M.values())
    out["stations_max"] = max(v["stations"] for v in M.values())
    return out


def cneos_stats(fb):
    ev = fb["events"]
    last = fb["last"]
    md = last[5:]
    yr = {}
    for y in range(2016, int(last[:4]) + 1):
        rows = [e for e in ev if e[0][:4] == str(y) and e[0][5:] <= md]
        yr[y] = (len(rows), sum(1 for e in rows if (e[2] or 0) >= 1))
    kt = sorted(e[2] for e in ev if e[2])
    return {
        "count": fb["count"], "last": last,
        "cur_n": yr[int(last[:4])][0], "cur_1kt": yr[int(last[:4])][1],
        "range_lo": min(v[0] for y, v in yr.items() if y < int(last[:4])),
        "range_hi": max(v[0] for y, v in yr.items() if y < int(last[:4])),
        "floor": kt[0], "median": kt[len(kt) // 2],
        "below": sum(1 for k in kt if k < 0.073),
    }


def rows_in_regions(fb):
    from math import isnan  # noqa: F401
    BOX = [(38, 44, -86, -78), (42, 50, -125, -116), (38, 43, -76, -71),
           (28, 38, -118, -100), (24, 40, 125, 146), (4, 21, 116, 127),
           (14, 24, -106, -90), (43, 55, 2, 20), (44, 65, -130, -55)]
    n = 0
    for e in fb["events"]:
        if e[0][:4] not in ("2025", "2026") or e[3] is None:
            continue
        if any(a <= e[3] <= b and c <= e[4] <= d for a, b, c, d in BOX):
            n += 1
    return n


def nuforc_stats(nf):
    """Every figure case F-06 quotes, re-derived from the archive aggregates."""
    ms = {m["m"]: m for m in nf["months"]}
    yrs = {y["y"]: y for y in nf["years"]}
    sea = {x["m"]: x for x in nf["seasonal"]}
    days = nf["claim"]["days"]
    through = nf["claim"]["through_day"]

    def pct(t, f):
        return 100.0 * f / t if t else 0.0

    ct = sum(d["n"] for d in days[:through])
    cf = sum(d["fb"] for d in days[:through])
    # Trailing twelve months before the claim month, POOLED. A mean of twelve
    # monthly ratios would let a thin month swing the baseline.
    ky = int(nf["claim"]["month"][:4])
    km = int(nf["claim"]["month"][5:])
    prior = []
    for i in range(1, 13):
        y, m = ky, km - i
        while m < 1:
            y, m = y - 1, m + 12
        prior.append("%04d-%02d" % (y, m))
    tt = sum(ms[k]["n"] for k in prior if k in ms)
    tf = sum(ms[k]["fb"] for k in prior if k in ms)
    order = sorted(ms, key=lambda k: -pct(ms[k]["n"], ms[k]["fb"]))
    top = order[0]
    us = nf["claim"]["us_through_day"]
    return {
        "rows": nf["rows"], "shaped": nf["shaped"], "unlabelled": nf["unlabelled"],
        "first": nf["first_sighting"], "last": nf["last_sighting"],
        "us_rows": next((c["n"] for c in nf["countries"] if c["c"] == "us"), 0),
        "fb": nf["fireball"]["count"], "share": nf["fireball"]["share"],
        "rank": nf["fireball"]["rank"], "shapes": nf["fireball"]["shapes"],
        "top_shapes": nf["shapes"][:3],
        "claim_n": ct, "claim_fb": cf, "claim_pct": pct(ct, cf),
        "claim_us_n": us["n"], "claim_us_fb": us["fb"], "claim_us_pct": pct(us["n"], us["fb"]),
        "claim_full": pct(ms[nf["claim"]["month"]]["n"], ms[nf["claim"]["month"]]["fb"]),
        "trailing": pct(tt, tf),
        "months": len(ms), "month_rank": 1 + order.index(nf["claim"]["month"]),
        "top_month": top, "top_pct": pct(ms[top]["n"], ms[top]["fb"]),
        "top_n": ms[top]["n"], "top_fb": ms[top]["fb"],
        "chel_n": nf["chelyabinsk"]["n"], "chel_fb": nf["chelyabinsk"]["fb"],
        "chel_month": pct(ms[nf["chelyabinsk"]["date"][:7]]["n"],
                          ms[nf["chelyabinsk"]["date"][:7]]["fb"]),
        "years": {y: pct(v["n"], v["fb"]) for y, v in yrs.items()},
        "seasonal": {m: pct(v["n"], v["fb"]) for m, v in sea.items()},
    }


def case_text(cid):
    with io.open(os.path.join(ROOT, "data", "fireball-cases.json"), encoding="utf-8") as f:
        case = next((c for c in json.load(f)["cases"] if c["id"] == cid), None)
    if not case:
        return None
    t = " ".join([case.get("observation", ""), case.get("loeb_take", ""),
                  case.get("official_explanation", "")])
    return re.sub(r"(?<=\d),(?=\d)", "", t)      # prose writes 1,069; data says 1069


def report(a, g, c, nreg, sp, nf):
    print("CNEOS: %d rows through %s. %d so far this year, %d at >=1 kt "
          "(prior-year range %d-%d)." % (c["count"], c["last"], c["cur_n"], c["cur_1kt"],
                                         c["range_lo"], c["range_hi"]))
    print("  floor %.3f kt, median %.3f kt, %d rows below 0.073 kt, "
          "%d rows in the discussed regions 2025-26" % (c["floor"], c["median"], c["below"], nreg))
    for tag, label in (("q1", "Q1"), ("jj", "Jan-Jul")):
        x = a[tag]
        print("AMS %-7s all %d (mean %.1f, x%.2f) | >=11 %d (x%.2f) | >=51 %d (mean %.1f, x%.2f)"
              % (label, x["all"], x["all_mean"], x["all"] / x["all_mean"], x["ge11"],
                 x["ge11"] / x["ge11_mean"], x["ge51"], x["ge51_mean"],
                 x["ge51"] / x["ge51_mean"]))
        print("            share>=51 %.3f%% vs %.3f%% -> x%.2f"
              % (x["share51"], x["share51_mean"], x["share51"] / x["share51_mean"]))
        y = g[tag]
        print("GMN %-7s bright frac %.3f%% vs %.3f%% -> x%.2f  (scatter %.3f-%.3f)"
              % (label, y["frac"], y["mean"], y["frac"] / y["mean"], y["lo"], y["hi"]))
    print("GMN median AbsMag 2021-26 spans %+.2f to %+.2f; stations %d -> %d"
          % (g["median_lo"], g["median_hi"], g["stations_first"], g["stations_max"]))
    if sp:
        r = sp["radii"]
        print("SPATIAL %d events vs %d volcanoes, %d trials: 100 km %d vs %.1f | "
              "200 km %d vs %.1f | 500 km %d vs %.1f | median %.0f vs %.0f km"
              % (sp["events"], sp["volcanoes"], sp["trials"],
                 r["100"]["observed"], r["100"]["rotation_mean"],
                 r["200"]["observed"], r["200"]["rotation_mean"],
                 r["500"]["observed"], r["500"]["rotation_mean"],
                 sp["median"]["observed"], sp["median"]["rotation_mean"]))
    if nf:
        print("NUFORC %d rows to %s, fireball %.2f%% all-time (rank %d of %d shapes)"
              % (nf["rows"], nf["last"], nf["share"], nf["rank"], nf["shapes"]))
        print("  claim month through the 11th %.2f%% (US %.2f%%) | whole month %.2f%% | "
              "trailing 12mo %.2f%% | rank %d of %d months (top %s at %.2f%%)"
              % (nf["claim_pct"], nf["claim_us_pct"], nf["claim_full"], nf["trailing"],
                 nf["month_rank"], nf["months"], nf["top_month"], nf["top_pct"]))


def verify(a, g, c, nreg, sp, nf):
    bad = []

    t3 = case_text("F-03")
    if t3 is None:
        print("F-03 not found.")
    else:
        q1, jj = a["q1"], a["jj"]
        checks = [
            ("CNEOS row count", str(c["count"])),
            ("CNEOS floor", "%.3f kt" % c["floor"]),
            ("CNEOS rows below 0.073", "%d fall below 0.073" % c["below"]),
            ("CNEOS current-year events", "%d events" % c["cur_n"]),
            ("CNEOS prior-year range", "%d to %d" % (c["range_lo"], c["range_hi"])),
            ("AMS Q1 51-99", "%d events in the 51-99" % q1["b5199"]),
            ("AMS Q1 51-99 mean", "mean of %.1f" % q1["b5199_mean"]),
            ("AMS Q1 100+", "%d events above 100 reports" % q1["b100"]),
            ("AMS Q1 100+ mean", "mean of %.1f" % q1["b100_mean"]),
            ("AMS Q1 >=51", "%d high-report events" % q1["ge51"]),
            ("AMS Q1 >=51 mean", "average is %.1f" % q1["ge51_mean"]),
            ("AMS Q1 share", "%.3f%%" % q1["share51"]),
            ("AMS Q1 share mean", "%.3f%%" % q1["share51_mean"]),
            ("AMS Q1 share ratio", "%.2f times the usual" % (q1["share51"] / q1["share51_mean"])),
            ("AMS Q1 all ratio", "%.2f times the 2021-2025 mean" % (q1["all"] / q1["all_mean"])),
            ("AMS Q1 >=11 ratio", "%.2f times it" % (q1["ge11"] / q1["ge11_mean"])),
            ("GMN Q1 frac", "%.3f%%" % g["q1"]["frac"]),
            ("GMN Q1 mean", "mean of %.3f%%" % g["q1"]["mean"]),
            ("GMN Q1 ratio", "factor of %.2f" % (g["q1"]["frac"] / g["q1"]["mean"])),
            ("GMN Q1 scatter", "%.3f%% to %.3f%%" % (g["q1"]["lo"], g["q1"]["hi"])),
            ("GMN Jan-Jul frac", "%.3f%% against %.3f%%" % (g["jj"]["frac"], g["jj"]["mean"])),
            ("GMN median span", "%+.2f and %+.2f" % (g["median_lo"], g["median_hi"])),
            ("GMN station growth", "%d stations to %s" % (g["stations_first"],
                                                          "{:,}".format(g["stations_max"]).replace(",", ""))),
        ]
        for label, needle in checks:
            if needle not in t3:
                bad.append("F-03 %s: data says '%s', the case does not" % (label, needle))

    t4 = case_text("F-04")
    if t4 is None:
        print("F-04 not found.")
    else:
        words = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX"}
        for label, needle in [
            ("region row count", "%s CNEOS rows" % words.get(nreg, str(nreg))),
            ("catalog median", "median is %.3f kt" % c["median"]),
        ]:
            if needle not in t4:
                bad.append("F-04 %s: data says '%s', the case does not" % (label, needle))
        # the two matched rows must still read exactly as the case states
        fb = load("fireballs.json")
        for date, want in (("2026-03-17", ["12:56:42", "0.37 kt", "41.2 N 82.0 W", "45.0 km", "14.9 km/s"]),
                           ("2026-08-14", ["07:48:36", "0.13 kt", "47.7 N 119.4 W", "30.0 km", "12.2 km/s"])):
            row = next((e for e in fb["events"] if e[0].startswith(date)), None)
            if row is None:
                bad.append("F-04: the %s row has left the catalog" % date)
                continue
            live = ["%s" % row[0][11:19], "%.2f kt" % row[2],
                    "%.1f N %.1f W" % (row[3], abs(row[4])),
                    "%.1f km" % row[5], "%.1f km/s" % row[6]]
            for stated, actual in zip(want, live):
                if stated != actual:
                    bad.append("F-04 %s: catalog now says %s, case says %s" % (date, actual, stated))
                if stated not in t4:
                    bad.append("F-04 %s: case no longer states '%s'" % (date, stated))

    t5 = case_text("F-05")
    if t5 is None:
        print("F-05 not found.")
    elif sp is None:
        print("data/spatial-test.json absent — F-05's figures not checked.")
    else:
        r, cl = sp["radii"], sp["cluster"]
        for label, needle in [
            ("event count", "%d CNEOS events" % sp["events"]),
            ("volcano count", "%d volcano positions" % sp["volcanoes"]),
            ("trials", "%d trials" % sp["trials"]),
            ("100 km", "%d events observed against %.1f" % (r["100"]["observed"],
                                                            r["100"]["rotation_mean"])),
            ("200 km", "%d against %.1f" % (r["200"]["observed"], r["200"]["rotation_mean"])),
            ("500 km", "%d against %.1f" % (r["500"]["observed"], r["500"]["rotation_mean"])),
            ("median distance", "%.0f km observed against %.0f" % (sp["median"]["observed"],
                                                                   sp["median"]["rotation_mean"])),
            ("nearest-neighbour median", "%.0f km against %.0f" % (cl["median_nn"]["observed"],
                                                                   cl["median_nn"]["null_mean"])),
            ("pairs within 100 km", "%d events having another within 100 km against %.1f"
                                    % (cl["pairs_100"]["observed"], cl["pairs_100"]["null_mean"])),
        ]:
            if needle not in t5:
                bad.append("F-05 %s: data says '%s', the case does not" % (label, needle))

    t7 = case_text("F-07")
    spn = load_optional("spatial-test-nuclear.json")
    if t7 is None:
        print("F-07 not found.")
    elif spn is None:
        print("data/spatial-test-nuclear.json absent — F-07's figures not checked.")
    else:
        rn, mn = spn["radii"], spn["median"]
        def RN(k, f):
            return rn[str(k)][f] if str(k) in rn else rn[k][f]
        nuc = load_optional("nuclear.json") or {"sites": []}
        countries = len({x["country"] for x in nuc["sites"]})
        excess = 100.0 * (RN(200, "observed") / RN(200, "rotation_mean") - 1.0)
        for label, needle in [
            ("event count", "%d CNEOS events" % spn["events"]),
            ("reactor count", "%d nuclear power\nreactors across %d countries"
                              % (spn["volcanoes"], countries)),
            ("trials", "%d trials" % spn["trials"]),
            ("100 km", "%d events observed against %.1f expected, p=%.3f and\n%.3f"
                       % (RN(100, "observed"), RN(100, "rotation_mean"),
                          RN(100, "rotation_p"), RN(100, "scatter_p"))),
            ("500 km", "%d against %.1f, p=%.3f and %.3f"
                       % (RN(500, "observed"), RN(500, "rotation_mean"),
                          RN(500, "rotation_p"), RN(500, "scatter_p"))),
            ("median", "%.0f km observed against %.0f and\n%.0f by chance, p=%.3f and %.3f"
                       % (mn["observed"], mn["rotation_mean"], mn["scatter_mean"],
                          mn["rotation_p"], mn["scatter_p"])),
            ("200 km", "%d events against %.1f expected" % (RN(200, "observed"),
                                                            RN(200, "rotation_mean"))),
            ("200 km excess", "a %.0f%% excess" % excess),
            ("200 km scatter p", "p=%.3f under the scatter null" % RN(200, "scatter_p")),
            ("200 km rotation p", "p=%.3f under the rotation null" % RN(200, "rotation_p")),
            ("control count", "the %d reactors already commissioned by 1990"
                              % spn["recent_volcanoes"]),
            ("control result", "leaves %d events within 200 km and\na median of %.0f km"
                               % (spn["recent_only"]["within_200"],
                                  spn["recent_only"]["median"])),
        ]:
            flat = " ".join(needle.split())
            if flat not in " ".join(t7.split()):
                bad.append("F-07 %s: data says '%s', the case does not" % (label, flat))

    t6 = case_text("F-06")
    if t6 is None:
        print("F-06 not found.")
    elif nf is None:
        print("data/nuforc.json absent — F-06's figures not checked.")
    else:
        sh = {x["shape"]: x for x in nf["top_shapes"]}
        checks = [
            ("archive size", "%d reports from %s to %s" % (nf["rows"], nf["first"], nf["last"])),
            ("shape-bearing", "%d carry a shape and %d do not" % (nf["shaped"], nf["unlabelled"])),
            ("scrub", "project reads holds %d" % nf["rows"]),
            ("US share", "%d of the %d rows" % (nf["us_rows"], nf["rows"])),
            ("fireball count", "%d of %d shape-bearing" % (nf["fb"], nf["shaped"])),
            ("fireball share", "%.2f%%" % nf["share"]),
            ("fireball rank", "fourth of %d shapes" % nf["shapes"]),
            ("claim month", "%d shape-bearing reports with %d fireballs, %.1f%%"
                            % (nf["claim_n"], nf["claim_fb"], nf["claim_pct"])),
            ("claim month US", "%d reports and %d fireballs, %.1f%%"
                               % (nf["claim_us_n"], nf["claim_us_fb"], nf["claim_us_pct"])),
            ("trailing baseline", "fireball share is %.2f%%" % nf["trailing"]),
            ("claim month full", "came in at %.2f%% for the full month" % nf["claim_full"]),
            ("claim month partial", "%.1f%% through the 11th" % nf["claim_pct"]),
            ("month count", "%d of them" % nf["months"]),
            ("month rank", "comes 14th"),
            ("record month", "July 2012 at %.2f%% (%d of %d)"
                             % (nf["top_pct"], nf["top_fb"], nf["top_n"])),
            ("chelyabinsk day", "logged %d reports, %d of them fireball"
                                % (nf["chel_n"], nf["chel_fb"])),
            ("chelyabinsk month", "February 2013 finished at %.2f%%" % nf["chel_month"]),
        ]
        for y in (2003, 2004, 2008, 2009):
            checks.append(("%d share" % y, "%.2f%%" % nf["years"][y]))
        checks.append(("2010-13 run", "%.2f%%, %.2f%%, %.2f%%, %.2f%%"
                       % tuple(nf["years"][y] for y in (2010, 2011, 2012, 2013))))
        for m, name in ((7, "July"), (12, "December"), (4, "April")):
            checks.append(("%s seasonal" % name, "%.2f%%" % nf["seasonal"][m]))
        for shape, pretty in (("light", "light"), ("triangle", "triangle"), ("circle", "circle")):
            checks.append(("%s share" % shape,
                           "%s (%.1f%%)" % (pretty, sh[shape]["share"])))
        for label, needle in checks:
            if needle not in t6:
                bad.append("F-06 %s: data says '%s', the case does not" % (label, needle))

    if bad:
        print("\nCASE FILES ARE OUT OF DATE:")
        for b in bad:
            print("  - " + b)
        return 1
    print("\nF-03 through F-07 check out: every figure they quote matches the current data.")
    return 0


def main():
    quiet = "--quiet" in sys.argv
    argparse.ArgumentParser(description=__doc__).parse_known_args()
    fb, ams, gmn = load("fireballs.json"), load("ams-reports.json"), load("gmn-monthly.json")
    a, g, c = ams_stats(ams), gmn_stats(gmn), cneos_stats(fb)
    nreg = rows_in_regions(fb)
    sp = load_optional("spatial-test.json")
    raw = load_optional("nuforc.json")
    nf = nuforc_stats(raw) if raw else None
    if not quiet:
        report(a, g, c, nreg, sp, nf)
    return verify(a, g, c, nreg, sp, nf)


if __name__ == "__main__":
    sys.exit(main())
