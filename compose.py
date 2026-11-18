#!/usr/bin/env python3
"""Compose the news-image-20261117 front page v3: hero-led editorial poster.

One image that sums up Tuesday 17 November 2026, re-hierarchised around the
day's most sensational story: masthead + date + story count, a BIG HERO
panel for the Kerch Bridge span falling (large flat-vector illustration
drawn programmatically, no photos), a numbered world map, five lead cards
for the other leads, an ALSO one-liner list, BY THE NUMBERS as a 2x2 card,
and a source line. Fully deterministic (identical bytes on every run), no
network, no photos: every drawing is made here from PIL primitives. All
facts were verified against real reporting before locking; disputed claims
are hedged. Same 24 verified stories as v2, same facts, same hedges.
"""
from PIL import Image, ImageDraw, ImageFont

OUT = "entry.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
# Noto Serif Display — a proper newspaper display face (condensed, high
# contrast). Headlines and masthead use it; body stays DejaVu Sans.
DISPB = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"
DISPBLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (11, 29, 51)
RED = (193, 39, 45)
GOLD = (180, 140, 40)
GREY = (90, 90, 86)
CARD = (255, 255, 255)
BORDER = (206, 200, 186)
OCEAN = (203, 224, 234)
LAND = (172, 184, 152)
GRAT = (190, 205, 212)
SLATE = (44, 68, 98)

MAP_X0, MAP_X1 = 16, 1008
MAP_Y0, MAP_Y1 = 360, 440
LON0, LON1 = -170.0, 190.0
LAT0, LAT1 = 72.0, -50.0

# Hero panel geometry
HERO_Y0, HERO_Y1 = 100, 336
HERO_ILL_X0, HERO_ILL_Y0 = 508, 108
HERO_ILL_W, HERO_ILL_H = 484, 220

# Lead cards (stories 2-6): 2 columns x 3 rows; the 6th slot holds
# BY THE NUMBERS as a 2x2 card.
CARDS_Y0 = 448
CARD_W, CARD_H, CARD_GAP = 492, 116, 6

ALSO_Y = 816


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def project(lon, lat):
    x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_Y1 - MAP_Y0)
    return (x, y)


