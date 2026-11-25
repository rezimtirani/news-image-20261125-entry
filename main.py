"""The World in One Day - 25 November 2026.

Draws a one-page newspaper front page that sums up 25 November 2026
in a single 1024x1024 PNG image. Standard library only: the picture
is painted pixel by pixel onto a canvas, the letters come from a small
bitmap font defined below, and the PNG bytes are encoded by hand with
zlib. No network, no third-party libraries, fully deterministic.

The program writes exactly one file: $MAKEFUN_OUTPUT_DIR/entry.png.
"""

import binascii
import hashlib
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024
PAPER = (246, 241, 227)
INK = (22, 21, 19)
RED = (158, 27, 27)
BLUE = (31, 58, 95)
GREY = (107, 101, 90)

# A 5x7 bitmap font. Each glyph is seven rows of five cells; "1" is ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

# The day's news, researched on 25 November 2026.
LEAD_KICKER = "CYBERATTACK - WASHINGTON"
LEAD_HEADLINE = "US SPY AGENCIES HIT BY CYBER BREACH"
LEAD_BODY = (
    "Sources say unclassified systems at the CIA and the Office of the "
    "Director of National Intelligence were breached - the latest in a "
    "run of cyber incidents hitting Washington."
)

COLUMNS = [
    (
        "US COURT - TECH",
        "HUAWEI GUILTY OF STEALING TRADE SECRETS",
        "A New York jury convicts the Chinese telecoms giant on 10 of "
        "12 counts, including bank fraud and conspiracy to steal trade "
        "secrets, after a three-month trial.",
    ),
    (
        "WAR AT SEA",
        "ZELENSKYY CONFIRMS SHIP STRIKE",
        "Ukraine says it hit a Russian cargo ship in the Gulf of "
        "Finland, days after sinking a Russian warship off Libya.",
    ),
    (
        "MIDDLE EAST",
        "HOUTHIS HIT RIYADH'S TALLEST TOWER",
        "A drone strike on the capital's tallest tower wounds 11 "
        "people, Saudi civil defence says, as the Yemen war spills over.",
    ),
]

ALSO_TODAY = [
    "NATO TO SEND EARLY-WARNING AIRCRAFT TO POLAND AFTER MISSILE REPORTS",
    "WHO EVACUATES STAFF IN CONGO AS EBOLA AND FIGHTING SPREAD",
    "NVIDIA SHARES FALL 7% AS DELL LIFTS FORECASTS ON AI SERVER BOOM",
    "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS AHEAD OF THANKSGIVING",
]


