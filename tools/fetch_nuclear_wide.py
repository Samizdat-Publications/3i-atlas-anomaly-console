"""Pull a WIDER nuclear target set than civil power reactors -> data/nuclear-wide.json.

F-07 tested CNEOS fireballs against the 195 civil power reactors in the WRI
database, and said plainly that this was the wrong target set: the claim, from
LaPaz's 1948-51 green fireballs onward, is about radiation and the weapons
complex generally (research reactors, enrichment, reprocessing, waste storage,
test sites, laboratories, missile fields), not about power stations.

    python tools/fetch_nuclear_wide.py

Positions come from Wikidata (CC0) through its public SPARQL endpoint:
  * research reactors   instances of Q1438105 or any subclass (TRIGA, MTR, ...)
  * enrichment plants   Q54360657
  * reprocessing sites  Q64785417
  * waste repositories  Q21493801
  * nuclear test sites  Q53732481
  * "nuclear facility" (Q1739545) and "nuclear reactor" (Q80877) items that are
    not power plants or parts of one
  * the weapons complex and missile fields NAMED IN THE TESTIMONY, looked up by
    their Wikidata item (Los Alamos, Sandia, Kirtland, Pantex, Y-12, Hanford,
    Savannah River, Rocky Flats, Lawrence Livermore, Oak Ridge, Nevada Test Site,
    Malmstrom, Minot, F. E. Warren, RAF Bentwaters / Woodbridge)
Every row keeps its Wikidata QID, so any position can be checked by hand.

Sites within 3 km of each other collapse to one (several reactors at one lab are
one place to an airburst 100 km away), keeping the highest-priority category.

THE GATE: a thin target set ships a fake null, which is the failure the 2,000 km
cap once produced. The script refuses to write unless at least MIN_SITES
non-power sites survive de-duplication.
"""
import json, math, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "nuclear-wide.json")
SPARQL = "https://query.wikidata.org/sparql"
UA = "3i-atlas-console/2.19 (https://github.com/Samizdat-Publications/3i-atlas-anomaly-console)"
MIN_SITES = 150
MERGE_KM = 3.0

CLASSES = [
    ("research_reactor", "?c wdt:P279* wd:Q1438105 . ?i wdt:P31 ?c ."),
    ("enrichment", "?i wdt:P31 wd:Q54360657 ."),
    ("reprocessing", "?i wdt:P31 wd:Q64785417 ."),
    ("waste_repository", "?i wdt:P31 wd:Q21493801 ."),
    ("test_site", "?i wdt:P31 wd:Q53732481 ."),
    # Generic classes, filtered: anything that is also a power plant is dropped,
    # and so is anything within MERGE_KM of a WRI power reactor (below).
    ("other_facility", "?i wdt:P31 wd:Q1739545 . FILTER NOT EXISTS { ?i wdt:P31 wd:Q134447 }"),
    ("other_reactor", "?i wdt:P31 wd:Q80877 . FILTER NOT EXISTS { ?i wdt:P31 wd:Q134447 } "
                      "FILTER NOT EXISTS { ?i wdt:P361 ?pp . ?pp wdt:P31 wd:Q134447 }"),
]

# English Wikidata labels of the places the testimony names (LaPaz 1948-51,
# Malmstrom 1967, Rendlesham 1980, the Hastings missile-officer interviews).
WEAPONS = [
    "Los Alamos National Laboratory", "Sandia National Laboratories", "Kirtland Air Force Base",
    "Pantex Plant", "Y-12 National Security Complex", "Hanford Site", "Savannah River Site",
    "Rocky Flats Plant", "Lawrence Livermore National Laboratory", "Oak Ridge National Laboratory",
    "Nevada National Security Site", "Malmstrom Air Force Base", "Minot Air Force Base",
    "Francis E. Warren Air Force Base", "RAF Bentwaters", "RAF Woodbridge",
]

PRIORITY = ["weapons", "test_site", "reprocessing", "enrichment", "research_reactor", "other_reactor",
            "waste_repository", "other_facility"]


