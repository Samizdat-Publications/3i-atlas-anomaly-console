"""Pull Global Meteor Network monthly statistics -> data/gmn-monthly.json.

THE THIRD INSTRUMENT. The fireball argument is stuck between two datasets that
each fail in an opposite direction: AMS counts eyewitness reports (people, not
photons) and CNEOS measures energy but is blind below about 0.05 kt. See
docs/two-instrument-problem.md.

GMN is a global network of video cameras that computes trajectories and reports
an ABSOLUTE MAGNITUDE for every meteor — a real brightness, measured, with no
human deciding whether to file a report. It is the one source that could settle
whether a year genuinely had more bright meteors.

    python tools/fetch_gmn.py                  # fill in whatever months are missing
    python tools/fetch_gmn.py --since 2022     # narrower window
    python tools/fetch_gmn.py --refresh-last   # re-pull the newest month (it grows)

IT HAS ITS OWN BIAS, AND IT IS A BIG ONE. The network grew from a handful of
cameras to thousands: August 2018 is a 162-byte file, August 2024 is 105 MB. Raw
counts across years measure the network, not the sky — exactly the mistake the
CNEOS record invites for its pre-1994 years. So this records, per month, both the
counts AND the number of distinct stations that contributed, and the bright-meteor
FRACTION, which is the figure that survives network growth: if cameras multiply,
faint and bright detections multiply together and the ratio holds. A real excess
of bright meteors moves the ratio. Report the ratio; never the raw count alone.

Files are 100+ MB a month and are streamed, never stored — only the aggregates
are kept.
"""
import argparse, datetime, json, os, sys, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "gmn-monthly.json")
BASE = ("https://globalmeteornetwork.org/data/traj_summary_data/monthly/"
        "traj_summary_monthly_%s.txt")

# Column indices in the ';'-separated trajectory summary. Verified against the
# file header 2026-08-23; if GMN changes the format these must be rechecked.
C_TIME, C_ABSMAG, C_MASS, C_STATIONS = 2, 76, 79, 85

# Meteor astronomy calls absolute magnitude <= -4 a fireball. The others bracket it.
BINS = [("m0", 0.0), ("m2", -2.0), ("m4", -4.0), ("m6", -6.0)]


def stream_month(ym, retries=3):
    """Aggregate one month without ever holding the file in memory or on disk."""
    url = BASE % ym
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "3i-atlas-anomaly-console/1.0 (data refresh)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                total = 0
                counts = dict((k, 0) for k, _ in BINS)
                stations = set()
                mags = []
                for raw in r:
                    if not raw or raw[:1] == b"#":
                        continue
                    parts = raw.decode("utf-8", "replace").split(";")
                    if len(parts) <= C_STATIONS:
                        continue
                    try:
                        mag = float(parts[C_ABSMAG])
                    except ValueError:
                        continue
                    total += 1
                    for key, thresh in BINS:
                        if mag <= thresh:
                            counts[key] += 1
                    for st in parts[C_STATIONS].strip().split(","):
                        st = st.strip()
                        if st:
                            stations.add(st)
                    if len(mags) < 200000:            # enough for a stable median
                        mags.append(mag)
                if not total:
                    return None
                mags.sort()
                return {
                    "n": total,
                    "counts": counts,
                    "stations": len(stations),
                    "median_absmag": round(mags[len(mags) // 2], 2),
                    "frac_m4": round(counts["m4"] / float(total), 6),
                    "per_station": round(total / float(len(stations)), 1) if stations else None,
                }
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None                            # month not published
            last = e
        except Exception as e:                         # noqa: BLE001
            last = e
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    print("    ! %s failed: %s" % (ym, last), flush=True)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", type=int, default=2019, help="first year to pull")
    ap.add_argument("--refresh-last", action="store_true",
                    help="re-pull the most recent stored month (the current one keeps growing)")
    args = ap.parse_args()

    data = {"source": BASE % "YYYYMM", "months": {}}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
    months = data.setdefault("months", {})

    if args.refresh_last and months:
        months.pop(max(months), None)

    today = datetime.date.today()
    want = []
    for y in range(args.since, today.year + 1):
        for m in range(1, 13):
            if (y, m) > (today.year, today.month):
                break
            ym = "%04d%02d" % (y, m)
            if ym not in months:
                want.append(ym)

    if not want:
        print("Nothing to fetch — %d months already stored." % len(months))
    else:
        print("Fetching %d month(s). These are 100+ MB each and are streamed, not saved."
              % len(want))
    for i, ym in enumerate(want, 1):
        t0 = time.time()
        print("  [%d/%d] %s ..." % (i, len(want), ym), end=" ", flush=True)
        got = stream_month(ym)
        if got is None:
            print("no data")
            months[ym] = None
            continue
        months[ym] = got
        print("%d meteors, %d stations, %d at mag<=-4  (%.0fs)"
              % (got["n"], got["stations"], got["counts"]["m4"], time.time() - t0), flush=True)
        with open(OUT, "w", encoding="utf-8") as f:   # checkpoint every month
            json.dump(data, f, ensure_ascii=False, indent=1)

    data["fetched"] = today.isoformat()
    data["note"] = ("Monthly aggregates of GMN meteor trajectories. The network grew "
                    "enormously over this period, so RAW COUNTS ARE NOT COMPARABLE "
                    "ACROSS YEARS. Use frac_m4 (bright meteors as a share of all "
                    "detections), which is insensitive to how many cameras were running.")
    data["columns_verified"] = "2026-08-23 (absmag=76, mass=79, stations=85)"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    live = {k: v for k, v in months.items() if v}
    print("\nStored %d months in %s" % (len(live), OUT))
    if live:
        print("\n  year   meteors   stations   mag<=-4   bright fraction")
        for y in sorted(set(k[:4] for k in live)):
            ms = [v for k, v in live.items() if k[:4] == y]
            n = sum(v["n"] for v in ms)
            b = sum(v["counts"]["m4"] for v in ms)
            st = max(v["stations"] for v in ms)
            print("  %s %9d %9d %9d        %.4f%%" % (y, n, st, b, 100.0 * b / n if n else 0))
        print("\n  Compare the FRACTION column across years, not the counts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