class Sheet:
    """A plain RGB canvas with helpers for boxes, rules and bitmap text."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            at = (y * self.width + x) * 3
            self.pixels[at:at + 3] = bytes(color)

    def fill(self, x, y, w, h, color):
        for row in range(y, y + h):
            for col in range(x, x + w):
                self.put(col, row, color)

    def rule(self, x, y, w, color, thick=2):
        self.fill(x, y, w, thick, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale

    def draw_text(self, x, y, text, scale, color):
        cursor = x
        for char in text.upper():
            glyph = FONT.get(char, FONT[" "])
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == "1":
                        self.fill(
                            cursor + gx * scale, y + gy * scale,
                            scale, scale, color,
                        )
            cursor += 6 * scale
        return cursor

    def draw_centered(self, y, text, scale, color, width=None):
        span = self.text_width(text, scale)
        room = width if width is not None else self.width
        return self.draw_text((room - span) // 2, y, text, scale, color)

    def wrap(self, text, scale, max_width):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        lines = []
        current = ""
        for word in text.split(" "):
            trial = word if not current else current + " " + word
            if self.text_width(trial, scale) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines


def draw_masthead(sheet):
    sheet.draw_centered(36, "THE WORLD IN ONE DAY", 6, INK)
    sheet.rule(36, 92, 952, INK, 3)
    sheet.rule(36, 99, 952, INK, 1)
    sheet.draw_centered(112, "WEDNESDAY, 25 NOVEMBER 2026", 2, RED)
    sheet.draw_centered(136, "ONE IMAGE - THE WHOLE DAY'S NEWS", 2, GREY)
    sheet.rule(36, 162, 952, INK, 2)


def draw_lead(sheet):
    sheet.draw_text(36, 182, LEAD_KICKER, 2, RED)
    lines = sheet.wrap(LEAD_HEADLINE, 6, 952)
    y = 210
    for line in lines:
        sheet.draw_text(36, y, line, 6, INK)
        y += 48
    body = sheet.wrap(LEAD_BODY, 2, 952)
    y = 318
    for line in body:
        sheet.draw_text(36, y, line, 2, INK)
        y += 24
    sheet.draw_text(36, 408, "SOURCES: REUTERS / CNN - 25 NOVEMBER 2026", 2, GREY)


def draw_columns(sheet):
    tops = [36, 361, 686]
    for col_x, (kicker, headline, body) in zip(tops, COLUMNS):
        sheet.draw_text(col_x, 492, kicker, 2, RED)
        lines = sheet.wrap(headline, 3, 301)
        y = 522
        for line in lines:
            sheet.draw_text(col_x, y, line, 3, INK)
            y += 26
        body_lines = sheet.wrap(body, 2, 301)
        y += 6
        for line in body_lines:
            sheet.draw_text(col_x, y, line, 2, INK)
            y += 22


def draw_also_today(sheet):
    sheet.rule(36, 812, 952, INK, 2)
    sheet.draw_text(36, 828, "ALSO TODAY", 3, BLUE)
    y = 866
    for item in ALSO_TODAY:
        sheet.draw_text(36, y, "*", 2, RED)
        sheet.draw_text(60, y, item, 2, INK)
        y += 24


def draw_footer(sheet):
    sheet.rule(36, 962, 952, INK, 1)
    sheet.draw_text(
        36, 972,
        "SOURCES: REUTERS, AP, CNN, BBC - 25 NOV 2026", 2, GREY,
    )
    sheet.draw_text(
        36, 994,
        "25 NOV: INTL DAY FOR THE ELIMINATION OF VIOLENCE AGAINST WOMEN",
        2, GREY,
    )


def compose():
    sheet = Sheet(WIDTH, HEIGHT, PAPER)
    draw_masthead(sheet)
    draw_lead(sheet)
    draw_columns(sheet)
    draw_also_today(sheet)
    draw_footer(sheet)
    return sheet.pixels


def png_chunk(kind, payload):
    block = kind + payload
    return struct.pack(">I", len(payload)) + block + struct.pack(
        ">I", binascii.crc32(block) & 0xFFFFFFFF
    )


def encode_png(pixels):
    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = WIDTH * 3
    for row in range(HEIGHT):
        raw.append(0)
        raw += pixels[row * stride:(row + 1) * stride]
    blob = b"".join([
        b"\x89PNG\r\n\x1a\n",
        png_chunk(b"IHDR", header),
        png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
        png_chunk(b"IEND", b""),
    ])
    return blob


def verify_png_bytes(data):
    """Check the encoded PNG against the competition gate before saving.

    Returns the byte size. Raises ValueError when the magic is wrong,
    the IEND trailer is missing, the dimensions are not 1024x1024,
    or the file is over the 1 MiB limit.
    """
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("PNG magic missing")
    if not data.endswith(b"IEND" + struct.pack(">I", 0xAE426082)):
        raise ValueError("PNG IEND missing")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError("PNG is %dx%d, expected 1024x1024" % (width, height))
    if len(data) > 1024 * 1024:
        raise ValueError("PNG is %d bytes, over the 1 MiB limit" % len(data))
    return len(data)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(compose())
    size = verify_png_bytes(data)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (target, size, digest))


if __name__ == "__main__":
    sys.exit(main())
