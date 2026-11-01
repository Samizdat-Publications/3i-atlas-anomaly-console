"""Where would 3I/ATLAS be if only gravity had acted on it?

The question behind arXiv:2610.38485 ("Nongravitational Motion of 3I/ATLAS Far
from the Sun", Królikowska, Spada & Dones, 2026-10-28) and the "changing course"
claim, answered in kilometres from JPL's own solution rather than asserted.

METHOD (every orbit integrated by JPL Horizons, not by this script):
  1. REAL   - the pinned JPL#54 solution, non-gravitational push included
              (jpl_solution.py). This is the path the console draws.
  2. ARRIVAL ELEMENTS - #54's osculating elements on 2025-05-15, the first day
              of the console's clock, taken from the REAL run.
  3. GHOST  - those same arrival elements with the push switched off. Same
              planets, same small perturbers, same Jupiter; the only difference
              from REAL is A1 = A2 = A3 = 0. So REAL minus GHOST is the push.
  4. CROSS-CHECK - the paper's own gravity-only orbit fitted to the distant
              pre-perihelion astrometry (its Table 5, column 1), propagated the
              same way. A second, independent "gravity only" answer; if it and
              the GHOST disagree by an order of magnitude something is wrong.

VALIDATION: REAL must reproduce the previously shipped #54 path (git HEAD
data/ephemeris.json) on every overlapping day, or the script aborts. A
counterfactual that cannot reproduce the real path is not a counterfactual.

Outputs data/counterfactual.json (derived series + the ghost path) and re-bakes
src/data-ephemeris.js. Run after tools/fetch_ephemeris.py.

    python tools/fetch_counterfactual.py
"""
import datetime, json, math, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from jpl_solution import JPL54, ELEM_KEYS, horizons, user_params, jpl54_params  # noqa: E402
from fetch_ephemeris import parse_vectors, bake_js  # noqa: E402

START, STOP = "2025-05-15", "2027-12-31"   # must match the 3I era in fetch_ephemeris.py
AU_KM = 149597870.7
ARCSEC = 180 / math.pi * 3600
TOL_AU = 2e-6            # shipped positions are rounded to 1e-6 AU

# Paper Table 5, col. 1: pre-perihelion purely gravitational orbit, distant
# data only (2025-05-15 .. 07-31, r > 3.49 au). Epoch 2025-11-21 = JD 2461000.5.
# T = 2025 10 29.477610557 TDB -> JD 2460977.5 + 0.477610557.
PAPER_GR = {"EPOCH": "2461000.5", "EC": "6.142500852316", "QR": "1.356868048914",
            "TP": str(2460977.5 + 0.477610557), "OM": "322.164719671",
            "W": "128.010031534", "IN": "175.113491556"}

# The two distant arcs the paper used, and the window it excluded on purpose.
PAPER_ARCS = {"pre": ["2025-05-15", "2025-07-31"], "post": ["2026-01-01", "2026-04-14"]}


def parse_elements(text):
    lines = text.splitlines()
    head = [h.strip() for h in next(l for l in lines if l.strip().startswith("JDTDB")).split(",")]
    row = lines[lines.index("$$SOE") + 1]
    vals = [v.strip() for v in row.split(",")]
    d = dict(zip(head, vals))
    return {"EPOCH": d["JDTDB"], "EC": d["EC"], "QR": d["QR"], "TP": d["Tp"],
            "OM": d["OM"], "W": d["W"], "IN": d["IN"]}


def vectors(extra, label):
    print(f"  Horizons: {label} {START}..{STOP}", flush=True)
    text = horizons(extra, START, STOP, "1 d")
    time.sleep(0.7)
    return parse_vectors(text)


def sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def norm(a):
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def unit(a):
    n = norm(a)
    return [a[0] / n, a[1] / n, a[2] / n]


def angle(a, b):
    c = dot(a, b) / (norm(a) * norm(b))
    return math.acos(max(-1.0, min(1.0, c)))


def shipped_target():
    """The #54 path as previously shipped (git HEAD), for validation."""
    try:
        raw = subprocess.check_output(["git", "show", "HEAD:data/ephemeris.json"], cwd=ROOT)
        return json.loads(raw)["eras"]["3i"]["objects"]["target"]
    except Exception as e:
        sys.exit(f"Cannot read the shipped ephemeris from git for validation: {e}")


