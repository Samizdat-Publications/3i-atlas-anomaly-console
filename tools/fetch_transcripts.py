"""Bulk-pull YouTube transcripts for a channel into data/transcripts/ (local only).

Wraps yt-dlp. Written because the console keeps arguing with claims that are made
in videos, and reading fifty of them by hand is not a plan.

    pip install -U yt-dlp
    python tools/fetch_transcripts.py                      # default channel, last 365 days
    python tools/fetch_transcripts.py --since 2025-08-01
    python tools/fetch_transcripts.py --match fireball,meteor,atlas
    python tools/fetch_transcripts.py --channel @SomeOtherChannel
    python tools/fetch_transcripts.py --list                # just show what would be fetched

DATES: YouTube's channel listing is fast because it does not open each video,
and the price of that is that it carries no upload date at all — every entry
comes back undated. Rather than ask YouTube 1,500 times, this walks the listing
(which is newest-first) with a binary search to find where uploads cross
--since: about eleven probes instead of fifteen hundred. Real dates for the
videos actually fetched come out of the fetch itself, for free.

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


def list_videos(ytdlp, channel, extra, newest=0):
    """Channel listing without touching each video page — one request, fast.

    Fast, but dateless: a flat listing gives id, title and ORDER (newest first)
    and nothing else. `newest` caps the walk via --playlist-end.
    """
    url = "https://www.youtube.com/%s/videos" % channel.lstrip("/")
    bound = ["--playlist-end", str(newest)] if newest else []
    r = run(ytdlp + ["--flat-playlist", "--dump-json"] + bound + extra + [url])
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


def resolve_dates(ytdlp, vids, extra, chunk=20, quiet=False):
    """Fill in upload_date for entries the flat listing left blank.

    Costs one request per video, so it is only ever called on a SHORT list: the
    binary-search probes, or a --list of already-narrowed matches.
    """
    todo = [v for v in vids if not v["date"] and v["id"]]
    if not todo:
        return
    got = {}
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        r = run(ytdlp + ["--skip-download", "--no-warnings", "--ignore-errors",
                         "--print", "%(id)s\t%(upload_date)s"] + extra
                + ["https://www.youtube.com/watch?v=" + v["id"] for v in part])
        for line in (r.stdout or "").splitlines():
            if "\t" not in line:
                continue
            vid, d = line.strip().split("\t", 1)
            d = d.strip()
            if re.match(r"^\d{8}$", d):
                got[vid] = d
        if not quiet and len(todo) > chunk:
            print("    dated %d/%d" % (min(i + chunk, len(todo)), len(todo)), flush=True)
    for v in vids:
        if not v["date"]:
            v["date"] = got.get(v["id"])


def cutoff_index(ytdlp, vids, extra, since_c):
    """Index of the first video OLDER than since_c, in a newest-first listing.

    Binary search: about eleven probes across a 1,500-video channel instead of
    fifteen hundred. Assumes the listing is in upload order, which is what
    /videos returns; a video whose date will not resolve (private, removed,
    members-only) is stepped over rather than trusted either way.
    """
    def date_at(i):
        for j in (i, i + 1, i - 1, i + 2, i - 2):
            if 0 <= j < len(vids):
                resolve_dates(ytdlp, [vids[j]], extra, quiet=True)
                if vids[j]["date"]:
                    return vids[j]["date"]
        return None

    lo, hi = 0, len(vids)
    while lo < hi:
        mid = (lo + hi) // 2
        d = date_at(mid)
        if d is None or d >= since_c:      # unresolvable -> assume in-window
            lo = mid + 1
        else:
            hi = mid
    return lo


def fetch_one(ytdlp, vid, extra, tmp):
    """Download captions for one video. The info json comes along for the ride,
    which is where the real upload date finally arrives — the listing never had
    it, and this request was being made anyway."""
    r = run(ytdlp + ["--skip-download", "--write-auto-subs", "--write-subs",
                     "--write-info-json",
                     "--sub-langs", "en.*", "--sub-format", "vtt", "--no-warnings"]
            + extra + ["-o", os.path.join(tmp, "%(id)s.%(ext)s"),
                       "https://www.youtube.com/watch?v=" + vid])

    date = None
    info = os.path.join(tmp, vid + ".info.json")
    if os.path.exists(info):
        try:
            with open(info, encoding="utf-8", errors="ignore") as f:
                j = json.load(f)
            date = j.get("upload_date") or ts_to_date(j.get("timestamp"))
        except ValueError:
            pass
        os.remove(info)

    got = [f for f in os.listdir(tmp) if f.startswith(vid) and f.endswith(".vtt")]
    if not got:
        why = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or ["no captions"]
        return None, date, why
    got.sort(key=lambda f: (".en.vtt" not in f, len(f)))   # prefer plain en
    return os.path.join(tmp, got[0]), date, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channel", default=DEFAULT_CHANNEL)
    ap.add_argument("--since", help="YYYY-MM-DD (default: 365 days ago)")
    ap.add_argument("--match", help="comma-separated words; keep titles containing any of them")
    ap.add_argument("--limit", type=int, default=0, help="stop after N videos")
    ap.add_argument("--newest", type=int, default=0,
                    help="only look at the N most recent uploads (skips the date probe entirely)")
    ap.add_argument("--all-dates", action="store_true",
                    help="ignore --since; consider the channel's whole back catalog")
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
    vids = list_videos(ytdlp, args.channel, extra, args.newest)
    print("  %d videos visible%s" % (len(vids), " (newest %d)" % args.newest if args.newest else ""))

    # Date window. The flat listing is dateless, so unless yt-dlp surprised us
    # with dates, find the --since boundary by probing the ordered list.
    window = "whole back catalog"
    if args.all_dates:
        pass
    elif any(v["date"] for v in vids):
        vids = [v for v in vids if v["date"] and v["date"] >= since_c]
        window = "since %s" % since
    elif vids:
        print("  listing carries no dates — probing for the %s boundary ..." % since, flush=True)
        n = cutoff_index(ytdlp, vids, extra, since_c)
        print("  the newest %d of %d uploads are on or after %s" % (n, len(vids), since))
        vids = vids[:n]
        window = "since %s" % since

    keep = [v for v in vids
            if not words or any(w in v["title"].lower() for w in words)]
    if args.limit:
        keep = keep[:args.limit]

    print("  %d match (%s%s)" % (len(keep), window,
                                 ", title contains " + "/".join(words) if words else ""))

    if args.list or not keep:
        # A listing that prints ???????? for every row is worse than useless —
        # it was the bug. Resolve dates for what is actually on screen.
        if keep and len(keep) <= 60:
            print("  resolving upload dates ...", flush=True)
            resolve_dates(ytdlp, keep, extra)
        for v in keep:
            print("  %s  %s" % (v["date"] or "????????", v["title"][:88]))
        if keep and len(keep) > 60:
            print("  (dates not resolved — narrow with --match/--limit/--newest to see them)")
        return 0

    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, ".tmp")
    os.makedirs(tmp, exist_ok=True)

    index, failed = [], []
    for i, v in enumerate(keep, 1):
        # Match on id, not on filename: the date is not known until the fetch.
        have = [f for f in os.listdir(OUT) if f.endswith("-%s.txt" % v["id"])]
        if have:
            print("  [%d/%d] have %s" % (i, len(keep), have[0]))
            index.append(dict(v, date=v["date"] or have[0][:8], file=have[0]))
            continue
        print("  [%d/%d] %s — %s" % (i, len(keep), v["id"], v["title"][:64]), flush=True)
        vtt, date, err = fetch_one(ytdlp, v["id"], extra, tmp)
        if date:
            v["date"] = date
        if not vtt:
            failed.append((v, err[0] if err else "?"))
            continue
        text = vtt_to_text(vtt)
        os.remove(vtt)
        if len(text) < 200:
            failed.append((v, "transcript suspiciously short (%d chars)" % len(text)))
            continue
        name = "%s-%s.txt" % (v["date"] or "00000000", v["id"])
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write("# %s\n# %s  %s\n\n%s\n" % (v["title"], v["date"] or "", v["url"], text))
        index.append(dict(v, file=name, chars=len(text)))

    shutil.rmtree(tmp, ignore_errors=True)
    index.sort(key=lambda v: v.get("date") or "")
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"channel": args.channel, "since": None if args.all_dates else since,
                   "match": words, "fetched": datetime.date.today().isoformat(),
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
