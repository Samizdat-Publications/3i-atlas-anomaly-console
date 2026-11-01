# 3I/ATLAS: Interstellar Anomaly Review Console

**Live on the web:** https://3i-atlas-anomaly-console.pages.dev (share this link with anyone).
**Source:** https://github.com/Samizdat-Publications/3i-atlas-anomaly-console

**Offline copy:** `C:\Users\stewa\Documents\Claude\3I ATLAS Anomaly Console\_LATEST - 3I-ATLAS Anomaly Console.html`.
Double-click it. It works completely offline with nothing to install. Sound starts after you
"authenticate" (any key on the boot screen). ESC skips the boot.

## What it is
A fictional "Interstellar Object Working Group" terminal for the three interstellar objects
(3I/ATLAS, 1I/'Oumuamua and 2I/Borisov) on their real JPL Horizons trajectories, plus the
CNEOS fireball map. Every case file puts the claim next to the official explanation, so you
can weigh both sides. The BRIEFINGS tab is the place to start: each one answers a single
question, such as BR-09, "Is 3I/ATLAS changing course?". Unofficial, for education and
entertainment.

## Controls
| Input | Action |
|---|---|
| SPACE | play / pause the timeline |
| drag timeline | scrub time |
| click timeline marker | open that record (amber = anomaly case, cyan = mission event) |
| left / right arrow (shift = 7 days) | step days |
| 1 / 2 / 3 / 4 / 5 | TRACK / ANOMALIES / COMPARE / FIREBALLS / ARCHIVE |
| N | jump to today's real position |
| M | mute; the grid-icon button toggles the CRT effect |
| mouse drag / wheel | orbit / zoom the 3D view (FREE or TOP-DOWN camera) |

Try: briefing **BR-09** and then the **GRAVITY-ONLY** pod in TRACK, the **CHASE** camera
around October 2025 (perihelion), the **A-05 case file, then VISUALIZE IN TRACKER**
(sunward anti-tail), **FROM MARS** on 2025-10-03, and the redacted documents in **ARCHIVE**
(click the black bars).

## Rebuilding and republishing after edits
Paste into Windows PowerShell:
```powershell
cd "C:\Users\stewa\Documents\Claude\3I ATLAS Anomaly Console"; python tools/build.py; cd public; npx wrangler pages deploy . --project-name 3i-atlas-anomaly-console --branch main
```
Deploying from inside `public` matters: run from the project folder, wrangler would also
upload the landing page's `functions` folder into the console. A push to `main` on GitHub
deploys automatically, so the manual step is only needed when GitHub Actions is unavailable.
`build.py` writes both the offline `_LATEST` file and `public\index.html` (what the website
serves) from the same bytes. See `CLAUDE.md` for the full architecture.
