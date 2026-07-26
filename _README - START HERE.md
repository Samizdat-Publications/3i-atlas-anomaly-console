# 3I/ATLAS — Interstellar Anomaly Review Console

**Live on the web:** https://3i-atlas-anomaly-console.pages.dev — share this link with anyone.
**Source:** https://github.com/Samizdat-Publications/3i-atlas-anomaly-console

**Offline copy:** `_LATEST - 3I-ATLAS Anomaly Console.html` — double-click it.
Works completely offline, nothing to install. Sound starts after you "authenticate"
(any key on the boot screen). ESC skips the boot.

## What it is
A fictional "Interstellar Object Working Group" terminal tracking 3I/ATLAS, the third
interstellar object, through its 2025-2026 pass — with the real trajectory (JPL Horizons
data) and Avi Loeb's full anomaly file (25 cases) presented next to the official
explanations, so you can weigh both sides. Unofficial, for education/entertainment.

## Controls
| Input | Action |
|---|---|
| SPACE | play / pause the timeline |
| drag timeline | scrub time |
| click timeline marker | jump to event (amber = anomaly, opens its case file) |
| ← / → (shift = 7d) | step days |
| 1 / 2 / 3 / 4 | TRACK / ANOMALIES / COMPARE / ARCHIVE |
| N | jump to today's real position |
| M | mute · ▦ toggles the CRT effect |
| mouse drag / wheel | orbit / zoom the 3D view (FREE or TOP-DOWN camera) |

Try: **CHASE** camera around October 2025 (perihelion), the **A-05 case file →
"VISUALIZE IN TRACKER"** (sunward anti-tail), **FROM MARS** on 2025-10-03, and the
redacted documents in **ARCHIVE** (click the black bars).

## Rebuilding and republishing after edits
```
python tools/build.py
npx wrangler pages deploy public --project-name 3i-atlas-anomaly-console
git add -A && git commit -m "..." && git push
```
`build.py` writes both the offline `_LATEST` file and `public/index.html` (what the website
serves) from the same bytes. See `CLAUDE.md` for the full architecture.
