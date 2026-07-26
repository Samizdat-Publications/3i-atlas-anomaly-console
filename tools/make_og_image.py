"""Render public/og-image.png — the 1200x630 social card.

Draws the console's aesthetic (deep-navy field, phosphor-cyan orbit arcs,
the three interstellar tracks) using the real trajectory data so the card
shows the actual geometry. Run after tools/build.py; committed to git.

Usage: python tools/make_og_image.py
"""
import json, math, os, random

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
BG = (4, 16, 25)
CYAN = (52, 225, 255)
DIM = (29, 109, 140)
AMBER = (255, 179, 71)
VIOLET = (217, 184, 255)
BLUE = (159, 217, 255)
TXT = (191, 228, 242)
FAINT = (61, 90, 108)

ERA_COLOR = {"3i": AMBER, "1i": VIOLET, "2i": BLUE}


def font(size, bold=False):
    for name in (("consolab.ttf", "consola.ttf") if bold else ("consola.ttf",)) + ("cour.ttf",):
        p = os.path.join("C:\\Windows\\Fonts", name)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def main():
    random.seed(3)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")

    # starfield
    for _ in range(420):
        x, y = random.randrange(W), random.randrange(H)
        b = random.randint(40, 150)
        d.point((x, y), fill=(b, b + 15, b + 30))

    cx, cy = 470, 330          # sun position on the card
    AU = 62                    # pixels per AU

    # planet orbit rings
    for au, alpha in ((0.39, 90), (0.72, 100), (1.0, 115), (1.52, 100), (5.2, 70)):
        r = au * AU
        d.ellipse([cx - r, cy - r * 0.42, cx + r, cy + r * 0.42], outline=DIM + (alpha,), width=2)

    # real trajectories, projected to the card's flattened ecliptic view
    with open(os.path.join(ROOT, "data", "ephemeris.json"), encoding="utf-8") as f:
        eph = json.load(f)
    for era in ("2i", "1i", "3i"):
        tgt = (eph.get("eras", {}).get(era) or {}).get("objects", {}).get("target")
        if not tgt:
            continue
        pts = []
        for p in tgt["pos"]:
            x = cx + p[0] * AU
            y = cy - p[1] * AU * 0.42 - p[2] * AU * 0.30
            if -900 < x < W + 900 and -900 < y < H + 900:
                pts.append((x, y))
        if len(pts) > 1:
            d.line(pts, fill=ERA_COLOR[era] + (215,), width=3, joint="curve")

    # sun
    for r, a in ((26, 30), (17, 60), (10, 130), (5, 255)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 244, 214, a))

    # vignette-ish left panel for text legibility
    d.rectangle([0, 0, 470, H], fill=(4, 16, 25, 172))

    # ---- text block ----
    d.text((60, 92), "3I / ATLAS", font=font(58, True), fill=CYAN)
    d.text((62, 160), "INTERSTELLAR ANOMALY", font=font(25), fill=TXT)
    d.text((62, 192), "REVIEW  CONSOLE", font=font(25), fill=TXT)

    d.line([(60, 240), (410, 240)], fill=DIM, width=2)

    rows = [
        (AMBER, "3I/ATLAS", "25 case files"),
        (VIOLET, "1I/'OUMUAMUA", "11 case files"),
        (BLUE, "2I/BORISOV", "5 case files"),
    ]
    y = 262
    for col, name, sub in rows:
        d.ellipse([62, y + 7, 74, y + 19], fill=col)
        d.text((88, y), name, font=font(23, True), fill=col)
        d.text((88, y + 28), sub, font=font(17), fill=FAINT)
        y += 66

    d.text((60, 470), "REAL JPL HORIZONS TRAJECTORIES", font=font(17), fill=CYAN)
    d.text((60, 496), "LOEB'S ANOMALY CLAIMS VS THE", font=font(17), fill=FAINT)
    d.text((60, 518), "OFFICIAL EXPLANATIONS, FACT-CHECKED", font=font(17), fill=FAINT)

    d.text((60, 566), "UNOFFICIAL SIMULATION \u00b7 NOT AFFILIATED WITH NASA/JPL",
           font=font(13), fill=(45, 66, 80))

    # frame
    d.rectangle([0, 0, W - 1, H - 1], outline=(14, 58, 79), width=3)

    out = os.path.join(ROOT, "public", "og-image.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print("Wrote %s (%d KB)" % (out, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
