"""Build the single self-contained HTML file.

Inlines CSS (with the terminal font as a base64 data URI), vendor JS,
baked data, and app JS into ONE file at the project root:
  _LATEST - 3I-ATLAS Anomaly Console.html

Usage: python tools/build.py
"""
import base64, os, re, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "_LATEST - 3I-ATLAS Anomaly Console.html")

# Deployed origin, e.g. "https://3i-atlas.pages.dev". Empty = relative og:image
# (fine locally; social cards need the absolute form). Override with SITE_URL env var.
SITE_URL = "https://3i-atlas-anomaly-console.pages.dev"

# Cloudflare Web Analytics beacon token (cookieless, no personal data). Empty =
# no analytics. Override with CF_ANALYTICS_TOKEN. Injected into public/index.html
# ONLY — the offline _LATEST file must never reference an external script.
# Alternative with no token at all: Pages project -> Settings -> enable Web
# Analytics, which injects the same beacon at the edge.
ANALYTICS_TOKEN = ""

JS_ORDER = [
    "vendor/three.min.js",
    "vendor/OrbitControls.js",
    "data-ephemeris.js",
    "data-content.js",
    "data-fireballs.js",
    "data-instruments.js",
    "js/core.js",
    "js/charts.js",
    "js/scene3d.js",
    "js/fireballs.js",
    "js/ui.js",
    "js/main.js",
]


def read(rel):
    with open(os.path.join(SRC, rel), "r", encoding="utf-8") as f:
        return f.read()


def main():
    css = read("console.css")
    font_path = os.path.join(SRC, "vendor", "sharetechmono.woff2")
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        css = css.replace('url("vendor/sharetechmono.woff2")',
                          'url(data:font/woff2;base64,' + b64 + ')')

    scripts = []
    for rel in JS_ORDER:
        body = read(rel)
        scripts.append("<script>/* == %s == */\n%s\n</script>" % (rel, body))

    # Social scrapers want an ABSOLUTE og:image URL. Set the deployed origin here
    # (or via the SITE_URL env var) once the Cloudflare Pages URL exists.
    site = os.environ.get("SITE_URL", SITE_URL).rstrip("/")
    og_image = (site + "/og-image.png") if site else "og-image.png"

    title = "3I/ATLAS — Interstellar Anomaly Review Console"
    desc = ("Track all three interstellar objects — 3I/ATLAS, 1I/'Oumuamua and 2I/Borisov — "
            "on real JPL Horizons trajectories, plus the CNEOS fireball map and its two "
            "disputed interstellar meteors, with 44 fact-checked case files weighing "
            "Avi Loeb's anomaly claims against the official explanations.")
    # inline SVG favicon: the console's sigil
    favicon = (
        "data:image/svg+xml,"
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        "%3Crect width='64' height='64' fill='%23041019'/%3E"
        "%3Ccircle cx='32' cy='32' r='21' fill='none' stroke='%2334e1ff' stroke-width='3'/%3E"
        "%3Ccircle cx='32' cy='32' r='7' fill='%23ffb347'/%3E"
        "%3C/svg%3E"
    )
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>" + title + "</title>",
        '<meta name="description" content="' + desc + '">',
        '<meta name="theme-color" content="#041019">',
        '<meta name="color-scheme" content="dark">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="' + title + '">',
        '<meta property="og:description" content="' + desc + '">',
        '<meta property="og:image" content="' + og_image + '">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="' + title + '">',
        '<meta name="twitter:description" content="' + desc + '">',
        '<meta name="twitter:image" content="' + og_image + '">',
        '<link rel="icon" href="' + favicon + '">',
    ]
    def page(extra_body=""):
        return "\n".join([
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            "\n".join(head),
            "<style>", css, "</style>",
            "</head>",
            "<body>",
            "\n".join(scripts),
            extra_body,
            "</body>",
            "</html>",
        ])

    # Offline copy: zero external references, works with no network at all.
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page())
    print("Built %s (%d KB)" % (OUT, os.path.getsize(OUT) // 1024))

    # Cloudflare Pages deploy directory: same bytes + optional analytics beacon.
    token = os.environ.get("CF_ANALYTICS_TOKEN", ANALYTICS_TOKEN).strip()
    beacon = ""
    if token:
        beacon = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                  "data-cf-beacon='{\"token\": \"" + token + "\"}'></script>")
    pub_dir = os.path.join(ROOT, "public")
    os.makedirs(pub_dir, exist_ok=True)
    pub = os.path.join(pub_dir, "index.html")
    with open(pub, "w", encoding="utf-8") as f:
        f.write(page(beacon))
    print("Built %s (%d KB)%s" % (pub, os.path.getsize(pub) // 1024,
                                  " + analytics beacon" if token else ""))

    # Landing page: src/about.html -> public/about.html, with the font inlined and
    # __SITE__ resolved so its OpenGraph tags carry absolute URLs.
    about_src = os.path.join(SRC, "about.html")
    if os.path.exists(about_src):
        about = read("about.html")
        font_uri = ""
        if os.path.exists(font_path):
            with open(font_path, "rb") as f:
                font_uri = "data:font/woff2;base64," + base64.b64encode(f.read()).decode("ascii")
        about = about.replace("__FONT__", font_uri).replace("__SITE__", SITE_URL)
        about = "<!doctype html>\n<html lang=\"en\">\n" + about + "\n</html>\n"
        if beacon:
            about = about.replace("</html>", beacon + "\n</html>")
        dest = os.path.join(pub_dir, "about.html")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(about)
        print("Built %s (%d KB)" % (dest, os.path.getsize(dest) // 1024))


if __name__ == "__main__":
    main()
