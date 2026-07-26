"""Bake research payloads into src/data-content.js — THREE-OBJECT edition.

Inputs:
  1) 3I payload  (default data/research.json)      — atlas-research workflow result
  2) ISO payload (default data/research-iso.json)  — iso-research workflow result
     (anomalies1i/anomalies2i, timeline1i/timeline2i, quotes, verifies)
If the ISO payload's anomaly lists are empty (research not landed yet), the
hand-authored data/provisional-iso-anomalies.json fills in, marked PROVISIONAL.

Usage: python tools/bake_content.py [<3i-payload> [<iso-payload>]]
Raw task-output wrappers ({'result': ...}) are unwrapped automatically and the
bare payloads are checkpointed back to data/research.json / data/research-iso.json.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_payload(path, checkpoint_name):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    if "result" in d and not any(k in d for k in ("anomalies", "anomalies1i")):
        d = d["result"]
        if isinstance(d, str):
            d = json.loads(d)
    with open(os.path.join(ROOT, "data", checkpoint_name), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return d


def map_anomaly(a, obj, provisional=False):
    return {
        "object": obj,
        "id": a.get("id"),
        "title": a.get("title"),
        "date": a.get("date"),
        "observation": a.get("observation"),
        "loeb_take": a.get("loeb_take"),
        "loeb_quote": a.get("loeb_quote") or "",
        "quote_source": a.get("quote_source") or "",
        "official_explanation": a.get("official_explanation"),
        "loeb_scale": a.get("loeb_scale"),
        "viz_hint": a.get("viz_hint") or "lightcurve",
        "verify": "PROVISIONAL" if provisional else (a.get("_verify") or "UNCHECKED"),
        "sources": (a.get("sources") or [])[:4],
    }


def map_events(events, obj):
    out = []
    for e in events or []:
        e2 = dict(e)
        e2["object"] = obj
        e2.pop("sources", None)
        out.append(e2)
    return out


def verdict_of(v):
    return (v or {}).get("verdict")


def main():
    p3 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "research.json")
    piso = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "research-iso.json")
    d3 = load_payload(p3, "research.json")
    diso = load_payload(piso, "research-iso.json") if os.path.exists(piso) else {}

    with open(os.path.join(ROOT, "data", "provisional-iso-anomalies.json"), encoding="utf-8") as f:
        prov = json.load(f)

    # --- anomalies ---
    anomalies = [map_anomaly(a, "3i") for a in d3.get("anomalies", [])]
    a1 = diso.get("anomalies1i") or []
    a2 = diso.get("anomalies2i") or []
    prov1 = not a1
    prov2 = not a2
    anomalies += [map_anomaly(a, "1i", prov1) for a in (a1 or prov.get("anomalies1i", []))]
    anomalies += [map_anomaly(a, "2i", prov2) for a in (a2 or prov.get("anomalies2i", []))]

    # --- timeline ---
    timeline = map_events((d3.get("timeline") or {}).get("events", []), "3i")
    timeline += map_events((diso.get("timeline1i") or {}).get("events", []), "1i")
    timeline += map_events((diso.get("timeline2i") or {}).get("events", []), "2i")

    # --- compare + quotes ---
    compare = (d3.get("comparison") or {}).get("objects", [])
    quotes = (d3.get("quotes") or {}).get("quotes", [])
    quotes += (diso.get("quotes") or {}).get("quotes", [])

    # --- per-object meta ---
    n3 = sum(1 for a in anomalies if a["object"] == "3i")
    n1 = sum(1 for a in anomalies if a["object"] == "1i")
    n2 = sum(1 for a in anomalies if a["object"] == "2i")

    tv3 = verdict_of(d3.get("timelineVerify"))
    cv3 = verdict_of(d3.get("comparisonVerify"))
    tv1 = verdict_of(diso.get("timeline1iVerify"))
    tv2 = verdict_of(diso.get("timeline2iVerify"))

    # 1I retro Loeb-scale rank: prefer a value carried in the research entries
    scale1 = None
    for a in (a1 or []):
        if a.get("loeb_scale") is not None:
            scale1 = a["loeb_scale"]
    if scale1 is None:
        scale1 = 6  # provisional retro-rank pending research confirmation

    meta = {
        "tagline": "INTERSTELLAR ANOMALY REVIEW CONSOLE",
        "objects": {
            "3i": {
                "designation": "3I/ATLAS · C/2025 N1",
                "loebScale": 3, "pillNote": "REVIEW ACTIVE",
                "loebScaleHistory": "RANK 4 JUL 2025 · HELD 4 DEC 2025 · REDUCED TO 3 MAR 2026 (QUIET JUPITER PASS)",
                "anomalyCountNote": "LOEB'S FINAL PUBLISHED TALLY: 22 (2026-03-12) — REGISTER TRACKS " + str(n3) + " GRANULAR CASES",
                "datasetVerify": ("TIMELINE DATASET: %s · COMPARISON DATASET: %s · ANOMALY CASES INDIVIDUALLY FACT-CHECKED" % (tv3, cv3))
                                 if tv3 and cv3 else "DATASET VERIFY PENDING",
            },
            "1i": {
                "designation": "1I/'OUMUAMUA · 1I/2017 U1",
                "loebScale": scale1, "pillNote": "RETROSPECTIVE FILE",
                "loebScaleHistory": "THE ORIGINAL CASE — BIALY-LOEB LIGHTSAIL 2018 · RETRO-RANKED ON THE 2025 LOEB SCALE",
                "anomalyCountNote": str(n1) + " CASES ON FILE" + (" — PROVISIONAL DRAFT, VERIFIED RESEARCH PENDING" if prov1 else ""),
                "datasetVerify": ("TIMELINE DATASET: " + tv1 + (" · ANOMALY CASES INDIVIDUALLY FACT-CHECKED" if not prov1 else " · CASES PROVISIONAL"))
                                 if tv1 else ("TIMELINE: SINGLE-SOURCE RESEARCH PASS · CASES " + ("PROVISIONAL" if prov1 else "FACT-CHECKED")),
            },
            "2i": {
                "designation": "2I/BORISOV · C/2019 Q4",
                "loebScale": 0, "pillNote": "NATURAL CONTROL",
                "loebScaleHistory": "THE CONTROL CASE — AN ORDINARY COMET FROM ANOTHER STAR. FILE THIN BY DESIGN.",
                "anomalyCountNote": str(n2) + " NOTABLE ITEMS" + (" — PROVISIONAL DRAFT, VERIFIED RESEARCH PENDING" if prov2 else ""),
                "datasetVerify": ("TIMELINE DATASET: " + tv2 + (" · ITEMS INDIVIDUALLY FACT-CHECKED" if not prov2 else " · ITEMS PROVISIONAL"))
                                 if tv2 else ("TIMELINE: SINGLE-SOURCE RESEARCH PASS · ITEMS " + ("PROVISIONAL" if prov2 else "FACT-CHECKED")),
            },
        },
    }

    content = {"meta": meta, "anomalies": anomalies, "timeline": timeline, "compare": compare, "quotes": quotes}

    out = os.path.join(ROOT, "src", "data-content.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("/* GENERATED by tools/bake_content.py — three-object content. Do not hand-edit. */\n")
        f.write("window.ATLAS_CONTENT = ")
        json.dump(content, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("Wrote %s (%d KB): 3i=%d 1i=%d%s 2i=%d%s anomalies, %d events, %d quotes, %d ISO profiles"
          % (out, os.path.getsize(out) // 1024, n3,
             n1, "(prov)" if prov1 else "", n2, "(prov)" if prov2 else "",
             len(timeline), len(quotes), len(compare)))


if __name__ == "__main__":
    main()
