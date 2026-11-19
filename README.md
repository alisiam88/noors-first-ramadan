# Noor's First Ramadan — KDP coloring book

Working repo for the art pipeline.

- `PROMPTS.md` — image jobs for ChatGPT, with checkboxes for progress.
- `reference/` — approved character/style reference (page 1).
- `raw/` — images exactly as generated (`page05.png` … `page15.png`, `cover_front.png`).
- `print/` — print-ready pages: 2550×3300 px, 300 DPI, 1-bit black and white, story line added.
- `prep_page.py` — turns a raw page into a print page:
  `python3 prep_page.py raw/page05.png print/Noor_page05_print.png "Story line here"`

Book: 8.5" × 11", 15 single-sided coloring pages, 36 pages total, B&W interior, white paper, no bleed.
