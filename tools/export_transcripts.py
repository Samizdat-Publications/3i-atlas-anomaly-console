"""Consolidate the transcript corpus into a few uploadable documents.

The transcripts are the claim source for the whole register, so a research
notebook without them is working from the analysis but not the evidence. They
cannot be published here — this repository is public and they are a creator's
work — but they can be batched into a handful of files that a person uploads
into their own private notebook by hand.

    python tools/export_transcripts.py
    python tools/export_transcripts.py --out "C:/somewhere/else"

Reads data/transcripts/ (gitignored, local only) and writes batched Markdown to
the PRIVATE companion repo by default. Batching matters: a notebook typically
caps the NUMBER of sources well below 114, while allowing a very large word count
per source, so a few big files ingest where many small ones will not.

WHAT THIS IS NOT. It is not a licence to republish. The output belongs in a
private notebook or the private repo, never in the public one. What goes public
is the analysis derived from these, and short attributed excerpts inside case
files labelled as auto-caption transcription rather than as published text.
"""
import argparse, glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "transcripts")
DEFAULT_OUT = os.path.abspath(os.path.join(ROOT, os.pardir, "3i-atlas-transcripts", "notebook"))
BATCH_WORDS = 120000          # comfortably inside a per-source cap, few enough files


def read(path):
    with io.open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().split("\n")
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else os.path.basename(path)
    date, url, body = "", "", lines[1:]
    if body and body[0].startswith("# "):
        head = body[0][2:].strip().split()
        if head and re.match(r"^\d{8}$", head[0]):
            date = head[0]
        if head and head[-1].startswith("http"):
            url = head[-1]
        body = body[1:]
    return title, date, url, "\n".join(body).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--batch-words", type=int, default=BATCH_WORDS)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.src, "*.txt")))
    if not files:
        sys.exit("No transcripts in %s — nothing to export." % args.src)
    os.makedirs(args.out, exist_ok=True)

    docs = [read(p) for p in files]
    docs = [d for d in docs if d[3]]
    docs.sort(key=lambda d: d[1] or "")

    batches, cur, cur_words = [], [], 0
    for d in docs:
        w = len(d[3].split())
        if cur and cur_words + w > args.batch_words:
            batches.append(cur); cur, cur_words = [], 0
        cur.append(d); cur_words += w
    if cur:
        batches.append(cur)

    index = ["# Transcript corpus — batched for notebook upload\n",
             "> PRIVATE. Third-party content, consolidated by `tools/export_transcripts.py`",
             "> in the public console repo. Upload these into your own notebook; do not",
             "> republish them.\n",
             "%d transcripts, %d words, %d batch file(s).\n"
             % (len(docs), sum(len(d[3].split()) for d in docs), len(batches)),
             "| File | Videos | Date range | Words |", "|---|---|---|---|"]

    for i, b in enumerate(batches, 1):
        lo = (b[0][1] or "?")
        hi = (b[-1][1] or "?")
        name = "transcripts-%02d-%s-to-%s.md" % (i, lo, hi)
        out = ["# Transcript batch %d of %d — %s to %s\n" % (i, len(batches), lo, hi),
               "> Auto-generated captions of third-party videos, used as the CLAIM SOURCE for",
               "> the 3I/ATLAS Anomaly Review Console. Machine transcription: treat wording as",
               "> approximate and never quote it as a published text.\n",
               "%d videos in this batch.\n" % len(b), "---\n"]
        for title, date, url, body in b:
            pretty = "%s-%s-%s" % (date[:4], date[4:6], date[6:]) if len(date) == 8 else (date or "undated")
            out.append("## %s — %s\n" % (pretty, title))
            if url:
                out.append("Source: <%s>\n" % url)
            out.append(body + "\n")
            out.append("---\n")
        text = "\n".join(out)
        with io.open(os.path.join(args.out, name), "w", encoding="utf-8") as f:
            f.write(text)
        words = sum(len(d[3].split()) for d in b)
        index.append("| `%s` | %d | %s → %s | %d |" % (name, len(b), lo, hi, words))
        print("  %-46s %3d videos  %7d words" % (name, len(b), words))

    with io.open(os.path.join(args.out, "00-INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index) + "\n")
    print("\nWrote %d batch file(s) + 00-INDEX.md to %s" % (len(batches), args.out))
    print("These are someone else's words. Private notebook only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
