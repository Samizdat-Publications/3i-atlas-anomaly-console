"""Fetch the CNEOS fireball (bolide) catalog + a coastline outline to draw it on.

Two real sources, both public domain / open:
  1. NASA/JPL CNEOS Fireball Data API — every atmospheric impact event detected
     by US Government sensors since 1988, with date, radiated energy, calculated
     total impact energy, and (where reported) latitude/longitude/altitude/speed.
     https://ssd-api.jpl.nasa.gov/doc/fireball.html
  2. Natural Earth 1:110m land polygons (public domain) — simplified here to a
     few thousand vertices so the map layer costs ~20 KB in the offline bundle.

Writes data/fireballs.json + data/world-land.json and bakes src/data-fireballs.js.

The two Loeb "interstellar meteor" candidates IM1 (2014-01-08) and IM2
(2017-03-09) are tagged in place from their CNEOS rows — nothing about them is
hand-entered, so if CNEOS revises a row the console follows it.

Usage: python tools/fetch_fireballs.py
"""
import datetime, json, math, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIREBALL_API = "https://ssd-api.jpl.nasa.gov/fireball.api"
LAND_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
            "master/geojson/ne_110m_land.geojson")

# CNEOS rows for the two candidates, matched on the API's own date string prefix.
IM_TAGS = {"2014-01-08": "IM1", "2017-03-09": "IM2"}

# Douglas-Peucker tolerance in degrees, and the minimum bounding-box span a ring
# must have to be worth drawing at world scale.
SIMPLIFY_EPS = 0.32
MIN_RING_SPAN = 1.6


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "3i-atlas-anomaly-console/2.5"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8")


# ---------------------------------------------------------------- fireballs
def fetch_fireballs():
    raw = json.loads(get(FIREBALL_API + "?vel-comp=true&req-loc=false"))
    fields = raw["fields"]
    idx = {name: i for i, name in enumerate(fields)}
    events, located = [], 0
    for row in raw["data"]:
        def val(name):
            v = row[idx[name]] if name in idx else None
            return None if v in (None, "") else float(v)

        date = row[idx["date"]]
        lat, lon = val("lat"), val("lon")
        if lat is not None and row[idx["lat-dir"]] == "S":
            lat = -lat
        if lon is not None and row[idx["lon-dir"]] == "W":
            lon = -lon
        if lat is not None and lon is not None:
            located += 1
        ev = [
            date,                                   # 0 "YYYY-MM-DD HH:MM:SS" UTC
            val("energy"),                          # 1 radiated energy, 1e10 J
            val("impact-e"),                        # 2 total impact energy, kt TNT
            lat,                                    # 3 deg, N positive
            lon,                                    # 4 deg, E positive
            val("alt"),                             # 5 peak-brightness altitude, km
            val("vel"),                             # 6 pre-entry speed, km/s
            IM_TAGS.get(date[:10]),                 # 7 tag or null
        ]
        events.append(ev)
    events.sort(key=lambda e: e[0])
    return {
        "source": "NASA/JPL CNEOS Fireball Data API " + raw["signature"].get("version", ""),
        "url": "https://cneos.jpl.nasa.gov/fireballs/",
        "fetched": datetime.date.today().isoformat(),
        "fields": ["date", "energy_1e10J", "impact_e_kt", "lat", "lon", "alt_km", "vel_kms", "tag"],
        "count": len(events),
        "located": located,
        "first": events[0][0][:10] if events else None,
        "last": events[-1][0][:10] if events else None,
        "events": events,
    }


# ---------------------------------------------------------------- coastlines
def rdp(pts, eps):
    """Ramer-Douglas-Peucker, iterative so a 3000-point ring cannot blow the stack."""
    if len(pts) < 3:
        return pts[:]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i0, i1 = stack.pop()
        if i1 <= i0 + 1:
            continue
        ax, ay = pts[i0]
        bx, by = pts[i1]
        dx, dy = bx - ax, by - ay
        den = math.hypot(dx, dy)
        worst, wi = -1.0, -1
        for i in range(i0 + 1, i1):
            px, py = pts[i]
            if den == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / den
            if d > worst:
                worst, wi = d, i
        if worst > eps:
            keep[wi] = True
            stack.append((i0, wi))
            stack.append((wi, i1))
    return [p for p, k in zip(pts, keep) if k]


def fetch_land():
    gj = json.loads(get(LAND_URL))
    rings = []
    for feat in gj["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            outer = poly[0]  # holes (lakes) are not drawn at this scale
            pts = [[round(float(x), 2), round(float(y), 2)] for x, y in outer]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if max(max(xs) - min(xs), max(ys) - min(ys)) < MIN_RING_SPAN:
                continue
            simp = rdp(pts, SIMPLIFY_EPS)
            if len(simp) >= 4:
                rings.append(simp)
    rings.sort(key=len, reverse=True)
    return {
        "source": "Natural Earth 1:110m land (public domain)",
        "url": "https://www.naturalearthdata.com/",
        "simplify_deg": SIMPLIFY_EPS,
        "rings": rings,
    }


def main():
    print("Fetching CNEOS fireball catalog ...", flush=True)
    fb = fetch_fireballs()
    print("  %d events (%d with a reported location), %s .. %s"
          % (fb["count"], fb["located"], fb["first"], fb["last"]))
    tagged = [e for e in fb["events"] if e[7]]
    for e in tagged:
        print("  tagged %s: %s  %.1f,%.1f  %.1f km/s  %s kt" % (e[7], e[0], e[3], e[4], e[6], e[2]))
    if len(tagged) != len(IM_TAGS):
        print("  WARNING: expected %d tagged rows, found %d" % (len(IM_TAGS), len(tagged)))

    print("Fetching Natural Earth 1:110m land ...", flush=True)
    land = fetch_land()
    print("  %d rings, %d vertices after simplification"
          % (len(land["rings"]), sum(len(r) for r in land["rings"])))

    for obj, name in ((fb, "fireballs.json"), (land, "world-land.json")):
        dest = os.path.join(ROOT, "data", name)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(obj, f, separators=(",", ":"))
        print("Wrote %s (%d KB)" % (dest, os.path.getsize(dest) // 1024))

    baked = {
        "meta": {k: fb[k] for k in ("source", "url", "fetched", "count", "located", "first", "last")},
        "fields": fb["fields"],
        "events": fb["events"],
        "land": {"source": land["source"], "rings": land["rings"]},
    }
    js = os.path.join(ROOT, "src", "data-fireballs.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write("/* GENERATED by tools/fetch_fireballs.py — CNEOS bolides + Natural Earth land. Do not hand-edit. */\n")
        f.write("window.ATLAS_FIREBALLS=")
        json.dump(baked, f, separators=(",", ":"))
        f.write(";\n")
    print("Baked %s (%d KB)" % (js, os.path.getsize(js) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
