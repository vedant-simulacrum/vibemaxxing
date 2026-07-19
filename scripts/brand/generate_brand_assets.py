#!/usr/bin/env python3
"""Generate the canonical outlined SVG masters for the vibemaxxing identity.

The output contains no live font references. Set VIBEMAXXING_BRAND_FONT to
override the development font used to construct the outlines.
"""

from __future__ import annotations

import html
import hashlib
import math
import os
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "brand" / "source"
DEFAULT_FONT = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf"
EXPECTED_FONT_SHA256 = "7f33328e6b4d4cd21b45fa625791928c9407dc702db6780e56b09ca9a3ecaa67"

INK = "#171714"
INDIGO = "#5847E8"
INDIGO_LIGHT = "#9187FF"
CANVAS = "#F4F2ED"
WHITE = "#FFFFFF"
MUTED = "#716F68"
LINE = "#DEDAD1"


def resolve_font() -> Path:
    override = os.environ.get("VIBEMAXXING_BRAND_FONT")
    if override and Path(override).exists():
        return Path(override)
    default = Path(DEFAULT_FONT)
    if default.exists():
        return default
    result = subprocess.run(
        ["fc-match", "Nimbus Sans:style=Bold", "-f", "%{file}"],
        check=True,
        capture_output=True,
        text=True,
    )
    matched = Path(result.stdout.strip())
    if not matched.exists():
        raise SystemExit("Nimbus Sans Bold not found; set VIBEMAXXING_BRAND_FONT")
    return matched


FONT_PATH = resolve_font()
FONT_SHA256 = hashlib.sha256(FONT_PATH.read_bytes()).hexdigest()
if FONT_SHA256 != EXPECTED_FONT_SHA256 and os.environ.get("VIBEMAXXING_ALLOW_UNPINNED_FONT") != "1":
    raise SystemExit(
        "Brand font checksum mismatch. Expected "
        f"{EXPECTED_FONT_SHA256}, received {FONT_SHA256}. "
        "Do not regenerate identity assets with a different font without visual approval. "
        "Set VIBEMAXXING_ALLOW_UNPINNED_FONT=1 only for an explicitly reviewed migration."
    )
FONT = TTFont(FONT_PATH)
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UPM = FONT["head"].unitsPerEm
HMTX = FONT["hmtx"].metrics


def kerning() -> dict[tuple[str, str], int]:
    pairs: dict[tuple[str, str], int] = {}
    if "kern" in FONT:
        for table in FONT["kern"].kernTables:
            pairs.update(table.kernTable)
    return pairs


KERN = kerning()


def text_paths(
    text: str,
    size: float,
    x: float,
    baseline: float,
    fill: str,
    tracking: float = 0,
) -> tuple[str, float]:
    scale = size / UPM
    cursor = x
    elements: list[str] = []
    previous: str | None = None
    for char in text:
        glyph_name = CMAP.get(ord(char))
        if not glyph_name:
            cursor += size * 0.35
            previous = None
            continue
        if previous:
            cursor += KERN.get((previous, glyph_name), 0) * scale
        pen = SVGPathPen(GLYPHS)
        GLYPHS[glyph_name].draw(pen)
        path = pen.getCommands()
        if path:
            elements.append(
                f'<path d="{path}" fill="{fill}" '
                f'transform="translate({cursor:.3f} {baseline:.3f}) scale({scale:.7f} {-scale:.7f})"/>'
            )
        cursor += HMTX[glyph_name][0] * scale + tracking
        previous = glyph_name
    return "\n".join(elements), cursor - x - tracking