# Simplified continent outlines (lon, lat). Schematic, not survey-grade.
CONTINENTS = [
    ("N. AMERICA", (-100, 52), [
        (-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73),
        (-105, 70), (-95, 80), (-85, 80), (-78, 73), (-70, 62),
        (-60, 55), (-55, 47), (-60, 44), (-68, 42), (-74, 38),
        (-76, 34), (-80, 27), (-84, 24), (-87, 16), (-92, 15),
        (-95, 18), (-100, 20), (-105, 22), (-112, 28), (-118, 33),
        (-124, 42), (-125, 49), (-132, 56), (-145, 60), (-155, 58),
        (-162, 60), (-168, 66)]),
    ("GREENLAND", (-42, 74), [
        (-55, 60), (-45, 60), (-38, 64), (-30, 68), (-22, 70),
        (-25, 76), (-35, 80), (-48, 79), (-58, 75), (-60, 70)]),
    ("S. AMERICA", (-60, -14), [
        (-80, 10), (-76, 6), (-72, 2), (-70, -2), (-76, -6),
        (-80, -10), (-77, -16), (-72, -20), (-70, -26), (-66, -32),
        (-62, -38), (-58, -44), (-56, -50), (-64, -54), (-68, -52),
        (-70, -46), (-72, -38), (-74, -30), (-76, -22), (-79, -14),
        (-81, -6), (-80, 2), (-80, 10)]),
    ("EUROPE", (0, 62), [
        (-10, 36), (-8, 43), (-2, 47), (0, 50), (4, 53),
        (8, 55), (12, 57), (18, 58), (22, 60), (26, 64),
        (30, 70), (36, 68), (40, 64), (42, 58), (38, 54),
        (32, 50), (28, 46), (24, 44), (20, 42), (16, 40),
        (12, 38), (8, 37), (4, 36), (0, 38), (-5, 36), (-10, 36)]),
    ("AFRICA", (10, 8), [
        (-17, 15), (-12, 28), (-6, 34), (2, 37), (10, 37),
        (18, 33), (26, 32), (32, 31), (36, 28), (40, 18),
        (44, 12), (51, 11), (50, 4), (46, -2), (40, -8),
        (38, -14), (34, -22), (30, -28), (24, -34), (19, -34),
        (16, -28), (13, -18), (11, -8), (9, 2), (6, 5),
        (0, 6), (-6, 5), (-12, 8), (-16, 11), (-17, 15)]),
    ("ASIA", (98, 52), [
        (42, 68), (52, 70), (62, 70), (72, 72), (82, 73),
        (95, 76), (108, 76), (122, 73), (135, 72), (148, 71),
        (160, 69), (172, 66), (178, 65), (170, 60), (162, 56),
        (156, 51), (146, 46), (142, 40), (135, 36), (129, 33),
        (126, 38), (122, 31), (118, 24), (112, 18), (108, 10),
        (104, 8), (100, 12), (96, 16), (92, 21), (88, 22),
        (84, 19), (80, 12), (77, 8), (74, 14), (72, 20),
        (68, 23), (64, 25), (60, 25), (56, 26), (52, 28),
        (50, 30), (47, 30), (44, 34), (42, 38), (40, 42),
        (38, 48), (38, 56), (40, 62), (42, 68)]),
    ("OCEANIA", (134, -25), [
        (113, -22), (114, -28), (118, -33), (124, -33), (130, -32),
        (136, -35), (142, -38), (148, -38), (152, -32), (153, -27),
        (150, -22), (146, -19), (142, -11), (138, -13), (134, -12),
        (130, -13), (126, -14), (122, -16), (118, -20), (113, -22)]),
    ("", (121, 14), [  # Philippines sliver, so pin 2 has land to sit on
        (119.5, 18.5), (121.5, 18.5), (122.5, 16.0), (122.0, 12.0),
        (121.0, 9.0), (119.8, 12.0), (119.5, 16.0)]),
]

# (number, lon, lat, display offset px or None)
# Pin 6 (Eritrea) is nudged with a leader line: at r=11 its true spot sits
# ~21px below pin 1 (Kerch), so the two circles overlap; the offset puts it
# clear of pins 1, 3 and 5.
PINS = [
    (1, 37.5, 45.3, None),    # Kerch Bridge
    (2, 121.0, 14.6, None),   # Manila
    (3, 56.5, 26.5, None),    # Strait of Hormuz
    (4, -74.0, 40.7, None),   # New York / JPMorgan
    (5, 30.0, -2.0, None),    # Rwanda
    (6, 39.0, 15.3, (24, 16)),  # Eritrea, offset with leader
]

# (region, headline, summary, icon, tile colour)
# Lead 1 (Kerch) is the HERO panel, not a card; cards below are leads 2-6.
LEADS = [
    ("EUROPE", "KERCH BRIDGE ROAD SPAN FALLS",
     "Drones and missiles drop the road arch in a seven-stage operation; rail still stands.",
     "bridge", (46, 90, 136)),
    ("ASIA", "TRUMP LANDS IN MANILA",
     "Quad summit and Thailand deal at ASEAN; then Shenzhen to meet Xi and Putin.",
     "flags", (31, 107, 74)),
    ("M. EAST", "THIRD U.S. CARRIER IN THE GULF",
     "Theodore Roosevelt joins two carriers in the Gulf; Iran says six tankers hit by mines.",
     "carrier", (22, 50, 79)),
    ("AMERICAS", "JPMORGAN BUG HALTS BANKING",
     "A bug slows payments at Chase and other U.S. banks and delays Zelle. Not a cyberattack.",
     "bank", (122, 92, 46)),
    ("EUROPE", "FIVE EU STATES PLAN RWANDA RETURN HUB",
     "The five states open talks with Kigali; first transfers planned for 2027.",
     "globe", (44, 68, 98)),
    ("AFRICA", "WHO: ERITREA BEATS TRACHOMA",
     "Eritrea becomes the 34th country to eliminate trachoma as a public health problem.",
     "eye", (46, 125, 107)),
]

