"""Build the 36-page KDP interior PDF for Yahia's First Ramadan.
8.5 x 11 in, no bleed, black & white. Run from the repo root:
    python3 build_interior.py
"""
import math, os, cv2, numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

FONTS = os.environ.get("FONT_DIR", "fonts")
pdfmetrics.registerFont(TTFont("Fredoka-Bold", f"{FONTS}/Fredoka-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Fredoka-SemiBold", f"{FONTS}/Fredoka-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Fredoka-Medium", f"{FONTS}/Fredoka-Medium.ttf"))

W, H = 8.5 * inch, 11 * inch
OUT = "kdp/Yahias_First_Ramadan_interior.pdf"
os.makedirs("kdp", exist_ok=True)
os.makedirs("build", exist_ok=True)


def star(c, cx, cy, r, lw=2.2):
    """Outlined rounded 5-point star (colorable)."""
    p = c.beginPath()
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    c.setLineJoin(1); c.setLineWidth(lw); c.drawPath(p, stroke=1, fill=0)


def crescent(c, cx, cy, r, lw=2.2):
    """Outlined crescent moon: outer circle minus offset circle."""
    d, r2, tilt = 0.45 * r, 0.85 * r, math.radians(25)
    x = (r * r - r2 * r2 + d * d) / (2 * d); y = math.sqrt(r * r - x * x)
    a, b = math.atan2(y, x), math.atan2(y, x - d)
    pts = [(r * math.cos(t), r * math.sin(t)) for t in np.linspace(a, 2 * math.pi - a, 120)]
    pts += [(d + r2 * math.cos(t), r2 * math.sin(t)) for t in np.linspace(-b, -(2 * math.pi - b), 120)]
    p = c.beginPath()
    for i, (px, py) in enumerate(pts):
        X = cx + px * math.cos(tilt) - py * math.sin(tilt)
        Y = cy + px * math.sin(tilt) + py * math.cos(tilt)
        p.moveTo(X, Y) if i == 0 else p.lineTo(X, Y)
    p.close()
    c.setLineJoin(1); c.setLineWidth(lw); c.drawPath(p, stroke=1, fill=0)


def outline_text(c, text, font, size, y, lw=2.5):
    """Centered hollow (stroke-only) text that children can color in."""
    t = c.beginText()
    t.setTextRenderMode(1)
    t.setFont(font, size)
    t.setTextOrigin((W - pdfmetrics.stringWidth(text, font, size)) / 2, y)
    c.setLineWidth(lw); c.setLineJoin(1)
    t.textLine(text)
    t.setTextRenderMode(0)
    c.drawText(t)


def centered(c, text, font, size, y):
    c.setFont(font, size)
    c.drawCentredString(W / 2, y, text)


def line_art(path, crop=None):
    """Load line art as clean 1-bit (cached PNG) for embedding."""
    g = cv2.imread(path, 0)
    if crop:
        y0, y1, x0, x1 = crop
        g = g[y0:y1, x0:x1]
    g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
    g = cv2.GaussianBlur(g, (0, 0), 0.7)
    _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    out = f"build/{os.path.basename(path)[:-4]}_{'x'.join(map(str, crop or []))}.png"
    Image.fromarray(bw).convert("1").save(out)
    return out


def border(c, inset=0.55 * inch, lw=3):
    c.setLineWidth(lw)
    c.roundRect(inset, inset, W - 2 * inset, H - 2 * inset, 0.35 * inch, stroke=1, fill=0)


def corner_stars(c, inset=0.55 * inch):
    for x, y in [(inset, inset), (W - inset, inset), (inset, H - inset), (W - inset, H - inset)]:
        c.setFillColorRGB(1, 1, 1)
        c.circle(x, y, 0.32 * inch, stroke=0, fill=1)
        c.setFillColorRGB(0, 0, 0)
        star(c, x, y, 0.28 * inch, 2.5)


# ---------- pages ----------
def title_page(c):
    border(c); corner_stars(c)
    outline_text(c, "Yahia's First", "Fredoka-Bold", 66, H - 2.05 * inch, 2.6)
    outline_text(c, "Ramadan", "Fredoka-Bold", 82, H - 3.15 * inch, 2.8)
    centered(c, "A Coloring Story for Little Muslims", "Fredoka-Medium", 22, H - 3.85 * inch)
    art = line_art("raw/page01.png")
    iw, ih = Image.open(art).size
    h = 5.3 * inch; w = h * iw / ih
    c.drawImage(art, (W - w) / 2, 1.45 * inch, w, h, mask=None)
    centered(c, "Ages 3–6", "Fredoka-SemiBold", 20, 0.95 * inch)


