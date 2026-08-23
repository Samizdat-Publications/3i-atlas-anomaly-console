"""Describe what a data refresh actually changed, as markdown.

Compares the working-tree data files against the versions committed at HEAD and
prints a short report — used as the body of the pull request that
.github/workflows/refresh-data.yml opens, and useful by hand after running the
fetchers locally:

    python tools/fetch_fireballs.py && python tools/refresh_report.py

The per-run `fetched` stamp is ignored when deciding whether anything changed —
otherwise every run would look like a change and open a pull request saying
nothing.

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


def _strip_stamp(d):
    """Everything except the fetch timestamp, which changes on every run and is
    not a change in the data."""
    if not isinstance(d, dict):
        return d
    return {k: v for k, v in d.items() if k not in ("fetched",)}


def reports_section(lines):
    """AMS eyewitness counts and GMN photometry — the datasets cases F-03 and
    F-04 argue from, so a change here can invalidate case-file text just as a
    revised CNEOS row can."""
    changed = False

    a_old, a_new = committed("data/ams-reports.json"), working("data/ams-reports.json")
    if a_new and _strip_stamp(a_old or {}) != _strip_stamp(a_new):
        changed = True
        lines.append("### AMS eyewitness reports")
        lines.append("")
        if not a_old:
            lines.append("First pull: %d years, %s-%s."
                         % (len(a_new.get("years", {})), a_new.get("first_year"), a_new.get("last_year")))
        else:
            o, n = a_old.get("years", {}), a_new.get("years", {})
            new_years = sorted(set(n) - set(o))
            moved = sorted(y for y in set(n) & set(o) if n[y] != o[y])
            if new_years:
                lines.append("- New year(s): %s" % ", ".join(new_years))
            for y in moved:
                for key in n[y]:
                    if o[y].get(key) != n[y][key]:
                        lines.append("- %s `%s`: %s → %s"
                                     % (y, key, sum(o[y].get(key, [])), sum(n[y][key])))
        lines.append("")

    g_old, g_new = committed("data/gmn-monthly.json"), working("data/gmn-monthly.json")
    if g_new and _strip_stamp(g_old or {}) != _strip_stamp(g_new):
        changed = True
        om = (g_old or {}).get("months", {})
        nm = g_new.get("months", {})
        added = sorted(k for k in nm if k not in om and nm[k])
        revised = sorted(k for k in nm if k in om and nm[k] != om[k])
        lines.append("### Global Meteor Network")
        lines.append("")
        if added:
            lines.append("- New month(s): %s" % ", ".join(added))
        for k in revised:
            a, b = om[k], nm[k]
            if a and b:
                lines.append("- %s: %d → %d meteors, bright fraction %.4f%% → %.4f%%"
                             % (k, a["n"], b["n"], 100.0 * a["counts"]["m4"] / a["n"],
                                100.0 * b["counts"]["m4"] / b["n"]))
        lines.append("")

    if changed:
        lines.append("> ⚠️ Cases **F-03** and **F-04** quote figures computed from these "
                     "datasets. `tools/fireball_rate_check.py` re-derives every one of them; "
                     "if it failed, the case text needs rewriting before this is merged.")
        lines.append("")
    return changed


def main():
    lines = ["Automated refresh of the upstream datasets. **Nothing here is hand-written** — "
             "the fetchers pulled it and `tools/build.py` rebuilt the bundle.", ""]
    changed = fireball_section(lines)
    changed = ephemeris_section(lines) or changed
    changed = reports_section(lines) or changed
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
