"""Pull the NOAA/NCEI volcano location database -> data/volcanoes.json.

Needed to test a claim the fireball coverage keeps making: that bright fireballs
keep coming down near volcanoes. That is a positional claim, and the console
already ships 883 located CNEOS events with coordinates — so it is testable
rather than arguable, provided there is a volcano list to test against.

    python tools/fetch_volcanoes.py

Source is NOAA's National Centers for Environmental Information, which publishes
volcano locations as a paged JSON service. The Smithsonian Global Volcanism
Program is the other obvious source and is the one the field usually cites, but
it sits behind a bot filter that returns 403 to anything that is not a browser,
so NOAA it is. The two lists are close relatives and NOAA is a primary source in
its own right.

Stored fields are only what the proximity test needs: name, country, position,
elevation, and the eruption-recency code, which is the closest thing available to
a proxy for "is anyone pointing a camera at this one".
"""
import io, json, os, sys, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs?page=%d"
OUT = os.path.join(ROOT, "data", "volcanoes.json")

# NCEI's timeErupt codes, most recent first. D-codes are historical/dated
# eruptions; the rest are progressively older dating methods.
RECENT = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")


def get(url, attempts=4):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "3i-atlas-anomaly-console/1.0 (data refresh; "
                              "github.com/Samizdat-Publications/3i-atlas-anomaly-console)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:                      # noqa: BLE001
            last = e
            if i < attempts - 1:
                time.sleep(2 ** i)
    raise SystemExit("Could not fetch %s\n  %s" % (url, last))


def main():
    first = get(API % 1)
    pages = int(first.get("totalPages") or 1)
    items = list(first.get("items") or [])
    for p in range(2, pages + 1):
        items += list(get(API % p).get("items") or [])
        print("  page %d/%d (%d so far)" % (p, pages, len(items)), flush=True)

    out = []
    for v in items:
        lat, lon = v.get("latitude"), v.get("longitude")
        if lat is None or lon is None:
            continue
        out.append({
            "name": v.get("name") or "",
            "country": v.get("country") or "",
            "lat": round(float(lat), 4),
            "lon": round(float(lon), 4),
            "elev": v.get("elevation"),
            "erupt": v.get("timeErupt") or "",
            "morph": v.get("morphology") or "",
        })
    out.sort(key=lambda v: (v["country"], v["name"]))

    payload = {
        "source": "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs",
        "provider": "NOAA National Centers for Environmental Information",
        "note": ("Volcano locations, used to test whether CNEOS fireballs fall closer to "
                 "volcanoes than chance allows. `erupt` is NCEI's timeErupt dating code; "
                 "D1-D7 mark historically dated eruptions and are the best available proxy "
                 "for a volcano being actively watched by cameras."),
        "fetched": time.strftime("%Y-%m-%d"),
        "count": len(out),
        "recent_codes": list(RECENT),
        "volcanoes": out,
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    nrec = sum(1 for v in out if v["erupt"] in RECENT)
    print("Wrote %s (%d KB): %d volcanoes, %d with historically dated eruptions"
          % (OUT, os.path.getsize(OUT) // 1024, len(out), nrec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
