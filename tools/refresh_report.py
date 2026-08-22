"""Describe what a data refresh actually changed, as markdown.

Compares the working-tree data files against the versions committed at HEAD and
prints a short report — used as the body of the pull request that
.github/workflows/refresh-data.yml opens, and useful by hand after running the
fetchers locally:

    python tools/fetch_fireballs.py && python tools/refresh_report.py

Prints "No change." when the upstream data is identical, so the workflow can use
the exit status: 0 = something changed, 1 = nothing did.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def committed(path):
    """The version of `path` at HEAD, or None if it is not committed yet."""
    try:
        blob = subprocess.run(["git", "show", "HEAD:" + path], cwd=ROOT,
                              capture_output=True, check=True).stdout
        return json.loads(blob.decode("utf-8"))
    except (subprocess.CalledProcessError, ValueError):
        return None


def working(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    with open(full, encoding="utf-8") as f:
        return json.load(f)


def fmt_event(e):
    lat, lon = e[3], e[4]
    where = "no reported position"
    if lat is not None and lon is not None:
        where = "%.1f°%s %.1f°%s" % (abs(lat), "S" if lat < 0 else "N",
                                     abs(lon), "W" if lon < 0 else "E")
    kt = "%s kt" % e[2] if e[2] is not None else "energy not reported"
    speed = ", %s km/s" % e[6] if e[6] is not None else ""
    return "`%s` — %s, %s%s" % (e[0], where, kt, speed)


def fireball_section(lines):
    old, new = committed("data/fireballs.json"), working("data/fireballs.json")
    if not new:
        return False
    if not old:
        lines.append("### Fireballs\n\nFirst commit of the CNEOS catalog: **%d rows**.\n" % new["count"])
        return True
    if old.get("events") == new.get("events"):
        return False

    seen = {tuple(e[:1]) for e in old["events"]}
    added = [e for e in new["events"] if tuple(e[:1]) not in seen]
    new_dates = {e[0] for e in new["events"]}
    removed = [e for e in old["events"] if e[0] not in new_dates]
    # a row whose date survives but whose measurements were revised upstream
    old_by_date = {e[0]: e for e in old["events"]}
    revised = [e for e in new["events"]
               if e[0] in old_by_date and old_by_date[e[0]] != e]

    lines.append("### Fireballs — CNEOS")
    lines.append("")
    lines.append("| | before | after |")
    lines.append("|---|--:|--:|")
    lines.append("| rows | %d | **%d** |" % (old["count"], new["count"]))
    lines.append("| with a position | %d | **%d** |" % (old["located"], new["located"]))
    lines.append("| latest event | %s | **%s** |" % (old["last"][:10], new["last"][:10]))
    lines.append("")

    if added:
        lines.append("**%d new row%s:**" % (len(added), "" if len(added) == 1 else "s"))
        lines.append("")
        for e in sorted(added, key=lambda e: -(e[2] or 0))[:12]:
            lines.append("- " + fmt_event(e))
        if len(added) > 12:
            lines.append("- …and %d more" % (len(added) - 12))
        lines.append("")
    if revised:
        lines.append("**%d row%s revised upstream** (same timestamp, changed values) — "
                     "worth a look, since the case files quote these numbers:"
                     % (len(revised), "" if len(revised) == 1 else "s"))
        lines.append("")
        for e in revised[:8]:
            lines.append("- " + fmt_event(e) + ("  ← **%s**" % e[7] if e[7] else ""))
        lines.append("")
    if removed:
        lines.append("**%d row%s withdrawn from the catalog:**" % (len(removed), "" if len(removed) == 1 else "s"))
        lines.append("")
        for e in removed[:8]:
            lines.append("- " + fmt_event(e))
        lines.append("")

    # The two candidates are the whole point of the register — call them out.
    tagged_old = {e[7]: e for e in old["events"] if e[7]}
    tagged_new = {e[7]: e for e in new["events"] if e[7]}
    for tag in ("IM1", "IM2"):
        if tag in tagged_old and tag not in tagged_new:
            lines.append("> ⚠️ **%s no longer matches any row** — its case file will lose its "
                         "catalog anchor. Check `IM_TAGS` in `tools/fetch_fireballs.py`.\n" % tag)
        elif tag in tagged_new and tagged_old.get(tag) != tagged_new[tag]:
            lines.append("> ⚠️ **%s's row changed.** Case file text quotes these values verbatim "
                         "— re-read `data/fireball-cases.json` before merging.\n" % tag)
    return True


def ephemeris_section(lines):
    old, new = committed("data/ephemeris.json"), working("data/ephemeris.json")
    if not new or not old or old == new:
        return False
    lines.append("### Ephemerides — JPL Horizons")
    lines.append("")
    lines.append("Close approaches recomputed from the new vectors:")
    lines.append("")
    lines.append("| era | body | before | after |")
    lines.append("|---|---|---|---|")
    changed_any = False
    for era, edata in (new.get("eras") or {}).items():
        old_ca = ((old.get("eras") or {}).get(era) or {}).get("close_approaches") or {}
        for body, ca in (edata.get("close_approaches") or {}).items():
            before = old_ca.get(body)
            if before == ca:
                continue
            changed_any = True
            lines.append("| %s | %s | %s AU @ %s | **%s AU @ %s** |" % (
                era, body,
                before.get("au") if before else "—", before.get("date") if before else "—",
                ca.get("au"), ca.get("date")))
    if not changed_any:
        lines.append("| — | — | vectors changed, no close approach moved | |")
    lines.append("")
    lines.append("A shifted close approach means the README, the landing page and some case "
                 "file text quote a stale number. Grep for the old value before merging.")
    lines.append("")
    return True


def main():
    lines = ["Automated refresh of the upstream datasets. **Nothing here is hand-written** — "
             "the fetchers pulled it and `tools/build.py` rebuilt the bundle.", ""]
    changed = fireball_section(lines)
    changed = ephemeris_section(lines) or changed
    if not changed:
        print("No change.")
        return 1
    lines.append("---")
    lines.append("")
    lines.append("Merging this deploys it: a push to `main` rebuilds and ships to Cloudflare Pages.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
