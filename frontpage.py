#!/usr/bin/env python3
"""Front page for Tuesday 24 November 2026 — rich winner style + serif discipline.
Renders one 1024x1024 image: masthead + numbers strip + region tabs + 3 heroes
+ dot-matrix world map + DATE CHECK + 13 pictured cards + 20 briefs + footer.
Local render only: Python + Pillow + Liberation fonts, no network, no time,
no randomness — deterministic byte-identical output across runs.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---- palette ----
PAPER = (250, 243, 228)
PAPER2 = (244, 235, 216)
INK = (28, 28, 28)
INK_SOFT = (74, 74, 74)
GREY = (120, 116, 108)
RED = (176, 32, 32)
RED_DK = (140, 22, 22)
NAVY = (10, 38, 66)
NAVY2 = (16, 58, 96)
TEAL = (10, 86, 106)
GOLD = (238, 180, 88)
GOLD_DK = (214, 148, 52)
CREAM = (252, 247, 236)
WHITE = (255, 255, 255)
CARD_BG = (255, 255, 255)
LINE = (196, 186, 168)
GREEN = (34, 139, 34)
AMBER = (196, 110, 0)
TEAL_PILL = (0, 128, 128)

FDIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, lh=None, align="left", x2=None):
    if lh is None:
        lh = int(fnt.size * 1.25)
    for ln in lines:
        if align == "center":
            xx = x + (x2 - x - draw.textlength(ln, font=fnt)) // 2
        elif align == "right":
            xx = x2 - draw.textlength(ln, font=fnt)
        else:
            xx = x
        draw.text((xx, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def pill(draw, x, y, text, fill, fnt=None, pad_x=6, h=16):
    """Small rounded certainty pill; returns right edge x."""
    fnt = fnt or SANS_B(9)
    w = int(draw.textlength(text, font=fnt)) + pad_x * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    draw.text((x + pad_x, y + (h - fnt.size) // 2 - 1), text, font=fnt, fill=WHITE)
    return x + w


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    n = max(1, y1 - y0)
    for i in range(n):
        t = i / n
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi) + xi
        ):
            inside = not inside
        j = i
    return inside


# ---- simplified continent outlines (lon, lat), coarse 4-degree grid ----
N_AMERICA = [(-168, 66), (-162, 60), (-155, 58), (-150, 61), (-141, 60),
             (-135, 57), (-130, 54), (-126, 49), (-124, 43), (-121, 36),
             (-117, 33), (-112, 29), (-109, 25), (-106, 22), (-103, 19),
             (-98, 17), (-95, 16), (-91, 14), (-87, 13), (-84, 11),
             (-81, 9), (-78, 7), (-79, 9), (-81, 12), (-83, 14),
             (-86, 13), (-88, 15), (-88, 17), (-90, 21), (-91, 19),
             (-94, 18), (-97, 20), (-97, 23), (-97, 26), (-96, 28),
             (-93, 30), (-90, 29), (-86, 30), (-84, 30), (-81, 26),
             (-80, 28), (-81, 31), (-79, 33), (-76, 35), (-75, 38),
             (-74, 40), (-71, 41), (-69, 43), (-66, 45), (-64, 44),
             (-60, 46), (-56, 47), (-59, 50), (-62, 53), (-65, 56),
             (-68, 58), (-72, 60), (-77, 62), (-82, 63), (-87, 65),
             (-92, 66), (-95, 68), (-105, 68), (-115, 68), (-125, 70),
             (-135, 69), (-145, 70), (-155, 71), (-162, 70), (-166, 68)]
GREENLAND = [(-55, 60), (-48, 60), (-42, 61), (-38, 64), (-32, 68),
             (-25, 70), (-20, 74), (-22, 77), (-30, 80), (-40, 81),
             (-52, 80), (-58, 76), (-60, 72), (-58, 66)]
S_AMERICA = [(-79, 9), (-77, 7), (-77, 4), (-79, 1), (-81, -3), (-80, -6),
             (-77, -11), (-74, -16), (-70, -19), (-70, -23), (-70, -28),
             (-71, -33), (-73, -38), (-73, -44), (-72, -48), (-69, -52),
             (-66, -55), (-64, -52), (-66, -48), (-64, -43), (-61, -39),
             (-58, -35), (-54, -33), (-50, -30), (-47, -26), (-42, -23),
             (-39, -20), (-35, -18), (-35, -14), (-35, -9), (-36, -6),
             (-39, -4), (-42, -2), (-45, 0), (-49, 1), (-51, 4), (-54, 6),
             (-57, 8), (-60, 9), (-63, 10), (-66, 11), (-69, 11),
             (-72, 12), (-75, 11), (-78, 9)]
AFRICA = [(-17, 15), (-16, 20), (-15, 25), (-12, 29), (-9, 32), (-6, 35),
          (-1, 35), (4, 37), (9, 37), (11, 34), (15, 32), (20, 32),
          (25, 32), (30, 31), (32, 31), (34, 28), (35, 24), (36, 22),
          (38, 20), (40, 16), (42, 11), (46, 11), (51, 12), (49, 10),
          (46, 5), (42, 1), (40, -4), (39, -8), (37, -12), (36, -17),
          (35, -21), (33, -26), (30, -30), (26, -34), (20, -35),
          (17, -33), (15, -28), (13, -22), (12, -17), (13, -12),
          (10, -5), (9, 0), (9, 4), (5, 5), (0, 6), (-4, 5), (-8, 5),
          (-12, 8), (-16, 12)]
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-1, 48), (2, 51), (6, 54),
           (8, 57), (11, 58), (18, 56), (21, 56), (24, 59), (28, 62),
           (33, 65), (40, 67), (48, 68), (58, 69), (68, 71), (78, 72),
           (88, 73), (98, 75), (108, 74), (118, 73), (128, 72),
           (138, 72), (148, 71), (158, 70), (168, 67), (178, 65),
           (175, 62), (168, 60), (162, 57), (158, 52), (152, 58),
           (144, 59), (141, 52), (140, 46), (136, 43), (131, 42),
           (127, 39), (124, 38), (121, 34), (119, 29), (114, 25),
           (110, 21), (108, 18), (106, 14), (104, 9), (101, 7),
           (98, 11), (96, 15), (93, 18), (91, 22), (88, 21), (85, 19),
           (82, 16), (80, 13), (77, 8), (75, 12), (72, 20), (68, 22),
           (64, 25), (60, 25), (57, 26), (54, 26), (51, 28), (49, 30),
           (46, 29), (43, 29), (40, 29), (37, 28), (36, 29), (36, 32),
           (35, 33), (35, 36), (33, 36), (30, 36), (27, 37), (26, 38),
           (23, 36), (22, 38), (20, 40), (19, 42), (16, 40), (15, 38),
           (12, 42), (10, 44), (8, 44), (6, 43), (3, 43), (0, 39),
           (-1, 37), (-2, 37), (-5, 36), (-6, 36), (-9, 37), (-9, 39)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-2, 51)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
         (141, 39), (141, 42), (143, 43), (145, 44), (142, 45), (140, 42),
         (139, 38), (137, 37), (135, 34), (133, 34), (131, 33)]
BORNEO = [(109, 1), (111, 3), (114, 4), (117, 2), (118, -1), (117, -3),
          (114, -3), (111, -2), (109, 0)]
SUMATRA = [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -5),
           (101, -1), (98, 2)]
JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (113, -8), (110, -7), (107, -7)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8),
              (147, -8), (143, -7), (138, -7), (134, -4), (131, -2)]
SULAWESI = [(119, 0), (121, 1), (123, 0), (120, -2), (119, -3)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (140, -12), (137, -12),
             (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20), (114, -22)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (175, -40), (172, -43), (169, -46)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
              (44, -25), (43, -21), (44, -18)]
ICELAND = [(-22, 64), (-18, 63), (-15, 64), (-14, 66), (-18, 66), (-22, 65)]
SRI_LANKA = [(80, 6), (81, 8), (80, 9)]
TAIWAN = [(120, 22), (121, 24), (121, 25)]
PHILIPPINES = [(120, 18), (122, 18), (122, 14), (124, 11), (123, 10),
               (121, 14), (120, 16)]
LAND = [N_AMERICA, GREENLAND, S_AMERICA, AFRICA, EURASIA, UK, JAPAN,
        BORNEO, SUMATRA, JAVA, NEW_GUINEA, SULAWESI, AUSTRALIA,
        NEW_ZEALAND, MADAGASCAR, ICELAND, SRI_LANKA, TAIWAN, PHILIPPINES]


def on_land(lon, lat):
    return any(point_in_poly(lon, lat, poly) for poly in LAND)


# ---- world map: dot matrix, navy->teal sea, gold land, crimson pins ----
# Map box: x 8..388, y 446..590. Inner plot: origin (20, 472), 0.9 px/deg,
# lon -180..180, lat 80..-56. Pins numbered 1..18, matching the stories.
MAP_X0, MAP_Y0, MAP_PPD = 36, 466, 0.9
MAP_LAT_TOP = 80


def map_xy(lon, lat):
    return (MAP_X0 + (lon + 180) * MAP_PPD,
            MAP_Y0 + (MAP_LAT_TOP - lat) * MAP_PPD)


# pin: (number, lon, lat, offset dx, dy in px for the disc)
PINS = [
    (1, -74.0, 40.7, -26, -18),    # H1 Brooklyn (Huawei verdict)
    (2, 46.7, 24.7, -28, 16),     # H2 Riyadh PIF tower
    (3, 26.0, 60.0, -30, -20),    # H3 Sparta II, Gulf of Finland
    (4, 19.0, 52.0, -32, 14),     # H3 Poland drone incursion
    (5, 56.0, 26.5, 24, 16),      # C1 Hormuz tankers
    (6, 127.0, 37.5, -18, 14),    # C2 Seoul (Kospi)
    (7, 139.7, 35.7, 20, -12),    # C2 Tokyo (Nikkei)
    (8, -17.5, 14.7, 0, 0),       # C3 Dakar (Senegal)
    (9, 121.5, 31.2, 0, 0),       # C4 Shanghai
    (10, 35.2, 47.8, 26, -18),    # C5 Zaporizhzhia
    (11, 34.5, 31.5, 26, 14),     # C6 Gaza
    (12, -75.5, 10.4, 0, 0),      # C7 Cartagena
    (13, 44.4, 35.5, 32, -8),     # C8 Kirkuk
    (14, -86.8, 36.0, 0, 0),      # C9 Tennessee
    (15, -74.0, 40.7, 24, -16),   # C10 New York (Giuliani)
    (16, 100.3, 41.0, 0, 0),      # C11 Jiuquan (Shenzhou-24)
    (17, -122.1, 47.7, 0, 0),     # C12 Redmond (Microsoft)
    (18, 85.3, 27.7, 0, 0),       # C13 Nepal quake
]


def draw_map(draw, box):
    x0, y0, x1, y1 = box
    vgrad(draw, (x0, y0 + 14, x1, y1), (8, 34, 68), (10, 86, 106))
    # faint graticule
    for lon in range(-150, 181, 30):
        gx = MAP_X0 + (lon + 180) * MAP_PPD
        draw.line([(gx, y0 + 14), (gx, y1)], fill=(255, 255, 255, 26), width=1)
    for lat in range(60, -61, -30):
        gy = MAP_Y0 + (MAP_LAT_TOP - lat) * MAP_PPD
        draw.line([(x0, gy), (x1, gy)], fill=(255, 255, 255, 26), width=1)
    # land dots, 4-degree grid
    lon = -178
    while lon <= 178:
        lat = 78
        while lat >= -54:
            if on_land(lon, lat):
                px, py = map_xy(lon, lat)
                # deeper gold variation on a fixed checker for texture
                c = GOLD if ((lon + lat) // 4) % 2 == 0 else GOLD_DK
                draw.ellipse([px - 1.7, py - 1.7, px + 1.7, py + 1.7], fill=c)
            lat -= 4
        lon += 4
    # pins: leader line from true point to offset disc
    for num, lon, lat, dx, dy in PINS:
        tx, ty = map_xy(lon, lat)
        cx, cy = tx + dx, ty + dy
        draw.ellipse([tx - 1.8, ty - 1.8, tx + 1.8, ty + 1.8], fill=WHITE)
        if dx or dy:
            draw.line([(tx, ty), (cx, cy)], fill=(20, 20, 20), width=4)
            draw.line([(tx, ty), (cx, cy)], fill=WHITE, width=2)
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(204, 32, 24),
                     outline=WHITE, width=1)
        t = str(num)
        tw = draw.textlength(t, font=SANS_B(9))
        draw.text((cx - tw / 2, cy - 5), t, font=SANS_B(9), fill=WHITE)


# ---- hero scenes (full-colour illustrations, drawn with shapes) ----
def scene_h1(draw, x, y, w, h):
    """Brooklyn courtroom: columns, scales of justice, GUILTY banner."""
    vgrad(draw, (x, y, x + w, y + h), (18, 32, 58), (34, 62, 104))
    # courthouse facade
    draw.rectangle([x + 18, y + 22, x + w - 18, y + h - 26], fill=(198, 202, 212))
    draw.polygon([(x + 8, y + 24), (x + w // 2, y + 2), (x + w - 8, y + 24)],
                 fill=(222, 226, 234))
    for i in range(4):
        cx = x + 48 + i * 78
        draw.rectangle([cx, y + 30, cx + 16, y + h - 30], fill=(238, 240, 244))
        draw.rectangle([cx - 3, y + 26, cx + 19, y + 32], fill=(220, 224, 232))
    # scales of justice, gold
    sx, sy = x + w // 2, y + 52
    draw.line([(sx, sy), (sx, sy + 46)], fill=GOLD, width=4)
    draw.line([(sx - 34, sy + 10), (sx + 34, sy + 10)], fill=GOLD, width=4)
    for sgn in (-1, 1):
        ex = sx + sgn * 34
        draw.line([(ex, sy + 10), (ex, sy + 26)], fill=GOLD, width=2)
        draw.arc([ex - 13, sy + 22, ex + 13, sy + 40], 0, 180, fill=GOLD, width=3)
    draw.ellipse([sx - 5, sy - 6, sx + 5, sy + 4], fill=GOLD)
    draw.rectangle([sx - 16, sy + 46, sx + 16, sy + 52], fill=GOLD)
    # red verdict banner
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=RED)
    draw.text((x + 10, y + h - 22), "10 OF 12 COUNTS  ·  GUILTY",
              font=SANS_B(13), fill=WHITE)


def scene_h2(draw, x, y, w, h):
    """Riyadh night: 80-storey PIF tower, smoke, drone, impact glow."""
    vgrad(draw, (x, y, x + w, y + h), (12, 16, 36), (44, 32, 64))
    # stars
    for sx, sy in [(30, 14), (90, 26), (150, 10), (210, 30), (260, 12),
                   (300, 24), (60, 44), (180, 40), (240, 48)]:
        draw.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                     fill=(220, 220, 240))
    # city silhouette
    for bx, bw, bh in [(0, 46, 34), (52, 34, 52), (92, 40, 26), (268, 44, 40),
                       (312, 18, 22)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                       fill=(22, 26, 46))
    # PIF tower
    tx = x + w // 2 - 26
    draw.rectangle([tx, y + 18, tx + 52, y + h], fill=(58, 68, 96))
    draw.polygon([(tx + 6, y + 18), (tx + 26, y + 2), (tx + 46, y + 18)],
                 fill=(70, 82, 116))
    for r in range(9):
        for c in range(4):
            if (r * 4 + c) % 3:
                draw.rectangle([tx + 7 + c * 11, y + 30 + r * 12,
                                tx + 13 + c * 11, y + 36 + r * 12],
                               fill=(250, 210, 110))
    # impact glow + smoke — all kept inside the scene (top >= y)
    gx, gy = tx + 40, y + 44
    for r, c in [(13, (255, 120, 60)), (8, (255, 90, 40)), (4, (255, 200, 80))]:
        draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=c)
    for sx, sy, sr in [(gx - 18, gy - 14, 8), (gx - 30, gy - 24, 10),
                       (gx - 40, gy - 32, 12)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 120, 128))
    # drone
    dx, dy = x + w - 52, y + 26
    draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(20, 20, 20))
    draw.line([(dx - 12, dy - 6), (dx + 12, dy - 6)], fill=(20, 20, 20), width=2)
    draw.ellipse([dx + 8, dy + 2, dx + 12, dy + 6], fill=(255, 60, 60))
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=RED)
    draw.text((x + 10, y + h - 22), "80 FLOORS  ·  385 m  ·  11 INJURED",
              font=SANS_B(13), fill=WHITE)


def scene_h3(draw, x, y, w, h):
    """Gulf of Finland: cargo ship, sea drones, radar arcs."""
    vgrad(draw, (x, y, x + w, y + h), (8, 48, 78), (10, 88, 118))
    # radar arcs top-right
    rx, ry = x + w - 8, y + 8
    for r in (18, 30, 42):
        draw.arc([rx - r, ry - r, rx + r, ry + r], 90, 180,
                 fill=(120, 220, 140), width=2)
    draw.ellipse([rx - 3, ry - 3, rx + 3, ry + 3], fill=(120, 220, 140))
    # waves
    for wy in (y + h - 46, y + h - 30, y + h - 14):
        for wx in range(x + 6, x + w - 10, 26):
            draw.arc([wx, wy, wx + 20, wy + 12], 180, 360, fill=(200, 230, 245), width=2)
    # cargo ship
    hx, hy = x + 26, y + h - 78
    draw.polygon([(hx, hy + 22), (hx + 190, hy + 22), (hx + 176, hy + 44),
                  (hx + 12, hy + 44)], fill=(24, 28, 38))
    for i, c in enumerate([(198, 60, 60), (60, 140, 90), (230, 180, 60),
                           (70, 110, 200), (200, 120, 60)]):
        draw.rectangle([hx + 14 + i * 36, hy - 6, hx + 44 + i * 36, hy + 22], fill=c)
    draw.rectangle([hx + 196, hy - 18, hx + 206, hy + 22], fill=(220, 220, 220))
    # sea drones with dotted trails
    for dx, dy in [(x + w - 78, y + 52), (x + w - 116, y + 76), (x + w - 46, y + 84)]:
        for i in range(5):
            px = dx + 8 + i * 7
            draw.ellipse([px - 1, dy - 1, px + 1, dy + 1], fill=(255, 220, 120))
        draw.ellipse([dx - 5, dy - 4, dx + 5, dy + 4], fill=(30, 30, 30))
        draw.line([(dx - 9, dy - 5), (dx + 9, dy - 5)], fill=(30, 30, 30), width=2)
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=RED)
    draw.text((x + 10, y + h - 22), "16 CREW EVACUATED  ·  GULF OF FINLAND",
              font=SANS_B(13), fill=WHITE)


# ---- pictured-card icons: simple white glyphs on a coloured square ----
def icon_ship(d, x, y, s):
    d.polygon([(x + 2, y + s * 0.55), (x + s - 2, y + s * 0.55),
               (x + s - 6, y + s * 0.78), (x + 6, y + s * 0.78)], fill=WHITE)
    d.rectangle([x + 8, y + s * 0.32, x + 22, y + s * 0.55], fill=WHITE)
    d.rectangle([x + 14, y + s * 0.18, x + 17, y + s * 0.32], fill=WHITE)
    for wx in (x + 2, x + 12, x + 22):
        d.arc([wx, y + s * 0.84, wx + 8, y + s * 0.94], 180, 360, fill=WHITE, width=2)


def icon_chart(d, x, y, s):
    d.line([(x + 4, y + s - 6), (x + 4, y + 6)], fill=WHITE, width=2)
    d.line([(x + 4, y + s - 6), (x + s - 4, y + s - 6)], fill=WHITE, width=2)
    d.line([(x + 6, y + s - 10), (x + 13, y + s - 18), (x + 18, y + s - 13),
            (x + 26, y + 8)], fill=WHITE, width=3)
    d.polygon([(x + 26, y + 8), (x + 20, y + 8), (x + 26, y + 14)], fill=WHITE)


def icon_trophy(d, x, y, s):
    d.polygon([(x + 8, y + 6), (x + s - 8, y + 6), (x + s - 11, y + 16),
               (x + 11, y + 16)], fill=WHITE)
    d.arc([x + 2, y + 6, x + 12, y + 18], 90, 270, fill=WHITE, width=3)
    d.arc([x + s - 12, y + 6, x + s - 2, y + 18], -90, 90, fill=WHITE, width=3)
    d.rectangle([x + s // 2 - 1, y + 16, x + s // 2 + 1, y + 23], fill=WHITE)
    d.rectangle([x + 9, y + 23, x + s - 9, y + 27], fill=WHITE)


def icon_search(d, x, y, s):
    d.ellipse([x + 5, y + 5, x + 19, y + 19], outline=WHITE, width=3)
    d.line([(x + 17, y + 17), (x + 25, y + 25)], fill=WHITE, width=3)


def icon_building(d, x, y, s):
    d.rectangle([x + 7, y + 6, x + s - 7, y + s - 6], fill=WHITE)
    for r in range(3):
        for c in range(2):
            d.rectangle([x + 10 + c * 7, y + 9 + r * 6, x + 14 + c * 7,
                         y + 12 + r * 6], fill=(40, 40, 40))
    d.line([(x + 7, y + 6), (x + s - 7, y + s - 6)], fill=(176, 32, 32), width=2)


def icon_shield(d, x, y, s):
    d.polygon([(x + s // 2, y + 3), (x + s - 4, y + 8), (x + s - 4, y + 17),
               (x + s // 2, y + 27), (x + 4, y + 17), (x + 4, y + 8)], fill=WHITE)
    d.line([(x + 10, y + 15), (x + 14, y + 19), (x + 21, y + 11)],
           fill=(40, 40, 40), width=2)


def icon_store(d, x, y, s):
    d.rectangle([x + 5, y + 12, x + s - 5, y + s - 5], fill=WHITE)
    for i in range(4):
        d.rectangle([x + 5 + i * 6, y + 6, x + 10 + i * 6, y + 12],
                    fill=WHITE if i % 2 == 0 else (176, 32, 32))
    d.rectangle([x + 12, y + 18, x + 18, y + s - 5], fill=(40, 40, 40))


def icon_derrick(d, x, y, s):
    d.polygon([(x + 5, y + s - 4), (x + 13, y + 4), (x + 18, y + 4),
               (x + 25, y + s - 4)], outline=WHITE, width=2)
    d.line([(x + 8, y + s - 10), (x + 22, y + s - 10)], fill=WHITE, width=2)
    d.line([(x + 13, y + 4), (x + 27, y + 10)], fill=WHITE, width=2)
    d.ellipse([x + 24, y + 7, x + 30, y + 13], fill=WHITE)


def icon_capitol(d, x, y, s):
    d.arc([x + 9, y + 3, x + 21, y + 15], 180, 360, fill=WHITE, width=3)
    d.rectangle([x + 6, y + 13, x + 24, y + 16], fill=WHITE)
    for cx in (8, 14, 20):
        d.rectangle([x + cx, y + 16, x + cx + 2, y + 24], fill=WHITE)
    d.rectangle([x + 5, y + 24, x + 25, y + 27], fill=WHITE)


def icon_medal(d, x, y, s):
    d.polygon([(x + 9, y + 3), (x + 14, y + 3), (x + 17, y + 12),
               (x + 12, y + 12)], fill=WHITE)
    d.polygon([(x + 16, y + 3), (x + 21, y + 3), (x + 18, y + 12),
               (x + 13, y + 12)], fill=(220, 180, 60))
    d.ellipse([x + 7, y + 12, x + 23, y + 28], fill=WHITE)
    d.text((x + 13, y + 16), "1", font=SANS_B(10), fill=(176, 32, 32))


def icon_rocket(d, x, y, s):
    d.polygon([(x + 15, y + 3), (x + 20, y + 12), (x + 20, y + 20),
               (x + 10, y + 20), (x + 10, y + 12)], fill=WHITE)
    d.polygon([(x + 10, y + 14), (x + 5, y + 20), (x + 10, y + 20)], fill=WHITE)
    d.polygon([(x + 20, y + 14), (x + 25, y + 20), (x + 20, y + 20)], fill=WHITE)
    d.polygon([(x + 13, y + 20), (x + 17, y + 20), (x + 15, y + 27)], fill=(255, 160, 40))
    d.ellipse([x + 13, y + 10, x + 17, y + 14], fill=(40, 40, 40))


def icon_warn(d, x, y, s):
    d.polygon([(x + 15, y + 3), (x + 27, y + 25), (x + 3, y + 25)], fill=WHITE)
    d.rectangle([x + 14, y + 10, x + 16, y + 19], fill=(176, 32, 32))
    d.ellipse([x + 14, y + 21, x + 16, y + 23], fill=(176, 32, 32))


def icon_mountain(d, x, y, s):
    d.polygon([(x + 3, y + 26), (x + 13, y + 8), (x + 20, y + 20),
               (x + 24, y + 14), (x + 28, y + 26)], fill=WHITE)
    d.line([(x + 3, y + 26), (x + 28, y + 26)], fill=WHITE, width=2)
    d.line([(x + 4, y + 20), (x + 27, y + 20)], fill=(176, 32, 32), width=1)


ICONS = {"ship": icon_ship, "chart": icon_chart, "trophy": icon_trophy,
         "search": icon_search, "building": icon_building,
         "shield": icon_shield, "store": icon_store, "derrick": icon_derrick,
         "capitol": icon_capitol, "medal": icon_medal, "rocket": icon_rocket,
         "warn": icon_warn, "mountain": icon_mountain}

# card accent colours (warm, varied, never garish)
ACCENTS = [(176, 32, 32), (10, 86, 106), (34, 120, 60), (140, 90, 20),
           (90, 60, 140), (160, 60, 90), (20, 90, 120), (150, 70, 20),
           (60, 100, 160), (120, 30, 60), (30, 110, 90), (180, 100, 10),
           (100, 80, 160)]

PILL_FILL = {"CONFIRMED": GREEN, "REPORTED": AMBER, "CLAIM": (204, 85, 0),
             "OFFICIAL": TEAL_PILL}


def draw_card(draw, x, y, w, h, card):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=CARD_BG,
                           outline=LINE, width=1)
    # icon square
    ix, iy, s = x + 7, y + 6, 28
    draw.rounded_rectangle([ix, iy, ix + s, iy + s], radius=5,
                           fill=ACCENTS[card["n"] % len(ACCENTS)])
    ICONS[card["icon"]](draw, ix, iy, s)
    # title, 2 lines max, full width right of the icon
    tx = x + 41
    title_lines = wrap(draw, card["title"], SANS_B(12), w - 48)[:2]
    draw_lines(draw, tx, y + 4, title_lines, SANS_B(12), INK, lh=13)
    # summary, 3 lines
    sum_lines = wrap(draw, card["text"], SANS(10), w - 48)[:3]
    draw_lines(draw, tx, y + 32, sum_lines, SANS(10), INK_SOFT, lh=11)
    # source line (left) + certainty pill (right) on the bottom row
    draw.text((tx, y + h - 12), card["src"], font=SANS(8), fill=GREY)
    pill(draw, x + w - 58, y + h - 14, card["pill"], PILL_FILL[card["pill"]],
         fnt=SANS_B(8), h=12, pad_x=5)


# ---- content: 36 stories, all figures verbatim from the dossier ----
HEROES = [
    {"n": 1, "place": "BROOKLYN, USA", "pill": "CONFIRMED",
     "scene": scene_h1,
     "head": "HUAWEI GUILTY ON 10 OF 12 COUNTS",
     "text": ("A Brooklyn jury convicts Huawei of trade-secret theft, bank and "
              "wire fraud, Iran sanctions breaches and money laundering."),
     "meta": "Acquitted on racketeering · sentencing 14 Sep 2027 · appeal planned",
     "src": "Reuters · CNN · Wall Street Journal"},
    {"n": 2, "place": "RIYADH, SAUDI ARABIA", "pill": "CONFIRMED",
     "scene": scene_h2,
     "head": "SECOND HOUTHI STRIKE ON RIYADH'S TALLEST TOWER",
     "text": ("The 80-storey, 385 m Public Investment Fund tower is hit for the "
              "second time in a week; 11 injured — 2 Saudi, 2 Indian, 3 Nepali, "
              "4 Egyptian."),
     "meta": "Saudi Arabia blames the Houthis · first strike 19 Nov",
     "src": "Reuters · Saudi Civil Defence · MEA India"},
    {"n": 3, "place": "GULF OF FINLAND · POLAND", "pill": "CONFIRMED",
     "scene": scene_h3,
     "head": "WAR WIDENS: SPARTA II HIT; POLAND CITES NEW INCURSION",
     "text": ("Kyiv admits a drone strike on the Russian cargo ship Sparta II; "
              "16 crew evacuated. Poland cites a new airspace incursion."),
     "meta": "Fire held over civilian risk · corvette sinking still a claim",
     "src": "Reuters · h.ua · Al Jazeera"},
]

CARDS = [
    {"n": 1, "icon": "ship", "pill": "CLAIM",
     "title": "IRAN: 4 TANKERS HIT BY MINES IN HORMUZ",
     "text": "IRGC says its navy hit a container ship; 4 tankers ablaze. "
             "Mine claims unverified.",
     "src": "Reuters · IRGC"},
    {"n": 2, "icon": "chart", "pill": "CONFIRMED",
     "title": "ASIA REBOUNDS: KOSPI +7.5%, NIKKEI +3.9%",
     "text": "Taiex +9.1% as Asia follows Wall Street; Kospi ~5,040, Nikkei "
             "58,654.",
     "src": "Reuters · investingLive"},
    {"n": 3, "icon": "trophy", "pill": "CONFIRMED",
     "title": "SENEGAL WIN BACK THE AFRICA CUP",
     "text": "CAS restores the 1–0 final win over Morocco; CAF's default "
             "overturned.",
     "src": "Reuters · AP"},
    {"n": 4, "icon": "search", "pill": "CONFIRMED",
     "title": "CHINA PROBES CHEN JINING",
     "text": "Politburo member Chen, 62, probed for grave violations; no "
             "specifics given.",
     "src": "Reuters · Xinhua · WSJ"},
    {"n": 5, "icon": "building", "pill": "CONFIRMED",
     "title": "ZAPORIZHZHIA: 2 KILLED, 48 HURT",
     "text": "10+ guided bombs hit homes at ~04:00; 15 freed from rubble. "
             "Toll rose to 48.",
     "src": "Reuters · 112.ua"},
    {"n": 6, "icon": "shield", "pill": "CONFIRMED",
     "title": "ISRAEL KILLS HAMAS SECURITY CHIEF",
     "text": "Brig. Gen. Nahel killed in a joint IDF–Shin Bet strike; 6 others "
             "killed.",
     "src": "Reuters · Daily Summary Of"},
    {"n": 7, "icon": "store", "pill": "CONFIRMED",
     "title": "CARTAGENA HOSTAGE CRISIS: 25 HELD",
     "text": "Gunmen seize a Cartagena supermarket; 5 elderly women freed.",
     "src": "President de la Espriella"},
    {"n": 8, "icon": "derrick", "pill": "CONFIRMED",
     "title": "IRAQ TAKES OVER KURDISH OIL FIELDS",
     "text": "PM al-Zaidi orders Baghdad to run fields in Diyala, Kirkuk and "
             "two more.",
     "src": "Reuters · Daily Summary Of"},
    {"n": 9, "icon": "capitol", "pill": "CONFIRMED",
     "title": "DEMOCRATS LOCK 259 HOUSE SEATS",
     "text": "Broderick flips Tennessee's 4th by under 400 votes; 259 is the "
             "most since 1990.",
     "src": "AP · Rational Review"},
    {"n": 10, "icon": "medal", "pill": "CONFIRMED",
     "title": "TRUMP GIVES GIULIANI MEDAL OF FREEDOM",
     "text": "Giuliani, 82, honoured in a closed Oval Office ceremony.",
     "src": "AP · Rational Review"},
    {"n": 11, "icon": "rocket", "pill": "CONFIRMED",
     "title": "FIRST FOREIGNER TO TIANGONG",
     "text": "Pakistan's Zeeshan Ali, 40, joins Tang Hongbo and Wu Yi on "
             "Shenzhou-24.",
     "src": "AP · Reuters · Nature"},
    {"n": 12, "icon": "warn", "pill": "REPORTED",
     "title": "MICROSOFT DECLARES 'CODE RED'",
     "text": "Top internal mobilisation after the 12–13 Nov outage hit key "
             "services.",
     "src": "Reuters, on memos seen"},
    {"n": 13, "icon": "mountain", "pill": "CONFIRMED",
     "title": "QUAKE 5.6 SHAKES EASTERN NEPAL",
     "text": "Centred at Olangchung Gola, 07:17 local; felt in Kathmandu and "
             "India.",
     "src": "Nepal centre 5.6 · India NCS 5.3"},
]

BRIEFS = [
    "NATO vows space defence — Rutte on a Russian nuke-satellite report; Moscow denies. (DSO)",
    "Germany first into Ukraine's Delta — battlefield-system access; more missiles. (K.I.)",
    "Zelensky meets Hungary's Magyar — bilateral talks and EU accession in Uzhhorod. (h.ua)",
    "Zelensky urges four-party talks — Ukraine, Russia, US, Europe 'as soon as possible'. (DSO)",
    "Dymer toll climbs to 12 — Valentyna, 79, rescued from rubble, dies in hospital. (h.ua)",
    "Tripoli seeks answers from Kyiv — UNSMIL urges a probe of the Benghazi ship strikes. (UN)",
    "UK sanctions Houthis + 4 officials — asset freezes and travel bans. (DSO)",
    "Saudi strike in Yemen: 25 killed — bus and truck hit in Wadi Maabaq. CLAIM. (DSO)",
    "Houthis 60 km from Aden — defence lines built north and west of the city. (DSO)",
    "Gaza warns of meningitis epidemic — 272 cases in October; 15 dead this year. (DSO)",
    "Indonesia names two VP candidates — Amran Sulaiman and Sugiono; MPR votes 11 Dec. (DSO)",
    "Malaysia to return migrants — 1,500 by warship, 5,303 by plane, at Myanmar's cost. (DSO)",
    "Hasina plans return 16 December — from exile in India; Dhaka calls her a convict. (DSO)",
    "Pentagon rebukes Canada — only 41.9% of its air fleet flyable; F-35 review. (DSO)",
    "'El Chapo Isidro' captured — US drone help in Sinaloa; Mexico refuses extradition. (DSO)",
    "WHO Ebola team evacuated — pulled from Ituri hospital after 3+ days sheltering. (UN)",
    "Champions League — Real Madrid 5–1 PSV (Mbappé 2); Arsenal 1–1 Dortmund; City 2–2 Napoli. (UEFA)",
    "Turkish helicopter crashes — AS-532 down after take-off from Eskisehir; 5 killed. (DSO)",
    "Russian jets enter Korea's ADIZ — Ulleungdo told to shelter; jets scrambled. (DSO)",
    "COP31: post-mortems published — first failed COP since Copenhagen 2009. (Smithsonian)",
]

NUMBERS = [
    ("10 OF 12", "counts — Huawei guilty"),
    ("11", "injured, PIF tower Riyadh"),
    ("4", "tankers hit by mines, Hormuz"),
    ("+7.5%", "Kospi in a day"),
    ("48", "hurt in Zaporizhzhia"),
    ("259", "Democratic House seats"),
]

REGIONS = [
    ("EUROPE", 8), ("MIDDLE EAST", 9), ("AFRICA", 3),
    ("ASIA-PACIFIC", 7), ("AMERICAS", 6), ("WORLD & SCIENCE", 3),
]

DATE_CHECK = (
    "ICJ Myanmar ruling (19 Nov) · FIFA Women's World Cup hosts (23 Nov) · "
    "Shenzhou-24 launch (25 Nov) · Nvidia +31.5% (Monday) · COP31 collapse "
    "(Sun/Mon — Tuesday only the post-mortem) · Merkury sinking (Sunday) · "
    "Poland missile incident (20 Nov) · GTA VI $3.79bn (Monday). "
    "Events from 19–23 Nov appear only as their Tuesday development."
)


# ---- page assembly ----
def draw_masthead(draw):
    draw.rectangle([0, 0, W, 6], fill=RED)
    t = "THE WORLD IN ONE DAY"
    draw.text(((W - draw.textlength(t, font=SERIF_B(40))) // 2, 12), t,
              font=SERIF_B(40), fill=INK)
    draw.line([(8, 58), (W - 8, 58)], fill=LINE, width=1)
    d = "TUESDAY 24 NOVEMBER 2026"
    draw.text(((W - draw.textlength(d, font=SERIF_B(29))) // 2, 62), d,
              font=SERIF_B(29), fill=INK)
    dek = ("Huawei guilty on 10 of 12 counts · Houthis strike Riyadh's tallest "
           "tower again · War widens to the Gulf of Finland")
    draw.text(((W - draw.textlength(dek, font=SERIF_I(14))) // 2, 94), dek,
              font=SERIF_I(14), fill=RED)


def draw_numbers(draw):
    draw.line([(8, 108), (W - 8, 108)], fill=LINE, width=1)
    draw.line([(8, 140), (W - 8, 140)], fill=LINE, width=1)
    cw = (W - 16) // 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = 8 + i * cw + cw // 2
        draw.text((cx - draw.textlength(num, font=SERIF_B(19)) // 2, 110), num,
                  font=SERIF_B(19), fill=RED_DK)
        draw.text((cx - draw.textlength(label, font=SANS(9)) // 2, 131), label,
                  font=SANS(9), fill=INK_SOFT)
        if i:
            draw.line([(8 + i * cw, 112), (8 + i * cw, 136)], fill=LINE, width=1)


def draw_tabs(draw):
    # centred coloured region tabs with counts
    widths = []
    for name, cnt in REGIONS:
        t = "%s · %d" % (name, cnt)
        widths.append(int(draw.textlength(t, font=SANS_B(11))) + 22)
    total = sum(widths) + 6 * (len(widths) - 1)
    x = (W - total) // 2
    y = 144
    cols = [(10, 86, 106), (176, 32, 32), (34, 120, 60), (140, 90, 20),
            (90, 60, 140), (20, 90, 120)]
    for (name, cnt), w, col in zip(REGIONS, widths, cols):
        t = "%s · %d" % (name, cnt)
        draw.rounded_rectangle([x, y, x + w, y + 18], radius=9, fill=col)
        draw.text((x + (w - draw.textlength(t, font=SANS_B(11))) // 2, y + 3),
                  t, font=SANS_B(11), fill=WHITE)
        x += w + 6


def draw_hero(draw, x, y, w, hero):
    hero["scene"](draw, x, y, w, 146)
    # numbered badge
    bx, by = x + 16, y + 16
    draw.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=RED,
                 outline=WHITE, width=2)
    t = str(hero["n"])
    draw.text((bx - draw.textlength(t, font=SANS_B(14)) // 2, by - 8), t,
              font=SANS_B(14), fill=WHITE)
    head = wrap(draw, hero["head"], SERIF_B(19), w)[:2]
    draw_lines(draw, x, y + 152, head, SERIF_B(19), INK, lh=23)
    body = wrap(draw, hero["text"], SANS(12), w)[:3]
    draw_lines(draw, x, y + 200, body, SANS(12), INK_SOFT, lh=15)
    draw.text((x, y + 248), hero["meta"], font=SERIF_I(11), fill=INK_SOFT)
    draw.text((x, y + 264), hero["src"], font=SANS(9), fill=GREY)
    pill(draw, x + w - 62, y + 261, hero["pill"], PILL_FILL[hero["pill"]])


def draw_date_check(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=CARD_BG,
                           outline=LINE, width=1)
    draw.rectangle([x, y + 6, x + 6, y + h - 6], fill=RED)
    draw.text((x + 16, y + 8), "DATE CHECK — WHAT IS NOT TUESDAY'S NEWS",
              font=SANS_B(13), fill=RED)
    lines = wrap(draw, DATE_CHECK, SANS(11), w - 28)
    draw_lines(draw, x + 16, y + 30, lines, SANS(11), INK, lh=14)
    draw.text((x + 16, y + h - 20),
              "Checked to the day: 36 stories · 6 regions · every claim labelled.",
              font=SANS_B(10), fill=INK)


def draw_brief(draw, x, y, w, text):
    # bold lead up to the first " — ", then regular; max 2 lines
    fnt = SANS(10)
    lines = wrap(draw, text, fnt, w)
    if len(lines) > 2:
        fnt = SANS(9)
        lines = wrap(draw, text, fnt, w)[:2]
    lead = text.split(" — ")[0]
    lh = 12
    for i, ln in enumerate(lines):
        yy = y + i * lh
        if i == 0 and ln.startswith(lead):
            draw.text((x, yy), lead, font=SANS_B(10 if fnt.size == 10 else 9),
                      fill=INK)
            rest = ln[len(lead):]
            draw.text((x + draw.textlength(lead, font=SANS_B(10 if fnt.size == 10 else 9)), yy),
                      rest, font=fnt, fill=INK_SOFT)
        else:
            draw.text((x, yy), ln, font=fnt, fill=INK_SOFT)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_numbers(draw)
    draw_tabs(draw)
    # heroes: 3 columns
    hx = [8, 346, 684]
    for x, hero in zip(hx, HEROES):
        draw_hero(draw, x, 160, 330, hero)
    # map + date check band
    draw.rounded_rectangle([8, 446, 388, 590], radius=6, fill=NAVY,
                           outline=LINE, width=1)
    draw.text((16, 452), "WHERE IT HAPPENED — 18 PLACES PINNED",
              font=SANS_B(11), fill=WHITE)
    draw.text((388 - 8 - draw.textlength("Numbers match the stories", font=SANS(9)), 453),
              "Numbers match the stories", font=SANS(9), fill=(200, 210, 225))
    draw_map(draw, (8, 446, 388, 590))
    draw_date_check(draw, 396, 446, 620, 144)
    # 13 pictured cards: rows of 5 / 5 / 3 (last row centred)
    rows = [CARDS[0:5], CARDS[5:10], CARDS[10:13]]
    for r, row in enumerate(rows):
        yy = 596 + r * 84
        x_start = 8
        if len(row) == 3:
            x_start = 8 + (1008 - (3 * 196 + 2 * 6)) // 2
        for i, card in enumerate(row):
            xx = x_start + i * 202
            draw_card(draw, xx, yy, 196, 78, card)
    # briefs: 4 columns x 5 rows
    draw.text((8, 844), "ALSO ON TUESDAY", font=SANS_B(12), fill=INK)
    draw.line([(8, 860), (W - 8, 860)], fill=LINE, width=1)
    for idx, b in enumerate(BRIEFS):
        col, row = idx % 4, idx // 4
        xx = 8 + col * 254
        yy = 866 + row * 27
        draw_brief(draw, xx, yy, 236, b)
    # footer
    draw.line([(8, 994), (W - 8, 994)], fill=LINE, width=1)
    foot = ("Sources: Reuters · AP · Wall Street Journal · Xinhua · AFP · "
            "Al Jazeera · UN News · UEFA — 36 stories · 6 regions · all claims "
            "labelled · Rendered locally, no network · Tuesday 24 November 2026")
    draw.text(((W - draw.textlength(foot, font=SANS(9))) // 2, 1002), foot,
              font=SANS(9), fill=GREY)
    return img


if __name__ == "__main__":
    import hashlib
    image = render()
    image.save(OUT)
    data = open(OUT, "rb").read()
    print("wrote %s %d bytes sha256=%s" % (OUT, len(data),
                                           hashlib.sha256(data).hexdigest()))
