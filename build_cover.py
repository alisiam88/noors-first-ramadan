"""Build the KDP paperback wraparound cover for Yahia's First Ramadan.
8.5 x 11 in trim, 36 pages, white paper -> spine 36 * 0.002252 = 0.081 in.
Full cover with 0.125 in bleed: 17.331 x 11.25 in = 5199 x 3375 px @ 300 DPI.
Run from the repo root:  python3 build_cover.py
"""
import os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DPI = 300
BLEED, TRIM_W, TRIM_H = 0.125, 8.5, 11.0
PAGES = 36
SPINE = round(PAGES * 0.002252, 4)
COVER_W, COVER_H = 2 * BLEED + 2 * TRIM_W + SPINE, TRIM_H + 2 * BLEED
PX = lambda inch: int(round(inch * DPI))
W, H = PX(COVER_W), PX(COVER_H)
FONTS = os.environ.get("FONT_DIR", "fonts")
F = lambda name, pt: ImageFont.truetype(f"{FONTS}/{name}.ttf", int(pt / 72 * DPI))

BACK_X0, BACK_X1 = 0, PX(BLEED + TRIM_W)             # back panel incl. left bleed
SPINE_X0, SPINE_X1 = BACK_X1, PX(BLEED + TRIM_W + SPINE)
FRONT_X0 = SPINE_X1                                    # front trim starts here
SAFE = 0.375                                           # keep text 3/8" inside trim

CREAM, GOLD, NIGHT = (255, 246, 220), (246, 196, 82), (34, 18, 84)

cover = Image.new("RGB", (W, H), NIGHT)

# ---------- front: upscaled art (also runs across the thin spine) ----------
import sys
COVER_ART = sys.argv[1] if len(sys.argv) > 1 else "raw/cover_front.png"
art = cv2.imread(COVER_ART)
ah, aw = art.shape[:2]
fw, fh = W - BACK_X1, H                              # spine + front + right bleed
crop_h = int(round(aw * fh / fw))
top = int((ah - crop_h) * 0.75)                      # trim more sky than ground
art = art[top: top + crop_h]
art = cv2.resize(art, (fw, fh), interpolation=cv2.INTER_LANCZOS4)
blur = cv2.GaussianBlur(art, (0, 0), 2.0)
art = cv2.addWeighted(art, 1.45, blur, -0.45, 0)     # gentle unsharp mask
cover.paste(Image.fromarray(cv2.cvtColor(art, cv2.COLOR_BGR2RGB)), (BACK_X1, 0))
print(f"cover art: {aw}x{ah} crop top={top} h={crop_h} -> {fw}x{fh} (x{fw/aw:.2f})")


def text_center(d, cx, y, s, font, fill, stroke=0, stroke_fill=None, shadow=None):
    w = d.textlength(s, font=font)
    if shadow:
        d.text((cx - w / 2 + 8, y + 10), s, font=font, fill=shadow, stroke_width=stroke, stroke_fill=shadow)
    d.text((cx - w / 2, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


# soft dark glow behind the title for legibility
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
front_cx = FRONT_X0 + PX(TRIM_W) // 2
gd.ellipse([front_cx - PX(4.3), PX(-0.6), front_cx + PX(4.3), PX(3.9)], fill=150)
glow = glow.filter(ImageFilter.GaussianBlur(PX(0.45)))
cover = Image.composite(Image.new("RGB", (W, H), (20, 8, 60)), cover, glow)

d = ImageDraw.Draw(cover)
y0 = PX(BLEED + SAFE + 0.05)
text_center(d, front_cx, y0, "Yahia's First", F("Baloo2-ExtraBold", 62), CREAM, 10, (70, 30, 120), (15, 5, 45))
text_center(d, front_cx, y0 + PX(0.92), "Ramadan", F("Baloo2-ExtraBold", 104), GOLD, 12, (110, 50, 20), (15, 5, 45))

# subtitle ribbon
rib_y = y0 + PX(2.62)
sub = "A Coloring Story for Little Muslims"
sf = F("Fredoka-SemiBold", 25)
rw = d.textlength(sub, font=sf) + PX(0.7)
d.rounded_rectangle([front_cx - rw / 2, rib_y, front_cx + rw / 2, rib_y + PX(0.55)], radius=PX(0.27),
                    fill=CREAM, outline=GOLD, width=PX(0.04))
text_center(d, front_cx, rib_y + PX(0.07), sub, sf, (70, 30, 120))
text_center(d, front_cx, rib_y + PX(0.72), "by Ali M. Elsiad", F("Fredoka-SemiBold", 20), CREAM, 4, (60, 25, 110))

# "Ages 3-6" badge, lower right of the front
bx, by, br = W - PX(BLEED + SAFE + 0.75), H - PX(BLEED + SAFE + 0.75), PX(0.72)
d.ellipse([bx - br, by - br, bx + br, by + br], fill=GOLD, outline=CREAM, width=PX(0.05))
text_center(d, bx, by - PX(0.43), "Ages", F("Fredoka-Bold", 22), (70, 30, 120))
text_center(d, bx, by - PX(0.12), "3–6", F("Fredoka-Bold", 36), (70, 30, 120))

# ---------- back panel ----------
back = np.zeros((H, BACK_X1, 3), np.float32)
top_c, bot_c = np.array([30, 16, 78]), np.array([92, 52, 140])
t = np.linspace(0, 1, H)[:, None]
back[:] = (top_c * (1 - t) + bot_c * t)[:, None, :]
rng = np.random.default_rng(7)
bk = Image.fromarray(back.astype(np.uint8))
bd = ImageDraw.Draw(bk)
for _ in range(90):                                   # little twinkling stars
    x, y = rng.integers(0, BACK_X1), rng.integers(0, H)
    r = rng.choice([2, 3, 4])
    bd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 236, 170))