def sparql(q, attempts=5):
    url = SPARQL + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))["results"]["bindings"]
        except Exception as e:
            if i == attempts - 1:
                raise
            print("  retry after %s" % e, flush=True)
            time.sleep(5 * 2 ** i)


def point(wkt):
    # "Point(lon lat)"
    lon, lat = wkt[wkt.index("(") + 1:wkt.index(")")].split()
    return float(lat), float(lon)


def hav(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(h)))


def rows_for(category, pattern):
    q = ("SELECT ?i ?iLabel ?coord ?countryLabel WHERE { %s ?i wdt:P625 ?coord . "
         "OPTIONAL { ?i wdt:P17 ?country } "
         "SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". } }" % pattern)
    out = []
    for b in sparql(q):
        lat, lon = point(b["coord"]["value"])
        out.append({"name": b.get("iLabel", {}).get("value", ""), "qid": b["i"]["value"].rsplit("/", 1)[1],
                    "lat": round(lat, 4), "lon": round(lon, 4),
                    "country": b.get("countryLabel", {}).get("value", ""), "category": category})
    return out


def main():
    rows = []
    for cat, pat in CLASSES:
        r = rows_for(cat, pat)
        print("  %-17s %4d rows with coordinates" % (cat, len(r)), flush=True)
        rows += r
        time.sleep(1)
    labels = " ".join('"%s"@en' % w for w in WEAPONS)
    w = rows_for("weapons", "VALUES ?l { %s } ?i rdfs:label ?l ." % labels)
    found = {x["name"] for x in w}
    missing = [x for x in WEAPONS if x not in found]
    print("  %-17s %4d rows (%d named sites not found: %s)" % ("weapons", len(w), len(missing), ", ".join(missing) or "none"))
    rows += w

    # Power stations are F-07's first target set; drop anything sitting on one.
    with open(os.path.join(ROOT, "data", "nuclear.json"), encoding="utf-8") as f:
        power = [(p["lat"], p["lon"]) for p in json.load(f)["sites"]]
    before = len(rows)
    rows = [r for r in rows if r["category"] == "weapons"
            or all(hav((r["lat"], r["lon"]), p) >= MERGE_KM for p in power)]
    print("  dropped %d rows within %.0f km of a WRI power reactor" % (before - len(rows), MERGE_KM))

    # Duplicate QIDs (an item can carry two coordinates or two classes) and
    # co-located sites collapse to one, keeping the highest-priority category.
    rows.sort(key=lambda x: (PRIORITY.index(x["category"]), x["qid"]))
    sites = []
    for r in rows:
        dup = next((s for s in sites if s["qid"] == r["qid"] or hav((s["lat"], s["lon"]), (r["lat"], r["lon"])) < MERGE_KM), None)
        if dup:
            dup.setdefault("also", []).append(r["qid"])
            continue
        sites.append(r)

    counts = {}
    for s in sites:
        counts[s["category"]] = counts.get(s["category"], 0) + 1
    print("  %d sites after merging within %.0f km: %s" % (len(sites), MERGE_KM, counts))
    if len(sites) < MIN_SITES:
        sys.exit("GATE: only %d sites (need %d). Not writing; a thin target set ships a fake null." % (len(sites), MIN_SITES))

    out = {
        "source": "Wikidata (CC0) via query.wikidata.org; every site keeps its QID",
        "fetched": time.strftime("%Y-%m-%d"),
        "classes": {c: p for c, p in CLASSES},
        "weapons_named": WEAPONS, "weapons_missing": missing,
        "merge_km": MERGE_KM, "min_sites": MIN_SITES,
        "counts": counts, "n": len(sites),
        "limits": [
            "Wikidata is crowd-maintained: coverage is uneven by country, and many research reactors and "
            "fuel-cycle facilities have no item or no coordinates. Absence from this list is not absence on Earth.",
            "Civil power reactors are deliberately excluded; they are F-07's first target set (data/nuclear.json).",
            "Positions are as recorded on each item; a site's centroid can sit a few km from the facility.",
        ],
        "sites": sites,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("Wrote %s" % OUT)


if __name__ == "__main__":
    sys.exit(main())
