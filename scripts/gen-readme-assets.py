#!/usr/bin/env python3
"""Generate README image assets for dsh-fmea-table-check (docs/assets/).

Outputs (idempotent overwrite):
  dsh-fmea-table-check-flow-light.svg
  dsh-fmea-table-check-flow-dark.svg
      Hero data-flow diagram. Two hand-written SVG files (vector -- never
      rasterized to webp). Text inside is command-surface tokens only
      (tool name, file names, rule ids, report fields), so all five README
      languages share the same pair.

No evidence chart is generated: this repository ships no benchmark data.
The Pillow font probe below is the guard the family skeleton requires; it
fails loudly instead of ever rendering Chinese as tofu boxes.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e"),
}

# Evidence charts would be written as webp at this quality; kept here so a
# future benchmark lands on the same family setting.
WEBP_QUALITY = 90

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def check_font() -> None:
    """Draw a Chinese probe; fails at the first sign of a broken font."""
    probe = Image.new("RGB", (16, 16), "#ffffff")
    ImageDraw.Draw(probe).text((0, 0), "分析表", font=font(12), fill="#000000")


# ---------------------------------------------------------------------------
# Hero data-flow SVG (light + dark)
# ---------------------------------------------------------------------------
FLOW_NODES = [
    ("worksheet", "JSON / YAML"),
    ("rule pack", "rules/fmea-table-check.yaml"),
    ("fmea_table_check", "file | material"),
    ("report", "issueCount · skippedCount"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 420
    nw, nh, gap = 235, 100, 45
    y0 = 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="dsh-fmea-table-check '
        f'data flow">',
        f'<title>dsh-fmea-table-check data flow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        f'dsh-fmea-table-check</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">fmea_table_check · JSON / YAML · '
        f'rules/fmea-table-check.yaml</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub) in enumerate(FLOW_NODES):
        x = 60 + i * (nw + gap)
        accent = GREEN[skin] if i == len(FLOW_NODES) - 1 else (
            FAMILY if i == 1 else s["border"])
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 40}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="16" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 70}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="11">{sub}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 6
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # rule-under-check bar: FM-003 arithmetic + skipped-by-default rules
    bx, bw, by, bh = 60, 1075, 305, 56
    for i in (2, 3):  # node 2 and node 3 centres above the bar
        cx = 60 + i * (nw + gap) + nw // 2
        parts.append(
            f'<path d="M{cx} {y0 + nh}v{by - y0 - nh}" '
            f'stroke="{FAMILY}" stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="{bx + bw // 2}" y="{by + 34}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="14">FM-003: severity × occurrence × detection = rpn · '
        f'FM-004 / FM-006 unconfigured → skipped</text>')
    parts.append(
        f'<text x="60" y="395" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">Apache-2.0 · PerryLink DSH plugin family '
        f'· no network · no model call</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    check_font()
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-fmea-table-check-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG assets to docs/assets/ "
          "(no evidence chart: no benchmark data in this repository)")


if __name__ == "__main__":
    main()