# (tag, one-liner) — two columns of nine
ALSO_A = [
    ("SPACE", "Vulcan rocket fails; 40 Amazon satellites lost"),
    ("TECH", "Nvidia beats: revenue $115.8B, up 103%"),
    ("EUROPE", "Russia says it downed 1,336 drones in a night"),
    ("ASIA", "Japan scrambles jets as Russian planes enter airspace"),
    ("M. EAST", "Houthis advance toward Aden; Saudi swaps commander"),
    ("TECH", "U.S. curbs China's remote access to AI chips"),
    ("AFRICA", "Ebola in DR Congo passes 11,000 cases; 5,400 dead"),
    ("AFRICA", "17 killed in two mass shootings in South Africa"),
    ("EUROPE", "Russia hits two bridges in Kyiv"),
]
ALSO_B = [
    ("EUROPE", "UN rights chief warns over EU-Rwanda transfer plan"),
    ("M. EAST", "Nearly 4m Syrians have returned since Assad fell"),
    ("M. EAST", "Oman and Iran hold talks on Hormuz security"),
    ("S. AMERICA", "Uncontacted Aw\u00e1 seek help as loggers close in"),
    ("ASIA", "Bus plunges 100m into a gorge in India; 8 killed"),
    ("CLIMATE", "Indigenous leaders warn of 'sacrifice zones' at COP31"),
    ("ASIA", "Mongolia's president to resign over graft claims"),
    ("EUROPE", "Sweden rejects a central facial-biometrics register"),
    ("M. EAST", "Israel, UAE discuss resuming flydubai to Tel Aviv"),
]

# (big number, label) — labels must fit one line at 11pt in 238px
NUMBERS = [
    ("1,336", "drones Russia says it downed"),
    ("$115.8B", "Nvidia quarterly revenue, up 103%"),
    ("40", "Amazon satellites lost"),
    ("11,000+", "Ebola cases in DR Congo"),
]