cover.paste(bk, (0, 0))
d = ImageDraw.Draw(cover)

bx0 = PX(BLEED + SAFE + 0.2)
bx1 = BACK_X1 - PX(SAFE + 0.2)
bcx = (bx0 + bx1) // 2
y = PX(BLEED + SAFE + 0.15)
text_center(d, bcx, y, "The Ramadan moon is shining!", F("Baloo2-ExtraBold", 34), GOLD)
y += PX(0.85)

body = F("Fredoka-Medium", 17)


def para(text, y, font=body, fill=CREAM, lead=1.38):
    words, line = text.split(), ""
    for wd in words:
        trial = (line + " " + wd).strip()
        if d.textlength(trial, font=font) > bx1 - bx0:
            d.text((bx0, y), line, font=font, fill=fill); y += int(font.size * lead); line = wd
        else:
            line = trial
    if line:
        d.text((bx0, y), line, font=font, fill=fill); y += int(font.size * lead)
    return y


y = para("It's Yahia's very first Ramadan! Join him and his big sister Kayan as they hang lanterns "
         "and stars, wake up for suhoor, share food with their neighbors, break their fast with dates "
         "and celebrate a joyful Eid with the whole family.", y)
y += PX(0.18)
for b in ["15 story pages to color, each with a gentle story line",
          "Big, bold outlines and simple shapes for little hands",
          "Single-sided pages, so markers won't bleed through",
          "Includes a \"This Book Belongs To\" page and a Ramadan Star Certificate"]:
    import math
    scx, scy, sr = bx0 + PX(0.1), y + PX(0.13), PX(0.1)
    d.polygon([(scx + (sr if k % 2 == 0 else sr * 0.45) * math.cos(-math.pi / 2 + k * math.pi / 5),
                scy + (sr if k % 2 == 0 else sr * 0.45) * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)], fill=GOLD)
    sx = bx0
    bx0 += PX(0.32)
    y = para(b, y)
    bx0 = sx
    y += PX(0.08)

# three sample pages as little white cards
y += PX(0.4)
cw, ch = PX(2.25), PX(2.91)
gap = ((bx1 - bx0) - 3 * cw) // 2
for i, n in enumerate([2, 9, 15]):
    pg = Image.open(f"print/Noor_page{n:02d}_print.png").convert("RGB").resize((cw, ch), Image.LANCZOS)
    x = bx0 + i * (cw + gap)
    d.rounded_rectangle([x - 10, y - 10, x + cw + 10, y + ch + 10], radius=18, fill=(255, 255, 255),
                        outline=GOLD, width=6)
    cover.paste(pg, (x, y))
y += ch + PX(0.45)
text_center(d, bcx, y, "A perfect Ramadan gift for ages 3–6", F("Fredoka-SemiBold", 22), GOLD)

# barcode zone (KDP prints the barcode here): 2 x 1.2 in, lower right of back, 0.25 in in from trim
BC_W, BC_H = PX(2.0), PX(1.2)
bc_x1 = BACK_X1 - PX(0.25 + 0.0)
bc_y1 = H - PX(BLEED + 0.25)
barcode_box = (bc_x1 - BC_W, bc_y1 - BC_H, bc_x1, bc_y1)

os.makedirs("kdp", exist_ok=True)
cover.save("kdp/cover_preview.png", dpi=(DPI, DPI))

# guide overlay for checking (not for upload)
g = cover.copy(); gd = ImageDraw.Draw(g)
for x in [PX(BLEED), BACK_X1, SPINE_X0, SPINE_X1, W - PX(BLEED)]:
    gd.line([x, 0, x, H], fill=(0, 255, 255), width=4)
for yy in [PX(BLEED), H - PX(BLEED)]:
    gd.line([0, yy, W, yy], fill=(0, 255, 255), width=4)
gd.rectangle(barcode_box, outline=(255, 0, 0), width=8)
g.save("build/cover_guides.png")

cover.save("kdp/Yahias_First_Ramadan_cover.pdf", resolution=DPI, quality=95)
print(f"cover {W}x{H}px = {COVER_W:.3f} x {COVER_H:.3f} in, spine {SPINE} in; barcode box {barcode_box}; text bottom y={y}")
