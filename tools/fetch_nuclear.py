"""Pull nuclear power reactor positions -> data/nuclear.json.

The last untested positional claim in the fireball coverage is the oldest one.
In 1948-51 Lincoln LaPaz, investigating the New Mexico "green fireballs" for the
Air Force, reported that they appeared preferentially near sensitive military and
scientific installations — the worry being that something was probing the nuclear
program. The claim recurs in modern UAP coverage as a general association between
unusual aerial events and nuclear sites.

    python tools/fetch_nuclear.py

Positions come from the World Resources Institute Global Power Plant Database
(CC-BY 4.0), filtered to primary_fuel == Nuclear. It is the only openly licensed
global list with coordinates for every entry; the IAEA's PRIS is the canonical
register but publishes no machine-readable positions.

TWO LIMITS ARE BAKED INTO THE PAYLOAD because they decide what the test can mean:

  * POWER REACTORS ARE NOT WHAT LAPAZ WAS TALKING ABOUT. He meant Los Alamos,
    Sandia, Kirtland — the weapons complex. That list is a few dozen sites, far
    too small to support a Monte Carlo, and has no openly licensed positional
    dataset. This tests the modern civil-reactor population instead, and the case
    file has to say so rather than implying otherwise.
  * COMMISSIONING DATES MATTER. A reactor that started up in 2015 cannot have
    attracted anything in 1995, so `commissioned` travels with each row and the
    spatial test can restrict to sites that predate the events.
"""
import collections, csv, io, json, os, sys, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = ("https://raw.githubusercontent.com/wri/global-power-plant-database/master/"
       "output_database/global_power_plant_database.csv")
OUT = os.path.join(ROOT, "data", "nuclear.json")


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


def main():
    print("Fetching %s ..." % SRC, flush=True)
    raw = fetch(SRC)
    rows = list(csv.DictReader(io.StringIO(raw)))
    print("  %d plants of every fuel type" % len(rows), flush=True)

    out = []
    for r in rows:
        if (r.get("primary_fuel") or "").strip().lower() != "nuclear":
            continue
        try:
            lat, lon = float(r["latitude"]), float(r["longitude"])
        except (TypeError, ValueError, KeyError):
            continue
        try:
            year = int(float(r.get("commissioning_year") or 0)) or None
        except ValueError:
            year = None
        try:
            mw = round(float(r.get("capacity_mw") or 0), 1) or None
        except ValueError:
            mw = None
        out.append({
            "name": (r.get("name") or "").strip(),
            "country": (r.get("country") or "").strip(),
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "mw": mw,
            "commissioned": year,
        })
    out.sort(key=lambda v: (v["country"], v["name"]))

    payload = {
        "source": SRC,
        "provider": "World Resources Institute — Global Power Plant Database (CC-BY 4.0)",
        "note": ("Civil nuclear power reactor positions, used to test whether CNEOS "
                 "fireballs fall closer to nuclear sites than chance allows. TWO LIMITS "
                 "GOVERN ANY USE OF THIS FILE. (1) These are POWER REACTORS. The 1948-51 "
                 "green-fireball claim was about the weapons complex — Los Alamos, Sandia, "
                 "Kirtland — which is a few dozen sites with no openly licensed positional "
                 "dataset and far too few for a Monte Carlo. (2) CNEOS begins 1988-04-15, "
                 "forty years after the events LaPaz described, so his own fireballs cannot "
                 "be tested against it at all. `commissioned` is carried so the test can "
                 "restrict to reactors that predate the events being tested."),
        "fetched": time.strftime("%Y-%m-%d"),
        "count": len(out),
        "sites": out,
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    dated = [v for v in out if v["commissioned"]]
    by_country = collections.Counter(v["country"] for v in out)
    print("Wrote %s (%d KB): %d nuclear sites in %d countries"
          % (OUT, os.path.getsize(OUT) // 1024, len(out), len(by_country)))
    print("  top: " + ", ".join("%s %d" % (c, n) for c, n in by_country.most_common(6)))
    if dated:
        print("  %d carry a commissioning year, %d-%d"
              % (len(dated), min(v["commissioned"] for v in dated),
                 max(v["commissioned"] for v in dated)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
