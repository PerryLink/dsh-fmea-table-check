#!/usr/bin/env python3
"""README visuals for dsh-fmea-table-check, derived from the shipped checker.

Two figures, both read off `rules/fmea-table-check.yaml`, `src/model.ts`,
`src/shared/rows.ts` and `src/view.ts` -- not from a generic checker template.

  hero 1440x576 (Pillow, zh/en x light/dark, four WebP files)
      Left column: kicker / wordmark / two value lines / one subtitle / one meta
      line / footer.  Right side: the one thing this plugin computes --
      ① the RPN arithmetic for row 1 (severity 8 x occurrence 4 x detection 3
      = 96, while the sheet fills in 100, tolerance 0), ② the eight-rule rail
      with the three states a rule can end in (diff / clean / unset), and
      ③ the two output channels: one located issue and the two rules that
      report themselves as unconfigured.  Every number, label, state and
      sentence is the FM-003 fixture's real tool output (`100 != 8 x 4 x 3`,
      issueCount 1, skippedCount 2, FM-004 threshold 0, FM-006 values []).

  flow 1100x660 (hand-written SVG, light/dark)
      Grammar: FOUR READING SURFACES over one material, with a dual outlet.
      The sheet is not a pipeline: each rule reads one region of it -- the
      header, the analysis chain, the scores, the action closure -- so the
      rules are laid out as four parallel surfaces, grouped by the region
      they read, with the engine's own `params.check.kind` written under each
      rule id and the run state on the right.  Both inputs (material, rule
      pack) feed all four surfaces; nothing is gated on the surface above it.
      Under the surfaces, the two outlets keep `issues[]` (locator / found /
      expected / fix / basis) and `skipped[]` (rule + reason) apart, because
      an empty issue list is never a pass.

All labels are measured before they are drawn; a label that would overflow
aborts the run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-fmea-table-check"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

RADIUS = 20          # family rounding: 18-22
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", pill="#ece7f9", band="#f5f2fb",
        grid="#e7e4f0", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        shadow=(38, 30, 72), glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", pill="#242d42", band="#202839",
        grid="#262f42", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        shadow=(0, 0, 0), glow=48,
    ),
}


def font(size: int, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(26))
                                 ).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = RADIUS, shadow: int = SHADOW,
         fill: str | None = None, edge: str | None = None) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=s["shadow"] + (int(10 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=2)
    return base.convert("RGB")


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(int(round(size)), kind))


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def label(img: Image.Image, xy: tuple[float, float], content: str, size: float,
          kind: str, fill: str, max_w: float, what: str,
          anchor: str = "la") -> None:
    require_w(content, size, kind, max_w, what)
    ImageDraw.Draw(img).text(xy, content, font=font(int(round(size)), kind),
                             fill=hx(fill), anchor=anchor)


def pill(img: Image.Image, xy: tuple[int, int], content: str, s: dict,
         size: float = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    w = measure(content, size, kind)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), content, font=font(int(round(size)), kind),
           fill=hx(fg or s["accent"]), anchor="lm")
    return int(x + w + 30)


def chip_right(img: Image.Image, right: float, y: float, content: str, fg: str,
               bg: str, s: dict, size: float = 10.5, height: int = 20,
               kind: str = "cjk_bold", dashed: bool = False) -> int:
    d = ImageDraw.Draw(img)
    w = measure(content, size, kind) + 18
    x = right - w
    if dashed:
        dash_round_rect(d, (x, y, right, y + height), s["edge"], radius=height // 2)
    d.rounded_rectangle([x, y, right, y + height], radius=height / 2,
                        fill=hx(bg), outline=None if dashed else hx(bg), width=0)
    d.text((x + 9, y + height / 2), content, font=font(int(round(size)), kind),
           fill=hx(fg), anchor="lm")
    return int(x)


def badge(img: Image.Image, cx: float, cy: float, content: str, s: dict,
          size: float = 10) -> None:
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=hx(s["pill"]))
    d.text((cx, cy), content, font=font(int(round(size)), "cjk_bold"),
           fill=hx(s["accent"]), anchor="mm")


def dash_round_rect(d: ImageDraw.ImageDraw, box: tuple[float, float, float, float],
                    color: str, radius: int = 8, width: int = 2) -> None:
    x0, y0, x1, y1 = box
    for yy in (y0, y1):
        for x in range(int(x0 + radius), int(x1 - radius), 9):
            d.line([(x, yy), (min(x + 5, x1 - radius), yy)], fill=hx(color),
                   width=width)
    for y in range(int(y0 + radius), int(y1 - radius), 9):
        for xx in (x0, x1):
            d.line([(xx, y), (xx, min(y + 5, y1 - radius))], fill=hx(color),
                   width=width)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360,
          fill=hx(color), width=width)
    d.arc([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90,
          fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
# One real run: tests/fixtures/FM-003/FM-003-unsafe.json, observed through
# lib/index.mjs -> fmea_table_check (issueCount 1, skippedCount 2).
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核对器",
        value=["八条规则，逐行核对分析表", "每条差异落到行号与栏名"],
        sub="只列差异与算术，不下合规结论，原件不改。",
        meta="fmea_table_check · FM-001…FM-008 · issues + skipped",
        foot="Apache-2.0 · 只读 · 不联网 · 不调用模型",
        calc_title="风险演算 · 第 1 行",
        calc_sub="密封面泄漏 · 容差 0",
        formula="rpn = severity × occurrence × detection",
        factors=[("严重度", "8"), ("频度", "4"), ("探测度", "3")],
        calc_row="计算值",
        sheet_row="表内填报",
        delta="Δ +4 · 超过容差 0",
        footnote="四字段缺一即 skipped",
        rules_title="八条规则 · 本次状态",
        rules_sub="差异 1 · 无差异 6 · 未配置 2",
        rules=[
            ("FM-001", "分析链已记录", "clean"),
            ("FM-002", "评分可运算", "clean"),
            ("FM-003", "RPN 等于三者之积", "diff"),
            ("FM-004", "高风险须有措施", "unset"),
            ("FM-005", "措施有责任人与期限", "clean"),
            ("FM-006", "状态取值在册", "unset"),
            ("FM-007", "表头写明分析对象", "clean"),
            ("FM-008", "失效模式无占位符", "clean"),
        ],
        status_words={"diff": "差异", "clean": "无差异", "unset": "未配置"},
        out_title="两条输出通道",
        out_chip="issueCount 1 · skippedCount 2",
        issues_head="issues[] · 1 条",
        issues_found="第 1 行「rpn」填报 100，而 8 × 4 × 3 = 96",
        issues_expected="「rpn」应等于 severity × occurrence × detection",
        issues_locator="locator 第1行 · 字段 rpn · warn",
        issues_fix="fix 核对是否抄错或漏改；本条只做算术核对",
        skip_head="skipped[] · 2 条",
        skip_lines=["FM-004 · threshold 0 未配置",
                    "FM-006 · values [] 未配置"],
        skip_note="空 issues ≠ 没问题",
        skip_foot="结论留给审核人",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Eight rules over one FMEA sheet", "each difference on a row + column"],
        sub="Literal differences and arithmetic only — no verdict.",
        meta="fmea_table_check · FM-001…FM-008 · issues + skipped",
        foot="Apache-2.0 · read-only · no network · no model call",
        calc_title="Risk arithmetic · row 1",
        calc_sub="Seal-face leak · tolerance 0",
        formula="rpn = severity × occurrence × detection",
        factors=[("severity", "8"), ("occurrence", "4"), ("detection", "3")],
        calc_row="computed",
        sheet_row="in the sheet",
        delta="Δ +4 · tolerance 0",
        footnote="any unparsable factor → skipped",
        rules_title="Eight rules · this run",
        rules_sub="diff 1 · clean 6 · unset 2",
        rules=[
            ("FM-001", "analysis chain recorded", "clean"),
            ("FM-002", "scores computable", "clean"),
            ("FM-003", "RPN = S × O × D", "diff"),
            ("FM-004", "high risk needs action", "unset"),
            ("FM-005", "action has owner + dueAt", "clean"),
            ("FM-006", "status in vocabulary", "unset"),
            ("FM-007", "header names the object", "clean"),
            ("FM-008", "no template placeholders", "clean"),
        ],
        status_words={"diff": "diff", "clean": "clean", "unset": "unset"},
        out_title="Two output channels",
        out_chip="issueCount 1 · skippedCount 2",
        issues_head="issues[] · 1",
        issues_found="row 1 「rpn」 says 100, but 8 × 4 × 3 = 96",
        issues_expected="「rpn」 should equal severity × occurrence × detection",
        issues_locator="locator row 1 · field rpn · warn",
        issues_fix="fix check for a transcription slip; arithmetic only",
        skip_head="skipped[] · 2",
        skip_lines=["FM-004 · threshold 0 unset",
                    "FM-006 · values [] unset"],
        skip_note="empty issues ≠ all clear",
        skip_foot="the reviewer decides",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1110, 84, 380, s["accent"], s["glow"])
    img = glow(img, 170, 566, 280, s["accent"], max(8, s["glow"] // 3))

    m = 56
    col_w = 560

    # ---- left column --------------------------------------------------------
    pill(img, (m, 64), h["kicker"], s, size=15.5)
    title_size = fit(NAME, "mono_bold", 536, 60, 46)
    label(img, (m - 1, 124), NAME, title_size, "mono_bold", s["text"], 536,
          "hero title")
    value_size = fit_lines(h["value"], "cjk_bold", col_w,
                           37 if lang == "zh" else 35, 29)
    for i, line in enumerate(h["value"]):
        label(img, (m, 232 + i * 56), line, value_size, "cjk_bold", s["text"],
              col_w, "hero value line")
    label(img, (m, 354), h["sub"], 21, "cjk", s["sub"], col_w, "hero subtitle")
    label(img, (m + 1, 406), h["meta"], 18, "cjk", s["faint"], col_w,
          "hero meta")
    ImageDraw.Draw(img).line([m + 1, 456, m + col_w - 4, 456],
                             fill=hx(s["grid"]), width=2)
    label(img, (m + 1, 472), h["foot"], 15, "cjk", s["faint"], col_w,
          "hero footer")

    # ---- (1) RPN arithmetic -------------------------------------------------
    img = card(img, (636, 44, 1000, 352), s)
    d = ImageDraw.Draw(img)
    badge(img, 665, 64, "①", s)
    label(img, (682, 54), h["calc_title"], 14.5, "cjk_bold", s["text"], 210,
          "calc title")
    chip_right(img, 980, 52, "FM-003", s["accent"], s["pill"], s, size=10.5)
    d = ImageDraw.Draw(img)
    label(img, (656, 86), h["formula"], 11.5, "mono", s["accent"], 324,
          "calc formula")
    label(img, (656, 108), h["calc_sub"], 11.5, "cjk", s["sub"], 324,
          "calc subtitle")
    d = ImageDraw.Draw(img)
    d.line([656, 124, 980, 124], fill=hx(s["grid"]), width=1)
    d.rounded_rectangle([648, 140, 651, 300], radius=1.5, fill=hx(s["accent"]))

    factor_rows = (148, 182, 216)
    for i, (name, value) in enumerate(h["factors"]):
        y = factor_rows[i]
        if i == 0:
            label(img, (662, y - 15), name, 13.5, "cjk", s["sub"], 210,
                  "factor label")
        else:
            label(img, (662, y - 15), "×", 14, "mono", s["faint"], 18,
                  "factor times")
            label(img, (680, y - 15), name, 13.5, "cjk", s["sub"], 200,
                  "factor label")
        label(img, (980, y), value, 24, "mono_bold", s["text"], 120,
              "factor value", anchor="ra")

    d = ImageDraw.Draw(img)
    d.line([656, 238, 980, 238], fill=hx(s["edge"]), width=2)

    label(img, (662, 255), h["calc_row"], 13, "cjk", s["sub"], 210,
          "computed label")
    label(img, (980, 270), "96", 26, "mono_bold", s["accent"], 120,
          "computed value", anchor="ra")

    label(img, (662, 281), h["sheet_row"], 13, "cjk", s["sub"], 210,
          "declared label")
    label(img, (980, 296), "100", 26, "mono_bold", s["mark"], 120,
          "declared value", anchor="ra")

    # the delta sits on its own line, under the two values; it is anchored to
    # the card's left padding, so a long label can never run over the edge
    delta_w = measure(h["delta"], 10.5, "cjk") + 18
    require_w(h["delta"], 10.5, "cjk", 787 - 8 - 656 - 18, "hero delta chip")
    chip_right(img, 656 + delta_w, 306, h["delta"], s["mark"], s["mark_bg"], s,
               size=10.5, kind="cjk")
    label(img, (787, 322), h["footnote"], 10.5, "cjk", s["faint"], 190,
          "calc footnote")

    # ---- (2) rule rail ------------------------------------------------------
    img = card(img, (1016, 44, 1384, 352), s)
    d = ImageDraw.Draw(img)
    badge(img, 1045, 64, "②", s)
    label(img, (1062, 54), h["rules_title"], 14.5, "cjk_bold", s["text"], 230,
          "rules title")
    chip_right(img, 1364, 52, "8", s["accent"], s["pill"], s, size=10.5)
    d = ImageDraw.Draw(img)
    label(img, (1036, 88), h["rules_sub"], 11, "cjk", s["faint"], 328,
          "rules sub")
    d = ImageDraw.Draw(img)
    d.line([1036, 104, 1364, 104], fill=hx(s["grid"]), width=1)

    state_style = {
        "diff": (s["mark"], s["mark_bg"]),
        "clean": (s["ok"], s["ok_bg"]),
        "unset": (s["faint"], s["band"]),
    }
    first_cy = 126
    step = 28
    for i, (rid, desc, state) in enumerate(h["rules"]):
        cy = first_cy + i * step
        label(img, (1036, cy), rid, 12, "mono_bold", s["text"], 46,
              "rule id", anchor="lm")
        label(img, (1090, cy), desc, 12, "cjk", s["sub"], 208, "rule desc",
              anchor="lm")
        fg, bg = state_style[state]
        chip_right(img, 1364, cy - 9, h["status_words"][state], fg, bg, s,
                   size=10.5, height=18, dashed=state == "unset")
        d = ImageDraw.Draw(img)
        if i < len(h["rules"]) - 1:
            d.line([1036, cy + 14, 1364, cy + 14], fill=hx(s["grid"]), width=1)

    # ---- (3) two output channels -------------------------------------------
    img = card(img, (636, 368, 1384, 524), s)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([644, 384, 647, 503], radius=1.5, fill=hx(s["accent"]))
    badge(img, 665, 388, "③", s)
    label(img, (682, 378), h["out_title"], 13.5, "cjk_bold", s["text"], 260,
          "out title")
    chip_right(img, 1364, 376, h["out_chip"], s["accent"], s["pill"], s,
               size=10.5)
    d = ImageDraw.Draw(img)
    d.line([656, 406, 1364, 406], fill=hx(s["grid"]), width=1)
    d.line([1004, 412, 1004, 512], fill=hx(s["grid"]), width=1)

    label(img, (656, 426), h["issues_head"], 11.5, "cjk_bold", s["accent"],
          330, "issues head")
    label(img, (656, 448), h["issues_found"], 12, "cjk", s["text"], 330,
          "issues found")
    label(img, (656, 468), h["issues_expected"], 11.5, "cjk", s["sub"], 330,
          "issues expected")
    label(img, (656, 487), h["issues_locator"], 10.5, "cjk", s["faint"], 330,
          "issues locator")
    label(img, (656, 505), h["issues_fix"], 10.5, "cjk", s["faint"], 330,
          "issues fix")

    label(img, (1024, 426), h["skip_head"], 11.5, "cjk_bold", s["mark"], 340,
          "skip head")
    for i, line in enumerate(h["skip_lines"]):
        label(img, (1024, 448 + i * 20), line, 11.5, "cjk", s["sub"], 340,
              "skip line")
    label(img, (1024, 486), h["skip_note"], 12, "cjk_bold", s["text"], 340,
          "skip note")
    label(img, (1024, 505), h["skip_foot"], 10.5, "cjk", s["faint"], 340,
          "skip footer")

    name = f"{NAME}-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}x{H})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", surface="#f8f5fd", card="#ffffff", edge="#e6e2ef",
        band="#f5f2fb", pill="#ece7f9", text="#141419", sub="#4d5261",
        faint="#8f94a4",
        accent="#4B67B4", accent2="#15803d",
        warn="#b45309", warn_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        rule="#e7e4f0", shadow="#2b2440", shadow_op="0.13",
        dot="#cfc8e2", dot_op="0.55",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", surface="#171e2c", card="#1b2231", edge="#2e374b",
        band="#202839", pill="#242d42", text="#f0f3f9", sub="#a8b1c4",
        faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        warn="#d9a441", warn_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        rule="#2b3348", shadow="#000000", shadow_op="0.50",
        dot="#2a3346", dot_op="0.55",
    ),
}

FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = ("Consolas,'Microsoft YaHei',ui-monospace,monospace")

# id, one-line description, engine dispatch key, run state (FM-003 fixture)
LANES = [
    ("HEADER", [
        ("FM-007", "header item present", "headerPresence", "clean"),
    ]),
    ("CHAIN", [
        ("FM-001", "mode · effect · cause filled", "presenceAny", "clean"),
        ("FM-008", "no placeholder terms", "containsAny", "clean"),
    ]),
    ("SCORES", [
        ("FM-002", "severity is a number", "number", "clean"),
        ("FM-003", "RPN = S × O × D", "productOf", "diff"),
    ]),
    ("ACTIONS", [
        ("FM-004", "high risk needs action", "thresholdPresence", "unset"),
        ("FM-005", "action has owner/dueAt", "conditionalPresence", "clean"),
        ("FM-006", "status vocabulary", "enum", "unset"),
    ]),
]


class Svg:
    """Small SVG writer that measures every label before it is emitted."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def _w(self, content: str, size: float, kind: str,
           tracking: float | None = None) -> float:
        path = FONT_FILES[kind]
        if not content.isascii():
            path = FONT_FILES["cjk_bold" if "bold" in kind else "cjk"]
        got = _MEASURE.textlength(content, font=ImageFont.truetype(path, size))
        if tracking:
            got += tracking * max(len(content) - 1, 0)
        return got

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None, tracking: float | None = None) -> None:
        kind = ("mono" if mono else "cjk") + ("_bold" if weight else "")
        if mono and weight:
            kind = "mono_bold"
        if max_w is not None:
            got = self._w(content, size, kind, tracking)
            if got > max_w + 0.4:
                self.overflows.append(f"{content!r} needs {got:.1f}px > "
                                      f"{max_w:.0f}px")
        family = FONT_CSS_MONO if mono else FONT_CSS_SANS
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if tracking:
            attrs.append(f'letter-spacing="{tracking}"')
        self.add(f'<text {" ".join(attrs)}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.5, dash: str | None = None,
             marker: str | None = None, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             marker: str | None = None, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'd="{d}"', 'fill="none"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linejoin="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<path {" ".join(attrs)}/>')

    def circle(self, cx: float, cy: float, r: float, *, fill: str,
               stroke: str | None = None, sw: float = 1.5) -> None:
        attrs = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        self.add(f'<circle {" ".join(attrs)}/>')

    def chip_right(self, right: float, y: float, content: str, fg: str, bg: str,
                   *, size: float = 11, pad: float = 9, height: float = 22,
                   mono: bool = False, weight: int | None = None,
                   stroke: str | None = None, dash: str | None = None) -> float:
        kind = "mono" if mono else "cjk"
        if weight:
            kind += "_bold"
        w = self._w(content, size, kind) + pad * 2
        x = right - w
        self.rect(x, y, w, height, fill=bg, rx=height / 2, stroke=stroke,
                  sw=1.2, dash=dash)
        self.text(x + pad, y + height / 2 + size * 0.36, content, size, fg,
                  weight=weight, mono=mono)
        return x

    def svg(self, w: int, h: int, title: str, desc: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-labelledby="title desc">')
        return "\n".join([head, f'<title id="title">{escape(title)}</title>',
                          f'<desc id="desc">{escape(desc)}</desc>',
                          *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg()

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.2" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    v.add(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="180%">'
          f'<feDropShadow dx="0" dy="8" stdDeviation="10" '
          f'flood-color="{s["shadow"]}" flood-opacity="{s["shadow_op"]}"/></filter>')
    v.add('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    v.add(f'<pattern id="dots" width="24" height="24" '
          f'patternUnits="userSpaceOnUse">'
          f'<circle cx="1.2" cy="1.2" r="1.2" fill="{s["dot"]}"/></pattern>')
    v.add("</defs>")

    v.rect(0, 0, W, H, fill="url(#bg)")
    v.rect(0, 0, W, H, fill="url(#dots)", opacity=s["dot_op"])

    # ---- header -------------------------------------------------------------
    v.text(44, 58, NAME, 30, s["text"], weight=700, mono=True, max_w=560)
    v.text(44, 86,
           "Eight rules read one worksheet at four surfaces; an empty issue "
           "list is never “all clear”.", 14.5, s["sub"], max_w=770)
    v.chip_right(1056, 32, "rules/fmea-table-check.yaml · v2026.1",
                 s["accent"], s["pill"], size=11.5, pad=12, height=28, mono=True)
    v.text(44, 112, "IN · file | material · JSON / YAML · rows[]", 11,
           s["faint"], mono=True, max_w=520)
    v.text(1056, 112, "OUT · issues[] + skipped[]", 11, s["faint"],
           mono=True, anchor="end", max_w=280)
    v.line(44, 126, 1056, 126, stroke=s["rule"], sw=1)

    # ---- material card ------------------------------------------------------
    v.rect(44, 138, 286, 162, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(60, 160, "MATERIAL · READ-ONLY", 11, s["faint"], weight=700,
           tracking=1.0, max_w=254)
    v.text(60, 182, "FMEA worksheet", 13.5, s["text"], weight=700, max_w=254)
    v.text(60, 204, "file | material", 11.5, s["accent"], mono=True, max_w=254)
    v.text(60, 222, "JSON / YAML · rows[] + header", 11, s["sub"], max_w=254)
    v.text(60, 240, "row keys rows / items / failures / 失效", 11, s["sub"],
           max_w=254)
    v.text(60, 258, "15 alias groups zh/en → fields", 11, s["sub"], max_w=254)
    v.text(60, 276, "header item · team · method", 11, s["sub"], max_w=254)
    v.text(60, 294, "signedAt · revision", 11, s["sub"], max_w=254)

    # ---- rule pack card -----------------------------------------------------
    v.rect(44, 308, 286, 156, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(60, 330, "RULE PACK · DATA, NOT CODE", 11, s["faint"], weight=700,
           tracking=1.0, max_w=254)
    v.text(60, 352, "rules/fmea-table-check.yaml", 11.5, s["accent"], mono=True,
           max_w=254)
    v.text(60, 376, "8 rules · version 2026.1", 11, s["sub"], max_w=254)
    v.text(60, 394, "validated on load: id · severity ·", 11, s["sub"],
           max_w=254)
    v.text(60, 412, "basis.kind · excerpt ≥ 8 characters", 11, s["sub"],
           max_w=254)
    v.text(60, 434, "kind caps severity", 11, s["faint"], max_w=254)
    v.text(60, 452, "principle ≤ warn · institutional ≤ info", 11, s["sub"],
           max_w=254)

    # both inputs feed every surface: one bus, one entry, no gating implied
    v.line(330, 219, 340, 219, stroke=s["accent"], sw=1.5, opacity=0.75)
    v.line(330, 386, 340, 386, stroke=s["accent"], sw=1.5, opacity=0.75)
    v.line(340, 219, 340, 386, stroke=s["accent"], sw=1.5, opacity=0.75)
    v.circle(340, 316, 2.6, fill=s["accent"])
    v.line(340, 316, 352, 316, stroke=s["accent"], sw=1.5, marker="arr")

    # ---- four reading surfaces ---------------------------------------------
    v.rect(356, 136, 700, 328, fill=s["surface"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(376, 160, "FOUR READING SURFACES · RUN IN PARALLEL", 11, s["faint"],
           weight=700, tracking=1.0, max_w=470)

    legend = [("diff", s["warn"]), ("clean", s["ok"]), ("unset", s["faint"])]
    lx = 884
    for word, colour in legend:
        v.circle(lx + 3, 156, 3.2, fill=colour)
        v.text(lx + 11, 160, word, 11, colour, mono=True, max_w=44)
        lx += 11 + v._w(word, 11, "mono") + 16

    lane_tops = [176, 248, 320, 392]
    for lane_i, (lane_name, rules) in enumerate(LANES):
        top = lane_tops[lane_i]
        v.rect(366, top, 112, 64, fill=s["pill"], rx=14)
        v.rect(366, top + 14, 3, 36, fill=s["accent"], rx=1.5)
        v.text(380, top + 28, lane_name, 13, s["sub"], weight=700,
               tracking=0.6, max_w=90)
        v.text(380, top + 46, f"{len(rules)} rule" + ("s" if len(rules) > 1 else ""),
               11, s["faint"], max_w=90)

        if len(rules) == 1:
            widths = [272, 272]
        elif len(rules) == 2:
            widths = [272, 272]
        else:
            widths = [176, 176, 176]

        x = 490
        gap = 12 if len(rules) <= 2 else 14
        for rule_i, (rid, desc, kind, state) in enumerate(rules):
            w = widths[rule_i]
            v.rect(x, top + 2, w, 60, fill=s["card"], rx=14, stroke=s["edge"],
                   sw=1.3)
            v.text(x + 14, top + 24, rid, 13, s["text"], weight=700, mono=True,
                   max_w=w - 28)
            v.text(x + 14, top + 43, desc, 13, s["text"], max_w=w - 28)
            v.text(x + 14, top + 58, kind, 11, s["faint"], mono=True,
                   max_w=w - 28)
            state_colour = {"diff": (s["warn"], s["warn_bg"], None),
                            "clean": (s["ok"], s["ok_bg"], None),
                            "unset": (s["faint"], s["card"], "3 3")}[state]
            fg, bg, dash = state_colour
            v.chip_right(x + w - 10, top + 8, state, fg, bg, size=11,
                         pad=8, height=19, mono=True, stroke=fg if dash else None,
                         dash=dash)
            x += w + gap

        if len(rules) == 1:
            # header-scope explanation card: one value per sheet, not per row
            v.rect(x, top + 2, 272, 60, fill="none", rx=14, stroke=s["edge"],
                   sw=1.3, dash="5 5")
            v.text(x + 14, top + 22, "header scope", 11, s["faint"], weight=700,
                   max_w=244)
            v.text(x + 14, top + 40, "item · team · method ·", 11, s["sub"],
                   max_w=244)
            v.text(x + 14, top + 56, "signedAt · revision", 11, s["sub"],
                   max_w=244)

    # ---- two outlets --------------------------------------------------------
    v.rect(44, 476, 408, 120, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(60, 500, "issues[] · located differences", 11.5, s["accent"],
           weight=700, max_w=376)
    v.text(60, 523, "locator { row, field } · found · expected · fix · basis",
           11, s["sub"], mono=True, max_w=376)
    v.text(60, 543, "FM-003 · row 1 · field rpn · severity warn", 11,
           s["text"], mono=True, max_w=376)
    v.text(60, 563, "100 ≠ 8 × 4 × 3 = 96 · tolerance 0", 11, s["warn"],
           mono=True, max_w=376)
    v.text(60, 583, "basis derived-from-principle · wording guard", 11,
           s["faint"], max_w=376)

    v.rect(464, 476, 296, 120, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(480, 500, "skipped[] · never a silent pass", 11.5, s["warn"],
           weight=700, max_w=264)
    v.text(480, 523, "rule + reason, one entry per check", 11, s["sub"],
           max_w=264)
    v.text(480, 545, "FM-004 · threshold 0 — unset", 11, s["sub"], max_w=264)
    v.text(480, 565, "FM-006 · values [] — unset", 11, s["sub"], max_w=264)
    v.text(480, 587, "empty issues ≠ all clear", 11.5, s["accent"], weight=700,
           max_w=264)

    v.rect(772, 476, 284, 120, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(788, 500, "buildView()", 11.5, s["accent"], weight=700, mono=True,
           max_w=252)
    v.text(788, 523, "markdown + reportJson", 11, s["sub"], mono=True,
           max_w=252)
    v.text(788, 543, "issueCount 1 · skippedCount 2", 11, s["text"], mono=True,
           max_w=252)
    v.text(788, 563, "summary warn 1 · info 0", 11, s["sub"], mono=True,
           max_w=252)
    v.text(788, 583, "disclaimer always attached", 11, s["faint"], max_w=252)

    # ---- footer -------------------------------------------------------------
    v.line(44, 612, 1056, 612, stroke=s["rule"], sw=1)
    v.text(44, 632,
           "Four surfaces run in parallel; a rule that cannot run (field absent "
           "· threshold 0 · values []) is listed in skipped with its reason.",
           11, s["sub"], max_w=1012)
    v.text(44, 650,
           "no adjudication · original never modified · rulesFile / "
           "disabledRules / onlyRules / skipNotes / timeoutMs", 11, s["faint"],
           max_w=1012)

    if v.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " +
                         "\n  ".join(v.overflows))
    return v.svg(
        W, H,
        "dsh-fmea-table-check four reading surfaces with a dual outlet",
        "Eight rules read one FMEA worksheet at four surfaces: the header "
        "(FM-007), the analysis chain (FM-001, FM-008), the scores (FM-002, "
        "FM-003) and the action closure (FM-004, FM-005, FM-006). Each rule "
        "shows the engine's own check kind; unset configuration is dashed. "
        "The material and the rule pack both feed every surface, so no surface "
        "gates another. One run leaves 1 issue (FM-003, row 1, field rpn: 100 "
        "differs from 8 × 4 × 3 = 96) and 2 skipped rules (FM-004 threshold 0, "
        "FM-006 values []); issues carry locator, found, expected, fix and "
        "basis, skipped carries rule and reason, and buildView adds the counts "
        "and the disclaimer.",
    )


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"{NAME}-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100x660)")


if __name__ == "__main__":
    main()
