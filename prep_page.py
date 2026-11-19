"""Make a KDP print-ready coloring page: 2550x3300 px, 300 DPI, pure 1-bit B/W.
Usage: python3 prep_page.py input.png output.png
"""
import sys, cv2, numpy as np
from PIL import Image

W, H, DPI = 2550, 3300, 300
SAFE = int(0.375 * DPI)            # keep art ~3/8" inside the trim (KDP min is 1/4")

src, dst = sys.argv[1], sys.argv[2]
caption = sys.argv[3] if len(sys.argv) > 3 else ""
TEXT_H = int(1.0 * DPI) if caption else 0   # band reserved under the art for the story line
g = cv2.cvtColor(cv2.imread(src, cv2.IMREAD_COLOR), cv2.COLOR_BGR2GRAY)
gray_px = np.mean((g > 40) & (g < 215)) * 100   # share of mid-gray pixels in the source

# crop to the drawing, then fit inside the safe area
ys, xs = np.where(g < 200)
g = g[ys.min():ys.max()+1, xs.min():xs.max()+1]
s = min((W-2*SAFE)/g.shape[1], (H-2*SAFE-TEXT_H)/g.shape[0])
up = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
up = cv2.GaussianBlur(up, (0, 0), sigmaX=s*0.35)  # smooth stair-steps before thresholding
_, bw = cv2.threshold(up, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # drop specks

page = np.full((H, W), 255, np.uint8)
y0, x0 = SAFE + (H-2*SAFE-TEXT_H-bw.shape[0])//2, (W-bw.shape[1])//2
page[y0:y0+bw.shape[0], x0:x0+bw.shape[1]] = bw

# line-weight check: median stroke width in points
ink = (page == 0).astype(np.uint8)
dist = cv2.distanceTransform(ink, cv2.DIST_L2, 3)
ridge = dist[(dist > 0) & (dist == cv2.dilate(dist, np.ones((3, 3))))]
med_pt = 2 * np.median(ridge) / DPI * 72 if ridge.size else 0
n_regions = cv2.connectedComponents(1 - ink)[0] - 1

img = Image.fromarray(page)
if caption:
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(img)
    pt = 24
    while True:   # 24 pt, shrink only if the line won't fit inside the safe margins
        font = ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf", int(pt/72*DPI))
        tw = d.textlength(caption, font=font)
        if tw <= W - 2*SAFE or pt <= 16: break
        pt -= 1
    d.text(((W-tw)/2, H-SAFE-TEXT_H*0.62), caption, font=font, fill=0)
img.convert("1").save(dst, dpi=(DPI, DPI))
print(f"source gray pixels: {gray_px:.1f}% | upscale x{s:.2f} | median line ~{med_pt:.1f} pt "
      f"| ink {ink.mean()*100:.1f}% | colorable regions {n_regions}")
