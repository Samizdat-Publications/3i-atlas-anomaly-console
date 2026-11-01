"""Import a transcript fetched some other way into data/transcripts/.

fetch_transcripts.py is the normal route, but YouTube rate-limits the caption
endpoint (HTTP 429) for hours at a time, even from a home connection. When that
happens a transcript can be pulled through a captions API instead (the Firecrawl
'youtube-com / videos/video_transcript' capability returns JSON with
`video_id`, `title` and `full_text`), saved to a file, and imported here so it
lands in exactly the same format and index as everything else.

    python tools/import_transcript.py <saved.json> --date 2026-11-01

The JSON may be the raw tool result ({data: {alexandria: [{data: {...}}]}}) or
just the inner transcript object.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "transcripts")


def inner(d):
    if "full_text" in d:
        return d
    try:
        return d["data"]["alexandria"][0]["data"]
    except (KeyError, IndexError, TypeError):
        sys.exit("No transcript object (full_text) found in that JSON.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json_file")
    ap.add_argument("--date", required=True, help="upload date, YYYY-MM-DD")
    args = ap.parse_args()
    with open(args.json_file, encoding="utf-8") as f:
        t = inner(json.load(f))
    vid, title = t["video_id"], t.get("title") or ""
    text = re.sub(r"\s+", " ", t["full_text"]).strip()
    if len(text) < 200:
        sys.exit("Transcript suspiciously short (%d chars)." % len(text))
    date = args.date.replace("-", "")
    url = "https://www.youtube.com/watch?v=" + vid
    name = "%s-%s.txt" % (date, vid)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write("# %s\n# %s  %s\n\n%s\n" % (title, date, url, text))

    idx_path = os.path.join(OUT, "index.json")
    with open(idx_path, encoding="utf-8") as f:
        idx = json.load(f)
    idx["videos"] = [v for v in idx["videos"] if v["id"] != vid]
    idx["videos"].append({"id": vid, "title": title, "date": date, "url": url, "file": name,
                          "chars": len(text), "via": "captions API (YouTube 429 on direct fetch)"})
    idx["videos"].sort(key=lambda v: v.get("date") or "")
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
    print("Wrote %s (%d chars); index now %d videos" % (name, len(text), len(idx["videos"])))


if __name__ == "__main__":
    sys.exit(main())
