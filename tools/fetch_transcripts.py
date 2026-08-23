"""Bulk-pull YouTube transcripts for a channel into data/transcripts/ (local only).

Wraps yt-dlp. Written because the console keeps arguing with claims that are made
in videos, and reading fifty of them by hand is not a plan.

    pip install -U yt-dlp
    python tools/fetch_transcripts.py                      # default channel, last 365 days
    python tools/fetch_transcripts.py --since 2025-08-01
    python tools/fetch_transcripts.py --match fireball,meteor,atlas
    python tools/fetch_transcripts.py --channel @SomeOtherChannel
    python tools/fetch_transcripts.py --list                # just show what would be fetched

RUN THIS ON YOUR OWN MACHINE. YouTube blocks datacenter IPs — from a cloud
sandbox every request comes back "Sign in to confirm you're not a bot". From a
home connection it just works. If you do hit that from home, pass your browser's
cookies through:

    python tools/fetch_transcripts.py --cookies-from-browser chrome

Output: data/transcripts/YYYYMMDD-<id>.txt plus index.json. That directory is
GITIGNORED on purpose — those transcripts are someone else's work and this repo
is public. Analysis derived from them belongs in the repo; the transcripts
themselves do not.
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys

# Windows consoles default to cp1252 and a single em dash in a video title is
# enough to kill the run with UnicodeEncodeError halfway through a fetch.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "transcripts")
DEFAULT_CHANNEL = "@TheAngryAstronaut"


def need_ytdlp():
    """Base argv for yt-dlp. A list, never a string: on Windows the interpreter
    path is routinely 'C:\\Program Files\\Python312\\python.exe', and a shell
    string would split it at the space."""
    exe = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if exe:
        return [exe]
    try:
        import yt_dlp  # noqa: F401       importable but not on PATH — normal in a venv
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        sys.exit("yt-dlp not found. Install it with:  pip install -U yt-dlp")


def run(argv, **kw):
    # shell=False throughout: it also stops cmd.exe trying to expand the
    # %(id)s / %(ext)s in yt-dlp's output template as environment variables.
    return subprocess.run(argv, shell=False, text=True, capture_output=True, **kw)


def list_videos(ytdlp, channel, extra):
    """Channel listing without touching each video page — one request, fast."""
    url = "https://www.youtube.com/%s/videos" % channel.lstrip("/")
    r = run(ytdlp + ["--flat-playlist", "--dump-json"] + extra + [url])
    if r.returncode != 0 and not r.stdout.strip():
        sys.exit("Listing failed.\n" + (r.stderr or "").strip()[-1500:])
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            j = json.loads(line)
        except ValueError:
            continue
        out.append({
            "id": j.get("id"),
            "title": j.get("title") or "",
            # flat listings often omit upload_date; timestamp is usually there
            "date": j.get("upload_date") or ts_to_date(j.get("timestamp")),
            "duration": j.get("duration"),
            "url": "https://www.youtube.com/watch?v=" + (j.get("id") or ""),
        })
    return [v for v in out if v["id"]]


def ts_to_date(ts):
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y%m%d")


def _norm(w):
    return re.sub(r"[^\w']", "", w).lower()


def vtt_to_text(path):
    """Flatten a WebVTT caption file to readable prose.

    YouTube auto-captions scroll: each cue repeats the tail of the one before it
    with a word or two appended, and a single cue usually holds TWO lines of that
    rolling window. Parse by cue (not by line), then append only the words a cue
    adds beyond the longest overlap with what has already been emitted. Matching
    is done on punctuation-stripped lowercase tokens so "decade." still lines up
    with "decade".
    """
    cues, cur = [], []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            s = raw.strip()
            if not s or "-->" in s:
                if cur:
                    cues.append(" ".join(cur)); cur = []
                continue
            if s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or s.isdigit():
                continue
            s = re.sub(r"<[^>]+>", "", s)          # inline word-timing tags
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                cur.append(s)
    if cur:
        cues.append(" ".join(cur))

    words, norm = [], []
    for cue in cues:
        cw, cn = [], []
        for w in cue.split():
            n = _norm(w)
            if n:                                   # skip stray punctuation tokens
                cw.append(w); cn.append(n)
        if not cn:
            continue
        overlap = 0
        for n in range(min(len(norm), len(cn)), 0, -1):
            if norm[-n:] == cn[:n]:
                overlap = n
                break
        words.extend(cw[overlap:]); norm.extend(cn[overlap:])

    text = re.sub(r"\s+", " ", " ".join(words)).strip()
    return re.sub(r"(?<=[.!?]) (?=[A-Z])", "\n", text)   # soft paragraphs


def fetch_one(ytdlp, vid, extra, tmp):
    r = run(ytdlp + ["--skip-download", "--write-auto-subs", "--write-subs",
                     "--sub-langs", "en.*", "--sub-format", "vtt", "--no-warnings"]
            + extra + ["-o", os.path.join(tmp, "%(id)s.%(ext)s"),
                       "https://www.youtube.com/watch?v=" + vid])
    got = [f for f in os.listdir(tmp) if f.startswith(vid) and f.endswith(".vtt")]
    if not got:
        return None, (r.stderr or r.stdout or "").strip().splitlines()[-1:] or ["no captions"]
    got.sort(key=lambda f: (".en.vtt" not in f, len(f)))   # prefer plain en
    return os.path.join(tmp, got[0]), None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channel", default=DEFAULT_CHANNEL)
    ap.add_argument("--since", help="YYYY-MM-DD (default: 365 days ago)")
    ap.add_argument("--match", help="comma-separated words; keep titles containing any of them")
    ap.add_argument("--limit", type=int, default=0, help="stop after N videos")
    ap.add_argument("--list", action="store_true", help="list matches and exit")
    ap.add_argument("--cookies-from-browser", dest="cookies",
                    help="chrome | firefox | edge | safari — use if YouTube asks you to prove you are not a bot")
    ap.add_argument("--sleep", type=float, default=2.0, help="seconds between videos (be polite)")
    args = ap.parse_args()

    ytdlp = need_ytdlp()
    extra = []
    if args.cookies:
        extra += ["--cookies-from-browser", args.cookies]
    if args.sleep:
        extra += ["--sleep-requests", "%.1f" % args.sleep]

    since = args.since or (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    since_c = since.replace("-", "")
    words = [w.strip().lower() for w in (args.match or "").split(",") if w.strip()]

    print("Listing %s ..." % args.channel)
    vids = list_videos(ytdlp, args.channel, extra)
    print("  %d videos visible on the channel" % len(vids))

    keep = []
    undated = 0
    for v in vids:
        if not v["date"]:
            undated += 1                      # keep it; a missing date is not a reason to skip
        elif v["date"] < since_c:
            continue
        if words and not any(w in v["title"].lower() for w in words):
            continue
        keep.append(v)
    if args.limit:
        keep = keep[:args.limit]

    print("  %d match (since %s%s)%s" % (len(keep), since,
                                         ", title contains " + "/".join(words) if words else "",
                                         "; %d had no date and were kept" % undated if undated else ""))
    if args.list or not keep:
        for v in keep:
            print("  %s  %s" % (v["date"] or "????????", v["title"][:88]))
        return 0

    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, ".tmp")
    os.makedirs(tmp, exist_ok=True)

    index, failed = [], []
    for i, v in enumerate(keep, 1):
        dest = os.path.join(OUT, "%s-%s.txt" % (v["date"] or "00000000", v["id"]))
        if os.path.exists(dest):
            print("  [%d/%d] have %s" % (i, len(keep), os.path.basename(dest)))
            index.append(dict(v, file=os.path.basename(dest)))
            continue
        print("  [%d/%d] %s — %s" % (i, len(keep), v["id"], v["title"][:64]), flush=True)
        vtt, err = fetch_one(ytdlp, v["id"], extra, tmp)
        if not vtt:
            failed.append((v, err[0] if err else "?"))
            continue
        text = vtt_to_text(vtt)
        os.remove(vtt)
        if len(text) < 200:
            failed.append((v, "transcript suspiciously short (%d chars)" % len(text)))
            continue
        with open(dest, "w", encoding="utf-8") as f:
            f.write("# %s\n# %s  %s\n\n%s\n" % (v["title"], v["date"] or "", v["url"], text))
        index.append(dict(v, file=os.path.basename(dest), chars=len(text)))

    shutil.rmtree(tmp, ignore_errors=True)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"channel": args.channel, "since": since,
                   "fetched": datetime.date.today().isoformat(),
                   "videos": index}, f, ensure_ascii=False, indent=1)

    print("\n%d transcripts in %s" % (len(index), OUT))
    if failed:
        print("%d without usable captions:" % len(failed))
        for v, why in failed[:12]:
            print("  %s  %s  (%s)" % (v["date"] or "????????", v["title"][:56], str(why)[:60]))
    print("\ndata/transcripts/ is gitignored — these are someone else's words. "
          "Commit analysis derived from them, not the transcripts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
