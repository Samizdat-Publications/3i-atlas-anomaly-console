"""Put the three fireball datasets side by side for the same calendar window.

The "are fireballs increasing?" question cannot be answered by any one of these
alone, because each fails in a different direction:

  AMS    counts EYEWITNESS REPORTS   -> scales with audience, not brightness
  CNEOS  measures ENERGY             -> blind below ~0.05 kt
  GMN    measures ABSOLUTE MAGNITUDE -> honest brightness, but the camera network
                                        grew ~1000x, so only RATIOS are comparable

    python tools/three_instruments.py                # Jan-Aug, the default window
    python tools/three_instruments.py --months 12    # whole years
    python tools/three_instruments.py --json         # machine-readable

Each instrument is reported with the bias-resistant statistic for that instrument,
never the raw count:
  AMS   - well-reported events as a share of all events
  CNEOS - events at >=1 kt, which a detection-rate change cannot inflate
  GMN   - meteors at absolute magnitude <= -4 as a share of all detections

If all three of those move together, something real happened in the sky. If only
the raw counts move, what grew was the instruments. See
docs/two-instrument-problem.md.
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ams_window(ams, year, months):
    y = ams["years"].get(str(year))
    if not y:
        return None
    def s(k):
        return sum(y.get(k, [0] * 12)[:months])
    total = sum(s(b["key"]) for b in ams["bins"])
    big = s("51_99") + s("100_plus")
    mid = s("11_25") + s("26_50") + big
    if not total:
        return None
    return {"total": total, "ge51": big, "ge11": mid,
            "share_ge51": 100.0 * big / total, "share_ge11": 100.0 * mid / total}


def cneos_window(fb, year, months):
    # Whole months only. A partial current month compared against full months in
    # earlier years silently biases the current year downward.
    ev = [e for e in fb["events"]
          if e[0][:4] == str(year) and int(e[0][5:7]) <= months]
    if not ev:
        return None
    return {"n": len(ev),
            "ge1kt": sum(1 for e in ev if (e[2] or 0) >= 1),
            "ge01kt": sum(1 for e in ev if (e[2] or 0) >= 0.1)}


def gmn_window(gmn, year, months):
    ms = [v for k, v in gmn["months"].items()
          if v and k[:4] == str(year) and int(k[4:]) <= months]
    if not ms:
        return None
    n = sum(v["n"] for v in ms)
    b = sum(v["counts"]["m4"] for v in ms)
    if not n:
        return None
    return {"n": n, "m4": b, "frac_m4": 100.0 * b / n,
            "stations": max(v["stations"] for v in ms),
            "months": len(ms)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--months", type=int, default=7,
                    help="months of each year to include. Whole months only: the "
                         "current month is still filling up, and comparing a partial "
                         "month against full ones in earlier years biases this year low.")
    ap.add_argument("--from-year", type=int, default=2019)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ams, fb, gmn = load("ams-reports.json"), load("fireballs.json"), load("gmn-monthly.json")
    missing = [n for n, d in (("ams-reports.json", ams), ("fireballs.json", fb),
                              ("gmn-monthly.json", gmn)) if d is None]
    if missing:
        sys.exit("Missing %s — run the matching fetcher first." % ", ".join(missing))

    last = max(int(k[:4]) for k, v in gmn["months"].items() if v)
    rows = []
    for y in range(args.from_year, last + 1):
        rows.append({"year": y, "ams": ams_window(ams, y, args.months),
                     "cneos": cneos_window(fb, y, args.months),
                     "gmn": gmn_window(gmn, y, args.months)})

    if args.json:
        json.dump({"months": args.months, "rows": rows}, sys.stdout, indent=1)
        return 0

    print("Months 1-%d of each year.\n" % args.months)
    print("        |------------- AMS (reports) -------------|--- CNEOS (energy) ---|------- GMN (brightness) -------|")
    print("  year  |   events   >=51rpt   >=51 as %% of all   |  events    >=1 kt    |   meteors   mag<=-4    % bright|")
    for r in rows:
        a, c, g = r["ams"], r["cneos"], r["gmn"]
        print("  %d  | %8s %9s %14s      | %7s %9s    | %9s %9s %9s |" % (
            r["year"],
            a and a["total"] or "-", a and a["ge51"] or "-",
            a and "%.2f%%" % a["share_ge51"] or "-",
            c and c["n"] or "-", c and c["ge1kt"] or "-",
            g and g["n"] or "-", g and g["m4"] or "-",
            g and "%.3f%%" % g["frac_m4"] or "-"))

    cur = rows[-1]
    base = [r for r in rows[:-1] if r["year"] >= cur["year"] - 5]
    print("\n%d against the previous %d years:" % (cur["year"], len(base)))

    def cmp(label, get):
        vals = [get(r) for r in base if get(r) is not None]
        now = get(cur)
        if not vals or now is None:
            print("  %-34s no comparable data" % label)
            return
        m = sum(vals) / len(vals)
        print("  %-34s %8.3f   mean %8.3f   x%.2f" % (label, now, m, now / m if m else 0))

    print("  -- raw counts (instrument-sensitive) --")
    cmp("AMS events", lambda r: r["ams"] and float(r["ams"]["total"]))
    cmp("AMS events with >=51 reports", lambda r: r["ams"] and float(r["ams"]["ge51"]))
    cmp("GMN meteors detected", lambda r: r["gmn"] and float(r["gmn"]["n"]))
    cmp("GMN stations reporting", lambda r: r["gmn"] and float(r["gmn"]["stations"]))
    print("  -- bias-resistant statistics --")
    cmp("AMS >=51 as share of all events", lambda r: r["ams"] and r["ams"]["share_ge51"])
    cmp("CNEOS events at >=1 kt", lambda r: r["cneos"] and float(r["cneos"]["ge1kt"]))
    cmp("GMN mag<=-4 as share of detections", lambda r: r["gmn"] and r["gmn"]["frac_m4"])
    print("\n  A real excess of bright meteors moves the bias-resistant lines.")
    print("  Growth confined to the raw counts is growth in the instruments.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
