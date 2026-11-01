"""The orbit solution this console pins 3I/ATLAS to, and how to ask Horizons for it.

WHY PINNED: until 2026-10 Horizons served solution JPL#54 for C/2025 N1 (782 obs,
2025-05-15 .. 2026-02-19, the whole arc through perihelion). On 2026-10-21 JPL
replaced it with JPL#55, which SBDB labels "Temporary solution to support JWST
Program 13145": 117 observations from 2025-10-03 onward, nothing before
perihelion, and a transverse term of the opposite sign. Re-running a plain
DES=C/2025 N1 query would silently swap the shipped path for that one. So the
3I path is generated from #54's own elements and non-gravitational model,
submitted to Horizons as a user-defined object; Horizons then integrates it with
the same planets and small perturbers as its own record. Checked 2026-11-01:
the user-defined #54 reproduces the shipped #54 vectors to ~1e-11 AU.

Source of every number below: the header of the Horizons response for
DES=C/2025 N1 fetched 2026-07-24 (data/raw/3i_target.txt, gitignored), which
matches the paper's Table 1 (arXiv:2610.38485, "JPL SBDB NG solution #54").
"""
import time, urllib.parse, urllib.request

API = "https://ssd.jpl.nasa.gov/api/horizons.api"

JPL54 = {
    "label": "JPL#54",
    # Heliocentric IAU76/J2000 ecliptic osculating elements
    "EPOCH": "2461090.5",               # 2026-Feb-19.0 TDB
    "EC": "6.141351449317625",
    "QR": "1.356481057231181",
    "TP": "2460977.9952628477",
    "OM": "322.1696089290778",
    "W": "128.0228697185194",
    "IN": "175.1164570850441",
    # Non-gravitational model: g(r) = (1 au / r)^2, JPL's CO2 proxy
    "A1": "5.320206165314E-8",          # radial, au/d^2
    "A2": "1.148166060448E-8",          # transverse
    "A3": "-6.854491829872E-9",         # normal (out of the orbital plane)
    "DT": "9.478815",                   # days, peak offset after perihelion
    "R0": "1", "ALN": "1", "NM": "2", "NN": "0", "NK": "0",
}

NG_KEYS = ("A1", "A2", "A3", "DT", "R0", "ALN", "NM", "NN", "NK")
ELEM_KEYS = ("EPOCH", "EC", "QR", "TP", "OM", "W", "IN")


def user_params(elements, ng=None, name="3I"):
    """Horizons API parameters for a user-defined small body. `elements` holds
    ELEM_KEYS; `ng` holds NG_KEYS or is None for a gravity-only orbit."""
    p = {"COMMAND": "';'", "OBJECT": f"'{name}'", "ECLIP": "'J2000'"}
    for k in ELEM_KEYS:
        p[k] = str(elements[k])
    if ng:
        for k in NG_KEYS:
            p[k] = str(ng[k])
    return p


def horizons(extra, start, stop, step, ephem="VECTORS", tries=4):
    """One Horizons call, heliocentric ecliptic J2000, AU and days. Retries with
    backoff because the refresh may run unattended."""
    params = {
        "format": "text", "OBJ_DATA": "'NO'", "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": f"'{ephem}'", "CENTER": "'500@10'", "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'J2000'", "OUT_UNITS": "'AU-D'", "CSV_FORMAT": "'YES'",
        "START_TIME": f"'{start}'", "STOP_TIME": f"'{stop}'", "STEP_SIZE": f"'{step}'",
    }
    if ephem == "VECTORS":
        params["VEC_TABLE"] = "'2'"
    params.update(extra)
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "3i-atlas-console/2.19"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                text = r.read().decode("utf-8", "replace")
            if "$$SOE" not in text:
                raise RuntimeError("Horizons returned no ephemeris block:\n" + text[:1500])
            return text
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * 2 ** i)


def jpl54_params():
    return user_params(JPL54, JPL54, name="3I JPL54")
