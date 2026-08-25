"""Pull NASA's GLM bolide detections -> data/glm-bolides.json.

Case F-03 tests whether bright fireballs increased in 2026 and leans hardest on
the Global Meteor Network, because GMN measures brightness directly. GMN's
weakness is stated inside the case: IT IS NIGHT-BLIND, and several of 2026's most
prominent events were daytime. This is the instrument that closes that gap.

    python tools/fetch_glm.py

The Geostationary Lightning Mapper flies on the GOES East/West satellites. It was
built to map lightning and turns out to detect bolides, and NASA's Asteroid Threat
Assessment Project runs an automated detection pipeline over it, publishing the
results at neo-bolide.ndc.nasa.gov. For this question it has three properties no
other instrument in the register combines:

  * IT SEES DAYLIGHT. Staring down from geostationary orbit, day and night are the
    same to it. 47% of its detections are daytime — the half of the population GMN
    cannot see at all.
  * IT IS AUTOMATED. A detection pipeline decides, not a person choosing whether to
    file a report, which removes the audience effect that limits the AMS series.
  * IT TARGETS BOLIDES SPECIFICALLY, so it measures the bright end the claim is
    actually about, rather than the general meteor flux a radio survey would give.

TWO PROPERTIES OF THE CATALOG DECIDE HOW IT CAN BE USED, and both are recorded in
the payload so nothing downstream forgets them:

  * A PUBLICATION REGIME CHANGE ON 2025-03-06. Before that date every published
    event had been reviewed by a person. After it, roughly 38% are auto-published
    with confidenceRating "auto". So 2025-26 contain a class of record that earlier
    years do not, and any statistic spanning that date compares two different
    selection processes. The fix is not to filter on confidence — that filters on
    how long ago the event happened, since review lags — but to check the statistic
    both ways. The BRIGHT SHARE survives the split (x1.07 full vs x1.08
    human-published); the BRIGHT COUNT does not (x1.12 vs x0.71), because the
    volume of human-published events fell once auto-publishing took over. Use the
    share. Both are written out so the check can be repeated.
  * SENSITIVITY DRIFT. The faint-category share climbs from 30% in 2019 to 71% in
    2025 as the pipeline got better at dim events, which pushes the bright FRACTION
    down for free. That is the same confound F-03 ruled out for GMN using a stable
    median magnitude — here it is present, not absent, so GLM corroborates GMN
    rather than standing alone.
"""
import collections, datetime, io, json, math, os, sys, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "https://neo-bolide.ndc.nasa.gov/service/event/public"
OUT = os.path.join(ROOT, "data", "glm-bolides.json")

# Ordinal brightness scale the pipeline assigns. "Bright" and above is the
# bias-resistant bin, chosen to parallel GMN's absolute-magnitude <= -4 cut.
RANK = {"Faint": 0, "Fairly Bright": 1, "Bright": 2, "Very Bright": 3}
BRIGHT_AT = 2
REGIME_CHANGE = "2025-03-06"      # first auto-published event


def fetch(url, attempts=4):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "3i-atlas-anomaly-console/1.0 (data refresh; "
                              "github.com/Samizdat-Publications/3i-atlas-anomaly-console)",
                "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except Exception as e:                      # noqa: BLE001
            last = e
            if i < attempts - 1:
                time.sleep(2 ** i)
    raise SystemExit("Could not fetch %s\n  %s" % (url, last))


def solar_elevation(t, lat, lon):
    """Degrees above the horizon. Low-precision NOAA formulae — good to well
    under a degree, and the day/night cut only needs the sign."""
    n = (t - datetime.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0
    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2 * g)
    eps = math.radians(23.439 - 0.0000004 * n)
    dec = math.asin(math.sin(eps) * math.sin(lam))
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    gmst = (18.697374558 + 24.06570982441908 * n) % 24
    H = math.radians((gmst * 15 + lon) % 360) - ra
    la = math.radians(lat)
    return math.degrees(math.asin(math.sin(la) * math.sin(dec)
                                  + math.cos(la) * math.cos(dec) * math.cos(H)))