def main():
    print("Counterfactual: 3I/ATLAS with and without its non-gravitational push")
    jd, dates, real_p, real_v = vectors(jpl54_params(), "REAL (JPL#54, push on)")

    shipped = shipped_target()
    worst = max(norm(sub(real_p[i], shipped["pos"][i])) for i in range(min(len(real_p), shipped["n"])))
    print(f"  validation: REAL vs shipped #54 path, worst day = {worst:.2e} AU over {shipped['n']} days")
    if worst > TOL_AU:
        sys.exit(f"ABORT: REAL does not reproduce the shipped path (worst {worst:.2e} AU > {TOL_AU:.0e}).")

    print("  Horizons: arrival elements on " + START)
    arrival = parse_elements(horizons(jpl54_params(), START, "2025-05-16", "1 d", ephem="ELEMENTS"))
    time.sleep(0.7)
    _, _, ghost_p, ghost_v = vectors(user_params(arrival, None, "3I GRAVITY ONLY"), "GHOST (push off)")
    _, _, paper_p, _ = vectors(user_params(PAPER_GR, None, "3I PAPER PRE-PERI GR"), "CROSS-CHECK (paper GR orbit)")
    _, _, earth_p, _ = vectors({"COMMAND": "'399'"}, "Earth")

    n = len(real_p)
    assert len(ghost_p) == n == len(paper_p) == len(earth_p), "grids differ"
    sep_km, dv_ms, dvv_ms, ang_as, rtn_km, xc_km = [], [], [], [], [], []
    for i in range(n):
        d = sub(real_p[i], ghost_p[i])
        sep_km.append(round(norm(d) * AU_KM))
        dv_ms.append(round((norm(real_v[i]) - norm(ghost_v[i])) * AU_KM * 1000 / 86400, 3))
        # Size of the whole velocity change, direction included: the speed
        # difference alone understates a push that mostly turns the path.
        dvv_ms.append(round(norm(sub(real_v[i], ghost_v[i])) * AU_KM * 1000 / 86400, 3))
        R = unit(real_p[i]); N = unit(cross(real_p[i], real_v[i])); T = cross(N, R)
        rtn_km.append([round(dot(d, R) * AU_KM), round(dot(d, T) * AU_KM), round(dot(d, N) * AU_KM)])
        ang_as.append(round(angle(sub(real_p[i], earth_p[i]), sub(ghost_p[i], earth_p[i])) * ARCSEC, 2))
        xc_km.append(round(norm(sub(real_p[i], paper_p[i])) * AU_KM))

    def at(iso):
        i = (datetime.date.fromisoformat(iso) - datetime.date.fromisoformat(START)).days
        i = max(0, min(n - 1, i))
        return {"date": dates[i], "sep_km": sep_km[i], "dv_ms": dv_ms[i], "dvv_ms": dvv_ms[i], "arcsec": ang_as[i],
                "rtn_km": rtn_km[i], "crosscheck_km": xc_km[i],
                "r_au": round(norm(real_p[i]), 3)}

    today = time.strftime("%Y-%m-%d")
    milestones = {
        "end_pre_arc": at(PAPER_ARCS["pre"][1]),
        "perihelion": at("2025-10-29"),
        "jupiter": at("2026-03-16"),
        "end_post_arc": at(PAPER_ARCS["post"][1]),
        "fetched": at(today),
        "end": at(STOP),
    }
    # The two answers should agree in scale where the paper's orbit applies.
    ratio = (milestones["end_post_arc"]["crosscheck_km"] / max(1, milestones["end_post_arc"]["sep_km"]))
    print(f"  at end of paper's post arc ({PAPER_ARCS['post'][1]}): ghost {milestones['end_post_arc']['sep_km']:,} km, "
          f"paper-GR cross-check {milestones['end_post_arc']['crosscheck_km']:,} km (ratio {ratio:.2f})")
    if not (0.1 <= ratio <= 10):
        sys.exit("ABORT: the two gravity-only answers disagree by more than an order of magnitude.")

    out = {
        "what": "3I/ATLAS real path (JPL#54, push on) minus the same object with the push switched off on "
                + START + ". All orbits integrated by JPL Horizons.",
        "fetched": today,
        "solution": {k: JPL54[k] for k in JPL54 if k != "label"},
        "solution_label": JPL54["label"],
        "arrival_elements": arrival,
        "paper": {"arxiv": "2610.38485", "arcs": PAPER_ARCS, "gr_orbit": PAPER_GR,
                  "astrometric_rms_arcsec": 0.25},
        "validation": {"worst_au_vs_shipped": float(f"{worst:.3e}"), "tolerance_au": TOL_AU},
        "start": START, "step_days": 1, "n": n,
        "series": {"sep_km": sep_km, "dv_ms": dv_ms, "dvv_ms": dvv_ms, "arcsec": ang_as, "rtn_km": rtn_km,
                   "crosscheck_km": xc_km},
        "milestones": milestones,
        "ghost": {"start": dates[0], "end": dates[-1], "step_days": 1, "n": n,
                  "pos": [[round(x, 6) for x in p] for p in ghost_p]},
    }
    dest = os.path.join(ROOT, "data", "counterfactual.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"Wrote {dest} ({os.path.getsize(dest) // 1024} KB)")
    for k, m in milestones.items():
        print(f"  {k:13s} {m['date']}  sep {m['sep_km']:>10,} km  dspeed {m['dv_ms']:>7} m/s  dv {m['dvv_ms']:>6} m/s  "
              f"{m['arcsec']:>8} arcsec  RTN {m['rtn_km']}")
    bake_js()


if __name__ == "__main__":
    sys.exit(main())
