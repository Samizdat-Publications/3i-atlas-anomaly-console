"""Match fireball events described in transcripts to rows in the CNEOS catalog.

A case file that says "the event he describes is this row, here it is on the map"
is worth more than one that argues about it. This finds the candidates.

    python tools/match_claims.py                     # scan data/transcripts/
    python tools/match_claims.py --region            # list CNEOS rows in the
                                                     # regions the videos discuss
    python tools/match_claims.py --date 2026-08-14   # check one date

DATE ALONE IS NOT A MATCH. CNEOS logs two or three events a month worldwide, so
any given date has a fair chance of carrying an unrelated row — an event over the
South Pacific will happily "match" a story about a roof strike in Ohio. Two things
turn a candidate into a match, and both are cheap to check:

  1. LOCATION. Does the row fall in the region described?
  2. TIME OF DAY. Convert the row's UTC to the local time quoted in the video.
     CNEOS timestamps are to the second, and a fireball is witnessed at a
     specific minute — so this is a near-unique fingerprint. Two of the events
     checked so far agree to within a minute, which no coincidence produces.

Transcripts are third-party content and are gitignored; point --transcripts
wherever they live.
"""
import argparse, collections, datetime, glob, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rough boxes for the regions the videos keep returning to: lat_min, lat_max, lon_min, lon_max
REGIONS = {
    "US midwest / Lake Erie":  (38, 44, -86, -78),
    "US Pacific Northwest":    (42, 50, -125, -116),
    "US northeast / NJ":       (38, 43, -76, -71),
    "US southwest":            (28, 38, -118, -100),
    "Japan / Ryukyu":          (24, 40, 125, 146),
    "Philippines":             (4, 21, 116, 127),
    "Mexico / Popocatepetl":   (14, 24, -106, -90),
    "central Europe":          (43, 55, 2, 20),
    "Canada":                  (44, 65, -130, -55),
}

# UTC offsets for converting a row's timestamp to the local clock a video quotes.
ZONES = [("US Eastern", -4), ("US Central", -5), ("US Mountain", -6),
         ("US Pacific", -7), ("Japan", 9), ("central Europe", 2), ("Philippines", 8)]

MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october "
    "november december".split(), 1)}
DATE_RE = re.compile(r"\b(%s)\s+(\d{1,2})(?:st|nd|rd|th)?\b" % "|".join(MONTHS), re.I)
FIREBALL_RE = re.compile(r"fireball|bolide|belide|meteor|sonic boom|re-?entry", re.I)


def load_rows():
    with open(os.path.join(ROOT, "data", "fireballs.json"), encoding="utf-8") as f:
        fb = json.load(f)
    by_date = collections.defaultdict(list)
    for e in fb["events"]:
        by_date[e[0][:10]].append(e)
    return fb, by_date


def describe(e):
    where = ", ".join(n for n, (a, b, c, d) in REGIONS.items()
                      if e[3] is not None and a <= e[3] <= b and c <= e[4] <= d)
    return ("%s UTC  %6.3f kt  %s,%s  alt %s km  vel %s km/s%s"
            % (e[0][:16], e[2] or 0, e[3], e[4], e[5], e[6],
               "   [%s]" % where if where else ""))


def local_times(e):
    t = datetime.datetime.strptime(e[0][:19], "%Y-%m-%d %H:%M:%S")
    out = []
    for name, off in ZONES:
        lt = t + datetime.timedelta(hours=off)
        out.append("%-14s %s" % (name, lt.strftime("%Y-%m-%d %H:%M")))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcripts", default=os.path.join(ROOT, "data", "transcripts"))
    ap.add_argument("--date", help="YYYY-MM-DD — show CNEOS rows on this date and their local times")
    ap.add_argument("--region", action="store_true", help="list rows inside the known regions")
    ap.add_argument("--year", default="2025,2026", help="years to consider, comma separated")
    args = ap.parse_args()

    fb, by_date = load_rows()
    years = tuple(y.strip() for y in args.year.split(","))

    if args.date:
        rows = by_date.get(args.date, [])
        if not rows:
            print("No CNEOS row on %s." % args.date)
            return 0
        for e in rows:
            print(describe(e))
            for line in local_times(e):
                print("     " + line)
        return 0

    if args.region:
        print("CNEOS rows inside the regions these videos discuss (%s):" % args.year)
        n = 0
        for e in sorted(fb["events"]):
            if e[0][:4] not in years or e[3] is None:
                continue
            if any(a <= e[3] <= b and c <= e[4] <= d for a, b, c, d in REGIONS.values()):
                print("  " + describe(e))
                n += 1
        print("\n  %d rows. Everything else these videos cover is below the CNEOS" % n)
        print("  detection floor (~0.05 kt) and has no row to match.")
        return 0

    files = sorted(glob.glob(os.path.join(args.transcripts, "*.txt")))
    if not files:
        sys.exit("No transcripts in %s" % args.transcripts)
    print("Scanning %d transcripts for dates spoken near fireball language ...\n" % len(files))
    seen, cand = set(), 0
    for path in files:
        base = os.path.basename(path)
        vdate = base[:8]
        try:
            vday = datetime.date(int(vdate[:4]), int(vdate[4:6]), int(vdate[6:8]))
        except ValueError:
            continue
        txt = re.sub(r"\s+", " ", io.open(path, encoding="utf-8", errors="ignore").read())
        title = txt[2:120].split("#")[0].strip()
        for m in DATE_RE.finditer(txt):
            ctx = txt[max(0, m.start() - 170):m.end() + 170]
            if not FIREBALL_RE.search(ctx):
                continue
            mo, day = MONTHS[m.group(1).lower()], int(m.group(2))
            for yr in (vday.year, vday.year - 1):
                try:
                    d = datetime.date(yr, mo, day)
                except ValueError:
                    continue
                if d > vday:
                    continue
                hits = by_date.get(d.isoformat(), [])
                if hits and (d.isoformat(), title) not in seen:
                    seen.add((d.isoformat(), title))
                    cand += 1
                    print("%s  %s" % (d.isoformat(), title[:66]))
                    for e in hits:
                        print("    " + describe(e))
                    print("    said: ...%s...\n" % ctx[:150])
                break
    print("%d date candidates. CHECK LOCATION AND LOCAL TIME before calling any of" % cand)
    print("them a match — run --date on the promising ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
