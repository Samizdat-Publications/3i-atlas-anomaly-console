"""Write the "now tracking" block into the README and both landing pages.

The console follows two running sources, The Angry Astronaut's videos and Avi
Loeb's posts. data/tracking.json records the newest one of each that has been
built into the console; this script renders that record into every page that
shows it, between <!-- tracking:start --> and <!-- tracking:end --> markers,
and refreshes the counts and index table in data/transcripts/README.md from
data/transcripts/index.json.

    python tools/update_tracking.py           # rewrite the files
    python tools/update_tracking.py --check   # exit 1 if any file is stale (CI)

The video in tracking.json must be one whose transcript is in the repo: the
claim behind "now including data through" is that its transcript was read.
"""
import datetime
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONSOLE = "https://3i-atlas-anomaly-console.pages.dev/"
START, END = "<!-- tracking:start -->", "<!-- tracking:end -->"

# (path, format, base URL for links into the console)
TARGETS = [
    ("README.md", "md", CONSOLE),
    ("src/about.html", "html", "/"),
    ("site/index.html", "html", CONSOLE),
]


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def nice_date(iso):
    d = datetime.date.fromisoformat(iso)
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def title(t):
    # YouTube titles carry double spaces after "!"; they collapse in HTML anyway.
    return re.sub(r"\s+", " ", t).strip()


def check_record(trk, index):
    aa = trk["angry_astronaut"]
    vids = {v["id"]: v for v in index["videos"]}
    v = vids.get(aa["video_id"])
    if not v:
        sys.exit("tracking.json names video %s, which has no transcript in data/transcripts/" % aa["video_id"])
    if title(v["title"]) != title(aa["title"]):
        sys.exit("tracking.json title does not match the transcript index:\n  %r\n  %r" % (aa["title"], v["title"]))
    if v["date"] != aa["date"].replace("-", ""):
        sys.exit("tracking.json date %s does not match the transcript index %s" % (aa["date"], v["date"]))


def and_list(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def used_md(src, base):
    return and_list(["[%s](%s%s)" % (u["label"], base, u["hash"]) for u in src["used_in"]])


def used_html(src, base):
    return and_list(['<a href="%s%s">%s</a>' % (base, u["hash"], html.escape(u["label"])) for u in src["used_in"]])


def block_md(trk, base):
    aa, lo = trk["angry_astronaut"], trk["loeb"]
    return "\n".join([
        "> ### Now tracking: The Angry Astronaut and Avi Loeb",
        ">",
        "> This console follows two running sources on 3I/ATLAS and the fireball claims, and checks",
        "> each new claim against the data as it comes in.",
        ">",
        "> - **[%s](%s)** on %s: now including data through **[%s](%s)** (%s), built into %s."
        % (aa["who"], aa["channel_url"], aa["where"], title(aa["title"]), aa["url"], nice_date(aa["date"]), used_md(aa, base)),
        "> - **[%s](%s)** on %s: through **[%s](%s)** (%s), built into %s."
        % (lo["who"], lo["channel_url"], lo["where"], title(lo["title"]), lo["url"], nice_date(lo["date"]), used_md(lo, base)),
        ">",
        "> Everything else is checked against the published record to %s." % nice_date(trk["content_current_to"]),
    ])


def block_html(trk, base):
    aa, lo = trk["angry_astronaut"], trk["loeb"]
    e = html.escape

    def li(s, lead):
        return ('    <li><b><a href="%s">%s</a></b> on %s: %s <a class="tracking-src" href="%s">%s</a> (%s), built into %s.</li>'
                % (e(s["channel_url"]), e(s["who"]), e(s["where"]), lead, e(s["url"]), e(title(s["title"])),
                   nice_date(s["date"]), used_html(s, base)))
    return "\n".join([
        '<aside class="tracking" aria-labelledby="tracking-title">',
        '  <p class="tracking-k" id="tracking-title">NOW TRACKING &middot; UPDATED %s</p>' % nice_date(trk["content_current_to"]).upper(),
        '  <p class="tracking-lede">This console follows two running sources on 3I/ATLAS and the fireball claims, and checks each new claim against the data as it comes in.</p>',
        '  <ul>',
        li(aa, "now including data through"),
        li(lo, "through"),
        '  </ul>',
        '</aside>',
    ])


def splice(text, block, rel):
    i, j = text.find(START), text.find(END)
    if i < 0 or j < i:
        sys.exit("%s has no %s ... %s markers" % (rel, START, END))
    return text[:i + len(START)] + "\n" + block + "\n" + text[j:]


def transcripts_readme(text, index):
    vids = sorted(index["videos"], key=lambda v: (v["date"], v["id"]))
    tdir = os.path.join(ROOT, "data", "transcripts")
    words = 0
    for v in vids:
        with open(os.path.join(tdir, v["file"]), encoding="utf-8") as f:
            words += len(f.read().split())
    n = len(vids)
    batches = len([f for f in os.listdir(os.path.join(tdir, "notebook")) if f.startswith("transcripts-")])
    iso = lambda d: "%s-%s-%s" % (d[:4], d[4:6], d[6:])

    text = re.sub(r"Auto-generated captions from \*\*\d+ YouTube videos\*\*",
                  "Auto-generated captions from **%d YouTube videos**" % n, text)
    text = re.sub(r"covering \d{4}-\d\d-\d\d to \d{4}-\d\d-\d\d \S+ roughly [\d,]+ words\.",
                  "covering %s to %s, roughly {:,} words.".format(words) % (iso(vids[0]["date"]), iso(vids[-1]["date"])), text)
    text = re.sub(r"`\*\.txt` \S+ \d+ individual transcripts",
                  "`*.txt`: %d individual transcripts" % n, text)
    text = re.sub(r"consolidated into \d+ files for research-notebook ingestion,\n  which caps the number of sources far below \d+\.",
                  "consolidated into %d files for research-notebook ingestion,\n  which caps the number of sources far below %d." % (batches, n), text)
    rows = ["| %s | %s | <%s> |" % (iso(v["date"]), v["title"].replace("|", "\\|"), v["url"]) for v in vids]
    head = "| Date | Title | Source |\n|---|---|---|\n"
    i = text.index(head) + len(head)
    return text[:i] + "\n".join(rows) + "\n"


def main():
    check = "--check" in sys.argv
    trk = json.loads(load("data/tracking.json"))
    index = json.loads(load("data/transcripts/index.json"))
    check_record(trk, index)

    out = {}
    for rel, fmt, base in TARGETS:
        block = block_md(trk, base) if fmt == "md" else block_html(trk, base)
        out[rel] = splice(load(rel), block, rel)
    out["data/transcripts/README.md"] = transcripts_readme(load("data/transcripts/README.md"), index)

    stale = [rel for rel, new in out.items() if load(rel) != new]
    if check:
        if stale:
            sys.exit("stale, run python tools/update_tracking.py: " + ", ".join(stale))
        print("tracking block current in %d files" % len(out))
        return
    for rel in stale:
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(out[rel])
    print("updated: " + (", ".join(stale) if stale else "nothing, all current"))


if __name__ == "__main__":
    main()
