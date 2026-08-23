"""Re-derive every number cases F-03 and F-04 quote, and fail if any has drifted.

F-03 and F-04 are the only case files argued from figures COMPUTED off the shipped
datasets rather than from a published paper. Those figures go stale the moment
CNEOS adds a row, AMS logs another month, or GMN publishes more trajectories — so
they are checked here instead of trusted.

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


def case_text(cid):
    with io.open(os.path.join(ROOT, "data", "fireball-cases.json"), encoding="utf-8") as f:
        case = next((c for c in json.load(f)["cases"] if c["id"] == cid), None)
    if not case:
        return None
    t = " ".join([case.get("observation", ""), case.get("loeb_take", ""),
                  case.get("official_explanation", "")])
    return re.sub(r"(?<=\d),(?=\d)", "", t)      # prose writes 1,069; data says 1069


def report(a, g, c, nreg):
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


def verify(a, g, c, nreg):
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

    if bad:
        print("\nCASE FILES ARE OUT OF DATE:")
        for b in bad:
            print("  - " + b)
        return 1
    print("\nF-03 and F-04 check out: every figure they quote matches the current data.")
    return 0


def main():
    quiet = "--quiet" in sys.argv
    argparse.ArgumentParser(description=__doc__).parse_known_args()
    fb, ams, gmn = load("fireballs.json"), load("ams-reports.json"), load("gmn-monthly.json")
    a, g, c = ams_stats(ams), gmn_stats(gmn), cneos_stats(fb)
    nreg = rows_in_regions(fb)
    if not quiet:
        report(a, g, c, nreg)
    return verify(a, g, c, nreg)


if __name__ == "__main__":
    sys.exit(main())
