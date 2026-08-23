"""Boil the fetched transcripts down to something you can paste into a chat.

data/transcripts/ is gitignored on purpose — those are someone else's words and
this repo is public — which also means a cloud session cannot read them. This
reads them locally and prints only the CLAIM-BEARING sentences: the ones that
name a fireball-ish subject and then say something checkable about it, whether
that is a number, a trend, or a correlation with a place. Small enough to paste
from a phone; specific enough to check a row of CNEOS against.

    cd "C:\\Users\\stewa\\OneDrive\\Documents\\Claude\\3I ATLAS Anomaly Console"
    python tools/transcript_digest.py

    python tools/transcript_digest.py --per-video 8      # more from each
    python tools/transcript_digest.py --grep volcano     # one theme only
    python tools/transcript_digest.py --numbers          # only quantitative claims

A full copy also lands in data/transcripts/digest.md, which stays gitignored
with everything else in that folder. What belongs in the repo is the analysis
that comes out of this, not the source.
"""
import argparse, glob, io, os, re, sys, collections

for _s in (sys.stdout, sys.stderr):          # Windows cp1252 vs. an em dash
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "transcripts")

# A sentence is interesting when it names a SUBJECT and then says something
# that can be checked. Subject alone is just narration.
SUBJECT = r"fireball|bolide|meteor|meteorite|uap|ufo|cneos|3i|atlas|interstellar|impact|asteroid|comet"
TREND = (r"increas|rising|risen|climb|more than ever|record|trend|uptick|spike|surge|outbreak|"
         r"unprecedented|never seen|doubl|tripl|accelerat|frequen|rate of|per year|per month|"
         r"last year|this year|decade")
PLACE = (r"volcano|volcanic|eruption|nuclear|reactor|power plant|air base|military|"
         r"same place|same location|same area|same spot|cluster|correlat|coincid|pattern")
MEASURE = (r"kiloton|kilotonne|\bkt\b|km/s|kilometers per second|joule|magnitude|altitude|"
           r"sonic boom|infrasound|trajectory|velocity|speed of|energy of|degrees")

GROUPS = [("trend", TREND), ("place", PLACE), ("measure", MEASURE)]


def sentences(text):
    """Auto-captions have no punctuation to speak of, so fall back to chunking."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) <= 320:
            out.append(p)
            continue
        words = p.split()                       # unpunctuated run — cut into ~40-word lines
        for i in range(0, len(words), 40):
            out.append(" ".join(words[i:i + 40]))
    return out


def score(s):
    low = s.lower()
    tags = [name for name, pat in GROUPS if re.search(pat, low)]
    n = bool(re.search(r"\d", s))
    if n:
        tags.append("number")
    if not re.search(SUBJECT, low):
        # No subject noun, but "the energy on this one was 1.2 kilotons at 28 km"
        # is the most checkable sentence in the video and refers to its subject
        # by pronoun. A measured quantity carries itself; nothing else does.
        if not (n and "measure" in tags):
            return 0, []
    if not tags:
        return 0, []
    # a number plus a trend word is the shape of the claim we most want to test
    return len(tags) + (2 if ("number" in tags and "trend" in tags) else 0), tags


def read(path):
    with io.open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().split("\n")
    title, date, url, body = "", "", "", lines
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = lines[1:]
    if body and body[0].startswith("# "):
        head = body[0][2:].strip().split()
        date = head[0] if head and re.match(r"^\d{8}$", head[0]) else ""
        url = head[-1] if head and head[-1].startswith("http") else ""
        body = body[1:]
    return title, date, url, "\n".join(body).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-video", type=int, default=5, help="claim lines to keep per transcript")
    ap.add_argument("--grep", help="only sentences matching this word/regex")
    ap.add_argument("--numbers", action="store_true", help="only sentences containing a number")
    ap.add_argument("--max-chars", type=int, default=14000,
                    help="stop printing past this; the file on disk is never truncated")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(SRC, "*.txt")))
    if not files:
        sys.exit("No transcripts in %s — run tools/fetch_transcripts.py first." % SRC)

    themes = collections.Counter()
    blocks = []
    for path in files:
        title, date, url, body = read(path)
        picks = []
        for s in sentences(body):
            sc, tags = score(s)
            if not sc:
                continue
            if args.numbers and "number" not in tags:
                continue
            if args.grep and not re.search(args.grep, s, re.I):
                continue
            picks.append((sc, s, tags))
        for _, _, tags in picks:
            themes.update(tags)
        picks.sort(key=lambda p: -p[0])
        picks = picks[:args.per_video]
        if not picks:
            continue
        vid = os.path.basename(path).rsplit("-", 1)[-1][:-4]
        head = "## %s · %s · %s" % (date or "????????", vid, title[:78])
        lines = [head] + ["- %s" % re.sub(r"\s+", " ", s).strip() for _, s, _ in picks]
        blocks.append("\n".join(lines))

    body = "\n\n".join(blocks)
    summary = ("# Transcript digest — %d transcripts, %d with claim lines\n"
               "# themes: %s\n" % (len(files), len(blocks),
                                   ", ".join("%s %d" % kv for kv in themes.most_common()) or "none"))

    out = os.path.join(SRC, "digest.md")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(summary + "\n" + body + "\n")

    print(summary)
    if len(body) <= args.max_chars:
        print(body)
    else:
        print(body[:args.max_chars])
        print("\n... truncated at %d of %d chars. The whole thing is in %s."
              % (args.max_chars, len(body), out))
        print("Narrow it: --per-video 3, or --grep volcano, or --numbers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
