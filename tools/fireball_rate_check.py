"""Recompute the per-year statistics case file F-03 quotes, and verify them.

F-03 ("Are fireballs actually increasing?") is the one case file whose argument
is made out of numbers derived from the shipped catalog rather than from a
published paper. Those numbers go stale the moment CNEOS adds rows, so they are
checked here instead of trusted.

    python tools/fireball_rate_check.py           # print the table, verify F-03
    python tools/fireball_rate_check.py --quiet   # exit status only

Exit 0 = every figure quoted in F-03 still matches the data. Exit 1 = drift; the
case file needs rewriting before the refresh is merged.
"""
import json, os, re, sys, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Eras the case file argues over. Keep in step with data/fireball-cases.json.
ERAS = [(2000, 2009), (2010, 2019), (2020, 2025)]
SPARSE_TO = 1993          # last year before the satellite record proper begins
MONTH_BASE = (2000, 2023)
MONTH_RECENT = 2024


def load():
    with open(os.path.join(ROOT, "data", "fireballs.json"), encoding="utf-8") as f:
        return json.load(f)


def stats(d):
    ev = d["events"]
    per_year = collections.Counter(e[0][:4] for e in ev)
    kt1 = collections.Counter(e[0][:4] for e in ev if (e[2] or 0) >= 1)
    kt5 = collections.Counter(e[0][:4] for e in ev if (e[2] or 0) >= 5)
    per_month = collections.Counter(e[0][:7] for e in ev)

    def rate(counter, a, b):
        return sum(counter.get(str(y), 0) for y in range(a, b + 1)) / (b - a + 1)

    last = d["last"]
    last_year = int(last[:4])
    doy = (datetime.date.fromisoformat(last) - datetime.date(last_year, 1, 1)).days + 1

    base_months = [per_month.get("%d-%02d" % (y, m), 0)
                   for y in range(MONTH_BASE[0], MONTH_BASE[1] + 1) for m in range(1, 13)]
    recent_months = [v for k, v in per_month.items() if int(k[:4]) >= MONTH_RECENT and k < last[:7]]

    return {
        "count": d["count"], "first": d["first"], "last": last,
        "sparse_rate": rate(per_year, int(d["first"][:4]), SPARSE_TO),
        "first_full_year": min((y for y in range(SPARSE_TO + 1, last_year + 1)
                                if per_year.get(str(y), 0) >= 10), default=None),
        "eras": [(a, b, rate(per_year, a, b), rate(kt1, a, b), rate(kt5, a, b)) for a, b in ERAS],
        "partial_year": last_year,
        "partial_n": per_year.get(str(last_year), 0),
        "partial_pace": per_year.get(str(last_year), 0) * 365.0 / doy,
        "month_base": sum(base_months) / len(base_months),
        "month_recent": sum(recent_months) / len(recent_months) if recent_months else 0.0,
    }


def report(s):
    print("CNEOS catalog: %d rows, %s .. %s" % (s["count"], s["first"], s["last"]))
    print("  pre-record (through %d): %.1f events/yr" % (SPARSE_TO, s["sparse_rate"]))
    print("  record begins in earnest: %s" % s["first_full_year"])
    for a, b, all_r, k1, k5 in s["eras"]:
        print("  %d-%d: all %.1f/yr   >=1kt %.1f/yr   >=5kt %.2f/yr" % (a, b, all_r, k1, k5))
    print("  %d so far: %d events, full-year pace %.0f" % (s["partial_year"], s["partial_n"], s["partial_pace"]))
    print("  monthly mean %d-%d: %.2f   vs %d+: %.2f"
          % (MONTH_BASE[0], MONTH_BASE[1], s["month_base"], MONTH_RECENT, s["month_recent"]))


def verify(s):
    """Every figure F-03 states must still be true of the data."""
    path = os.path.join(ROOT, "data", "fireball-cases.json")
    with open(path, encoding="utf-8") as f:
        case = next((c for c in json.load(f)["cases"] if c["id"] == "F-03"), None)
    if not case:
        print("F-03 not found — nothing to verify.")
        return 0
    text = " ".join([case.get("observation", ""), case.get("loeb_take", ""),
                     case.get("official_explanation", "")])
    # the prose writes 1,069 where the data says 1069
    text = re.sub(r"(?<=\d),(?=\d)", "", text)

    checks = [("row count", str(s["count"]), "%s events" % s["count"])]
    checks.append(("catalog span", s["first"], s["first"]))
    for a, b, all_r, k1, k5 in s["eras"]:
        checks.append(("%d-%d all" % (a, b), "%.1f" % all_r, "%.1f events a year" % all_r))
        checks.append(("%d-%d >=1kt" % (a, b), "%.1f" % k1, "%.1f per year at >=1kt" % k1))
        checks.append(("%d-%d >=5kt" % (a, b), "%.2f" % k5, "%.2f per year at >=5kt" % k5))
    checks.append(("partial-year pace", "%.0f" % s["partial_pace"], "pace of %.0f" % s["partial_pace"]))
    checks.append(("monthly baseline", "%.2f" % s["month_base"], "%.2f per month" % s["month_base"]))
    checks.append(("monthly recent", "%.2f" % s["month_recent"], "%.2f per month" % s["month_recent"]))

    bad = []
    for label, needle, human in checks:
        if needle not in text:
            bad.append("%s: data says %s, F-03 does not say so" % (label, needle))
    # the direction of the recent-months comparison is the claim's crux
    if s["month_recent"] > s["month_base"] and "slightly lower" in text:
        bad.append("recent monthly mean now EXCEEDS the baseline — F-03 still says 'slightly lower'")

    if bad:
        print("\nF-03 IS OUT OF DATE:")
        for b in bad:
            print("  - " + b)
        return 1
    print("\nF-03 checks out: every figure it quotes matches the current catalog.")
    return 0


def main():
    quiet = "--quiet" in sys.argv
    s = stats(load())
    if not quiet:
        report(s)
    return verify(s)


if __name__ == "__main__":
    sys.exit(main())
