"""Pull the NUFORC sighting-report archive -> data/nuforc.json.

The fireball coverage reaches back to a 2013 episode as a precedent for 2026:
Cheryl Costa, writing the New York Skies column for the Syracuse New Times,
reported that fireball-shaped UFO sightings ran about 20% of the National UFO
Reporting Center's traffic in the first two weeks of November 2013 against a
normal share near 7%. That is a checkable proposition about a public database,
so it is checked here rather than repeated.

    python tools/fetch_nuforc.py

nuforc.org itself returns 403 to a datacenter IP, as several of the sources this
project wants do. The route that works is the public mirror planetsig/ufo-reports,
which geocoded and time-normalised the archive in 2014 and — crucially for this
question — kept the SHAPE field, which is the field the claim is about.

TWO PROPERTIES OF THE MIRROR SHAPE EVERY FIGURE DERIVED FROM IT, and are recorded
in the payload so nothing downstream can quietly forget them:

  * It is SCRUBBED. The mirror documents 88,874 records in its unscrubbed set; the
    file read here holds 80,332, rows with an unresolvable location or an
    unparseable duration having been dropped. Counts here therefore run below
    NUFORC's own, unevenly across time.
  * It STOPS. The last sighting is 2014-05-08. The 2013 half of the parallel can
    be tested against it; the 2026 half cannot be tested against it at all.

Aggregates only are written out. The raw file is 14 MB of narrative report text —
somebody else's words, and not what this project needs. What it needs is counts.
"""
import collections, csv, io, json, os, sys, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = ("https://raw.githubusercontent.com/planetsig/ufo-reports/master/"
       "csv-data/ufo-scrubbed-geocoded-time-standardized.csv")
OUT = os.path.join(ROOT, "data", "nuforc.json")

# Columns in the mirror's CSV. It has no header row.
C_DATE, C_CITY, C_STATE, C_COUNTRY, C_SHAPE = 0, 1, 2, 3, 4
C_POSTED = 8

# The monthly series runs over whole calendar months only. The archive's first
# year with consistent volume is 2000, and it ends mid-2014, so April 2014 is the
# last month that is not a stub.
FIRST, LAST = (2000, 1), (2014, 4)
CLAIM = (2013, 11)      # the month the claim is about
CLAIM_DAY = 11          # "as of November 11th"

# The largest airburst since Tunguska, and the reference point for what this
# archive can see. Case F-06 quotes its day count, so the day count travels.
CHELYABINSK = (2013, 2, 15)


def fetch(url, attempts=4):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "3i-atlas-anomaly-console/1.0 (data refresh; "
                              "github.com/Samizdat-Publications/3i-atlas-anomaly-console)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:                      # noqa: BLE001
            last = e
            if i < attempts - 1:
                time.sleep(2 ** i)
    raise SystemExit("Could not fetch %s\n  %s" % (url, last))


def sighting_date(cell):
    """'10/10/1949 20:30' -> (1949, 10, 10). None if it will not parse."""
    try:
        m, d, y = [int(x) for x in cell.split(" ")[0].split("/")]
        return (y, m, d)
    except Exception:                               # noqa: BLE001
        return None


