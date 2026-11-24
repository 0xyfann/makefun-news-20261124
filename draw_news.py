#!/usr/bin/env python3
"""Deterministically draw the make.fun news-image-20261124 newspaper cover.

1024x1024 PNG, <= 1 MiB, standard library only. No network, no randomness,
no timestamps: every run emits byte-identical PNG data.

The typeface is a hand-built 5x7 bitmap font. Headlines use a bold,
doubled-strike rendering at scale 2; body text is scale 1.
"""

import struct
import zlib

W, H = 1024, 1024
OUT_PATH = "entry.png"

# ---------------------------------------------------------------- palette --
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
INK = (20, 20, 24)
PAPER = (248, 247, 242)
ACCENT = (138, 12, 12)      # dark newsprint red
GRAY = (110, 108, 102)


# ------------------------------------------------------------ 5x7 font --
# Each glyph: 7 rows of 5 bits (bit 4 = leftmost pixel).
def _g(r0, r1, r2, r3, r4, r5, r6):
    return (r0, r1, r2, r3, r4, r5, r6)

FONT = {
    "A": _g(0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": _g(0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": _g(0b11100, 0b10010, 0b10001, 0b10001, 0b10001, 0b10010, 0b11100),
    "E": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": _g(0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": _g(0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": _g(0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": _g(0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": _g(0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": _g(0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": _g(0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": _g(0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001),
    "O": _g(0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": _g(0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": _g(0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": _g(0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": _g(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": _g(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": _g(0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": _g(0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": _g(0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": _g(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "a": _g(0b00000, 0b00000, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111),
    "b": _g(0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110),
    "c": _g(0b00000, 0b00000, 0b01110, 0b10001, 0b10000, 0b10001, 0b01110),
    "d": _g(0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111),
    "e": _g(0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110),
    "f": _g(0b00110, 0b01000, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000),
    "g": _g(0b00000, 0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001),
    "h": _g(0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "i": _g(0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": _g(0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b00010, 0b10110),
    "k": _g(0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010),
    "l": _g(0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": _g(0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": _g(0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "o": _g(0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": _g(0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000),
    "q": _g(0b00000, 0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001),
    "r": _g(0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000),
    "s": _g(0b00000, 0b00000, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110),
    "t": _g(0b01000, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000, 0b00110),
    "u": _g(0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": _g(0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": _g(0b00000, 0b00000, 0b10001, 0b10001, 0b10101, 0b10101, 0b01010),
    "x": _g(0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": _g(0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": _g(0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111),
    "0": _g(0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": _g(0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": _g(0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111),
    "3": _g(0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": _g(0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": _g(0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": _g(0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": _g(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": _g(0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": _g(0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    "%": _g(0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    ".": _g(0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01110, 0b01110),
    ",": _g(0b00000, 0b00000, 0b00000, 0b00000, 0b00110, 0b00100, 0b01000),
    ":": _g(0b00000, 0b01110, 0b01110, 0b00000, 0b01110, 0b01110, 0b00000),
    ";": _g(0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    "'": _g(0b00010, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000),
    "-": _g(0b00000, 0b00000, 0b00000, 0b01110, 0b00000, 0b00000, 0b00000),
    "(": _g(0b00110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b00110),
    ")": _g(0b01100, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01100),
    "/": _g(0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "?": _g(0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b00000, 0b00100),
    "!": _g(0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
}

MISSING = set()


def text_width(s, scale):
    w = 0
    for ch in s:
        if ch == " ":
            w += 6 * scale
        else:
            if ch not in FONT:
                MISSING.add(ch)
            w += 6 * scale
    return w


def draw_text(img, s, x, y, scale=1, color=INK, bold=False):
    h = len(img)
    for ch in s:
        if ch == " ":
            x += 6 * scale
            continue
        pat = FONT[ch]
        for r in range(7):
            bits = pat[r]
            for c in range(5):
                if (bits >> (4 - c)) & 1:
                    px, py = x + c * scale, y + r * scale
                    for dx in (0, 1) if bold else (0,):
                        for dy in (0,):
                            if 0 <= py + dy < h and 0 <= px + dx < W:
                                row = img[py + dy]
                                o = (px + dx) * 3
                                row[o:o + 3] = color
        x += 6 * scale
    return x


def draw_center(img, s, y, scale=1, color=INK, bold=False):
    x = (W - text_width(s, scale)) // 2
    draw_text(img, s, x, y, scale=scale, color=color, bold=bold)


def fill_rect(img, x0, y0, x1, y1, color):
    rgb = bytes(color)
    for y in range(y0, y1):
        row = img[y]
        row[x0 * 3:(x1) * 3] = rgb * (x1 - x0)


# ------------------------------------------------------------- the cover --
def build():
    img = [bytearray(PAPER * W) for _ in range(H)]
    fill_rect(img, 0, 0, W, H, WHITE)      # outer border margin
    fill_rect(img, 4, 4, W - 4, H - 4, BLACK)  # front-page frame
    fill_rect(img, 10, 10, W - 10, H - 10, PAPER)  # safe drawing area

    # Masthead band.
    fill_rect(img, 10, 10, W - 10, 130, BLACK)
    draw_text(img, "THE GLOBAL HERALD", 34, 26, scale=4, color=WHITE)
    title_w = text_width("THE GLOBAL HERALD", 4)
    fill_rect(img, 34, 62, 34 + title_w, 65, ACCENT)  # masthead underline
    draw_text(img, "Tuesday, 24 November 2026", 34, 78, scale=3, color=WHITE)
    fill_rect(img, 10, 130, W - 10, 134, ACCENT)      # red rule

    stories = [
        ("LEAD - UKRAINE IN LIBYA",
         "UKRAINE'S NAVAL DRONES SINK RUSSIA'S NEWEST CORVETTE IN BENGHAZI",
         ["Seven sea drones and a Ka-27 helicopter destroyed with the Merkury corvette (2023) in the port;",
          "weapons freighter MV Angara also hit 2,400 km from the front. Zelenskyy: 'exemplary'."]),
        ("CLIMATE - COP31",
         "COP31 IN ANTALYA COLLAPSES WITHOUT A CLIMATE DEAL",
         ["Longest UN climate summit ever ends in failure - the first collapse since Copenhagen 2009;",
          "final draft deletes all 'fossil fuels' wording; EU refuses to sign; Guterres 'deeply disappointed'."]),
        ("GULF - IRAN",
         "IRGC SAYS PATRIOT RADAR BASES HIT IN BAHRAIN",
         ["'Ya Umm al-Banin' (Nov 21): Iran claims missiles and drones struck Al-Riffa and Awali in Bahrain;",
          "US denies losses; 2 hurt at Sitra; 2 tankers hit in Hormuz; IRGC says 20th US MQ-1 drone downed."]),
        ("INDONESIA",
         "CANDY FACTORY FIRE KILLS AT LEAST 24; DOZENS MISSING",
         ["At least 24 dead and dozens of workers still unaccounted for as rescuers search the burned plant."]),
        ("MARITIME",
         "RUSSIA'S SPARTA II STILL BLAZING IN GULF OF FINLAND",
         ["Cargo ship set alight by an apparent Ukrainian drone; the fire has not yet been extinguished."]),
        ("UKRAINE",
         "STRIKES HIT DYMIER IN KYIV REGION; 14 MISSING",
         ["Russian drones and missiles hit a building in Dymer; Zelenskyy says at least 14 people are missing."]),
        ("INTERNATIONAL LAW",
         "WORLD COURT FINDS MYANMAR COMMITTED GENOCIDE",
         ["ICJ rules Myanmar carried out genocide against the Muslim Rohingya minority."]),
        ("BUSINESS - NVIDIA",
         "HUANG RETURNS; NVIDIA SHARES JUMP 31% IN A DAY",
         ["CEO Jensen Huang back after an independent probe into a chip scandal amid China espionage claims."]),
        ("SPORT",
         "ALCARAZ WINS FIRST ATP FINALS TITLE IN TURIN",
         ["Alcaraz beats Zverev; India vs New Zealand draw in Wellington; chess worlds open in Geneva;",
          "defending champion D Gukesh starts against Javokhir Sindarov."]),
        ("GAZA - TECH",
         "GAZA AIR, SOIL, WATER UNSAFE FOR DECADES, SAYS OXFAM",
         ["Oxfam/CEOBS: strikes left heavy metals, explosive residue and asbestos that poison the Strip;",
          "Waymo pulls driverless taxis from all US roads without a safety driver."]),
    ]

    # Safe drawing area: x in [18, 1014], top wall 134, bottom wall H-10.
    SIDE, TOP = 24, 150
    RIGHT_LIM = 1000

    y = TOP
    for idx, (kicker, headline, leded) in enumerate(stories, 1):
        # Story index badge.
        fill_rect(img, SIDE, y + 1, SIDE + 30, y + 21, ACCENT)
        draw_text(img, "%02d" % idx, SIDE + 4, y + 6, scale=2, color=WHITE)
        draw_text(img, kicker, SIDE + 38, y + 7, scale=1, color=ACCENT)
        y += 28
        draw_text(img, headline, SIDE + 2, y, scale=2, color=BLACK, bold=True)
        y += 22
        for line in leded:
            draw_text(img, line, SIDE + 2, y, scale=1, color=INK)
            y += 12
        y += 8
        fill_rect(img, SIDE, y - 2, 988, y - 1, GRAY)  # faint rule between stories
        y += 4

    # Footer, pinned inside the frame.
    fy = min(y + 6, H - 30)
    fill_rect(img, SIDE, fy, 988, fy + 1, ACCENT)
    draw_center(img, "THE GLOBAL HERALD - VOL. CCLXXV - TUESDAY, 24 NOVEMBER 2026",
                fy + 12, color=BLACK)
    draw_center(img, "SUM UP 24 NOVEMBER'S WORLD NEWS IN ONE IMAGE - make.fun NEWS-IMAGE-20261124",
                fy + 24, scale=1, color=GRAY)

    if MISSING:
        raise ValueError("unsupported glyph: %r" % sorted(MISSING))
    return img


# ------------------------------------------------------------- png writer --
def png_bytes(width, height, rows):
    def chunk(tag, data):
        payload = tag + data
        return (struct.pack(">I", len(data)) + payload
                + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF))

    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter: none
        raw += row
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    img = build()
    with open(OUT_PATH, "wb") as f:
        f.write(png_bytes(W, H, img))
    import hashlib
    import os
    data = open(OUT_PATH, "rb").read()
    print("wrote %s  %d bytes  sha256=%s"
          % (OUT_PATH, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
