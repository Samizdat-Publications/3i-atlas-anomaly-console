"""Push the fetched transcripts to a PRIVATE repo so a cloud session can read them.

data/transcripts/ is gitignored in this repo and should stay that way — this repo
is public and those are someone else's words. But a Claude session running in the
cloud cannot read anything that never leaves your laptop, which makes the
transcripts useless for the analysis they were fetched for.

This copies them into a separate PRIVATE repo and pushes. Private costs nothing,
keeps his work unpublished, and gives a cloud session the whole text.

ONE-TIME SETUP: create the empty private repo first at https://github.com/new
  Name: 3i-atlas-transcripts     Visibility: Private     (tick "Add a README")

Then, from this folder:

    cd "C:\\Users\\stewa\\OneDrive\\Documents\\Claude\\3I ATLAS Anomaly Console"
    python tools/push_transcripts.py

Re-run it any time you fetch more; it only pushes what changed.
"""
import argparse, os, shutil, subprocess, sys, glob

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "transcripts")
DEFAULT_REPO = "Samizdat-Publications/3i-atlas-transcripts"

README = """# Transcript working store — PRIVATE

Auto-caption transcripts pulled by `tools/fetch_transcripts.py` in
[3i-atlas-anomaly-console](https://github.com/Samizdat-Publications/3i-atlas-anomaly-console),
used as source material for the fireball case files.

**This is third-party content.** It is somebody else's spoken work, stored here
so it can be read and analysed. It is not for publication and this repo must
stay private. What gets published is the analysis derived from it, in the public
console repo — never the source text.
"""


def git(args, cwd, check=True):
    r = subprocess.run(["git"] + args, cwd=cwd, shell=False, text=True, capture_output=True)
    if check and r.returncode != 0:
        sys.exit("git %s failed:\n%s" % (" ".join(args), (r.stderr or r.stdout).strip()[-1200:]))
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=DEFAULT_REPO, help="owner/name of the PRIVATE repo")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(SRC, "*.txt")))
    print("Source: %s" % SRC)
    print("  %d transcript files" % len(files))
    if not files:
        sys.exit(
            "\nNothing to push — that folder is empty or missing.\n"
            "Either the fetch has not finished yet, or it found no usable captions.\n"
            "Run this first, and watch for lines that say [n/N]:\n"
            "  python tools/fetch_transcripts.py --since 2025-06-20 "
            "--match fireball,uap,atlas,bolide,meteor,interstellar,loeb,comet,3i --limit 150")

    name = args.repo.split("/")[-1]
    work = os.path.abspath(os.path.join(ROOT, os.pardir, name))
    url = "https://github.com/%s.git" % args.repo
    print("Target: %s  ->  %s" % (work, args.repo))

    if not os.path.isdir(os.path.join(work, ".git")):
        print("Cloning %s ..." % args.repo)
        r = subprocess.run(["git", "clone", url, work], shell=False, text=True, capture_output=True)
        if r.returncode != 0:
            sys.exit(
                "Could not clone %s\n\n%s\n\n"
                "If it says 'Repository not found', the repo does not exist yet.\n"
                "Create it at https://github.com/new — name it '%s', set it to\n"
                "PRIVATE, tick 'Add a README', then run this again."
                % (url, (r.stderr or "").strip()[-600:], name))
    else:
        git(["pull", "--ff-only", "origin", "HEAD"], work, check=False)

    dest = os.path.join(work, "transcripts")
    os.makedirs(dest, exist_ok=True)
    copied = 0
    for f in files + glob.glob(os.path.join(SRC, "index.json")):
        target = os.path.join(dest, os.path.basename(f))
        if not os.path.exists(target) or os.path.getsize(target) != os.path.getsize(f):
            shutil.copy2(f, target)
            copied += 1

    readme = os.path.join(work, "README.md")
    if not os.path.exists(readme) or "third-party content" not in open(readme, encoding="utf-8", errors="ignore").read():
        with open(readme, "w", encoding="utf-8") as fh:
            fh.write(README)

    print("  %d files copied in (%d already current)" % (copied, len(files) - copied + 1))

    git(["add", "-A"], work)
    if not git(["diff", "--cached", "--quiet"], work, check=False).returncode:
        print("\nNothing new to push — all %d transcripts are already in %s."
              % (len(files), args.repo))
        return 0

    git(["-c", "user.name=Samizdat-Publications",
         "-c", "user.email=179866421+Samizdat-Publications@users.noreply.github.com",
         "commit", "-m", "Transcripts: %d files (%d new or changed)" % (len(files), copied)], work)
    for attempt in range(4):
        r = git(["push", "origin", "HEAD"], work, check=False)
        if r.returncode == 0:
            break
        print("  push failed, retrying ...")
    else:
        sys.exit("Push failed:\n" + (r.stderr or r.stdout).strip()[-800:])

    print("\nPushed %d transcripts to %s (private)." % (len(files), args.repo))
    print("Tell Claude it is there — it can attach that repo and read all of them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
