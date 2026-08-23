"""Pull the AMS/IMO fireball report statistics -> data/ams-reports.json.

The American Meteor Society's public stats page is the dataset behind every
"fireballs are increasing" argument made from report counts. It is rendered by
JavaScript, but the numbers themselves ship in the page as `all_series[YEAR]`
arrays: per-month event counts, split into bins by HOW MANY PEOPLE reported each
event. 2006 to the present.

    python tools/fetch_ams.py            # fetch, write data/ams-reports.json, report
    python tools/fetch_ams.py --quiet

WHAT THIS DATASET IS, AND IS NOT. Its unit of measurement is PEOPLE, not photons.
A bin labelled "more than 100 reports" counts events that a hundred people
noticed and bothered to file, which is a function of population, phone cameras,
social media reach and time of night as much as of the meteor. It cannot be read
as a brightness measurement, and an apparent rise in the top bins has to be
tested against the growth of the dataset as a whole before it means anything.
See docs/two-instrument-problem.md — that test is the whole point of pulling it.
"""
import argparse, json, os, re, sys, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = ("https://fireball.amsmeteors.org/members/imo_fireball_stats/"
       "events_per_month_per_year")
OUT = os.path.join(ROOT, "data", "ams-reports.json")

# Order matters: these are cumulative bins from fewest reports to most.
BINS = [
    ("one", "Events with only one report"),
    ("2_10", "Events with 1< number of reports <= 10"),
    ("11_25", "Events with 10< number of reports <= 25"),
    ("26_50", "Events with 25< number of reports <= 50"),
    ("51_99", "Events with 50< number of reports < 100"),
    ("100_plus", "Events with more than 100 reports"),
]


def get(url, attempts=4):
    """Retry with backoff — this is meant to be runnable from a monthly cron."""
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "3i-atlas-anomaly-console/1.0 (data refresh; "
                              "github.com/Samizdat-Publications/3i-atlas-anomaly-console)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:                      # noqa: BLE001 — retry anything
            last = e
            if i < attempts - 1:
                time.sleep(2 ** i)
    raise SystemExit("Could not fetch %s\n  %s" % (url, last))


def parse(html):
    years = {}
    for year, blob in re.findall(r"all_series\[(\d{4})\]=(\[.*?\]);", html, re.S):
        series = {}
        for name, arr in re.findall(r"name:'([^']+)',\s*data:\s*\[([0-9,\s]+)\]", blob):
            key = next((k for k, label in BINS if label == name), None)
            if key:
                months = [int(x) for x in arr.split(",")]
                if len(months) == 12:
                    series[key] = months
        if series:
            years[int(year)] = series
    if not years:
        raise SystemExit(
            "Parsed no series from the stats page. AMS has probably changed its "
            "markup — check for 'all_series[' in the response before trusting "
            "anything downstream.")
    return years


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    years = parse(get(URL))
    ys = sorted(years)

    # Months with zero across every bin are the future, not a quiet month.
    last = None
    for m in range(12):
        if any(years[ys[-1]].get(k, [0] * 12)[m] for k, _ in BINS):
            last = m + 1
    payload = {
        "source": URL,
        "note": ("Counts of fireball events by NUMBER OF EYEWITNESS REPORTS, per month. "
                 "A count of reporters, not a measurement of brightness or energy — see "
                 "docs/two-instrument-problem.md before drawing a trend from it."),
        "fetched": time.strftime("%Y-%m-%d"),
        "bins": [{"key": k, "label": label} for k, label in BINS],
        "first_year": ys[0], "last_year": ys[-1], "last_month": last,
        "years": {str(y): years[y] for y in ys},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    if args.quiet:
        return 0
    tot = sum(sum(sum(v) for v in years[y].values()) for y in ys)
    print("Wrote %s" % OUT)
    print("  %d years (%d-%d), %s complete through month %d, %d events total"
          % (len(ys), ys[0], ys[-1], ys[-1], last or 0, tot))
    print("\n  year   all   >=11 reports   >=51 reports")
    for y in ys[-6:]:
        s = years[y]
        n = last if y == ys[-1] else 12
        a = sum(sum(v[:n]) for v in s.values())
        b = sum(sum(s.get(k, [0] * 12)[:n]) for k in ("11_25", "26_50", "51_99", "100_plus"))
        c = sum(sum(s.get(k, [0] * 12)[:n]) for k in ("51_99", "100_plus"))
        print("  %d  %5d  %8d      %8d" % (y, a, b, c))
    print("\n  The >=51 column is the one people quote. Compare its growth against the")
    print("  'all' column before calling it a trend: if they rose together, what grew")
    print("  was the audience.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