def main():
    print("Fetching %s ..." % SRC, flush=True)
    raw = fetch(SRC)
    payload = json.loads(raw.decode("utf-8", "replace"))
    rows = payload.get("data") or []
    print("  %d published detections, %d bytes" % (len(rows), len(raw)), flush=True)
    if not rows:
        raise SystemExit("The catalog came back empty — refusing to overwrite good data.")

    ev = []
    for x in rows:
        if not x.get("datetime"):
            continue
        t = datetime.datetime.utcfromtimestamp(x["datetime"] / 1000.0)
        rank = max([RANK.get(v.get("category"), -1)
                    for v in (x.get("brightness") or {}).values()] or [-1])
        lat, lon = x.get("latitude"), x.get("longitude")
        elev = solar_elevation(t, lat, lon) if lat is not None and lon is not None else None
        ev.append({
            "t": t, "rank": rank,
            "day": (elev is not None and elev > 0),
            "night": (elev is not None and elev < -6),
            "human": (x.get("publishedBy") or "") != "auto",
            "conf": (x.get("confidenceRating") or "").lower(),
        })
    ev.sort(key=lambda e: e["t"])
    last = ev[-1]["t"]
    cut = (last.month, last.day)          # like-for-like window ends at the last full day

    def agg(sel):
        n = len(sel)
        return {
            "n": n,
            "bright": sum(1 for e in sel if e["rank"] >= BRIGHT_AT),
            "very": sum(1 for e in sel if e["rank"] == 3),
            "faint": sum(1 for e in sel if e["rank"] == 0),
            "day": sum(1 for e in sel if e["day"]),
            "night": sum(1 for e in sel if e["night"]),
            "human": sum(1 for e in sel if e["human"]),
            "human_bright": sum(1 for e in sel if e["human"] and e["rank"] >= BRIGHT_AT),
        }

    years = {}
    for y in range(min(e["t"].year for e in ev), last.year + 1):
        whole = [e for e in ev if e["t"].year == y]
        if not whole:
            continue
        window = [e for e in whole if (e["t"].month, e["t"].day) <= cut]
        q1 = [e for e in whole if e["t"].month <= 3]
        years[y] = {"year": y, "all": agg(whole), "window": agg(window), "q1": agg(q1)}

    months = collections.OrderedDict()
    for e in ev:
        k = "%04d-%02d" % (e["t"].year, e["t"].month)
        m = months.setdefault(k, {"m": k, "n": 0, "bright": 0, "day": 0})
        m["n"] += 1
        m["bright"] += 1 if e["rank"] >= BRIGHT_AT else 0
        m["day"] += 1 if e["day"] else 0

    day = sum(1 for e in ev if e["day"])
    night = sum(1 for e in ev if e["night"])

    out = {
        "source": SRC,
        "provider": "NASA Asteroid Threat Assessment Project — GLM bolide detections",
        "note": ("Bolides detected by the Geostationary Lightning Mapper on GOES East/West "
                 "and published by NASA's automated detection pipeline. Aggregates only. "
                 "THE POINT OF THIS DATASET is that it sees DAYLIGHT, which the Global "
                 "Meteor Network cannot: it is the instrument that answers F-03's own "
                 "stated night-blindness limit. TWO CAVEATS GOVERN ANY CROSS-YEAR USE. "
                 "(1) A publication regime change on " + REGIME_CHANGE + ": before it every "
                 "published event was human-reviewed, after it roughly 38% are "
                 "auto-published, so 2025-26 hold a class of record earlier years lack. Do "
                 "NOT filter on confidenceRating to correct for this — review lags, so that "
                 "filters on how recent an event is. Compare the statistic with and without "
                 "auto-published events instead: the bright SHARE survives, the bright COUNT "
                 "does not. (2) Sensitivity drift — the faint share climbs from 30% (2019) "
                 "to 71% (2025), which depresses the bright fraction for free. Coverage is "
                 "the GOES field of view, the Americas and neighbouring oceans, not global."),
        "fetched": time.strftime("%Y-%m-%d"),
        "count": len(ev),
        "first": ev[0]["t"].strftime("%Y-%m-%d"),
        "last": last.strftime("%Y-%m-%d"),
        "window_end": "%02d-%02d" % cut,
        "regime_change": REGIME_CHANGE,
        "bright_at": "Bright",
        "daytime": {"day": day, "night": night,
                    "day_pct": round(100.0 * day / len(ev), 2)},
        "confidence": dict(collections.Counter(e["conf"] for e in ev)),
        "years": [years[y] for y in sorted(years)],
        "months": list(months.values()),
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    def share(a):
        return 100.0 * a["bright"] / a["n"] if a["n"] else 0.0

    print("Wrote %s (%d KB): %d detections, %s to %s"
          % (OUT, os.path.getsize(OUT) // 1024, len(ev), out["first"], out["last"]))
    print("  daytime fraction %.1f%% (%d day / %d night)" % (out["daytime"]["day_pct"], day, night))
    print("  like-for-like window Jan 1 - %s" % out["window_end"])
    print("  year    n  bright  share    human-only share")
    for y in sorted(years):
        w = years[y]["window"]
        hs = 100.0 * w["human_bright"] / w["human"] if w["human"] else 0.0
        print("   %d %5d %5d %7.2f%% %12.2f%%" % (y, w["n"], w["bright"], share(w), hs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
