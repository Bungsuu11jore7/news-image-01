#!/usr/bin/env python3
"""news-image-01 entry: "The World in One Day".

A program that draws one infographic summing up the world's news of
Friday 13 November 2026, pixel by pixel, with the Python standard
library only, and writes it to /output/entry.png.

The AI judge has no news feed, so the image must explain itself: a
newspaper front page with six panels, each with a pictogram, a kicker,
a headline and a two-to-three-line summary, so a viewer who missed
the day can tell what happened from the image alone.

The six stories (all reported on Friday 13 November 2026):
  1. Europe joins the next round of Ukraine peace talks; work begins
     on the war's largest prisoner exchange.
  2. Nvidia chief Jensen Huang resigns; shares fall 16%; CFO Colette
     Kress becomes interim CEO.
  3. Microsoft 365 goes dark: Outlook and Teams fail worldwide.
  4. Four oil tankers struck in the Strait of Hormuz; Iran says it
     hit a US radar in Bahrain (claim unverified).
  5. Brooklyn building collapse: search ends, eight dead including
     two children, 18 hurt, city to check 100 sites.
  6. US court backs seizure of $1.2 billion stolen from Binance in
     the 29 October hack the FBI blames on North Korea.

Deterministic: every shape is drawn from fixed coordinates with
integer math; the PNG encoder is pure stdlib (zlib + struct), so two
runs write byte-identical files.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
NAVY = (20, 38, 63)            # masthead band, rules
NAVY_DARK = (12, 24, 42)
GOLD = (201, 162, 39)          # masthead rule, accents
CREAM = (247, 243, 234)        # page background
PAPER = (255, 253, 247)        # panel background
INK = (24, 24, 24)             # body text
MUTED = (90, 90, 90)           # kickers
WHITE = (255, 255, 255)
SKY = (135, 190, 220)          # globe
STEEL = (37, 99, 180)          # story 1 accent
GREEN = (46, 125, 50)          # story 2 accent
RED = (178, 34, 34)            # story 3 accent
TEAL = (0, 128, 128)           # story 4 accent
SLATE = (84, 84, 96)           # story 5 accent
AMBER = (176, 118, 0)          # story 6 accent
COIN = (212, 175, 55)          # gold coin
DARKGREY = (60, 60, 60)


# ------------------------------------------------------------------ font
# 5x7 bitmap font, uppercase plus digits and punctuation.
# '#' is a set pixel, '.' is empty.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".#...", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '(': ("..#..", ".#...", "#....", "#....", "#....", ".#...", "..#.."),
    ')': (".#..", "...#.", "....#", "....#", "....#", "...#.", ".#.."),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


class Canvas:
    """An RGB canvas backed by one bytearray; shapes clip to the edges."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * self.w + x0) * 3
            self.px[o:o + len(row)] = row

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.px[o:o + 3] = bytes(color)

    def hline(self, x0, x1, y, color):
        if x1 > x0:
            self.fill_rect(x0, y, x1 - x0, 1, color)

    def vline(self, x, y0, y1, color):
        if y1 > y0:
            self.fill_rect(x, y0, 1, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line, 1px wide."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, color, t=3):
        """A line drawn t px thick (square brush along the path)."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = t // 2
        while True:
            self.fill_rect(x0 - half, y0 - half, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            yy = cy + dy
            if yy < 0 or yy >= self.h:
                continue
            half = math.isqrt(r * r - dy * dy)
            self.fill_rect(cx - half, yy, 2 * half + 1, 1, color)

    def ring(self, cx, cy, r, color, t=3):
        for a in range(0, 360):
            rad = math.radians(a)
            for rr in range(r - t, r):
                x = cx + int(rr * math.cos(rad))
                y = cy + int(rr * math.sin(rad))
                self.set_px(x, y, color)

    def ellipse_outline(self, cx, cy, rx, ry, color):
        for a in range(0, 360):
            rad = math.radians(a)
            self.set_px(cx + int(rx * math.cos(rad)),
                        cy + int(ry * math.sin(rad)), color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via horizontal scanlines."""
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                xa = bx
            t2 = (y - ay) / max(1, cy - ay)
            xb = ax + (cx - ax) * t2
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(int(xa), y, int(xb) - int(xa) + 1, 1, color)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, s, x, y, scale, color):
    """Left-aligned text; unknown chars render as space."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for r, line in enumerate(glyph):
            for c, bit in enumerate(line):
                if bit == '#':
                    cv.fill_rect(cx + c * scale, y + r * scale,
                                 scale, scale, color)
        cx += 6 * scale


def draw_text_centered(cv, s, cx, y, scale, color):
    draw_text(cv, s, cx - text_width(s, scale) // 2, y, scale, color)


def png_bytes(rgb, w, h):
    raw = b''.join(b'\x00' + bytes(rgb[y * w * 3:(y + 1) * w * 3])
                   for y in range(h))

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data +
                struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


# ------------------------------------------------------------------ icons
def icon_globe(cv, x, y, s):
    """Story 1: the world at the table."""
    cx, cy = x + s // 2, y + s // 2
    cv.disc(cx, cy, 38, SKY)
    cv.ring(cx, cy, 38, NAVY, 3)
    cv.ellipse_outline(cx, cy, 38, 14, NAVY)
    cv.ellipse_outline(cx, cy, 14, 38, NAVY)
    cv.vline(cx, cy - 38, cy + 38, NAVY)
    cv.disc(cx - 16, cy - 14, 8, GREEN)
    cv.disc(cx + 18, cy + 12, 9, GREEN)
    cv.disc(cx + 14, cy - 18, 5, GREEN)


def icon_chip(cv, x, y, s):
    """Story 2: a processor chip."""
    cx, cy = x + s // 2, y + s // 2
    for i in range(4):
        off = -27 + i * 18
        cv.fill_rect(cx + off - 2, cy - 46, 4, 12, DARKGREY)
        cv.fill_rect(cx + off - 2, cy + 34, 4, 12, DARKGREY)
        cv.fill_rect(cx - 46, cy + off - 2, 12, 4, DARKGREY)
        cv.fill_rect(cx + 34, cy + off - 2, 12, 4, DARKGREY)
    cv.fill_rect(cx - 34, cy - 34, 68, 68, NAVY_DARK)
    cv.fill_rect(cx - 22, cy - 22, 44, 44, STEEL)
    cv.fill_rect(cx - 12, cy - 12, 24, 24, CREAM)


def icon_envelope(cv, x, y, s):
    """Story 3: mail down - an envelope crossed out."""
    cx, cy = x + s // 2, y + s // 2
    cv.fill_rect(cx - 38, cy - 24, 76, 52, WHITE)
    for dx in range(-38, 39):
        cv.fill_rect(cx + dx, cy - 24, 1, 1, NAVY)
    cv.fill_rect(cx - 38, cy - 24, 76, 3, NAVY)
    cv.fill_rect(cx - 38, cy + 25, 76, 3, NAVY)
    cv.fill_rect(cx - 38, cy - 24, 3, 52, NAVY)
    cv.fill_rect(cx + 35, cy - 24, 3, 52, NAVY)
    cv.line(cx - 35, cy - 21, cx, cy + 8, NAVY)
    cv.line(cx + 35, cy - 21, cx, cy + 8, NAVY)
    cv.thick_line(cx - 30, cy - 30, cx + 30, cy + 30, RED, 6)
    cv.thick_line(cx + 30, cy - 30, cx - 30, cy + 30, RED, 6)


def icon_tanker(cv, x, y, s):
    """Story 4: a tanker on the strait, blast above."""
    cx, cy = x + s // 2, y + s // 2
    cv.disc(cx + 22, cy - 34, 5, (232, 120, 30))
    cv.disc(cx + 14, cy - 40, 4, (232, 120, 30))
    cv.disc(cx + 30, cy - 40, 4, (232, 120, 30))
    cv.disc(cx + 22, cy - 46, 4, (240, 170, 40))
    cv.fill_rect(cx - 34, cy - 8, 68, 10, TEAL)
    cv.fill_rect(cx - 40, cy + 2, 80, 16, NAVY_DARK)
    cv.fill_rect(cx - 40, cy + 18, 80, 4, NAVY_DARK)
    cv.fill_rect(cx - 8, cy - 26, 14, 18, NAVY_DARK)
    cv.fill_rect(cx + 12, cy - 20, 8, 12, NAVY_DARK)
    for i, wx in enumerate((-38, -14, 10, 32)):
        cv.fill_rect(cx + wx, cy + 30 + (i % 2) * 6, 22, 3, SKY)


def icon_building(cv, x, y, s):
    """Story 5: a cracked building over rubble."""
    cx, cy = x + s // 2, y + s // 2
    cv.fill_rect(cx - 30, cy - 40, 60, 78, SLATE)
    cv.fill_rect(cx - 30, cy - 40, 60, 5, NAVY_DARK)
    for r in range(3):
        for c in range(3):
            cv.fill_rect(cx - 22 + c * 18, cy - 28 + r * 20, 10, 12, CREAM)
    cv.thick_line(cx + 2, cy - 40, cx - 8, cy - 14, RED, 3)
    cv.thick_line(cx - 8, cy - 14, cx + 6, cy + 10, RED, 3)
    cv.thick_line(cx + 6, cy + 10, cx - 4, cy + 38, RED, 3)
    cv.triangle(cx - 38, cy + 38, cx - 18, cy + 38, cx - 28, cy + 24, DARKGREY)
    cv.triangle(cx - 12, cy + 38, cx + 10, cy + 38, cx - 2, cy + 26, DARKGREY)
    cv.triangle(cx + 14, cy + 38, cx + 38, cy + 38, cx + 26, cy + 25, DARKGREY)


def icon_coin(cv, x, y, s):
    """Story 6: a seized gold coin."""
    cx, cy = x + s // 2, y + s // 2
    cv.disc(cx, cy, 38, COIN)
    cv.ring(cx, cy, 38, AMBER, 3)
    cv.ring(cx, cy, 30, AMBER, 2)
    draw_text_centered(cv, "$", cx, cy - 14, 4, NAVY_DARK)
    cv.fill_rect(cx - 30, cy + 22, 60, 4, NAVY_DARK)
    cv.fill_rect(cx - 24, cy + 28, 48, 3, NAVY_DARK)


ICONS = (icon_globe, icon_chip, icon_envelope,
         icon_tanker, icon_building, icon_coin)

STORIES = (
    # (accent, kicker, headline lines, body lines)
    (STEEL, "EUROPE - DIPLOMACY",
     ("EUROPE JOINS", "UKRAINE TALKS"),
     ("RUSSIA AGREES EUROPEANS SIT AT THE",
      "NEXT ROUND OF PEACE TALKS. WORK",
      "BEGINS ON THE WAR'S LARGEST SWAP.")),
    (GREEN, "TECH - MARKETS",
     ("NVIDIA CEO", "HUANG RESIGNS"),
     ("JENSEN HUANG STEPS DOWN AS CHIEF",
      "EXECUTIVE. SHARES FALL 16% AS CFO",
      "COLETTE KRESS BECOMES INTERIM CEO.")),
    (RED, "TECH - OUTAGE",
     ("MICROSOFT 365", "GOES DARK"),
     ("OUTLOOK AND TEAMS FAIL AROUND THE",
      "WORLD AS MICROSOFT SERVICES DROP",
      "OFFLINE FOR BUSINESSES EVERYWHERE.")),
    (TEAL, "MIDDLE EAST",
     ("TANKERS HIT IN", "STRAIT OF HORMUZ"),
     ("FOUR OIL TANKERS STRUCK BY BLASTS",
      "IN THE STRAIT. IRAN SAYS IT HIT A",
      "US RADAR IN BAHRAIN; UNVERIFIED.")),
    (SLATE, "USA - NEW YORK",
     ("BROOKLYN BUILDING", "COLLAPSE: 8 DEAD"),
     ("SEARCH ENDS AT THE FALLEN FLATBUSH",
      "BUILDING. EIGHT DEAD, INCL. TWO",
      "CHILDREN. 18 HURT. 100 SITES CHECKED.")),
    (AMBER, "CRYPTO - CRIME",
     ("DOJ TO SEIZE", "$1.2B IN CRYPTO"),
     ("COURT BACKS SEIZURE OF $1.2 BILLION",
      "STOLEN FROM BINANCE IN THE OCT 29",
      "HACK THE FBI BLAMES ON NORTH KOREA.")),
)


def draw_panel(cv, px, py, idx, story):
    accent, kicker, headline, body = story
    pw, ph = 472, 258
    cv.fill_rect(px, py, pw, ph, PAPER)
    cv.fill_rect(px, py, pw, 10, accent)
    cv.fill_rect(px, py, pw, 2, NAVY)
    cv.fill_rect(px, py + ph - 2, pw, 2, NAVY)
    cv.fill_rect(px, py, 2, ph, NAVY)
    cv.fill_rect(px + pw - 2, py, 2, ph, NAVY)
    # icon box
    cv.fill_rect(px + 16, py + 24, 96, 96, CREAM)
    cv.fill_rect(px + 16, py + 24, 96, 2, accent)
    cv.fill_rect(px + 16, py + 118, 96, 2, accent)
    cv.fill_rect(px + 16, py + 24, 2, 96, accent)
    cv.fill_rect(px + 110, py + 24, 2, 96, accent)
    ICONS[idx](cv, px + 16, py + 24, 96)
    # kicker + headline
    draw_text(cv, kicker, px + 128, py + 28, 2, MUTED)
    y = py + 54
    for line in headline:
        draw_text(cv, line, px + 128, y, 3, NAVY)
        y += 27
    cv.fill_rect(px + 128, py + 116, 312, 2, GOLD)
    # body
    y = py + 140
    for line in body:
        draw_text(cv, line, px + 16, y, 2, INK)
        y += 24


def main():
    cv = Canvas(W, H)
    cv.fill_rect(0, 0, W, H, CREAM)

    # --- masthead ---------------------------------------------------------
    cv.fill_rect(0, 0, W, 150, NAVY)
    draw_text_centered(cv, "FRIDAY, 13 NOVEMBER 2026", 512, 18, 3, GOLD)
    draw_text_centered(cv, "THE WORLD IN ONE DAY", 512, 52, 7, WHITE)
    draw_text_centered(cv, "SIX STORIES THAT DEFINED THE DAY",
                        512, 116, 2, (200, 210, 225))
    cv.fill_rect(0, 150, W, 6, GOLD)

    # --- six panels, 2 columns x 3 rows ----------------------------------
    for i, story in enumerate(STORIES):
        px = 32 + (i % 2) * 488
        py = 170 + (i // 2) * 270
        draw_panel(cv, px, py, i, story)

    # --- footer -----------------------------------------------------------
    draw_text_centered(
        cv, "ALL EVENTS HAPPENED OR WERE FIRST REPORTED ON FRIDAY 13 NOVEMBER 2026",
        512, 982, 2, MUTED)

    data = png_bytes(cv.px, W, H)
    # In the grader /output exists; outside it, MAKEFUN_OUTPUT_DIR
    # stands in for /output (the kit starter's convention).
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    out = os.path.join(outdir, 'entry.png') if os.path.isdir(outdir) else 'entry.png'
    with open(out, 'wb') as f:
        f.write(data)
    print(f"wrote {out}: {len(data)} bytes")


if __name__ == '__main__':
    main()