def main():
    print("Fetching %s ..." % SRC, flush=True)
    raw = fetch(SRC)
    rows = list(csv.reader(io.StringIO(raw)))
    print("  %d rows, %d bytes" % (len(rows), len(raw)), flush=True)

    # A row with a blank shape is a real report that nobody labelled. It counts
    # toward NUFORC's volume but cannot count toward a SHARE of shapes, so every
    # share below is over shape-bearing rows and the blanks are reported apart.
    shapes = collections.Counter()
    blanks = 0
    months = collections.defaultdict(lambda: [0, 0])     # (y,m) -> [total, fireball]
    years = collections.defaultdict(lambda: [0, 0])
    seasonal = collections.defaultdict(lambda: [0, 0])   # calendar month, 2000-2013
    countries = collections.Counter()
    claim_days = [[0, 0] for _ in range(32)]            # day of the claim month
    claim_us = [0, 0]
    chelyabinsk = [0, 0]
    dropped = 0
    first_seen = last_seen = None

    for r in rows:
        if len(r) <= C_POSTED:
            dropped += 1
            continue
        dt = sighting_date(r[C_DATE])
        if not dt:
            dropped += 1
            continue
        y, m, d = dt
        if first_seen is None or dt < first_seen:
            first_seen = dt
        if last_seen is None or dt > last_seen:
            last_seen = dt
        shape = r[C_SHAPE].strip().lower()
        country = r[C_COUNTRY].strip().lower()
        countries[country or "(blank)"] += 1
        if not shape:
            blanks += 1
            continue
        shapes[shape] += 1
        fb = 1 if shape == "fireball" else 0

        if FIRST <= (y, m) <= LAST:
            months[(y, m)][0] += 1
            months[(y, m)][1] += fb
        if 2000 <= y <= 2013:
            years[y][0] += 1
            years[y][1] += fb
            seasonal[m][0] += 1
            seasonal[m][1] += fb
        if (y, m, d) == CHELYABINSK:
            chelyabinsk[0] += 1
            chelyabinsk[1] += fb
        if (y, m) == CLAIM and 1 <= d <= 31:
            claim_days[d][0] += 1
            claim_days[d][1] += fb
            if d <= CLAIM_DAY and country == "us":
                claim_us[0] += 1
                claim_us[1] += fb

    total_shaped = sum(shapes.values())
    fireball_all = shapes["fireball"]
    ranked = shapes.most_common()
    rank = 1 + [s for s, _ in ranked].index("fireball")

    ordered = sorted(months)
    payload = {
        "source": SRC,
        "provider": "National UFO Reporting Center, via the planetsig/ufo-reports mirror",
        "note": ("Aggregates of the NUFORC sighting archive as geocoded and time-normalised "
                 "by planetsig/ufo-reports in 2014. Used to test a 2013 claim about the "
                 "fireball SHAPE label's share of reports. The mirror is SCRUBBED — rows "
                 "with an unresolvable location or unparseable duration were dropped, so "
                 "counts run below NUFORC's own — and it STOPS at 2014-05-08, so it can "
                 "test the 2013 half of the 2013/2026 parallel and not the 2026 half. "
                 "The shape field is what the WITNESS called the object; it is a "
                 "self-assigned label, not a photometric measurement, and 'fireball' here "
                 "does not mean what it means in the AMS or CNEOS datasets. Every SHARE is "
                 "over shape-bearing rows; unlabelled rows are counted separately."),
        "fetched": time.strftime("%Y-%m-%d"),
        "rows": len(rows),
        "dropped": dropped,
        "shaped": total_shaped,
        "unlabelled": blanks,
        "first_sighting": "%04d-%02d-%02d" % first_seen,
        "last_sighting": "%04d-%02d-%02d" % last_seen,
        "window": {"first": "%04d-%02d" % FIRST, "last": "%04d-%02d" % LAST,
                   "months": len(ordered)},
        "fireball": {
            "count": fireball_all,
            "share": round(100.0 * fireball_all / total_shaped, 4),
            "rank": rank,
            "shapes": len(shapes),
        },
        "shapes": [{"shape": s, "n": n, "share": round(100.0 * n / total_shaped, 4)}
                   for s, n in ranked],
        "countries": [{"c": c, "n": n} for c, n in countries.most_common(8)],
        "months": [{"m": "%04d-%02d" % k, "n": months[k][0], "fb": months[k][1]}
                   for k in ordered],
        "years": [{"y": y, "n": years[y][0], "fb": years[y][1]} for y in sorted(years)],
        "seasonal": [{"m": m, "n": seasonal[m][0], "fb": seasonal[m][1]}
                     for m in sorted(seasonal)],
        "claim": {
            "month": "%04d-%02d" % CLAIM,
            "through_day": CLAIM_DAY,
            "days": [{"d": d, "n": claim_days[d][0], "fb": claim_days[d][1]}
                     for d in range(1, 32)],
            "us_through_day": {"n": claim_us[0], "fb": claim_us[1]},
        },
        "chelyabinsk": {"date": "%04d-%02d-%02d" % CHELYABINSK,
                        "n": chelyabinsk[0], "fb": chelyabinsk[1]},
    }

    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    def share(t, f):
        return (100.0 * f / t) if t else 0.0

    ct = sum(claim_days[d][0] for d in range(1, CLAIM_DAY + 1))
    cf = sum(claim_days[d][1] for d in range(1, CLAIM_DAY + 1))
    mt, mf = months[CLAIM]
    trail = [months[k] for k in ordered if (2012, 11) <= k <= (2013, 10)]
    tt, tf = sum(v[0] for v in trail), sum(v[1] for v in trail)
    ranked_months = sorted(ordered, key=lambda k: -share(*months[k]))

    print("Wrote %s (%d KB)" % (OUT, os.path.getsize(OUT) // 1024))
    print("  %d rows, %d shape-bearing, %d unlabelled, %d unparseable"
          % (len(rows), total_shaped, blanks, dropped))
    print("  fireball all-time: %d = %.2f%%, rank %d of %d shapes"
          % (fireball_all, share(total_shaped, fireball_all), rank, len(shapes)))
    print("  2013-11 through the %dth: %d reports, %d fireball = %.2f%%"
          % (CLAIM_DAY, ct, cf, share(ct, cf)))
    print("  2013-11 whole month:      %d reports, %d fireball = %.2f%%"
          % (mt, mf, share(mt, mf)))
    print("  trailing 12 months before it:            %.2f%%" % share(tt, tf))
    print("  %s: %d reports in the archive, %d of them fireball"
          % (payload["chelyabinsk"]["date"], chelyabinsk[0], chelyabinsk[1]))
    print("  rank of 2013-11 among the %d months in window: %d (top is %s at %.2f%%)"
          % (len(ordered), 1 + ranked_months.index(CLAIM),
             "%04d-%02d" % ranked_months[0], share(*months[ranked_months[0]])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