def draw_bridge(d, x0, y0, s):
    """Suspension bridge: deck, two towers, cables."""
    w = (255, 255, 255)
    d.line([x0 + 4, y0 + s - 16, x0 + s - 4, y0 + s - 16], fill=w, width=3)
    for tx in (x0 + 14, x0 + s - 18):
        d.line([tx, y0 + 8, tx, y0 + s - 16], fill=w, width=3)
    d.line([x0 + 14, y0 + 8, x0 + s // 2, y0 + s - 22], fill=w, width=2)
    d.line([x0 + s - 18, y0 + 8, x0 + s // 2, y0 + s - 22], fill=w, width=2)
    d.line([x0 + 4, y0 + s - 10, x0 + s - 4, y0 + s - 10], fill=w, width=2)


def draw_flags(d, x0, y0, s):
    """Three flag poles with pennants."""
    cols = [(193, 39, 45), (255, 255, 255), (201, 162, 39)]
    for i, c in enumerate(cols):
        px = x0 + 12 + i * 18
        d.line([px, y0 + 10, px, y0 + s - 10], fill=(255, 255, 255), width=3)
        d.polygon([(px, y0 + 10), (px + 15, y0 + 15), (px, y0 + 20)], fill=c)
    d.line([x0 + 6, y0 + s - 8, x0 + s - 6, y0 + s - 8], fill=(255, 255, 255), width=3)


def draw_carrier(d, x0, y0, s):
    """Aircraft carrier silhouette + waves."""
    w = (255, 255, 255)
    d.polygon([(x0 + 6, y0 + s - 26), (x0 + s - 6, y0 + s - 26),
               (x0 + s - 14, y0 + s - 18), (x0 + 12, y0 + s - 18)], fill=w)
    d.rectangle([x0 + s - 26, y0 + s - 38, x0 + s - 18, y0 + s - 26], fill=w)
    d.line([x0 + 10, y0 + s - 14, x0 + s - 10, y0 + s - 14], fill=w, width=2)
    for wy in (y0 + s - 8, y0 + s - 4):
        d.arc([x0 + 8, wy - 4, x0 + s - 8, wy + 4], 0, 180, fill=w, width=2)


def draw_bank(d, x0, y0, s):
    """Classical bank: pediment, columns, steps."""
    w = (255, 255, 255)
    d.polygon([(x0 + s // 2, y0 + 8), (x0 + 8, y0 + 22), (x0 + s - 8, y0 + 22)], fill=w)
    for cx in (x0 + 14, x0 + s // 2 - 2, x0 + s - 18):
        d.rectangle([cx, y0 + 26, cx + 4, y0 + s - 18], fill=w)
    d.line([x0 + 6, y0 + s - 16, x0 + s - 6, y0 + s - 16], fill=w, width=3)
    d.line([x0 + 6, y0 + s - 10, x0 + s - 6, y0 + s - 10], fill=w, width=3)


def draw_globe(d, x0, y0, s):
    """Globe with a curved return arrow."""
    w = (255, 255, 255)
    cx, cy, r = x0 + s // 2 - 4, y0 + s // 2, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=w, width=3)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=w, width=2)
    d.line([cx, cy - r, cx, cy + r], fill=w, width=2)
    d.ellipse([cx - 8, cy - r, cx + 8, cy + r], outline=w, width=2)
    d.arc([x0 + s - 26, y0 + 6, x0 + s - 4, y0 + 28], 300, 60, fill=(255, 210, 63), width=3)
    d.polygon([(x0 + s - 8, y0 + 4), (x0 + s - 2, y0 + 12), (x0 + s - 12, y0 + 10)],
              fill=(255, 210, 63))


def draw_eye(d, x0, y0, s):
    """Eye: almond outline, iris, pupil."""
    w = (255, 255, 255)
    d.arc([x0 + 6, y0 + 16, x0 + s - 6, y0 + s - 16], 200, 340, fill=w, width=3)
    d.arc([x0 + 6, y0 + 16, x0 + s - 6, y0 + s - 16], 20, 160, fill=w, width=3)
    cx, cy = x0 + s // 2, y0 + s // 2
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=w)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(26, 26, 26))
    d.ellipse([cx + 2, cy - 8, cx + 6, cy - 4], fill=(255, 255, 255))


ICONS = {"bridge": draw_bridge, "flags": draw_flags, "carrier": draw_carrier,
         "bank": draw_bank, "globe": draw_globe, "eye": draw_eye}


def draw_hero_illustration(d, x0, y0, w, h):
    """Kerch Bridge span collapsing at dusk — flat vector, PIL only.

    Local coords (0,0) = top-left of the illustration box. Dusk sky
    (navy -> orange -> gold horizon), dark sea, the bridge deck broken
    in the middle with one span falling into the water, smoke rising
    from the break, an explosion flash, splash and debris. 100%
    original procedural drawing; no photo, no copied image.
    """
    deck = (235, 235, 228)
    # --- sky bands ---
    d.rectangle([x0, y0, x0 + w, y0 + 70], fill=(11, 29, 51))
    d.rectangle([x0, y0 + 70, x0 + w, y0 + 96], fill=(206, 110, 48))
    d.rectangle([x0, y0 + 96, x0 + w, y0 + 112], fill=(232, 176, 96))
    # --- sea ---
    d.rectangle([x0, y0 + 112, x0 + w, y0 + h], fill=(18, 48, 74))
    # --- stars (deterministic positions) ---
    for sx, sy in [(40, 18), (90, 30), (150, 14), (210, 26), (300, 16),
                   (360, 28), (430, 20), (250, 42), (120, 48), (330, 52)]:
        d.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2],
                  fill=(255, 255, 255))
    # --- waves ---
    for wx, wy in [(20, 135), (120, 140), (300, 132), (380, 145),
                   (60, 165), (200, 170), (340, 162), (420, 168),
                   (100, 200), (260, 198), (400, 202)]:
        d.arc([x0 + wx, y0 + wy - 6, x0 + wx + 60, y0 + wy + 6],
              200, 340, fill=(210, 225, 235), width=2)
    # --- bridge towers ---
    for tx in (70, 400):
        d.rectangle([x0 + tx - 3, y0 + 34, x0 + tx + 3, y0 + 118], fill=deck)
        d.rectangle([x0 + tx - 9, y0 + 48, x0 + tx + 9, y0 + 54], fill=deck)
    # --- cables ---
    for (cx0, cy0, cx1, cy1) in [
            (70, 34, 20, 114), (70, 34, 120, 114), (70, 34, 165, 114),
            (400, 34, 325, 114), (400, 34, 420, 114), (400, 34, 470, 114)]:
        d.line([x0 + cx0, y0 + cy0, x0 + cx1, y0 + cy1],
               fill=(220, 220, 214), width=2)
    # --- deck: left and right segments, gap in the middle ---
    d.rectangle([x0, y0 + 113, x0 + 170, y0 + 121], fill=deck)
    d.rectangle([x0 + 320, y0 + 113, x0 + w, y0 + 121], fill=deck)
    # --- collapsed span falling into the sea ---
    d.line([x0 + 175, y0 + 116, x0 + 255, y0 + 182], fill=deck, width=9)
    d.line([x0 + 255, y0 + 182, x0 + 275, y0 + 196], fill=deck, width=6)
    # --- splash where the span hits the water ---
    d.arc([x0 + 240, y0 + 170, x0 + 284, y0 + 202], 200, 340,
          fill=(255, 255, 255), width=2)
    d.arc([x0 + 248, y0 + 178, x0 + 276, y0 + 200], 200, 340,
          fill=(255, 255, 255), width=2)
    for dx, dy in [(235, 175), (290, 180), (250, 168), (296, 192)]:
        d.ellipse([x0 + dx - 2, y0 + dy - 2, x0 + dx + 2, y0 + dy + 2],
                  fill=(255, 255, 255))
    # --- debris on the water ---
    for dx, dy, dw in [(228, 170, 12), (290, 196, 10), (300, 190, 8)]:
        d.rectangle([x0 + dx, y0 + dy, x0 + dx + dw, y0 + dy + 3],
                    fill=(200, 200, 196))
    # --- smoke rising from the break ---
    for (sx0, sy0, sx1, sy1, c) in [
            (193, 66, 227, 100, (88, 88, 86)),
            (213, 46, 257, 90, (140, 140, 136)),
            (238, 62, 270, 94, (88, 88, 86)),
            (258, 78, 284, 104, (150, 150, 146)),
            (188, 86, 216, 112, (88, 88, 86))]:
        d.ellipse([x0 + sx0, y0 + sy0, x0 + sx1, y0 + sy1], fill=c)
    # --- explosion flash at the break point ---
    d.ellipse([x0 + 165, y0 + 99, x0 + 191, y0 + 125], fill=(232, 140, 40))
    d.ellipse([x0 + 171, y0 + 105, x0 + 185, y0 + 119], fill=(255, 210, 63))
    for (rx0, ry0, rx1, ry1) in [(178, 90, 178, 98), (178, 126, 178, 134),
                                 (156, 112, 164, 112), (192, 112, 200, 112)]:
        d.line([x0 + rx0, y0 + ry0, x0 + rx1, y0 + ry1],
               fill=(255, 210, 63), width=2)
    # --- pin badge 1, tying the hero to map pin 1 ---
    d.ellipse([x0 + 14, y0 + 14, x0 + 42, y0 + 42], fill=RED,
              outline=(255, 255, 255), width=2)
    d.text((x0 + 28, y0 + 27), "1", font=font(BOLD, 15),
           fill=(255, 255, 255), anchor="mm")
    # --- frame ---
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=BORDER, width=1)


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=OCEAN)
    # graticule every 30 degrees
    lon = -150
    while lon <= 180:
        x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
        d.line([x, MAP_Y0, x, MAP_Y1], fill=GRAT, width=1)
        lon += 30
    lat = 60
    while lat >= -30:
        y = MAP_Y0 + (LAT0 - lat) / (LAT0 - LAT1) * (MAP_Y1 - MAP_Y0)
        d.line([MAP_X0, y, MAP_X1, y], fill=GRAT, width=1)
        lat -= 30
    for _name, _label, poly in CONTINENTS:
        pts = [project(lo, la) for lo, la in poly]
        d.polygon(pts, fill=LAND, outline=(140, 152, 122))
    lab_f = font(BOLD, 11)
    for name, (llo, lla), _poly in CONTINENTS:
        if not name or name == "GREENLAND":
            continue
        lx, ly = project(llo, lla)
        d.text((lx, ly), name, font=lab_f, fill=(88, 96, 80), anchor="mm")
    pin_f = font(BOLD, 13)
    for num, lo, la, off in PINS:
        px, py = project(lo, la)
        dx, dy = px, py
        if off:
            dx, dy = px + off[0], py + off[1]
            d.line([dx, dy, px, py], fill=RED, width=1)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        d.ellipse([dx - 11, dy - 11, dx + 11, dy + 11], fill=RED,
                  outline=(255, 255, 255), width=2)
        d.text((dx, dy - 1), str(num), font=pin_f, fill=(255, 255, 255), anchor="mm")


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # ---- Masthead ----
    d.text((W // 2, 8), "THE WORLD IN ONE PAGE", font=font(DISPBLACK, 42),
           fill=NAVY, anchor="ma")
    # Date line: grey date, story counts picked out in red, centered as one unit.
    date_f = font(BOLD, 16)
    segs = [("TUESDAY, 17 NOVEMBER 2026  \u00b7  ", GREY),
            ("24 STORIES", RED),
            ("  \u00b7  ", GREY),
            ("5 CONTINENTS", RED)]
    total = sum(date_f.getlength(t) for t, _ in segs)
    sx = (W - total) // 2
    for t, c in segs:
        d.text((sx, 62), t, font=date_f, fill=c)
        sx += date_f.getlength(t)
    d.rectangle([16, 86, W - 16, 90], fill=RED)
    d.rectangle([16, 93, W - 16, 94], fill=INK)

    # ---- HERO panel: story 1, the day's biggest story ----
    d.rectangle([16, HERO_Y0, W - 16, HERO_Y1], fill=CARD, outline=BORDER, width=1)
    # kicker: number badge + region + "biggest story" line
    d.ellipse([32, 112, 56, 136], fill=RED)
    d.text((44, 123), "1", font=font(BOLD, 14),
           fill=(255, 255, 255), anchor="mm")
    d.text((64, 117), "EUROPE \u00b7 THE DAY'S BIGGEST STORY", font=font(BOLD, 13), fill=RED)
    # headline, Noto Serif Display Black 46 — clearly bigger than the 42pt
    # masthead, so the hero leads without drowning it
    head_f = font(DISPBLACK, 46)
    hlines = wrap(LEADS[0][1], head_f, 460)
    hy = 140
    for ln in hlines[:2]:
        d.text((32, hy), ln, font=head_f, fill=INK)
        hy += 52
    # summary, verbatim from v2
    sum_f = font(REG, 16)
    slines = wrap(LEADS[0][2], sum_f, 460)
    sy = 244
    for ln in slines[:2]:
        d.text((32, sy), ln, font=sum_f, fill=(60, 60, 58))
        sy += 20
    # bottom line: the outcome, restating the verified summary
    d.rectangle([32, 292, 92, 294], fill=RED)
    d.text((32, 302), "ROAD SPAN DOWN \u00b7 RAIL SPAN STANDS",
           font=font(BOLD, 14), fill=RED)
    # hero illustration, right half of the panel
    draw_hero_illustration(d, HERO_ILL_X0, HERO_ILL_Y0, HERO_ILL_W, HERO_ILL_H)

    # ---- Map strip ----
    d.text((16, 344), "WHERE THE NEWS HAPPENED", font=font(BOLD, 12), fill=GREY)
    d.text((W - 16, 344), "SIX LEADS, NUMBERED", font=font(BOLD, 12),
           fill=RED, anchor="ra")
    draw_map(d)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=BORDER, width=1)

    # ---- Lead cards 2-6: 2 columns x 3 rows; slot 6 is BY THE NUMBERS ----
    for i, (region, headline, summary, icon, tile) in enumerate(LEADS[1:]):
        num = i + 2
        col, row = i % 2, i // 2
        x = 16 + col * (CARD_W + CARD_GAP)
        y = CARDS_Y0 + row * (CARD_H + CARD_GAP)
        d.rectangle([x, y, x + CARD_W, y + CARD_H], fill=CARD, outline=BORDER, width=1)
        # number badge
        d.ellipse([x + 8, y + 8, x + 30, y + 30], fill=RED)
        d.text((x + 19, y + 18), str(num), font=font(BOLD, 14),
               fill=(255, 255, 255), anchor="mm")
        # icon tile
        tx, ty, ts = x + 38, y + 8, 56
        d.rounded_rectangle([tx, ty, tx + ts, ty + ts], radius=6, fill=tile)
        ICONS[icon](d, tx, ty, ts)
        # text block
        tx0 = x + 104
        d.text((tx0, y + 8), region, font=font(BOLD, 11), fill=RED)
        head_f = font(DISPB, 23)
        lines = wrap(headline, head_f, CARD_W - 104 - 10)
        hy = y + 24
        for ln in lines[:2]:
            d.text((tx0, hy), ln, font=head_f, fill=INK)
            hy += 26
        sum_f = font(REG, 13)
        slines = wrap(summary, sum_f, CARD_W - 104 - 10)
        sy = hy + 6
        for ln in slines[:2]:
            d.text((tx0, sy), ln, font=sum_f, fill=(60, 60, 58))
            sy += 15

    # ---- BY THE NUMBERS as a 2x2 card in the 6th slot ----
    nx, ny = 16 + CARD_W + CARD_GAP, CARDS_Y0 + 2 * (CARD_H + CARD_GAP)
    d.rectangle([nx, ny, nx + CARD_W, ny + CARD_H], fill=CARD, outline=BORDER, width=1)
    d.rectangle([nx + 8, ny + 11, nx + 16, ny + 19], fill=RED)
    d.text((nx + 22, ny + 8), "BY THE NUMBERS", font=font(BOLD, 13), fill=NAVY)
    d.rectangle([nx + 8, ny + 28, nx + CARD_W - 8, ny + 30], fill=INK)
    num_f = font(DISPB, 24)
    lab_f = font(REG, 11)
    for i, (num, label) in enumerate(NUMBERS):
        col, row = i % 2, i // 2
        cx = nx + 8 + col * 242
        cy = ny + 34 + row * 42
        d.text((cx, cy), num, font=num_f, fill=NAVY)
        d.text((cx, cy + 26), label, font=lab_f, fill=GREY)
        if col == 0:
            d.line([nx + 242, ny + 34, nx + 242, ny + 34 + 78], fill=BORDER, width=1)
    d.line([nx + 8, ny + 74, nx + CARD_W - 8, ny + 74], fill=BORDER, width=1)

    # ---- ALSO list ----
    ay = ALSO_Y
    d.rectangle([16, ay + 3, 24, ay + 11], fill=RED)
    d.text((32, ay), "ALSO ON THIS PAGE", font=font(BOLD, 14), fill=NAVY)
    d.rectangle([16, ay + 22, W - 16, ay + 24], fill=INK)
    tag_f = font(BOLD, 13)
    txt_f = font(REG, 13)
    ly = ay + 30
    for col_items, cx in ((ALSO_A, 16), (ALSO_B, 516)):
        cy = ly
        for tag, text in col_items:
            d.text((cx, cy), tag, font=tag_f, fill=RED)
            tw = tag_f.getlength(tag) + 8
            d.text((cx + tw, cy), text, font=txt_f, fill=INK)
            cy += 15
    d.line([508, ly, 508, ly + 9 * 15 - 4], fill=BORDER, width=1)

    # ---- Source line ----
    d.text((W // 2, 998),
           "Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera \u00b7 WHO \u00b7 UKMTO \u00b7 UN  \u2014  "
           "Claims marked \u201csays\u201d are unconfirmed. All drawings original.",
           font=font(REG, 11), fill=GREY, anchor="ma")

    page.save(OUT, "PNG", optimize=True)
    import os
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