def copyright_page(c):
    c.setFont("Fredoka-Medium", 11)
    lines = [
        "Yahia's First Ramadan: A Coloring Story for Little Muslims",
        "Copyright © 2026. All rights reserved.",
        "",
        "No part of this book may be reproduced in any form without",
        "written permission from the publisher, except for personal,",
        "non-commercial use by the purchaser.",
        "",
        "Coloring tip: every picture is printed on its own page, so markers",
        "won't bleed onto the next drawing. Slip a sheet of card behind the",
        "page you are coloring for extra protection.",
    ]
    y = 2.6 * inch
    for ln in lines:
        c.drawCentredString(W / 2, y, ln); y -= 16


def belongs_page(c):
    border(c); corner_stars(c)
    outline_text(c, "This Book", "Fredoka-Bold", 64, H - 2.3 * inch, 2.6)
    outline_text(c, "Belongs To", "Fredoka-Bold", 64, H - 3.3 * inch, 2.6)
    c.setLineWidth(2.5)
    c.line(1.6 * inch, H - 4.75 * inch, W - 1.6 * inch, H - 4.75 * inch)
    crescent(c, W / 2, 3.55 * inch, 1.35 * inch, 2.8)
    for (x, y, r) in [(1.75, 4.6, .42), (6.75, 4.7, .36), (2.2, 2.2, .32), (6.3, 2.0, .44),
                      (5.75, 5.25, .26), (2.75, 5.3, .24), (4.25, 1.3, .22)]:
        star(c, x * inch, y * inch, r * inch, 2.4)


def coloring_page(c, n):
    c.drawImage(f"print/Noor_page{n:02d}_print.png", 0, 0, W, H)


def certificate_page(c):
    border(c, 0.55 * inch, 3); border(c, 0.75 * inch, 1.5); corner_stars(c)
    outline_text(c, "Ramadan Star", "Fredoka-Bold", 60, H - 2.15 * inch, 2.6)
    outline_text(c, "Certificate", "Fredoka-Bold", 60, H - 3.1 * inch, 2.6)
    centered(c, "This certificate is proudly awarded to", "Fredoka-Medium", 20, H - 4.1 * inch)
    c.setLineWidth(2.5)
    c.line(1.6 * inch, H - 5.0 * inch, W - 1.6 * inch, H - 5.0 * inch)
    centered(c, "for a wonderful Ramadan full of", "Fredoka-Medium", 20, H - 5.7 * inch)
    centered(c, "good deeds, kindness and sharing!", "Fredoka-Medium", 20, H - 6.05 * inch)
    crescent(c, W / 2, H - 7.4 * inch, 0.75 * inch, 2.6)
    for dx, dy, r in [(-1.7, .2, .36), (1.7, .2, .36), (-2.6, -.35, .26), (2.6, -.35, .26)]:
        star(c, W / 2 + dx * inch, H - 7.4 * inch + dy * inch, r * inch, 2.4)
    c.setFont("Fredoka-Medium", 16)
    c.drawString(1.45 * inch, 1.75 * inch, "Date:")
    c.line(2.1 * inch, 1.72 * inch, 3.9 * inch, 1.72 * inch)
    c.drawString(4.5 * inch, 1.75 * inch, "Signed:")
    c.line(5.35 * inch, 1.72 * inch, 7.05 * inch, 1.72 * inch)


def blank(c):
    pass


plan = [title_page, copyright_page, belongs_page, blank]
for n in range(1, 16):
    plan += [lambda c, n=n: coloring_page(c, n), blank]
plan += [certificate_page, blank]
assert len(plan) == 36, len(plan)

c = canvas.Canvas(OUT, pagesize=(W, H), initialFontName="Fredoka-Medium", initialFontSize=12)
c.setTitle("Yahia's First Ramadan — interior"); c.setAuthor(""); c.setCreator("")
for fn in plan:
    c.setStrokeColorRGB(0, 0, 0); c.setFillColorRGB(0, 0, 0)
    fn(c)
    c.showPage()
c.save()
print("wrote", OUT, len(plan), "pages")