def svg_document(width: int, height: int, body: str, title: str, description: str) -> str:
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">{html.escape(title)}</title>
  <desc id="desc">{html.escape(description)}</desc>
{body}
</svg>
'''


def write(name: str, content: str) -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    (SOURCE / name).write_text(content, encoding="utf-8")


def wordmark(name: str, ink: str, base_rule: str, accent: str, with_rule: bool = True) -> None:
    paths, width = text_paths("vibemaxxing", 128, 38, 124, ink, tracking=-5.2)
    canvas_width = math.ceil(width + 76)
    rule = ""
    if with_rule:
        start = 38
        end = 38 + width
        accent_start = end - width * 0.20
        rule = f'''
  <path d="M{start:.2f} 148H{end:.2f}" stroke="{base_rule}" stroke-width="3"/>
  <path d="M{accent_start:.2f} 148H{end:.2f}" stroke="{accent}" stroke-width="8"/>'''
    height = 172 if with_rule else 144
    write(
        name,
        svg_document(
            canvas_width,
            height,
            f"  {paths}{rule}",
            "vibemaxxing wordmark",
            "Lowercase vibemaxxing wordmark with a restrained ledger rule ending in indigo." if with_rule else "Lowercase vibemaxxing wordmark without the ledger rule.",
        ),
    )


def mark(name: str, background: str | None, foreground: str, rule: str, accent: str, border: str | None = None) -> None:
    paths, width = text_paths("vm", 246, 0, 0, foreground, tracking=-10)
    x = (512 - width) / 2
    # Rewrite the origin transforms generated above for centered placement.
    paths, _ = text_paths("vm", 246, x, 334, foreground, tracking=-10)
    rect = ""
    if background:
        rect = f'  <rect x="2" y="2" width="508" height="508" rx="108" fill="{background}"' + (f' stroke="{border}" stroke-width="4"' if border else "") + "/>\n"
    body = f'''{rect}  {paths}
  <path d="M92 399H420" stroke="{rule}" stroke-width="7"/>
  <path d="M300 399H420" stroke="{accent}" stroke-width="16"/>'''
    write(name, svg_document(512, 512, body, "vibemaxxing vm mark", "Compact vm monogram with a ledger rule ending in indigo."))


def favicon() -> None:
    paths, width = text_paths("vm", 252, 0, 0, WHITE, tracking=-12)
    paths, _ = text_paths("vm", 252, (512 - width) / 2, 337, WHITE, tracking=-12)
    body = f'''  <rect width="512" height="512" rx="112" fill="{INK}"/>
  {paths}
  <rect x="330" y="393" width="90" height="18" rx="9" fill="{INDIGO_LIGHT}"/>'''
    write("favicon.svg", svg_document(512, 512, body, "vibemaxxing favicon", "Small-size vm mark with one indigo ledger dash."))


def maskable_mark() -> None:
    paths, width = text_paths("vm", 224, 0, 0, WHITE, tracking=-10)
    paths, _ = text_paths("vm", 224, (512 - width) / 2, 322, WHITE, tracking=-10)
    body = f'''  <rect width="512" height="512" fill="{INK}"/>
  {paths}
  <path d="M128 377H384" stroke="#5B5751" stroke-width="7"/>
  <path d="M290 377H384" stroke="{INDIGO_LIGHT}" stroke-width="16"/>'''
    write("mark-maskable.svg", svg_document(512, 512, body, "vibemaxxing maskable app icon", "Full-bleed maskable vm app icon with safe-zone padding."))


def social_card(name: str, width: int, height: int) -> None:
    word, word_width = text_paths("vibemaxxing", 54, 90, 120, INK, tracking=-2.3)
    burn, _ = text_paths("Burn more.", 88, 90, 326, INK, tracking=-2)
    rank, _ = text_paths("Rank higher.", 88, 90, 420, INK, tracking=-2)
    privacy, _ = text_paths("Public competition. Private transcripts.", 24, 94, 490, MUTED, tracking=0)
    line_end = 90 + word_width
    body = f'''  <rect width="{width}" height="{height}" fill="{CANVAS}"/>
  <rect x="42" y="42" width="{width - 84}" height="{height - 84}" rx="28" fill="{WHITE}" stroke="{LINE}"/>
  {word}
  <path d="M90 143H{line_end:.2f}" stroke="#C9C5BC" stroke-width="2"/>
  <path d="M{line_end - word_width * .2:.2f} 143H{line_end:.2f}" stroke="{INDIGO}" stroke-width="6"/>
  {burn}
  {rank}
  {privacy}
  <rect x="{width - 226}" y="{height - 116}" width="136" height="46" rx="23" fill="{INK}"/>
  <circle cx="{width - 197}" cy="{height - 93}" r="6" fill="{INDIGO_LIGHT}"/>
  <path d="M{width - 183} {height - 93}H{width - 119}" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>'''
    write(name, svg_document(width, height, body, "vibemaxxing social card", "Burn more. Rank higher. Public competition. Private transcripts."))


def social_card_dark() -> None:
    width, height = 1200, 630
    word, word_width = text_paths("vibemaxxing", 54, 90, 120, WHITE, tracking=-2.3)
    burn, _ = text_paths("Burn more.", 88, 90, 326, WHITE, tracking=-2)
    rank, _ = text_paths("Rank higher.", 88, 90, 420, WHITE, tracking=-2)
    privacy, _ = text_paths("Public competition. Private transcripts.", 24, 94, 490, "#AAA79F")
    line_end = 90 + word_width
    body = f'''  <rect width="{width}" height="{height}" fill="{INK}"/>
  {word}
  <path d="M90 143H{line_end:.2f}" stroke="#5B5751" stroke-width="2"/>
  <path d="M{line_end - word_width * .2:.2f} 143H{line_end:.2f}" stroke="{INDIGO_LIGHT}" stroke-width="6"/>
  {burn}
  {rank}
  {privacy}
  <rect x="974" y="514" width="136" height="46" rx="23" fill="{INDIGO}"/>
  <circle cx="1003" cy="537" r="6" fill="{WHITE}"/>
  <path d="M1017 537H1081" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>'''
    write("social-card-dark-1200x630.svg", svg_document(width, height, body, "vibemaxxing dark social card", "Dark campaign card: Burn more. Rank higher."))


def brand_sheet() -> None:
    word, word_width = text_paths("vibemaxxing", 94, 105, 200, INK, tracking=-4)
    vm_white, vm_width = text_paths("vm", 136, 0, 0, WHITE, tracking=-6)
    vm_white, _ = text_paths("vm", 136, 755 + (230 - vm_width) / 2, 231, WHITE, tracking=-6)
    headline, _ = text_paths("Burn more. Rank higher.", 45, 105, 505, INK, tracking=-1)
    privacy, _ = text_paths("Public competition. Private transcripts.", 21, 105, 547, MUTED)
    body = f'''  <rect width="1200" height="720" fill="{CANVAS}"/>
  <text x="105" y="75" fill="{MUTED}" font-family="Arial, sans-serif" font-size="15" font-weight="700" letter-spacing="2">VIBEMAXXING / APPROVED BRAND SYSTEM</text>
  {word}
  <path d="M105 225H{105 + word_width:.2f}" stroke="{INK}" stroke-width="2"/>
  <path d="M{105 + word_width * .8:.2f} 225H{105 + word_width:.2f}" stroke="{INDIGO}" stroke-width="6"/>
  <rect x="755" y="90" width="230" height="230" rx="50" fill="{INK}"/>
  {vm_white}
  <path d="M797 272H943" stroke="#5B5751" stroke-width="4"/>
  <path d="M890 272H943" stroke="{INDIGO_LIGHT}" stroke-width="10"/>
  <circle cx="1070" cy="135" r="34" fill="{INK}"/>
  <circle cx="1070" cy="213" r="34" fill="{INDIGO}"/>
  <circle cx="1070" cy="291" r="34" fill="{WHITE}" stroke="{LINE}"/>
  {headline}
  {privacy}
  <rect x="105" y="602" width="990" height="58" rx="12" fill="{WHITE}" stroke="{LINE}"/>
  <circle cx="135" cy="631" r="8" fill="{INK}"/>
  <circle cx="163" cy="631" r="8" fill="{INDIGO}"/>
  <circle cx="191" cy="631" r="8" fill="{CANVAS}" stroke="{LINE}"/>
  <text x="225" y="637" fill="{MUTED}" font-family="Arial, sans-serif" font-size="17">Ledger rule · Electric indigo #5847E8 · Ink #171714 · Canvas #F4F2ED</text>'''
    write("brand-sheet.svg", svg_document(1200, 720, body, "vibemaxxing brand sheet", "Approved wordmark, vm mark, color palette, and copy line."))


def main() -> None:
    wordmark("wordmark-primary.svg", INK, INK, INDIGO)
    wordmark("wordmark-reverse.svg", WHITE, "#5B5751", INDIGO_LIGHT)
    wordmark("wordmark-indigo.svg", INDIGO, INDIGO, INK)
    wordmark("wordmark-monochrome.svg", INK, INK, INK)
    wordmark("wordmark-no-rule.svg", INK, INK, INDIGO, with_rule=False)
    mark("mark-primary.svg", INK, WHITE, "#5B5751", INDIGO_LIGHT)
    mark("mark-indigo.svg", INDIGO, WHITE, "#8E84FF", WHITE)
    mark("mark-light.svg", WHITE, INK, "#CAC6BD", INDIGO, border=LINE)
    mark("mark-one-color.svg", None, INK, INK, INK)
    favicon()
    maskable_mark()
    social_card("social-card-1200x630.svg", 1200, 630)
    social_card("social-card-1200x675.svg", 1200, 675)
    social_card("github-social-1280x640.svg", 1280, 640)
    social_card_dark()
    brand_sheet()
    print(f"Generated outlined masters in {SOURCE.relative_to(ROOT)} using {FONT_PATH}")


if __name__ == "__main__":
    main()
