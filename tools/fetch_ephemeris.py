"""Fetch real heliocentric ephemerides from JPL Horizons — THREE ERAS.

Each interstellar object gets its own era: the target body plus all 8 planets
over that object's transit window, heliocentric ecliptic J2000, AU / AU-day.
  3i: 3I/ATLAS  (C/2025 N1)  2025-05-15 .. 2026-12-31 @ 1d
  1i: 1I/'Oumuamua           2017-06-01 .. 2018-08-31 @ 1d
  2i: 2I/Borisov             2019-03-01 .. 2020-12-31 @ 2d

Writes raw responses to data/raw/, a combined data/ephemeris.json (era
structure + per-era close approaches), and bakes src/data-ephemeris.js.

Usage: python tools/fetch_ephemeris.py
"""
import datetime, json, math, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)

API = "https://ssd.jpl.nasa.gov/api/horizons.api"

PLANETS = [("mercury", "199"), ("venus", "299"), ("earth", "399"), ("mars", "499"),
           ("jupiter", "599"), ("saturn", "699"), ("uranus", "799"), ("neptune", "899")]

ERAS = [
    ("3i", "DES=C/2025 N1;", "2025-05-15", "2026-12-31", "1 d"),
    ("1i", "DES=1I;",        "2017-06-01", "2018-08-31", "1 d"),
    ("2i", "DES=2I;",        "2019-03-01", "2020-12-31", "2 d"),
]


def fetch(command, start, stop, step):
    params = {
        "format": "text", "COMMAND": f"'{command}'", "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'", "EPHEM_TYPE": "'VECTORS'", "CENTER": "'500@10'",
        "REF_PLANE": "'ECLIPTIC'", "REF_SYSTEM": "'J2000'", "VEC_TABLE": "'2'",
        "OUT_UNITS": "'AU-D'", "CSV_FORMAT": "'YES'",
        "START_TIME": f"'{start}'", "STOP_TIME": f"'{stop}'", "STEP_SIZE": f"'{step}'",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "3i-atlas-console/2.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def parse_vectors(text):
    lines = text.splitlines()
    try:
        a = lines.index("$$SOE") + 1
        b = lines.index("$$EOE")
    except ValueError:
        raise RuntimeError("No $$SOE/$$EOE block:\n" + text[:2000])
    mon = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
           "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    jds, dates, pos, vel = [], [], [], []
    for ln in lines[a:b]:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) < 8:
            continue
        jds.append(float(parts[0]))
        cal = parts[1].replace("A.D. ", "")
        y, m, rest = cal.split("-", 2)
        dates.append(f"{y}-{mon[m]}-{rest.split(' ')[0]}")
        pos.append([float(parts[2]), float(parts[3]), float(parts[4])])
        vel.append([float(parts[5]), float(parts[6]), float(parts[7])])
    return jds, dates, pos, vel


def r6(v):
    return [round(x, 6) for x in v]


AU_KM = 149597870.7


def build_obj(jds, dates, pos, vel, want_vel):
    obj = {"start": dates[0], "end": dates[-1],
           "step_days": round(jds[1] - jds[0], 6) if len(jds) > 1 else 1,
           "n": len(pos), "pos": [r6(p) for p in pos]}
    if want_vel:
        kmps = AU_KM / 86400.0
        obj["speed_kms"] = [round(math.dist(v, [0, 0, 0]) * kmps, 3) for v in vel]
    return obj


def main():
    out = {"frame": "heliocentric ecliptic J2000, AU", "fetched": time.strftime("%Y-%m-%d"), "eras": {}}
    for era, command, start, stop, step in ERAS:
        era_out = {"objects": {}}
        for key, cmd, want_vel in [("target", command, True)] + [(k, c, False) for k, c in PLANETS]:
            print(f"[{era}:{key}] {cmd}  {start}..{stop} @ {step}", flush=True)
            text = fetch(cmd, start, stop, step)
            with open(os.path.join(RAW, f"{era}_{key}.txt"), "w", encoding="utf-8") as f:
                f.write(text)
            jds, dates, pos, vel = parse_vectors(text)
            era_out["objects"][key] = build_obj(jds, dates, pos, vel, want_vel)
            time.sleep(0.7)
        tgt = era_out["objects"]["target"]
        step_days = tgt["step_days"]
        d0 = tgt["start"]

        def date_at(i):
            return (datetime.date.fromisoformat(d0) + datetime.timedelta(days=round(i * step_days))).isoformat()

        approaches = {}
        sun_min = min((math.dist(p, [0, 0, 0]), i) for i, p in enumerate(tgt["pos"]))
        approaches["sun"] = {"au": round(sun_min[0], 4), "date": date_at(sun_min[1])}
        for key, _ in PLANETS[:6]:
            pl = era_out["objects"][key]
            n = min(tgt["n"], pl["n"])
            best = min((math.dist(tgt["pos"][i], pl["pos"][i]), i) for i in range(n))
            approaches[key] = {"au": round(best[0], 4), "km": round(best[0] * AU_KM), "date": date_at(best[1])}
        era_out["close_approaches"] = approaches
        era_out["start"] = tgt["start"]
        era_out["end"] = tgt["end"]
        out["eras"][era] = era_out
        print(f"  == {era}: {tgt['n']} pts, approaches: " +
              ", ".join(f"{k} {v['au']}AU@{v['date']}" for k, v in approaches.items()), flush=True)

    dest = os.path.join(ROOT, "data", "ephemeris.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"\nWrote {dest} ({os.path.getsize(dest) // 1024} KB)")

    js = os.path.join(ROOT, "src", "data-ephemeris.js")
    with open(js, "w", encoding="utf-8") as f:
        f.write("window.ATLAS_EPHEM=")
        json.dump(out, f, separators=(",", ":"))
        f.write(";\n")
    print(f"Baked {js} ({os.path.getsize(js) // 1024} KB)")


if __name__ == "__main__":
    sys.exit(main())
