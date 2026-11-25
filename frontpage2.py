#!/usr/bin/env python3
"""frontpage2.py — 'THE WORLD IN ONE DAY', Tuesday 24 November 2026 (v2).

Fresh authoring for news-image-20261124. Anatomy adopted from the user's
reference front page (a rival page): header counts line, giant serif
masthead + red dek naming the 3 heroes, region tabs, THE DAY IN NUMBERS
strip, 3 numbered heroes, pictured cards, numbered briefs 14-38 with
region dots, dot-matrix world map with pins 1-13, red DATE CHECK box.

Numbering (verified against the reference by cropping it): the 13 pictured
items are the 3 heroes (pins 1-3) + 10 mid cards (pins 4-13); briefs run
14-38 (25 briefs). 13 + 25 = 38 stories exactly. The header count is honest.

All 38 stories verified >=2 named sources (dossier stories.md + 2 additions
verified in-session: Sanofi $41bn Insmed, England-Australia T20).
Local render only: python3 + Pillow, no network, deterministic.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------------------------------------------------------- fonts
def _font(name, size, bold=False):
    cands = []
    if name == "serif":
        cands = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf" % ("Bold" if bold else "Regular"),
            "/usr/share/fonts/truetype/liberation/LiberationSerif-%sItalic.ttf" % ("Bold" if bold else ""),
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf" % ("-Bold" if bold else ""),
        ]
    else:
        cands = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
        ]
    for p in cands:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def Fserif(s, bold=False):
    return _font("serif", s, bold)

def Fsans(s, bold=False):
    return _font("sans", s, bold)

def Fserif_it(s):
    p = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
    if os.path.exists(p):
        return ImageFont.truetype(p, s)
    return Fserif(s)

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
INK = (18, 18, 18)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
GREY = (90, 88, 84)
LINE = (200, 192, 178)
TEAL = (13, 110, 110)      # OFFICIAL
GREEN = (34, 128, 60)      # CONFIRMED
AMBER = (176, 110, 0)      # REPORTED
CLAIMRED = (178, 34, 34)   # CLAIM
NAVY = (10, 42, 80)
TEALDEEP = (12, 92, 112)
GOLD = (240, 183, 92)
GOLDDARK = (214, 148, 52)
PINRED = (204, 32, 24)

REGIONS = [
    # name, colour, count (computed below, asserted)
    ("EUROPE", (52, 110, 180)),
    ("MIDDLE EAST", (18, 130, 110)),
    ("AFRICA", (205, 120, 30)),
    ("ASIA-PACIFIC", (178, 40, 40)),
    ("OCEANIA", (120, 80, 170)),
    ("AMERICAS", (190, 40, 110)),
    ("WORLD & SCIENCE", (90, 90, 95)),
]
RHEX = {name: col for name, col in REGIONS}

PILL_FILL = {"OFFICIAL": TEAL, "CONFIRMED": GREEN, "REPORTED": AMBER, "CLAIM": CLAIMRED}

# ---------------------------------------------------------------- data
# fields are used to compute the "20 FIELDS" header count honestly.
HEROES = [
    dict(num=1, region="ASIA-PACIFIC", field="politics", place="CHINA · POLITICS",
         pill="OFFICIAL", tag="UNDER INVESTIGATION",
         head="China investigates Politburo member Chen Jining",
         summ=("Shanghai party chief, 62, is under investigation for \"serious "
               "violations\", state media say. Xinhua, Reuters"),
         scene="shanghai", pin=(121.5, 31.2)),
    dict(num=2, region="AMERICAS", field="courts", place="NEW YORK · COURTS",
         pill="CONFIRMED", tag="10 OF 12 COUNTS",
         head="US jury finds Huawei guilty in trade-secrets case",
         summ=("Federal court, Brooklyn: guilty on 10 of 12 counts, cleared of "
               "racketeering. Huawei will appeal. Reuters, CNN"),
         scene="court", pin=(-74.0, 40.7)),
    dict(num=3, region="EUROPE", field="war", place="UKRAINE · WAR",
         pill="CONFIRMED", tag="WAR WIDENS",
         head="Kyiv hits Russian ship in the Gulf of Finland",
         summ=("Kyiv admits the Sparta II drone strike; 16 crew evacuated. "
               "Poland reports a new Russian drone incursion. Reuters"),
         scene="ship", pin=(25.0, 59.8)),
]

CARDS = [
    dict(num=4, region="MIDDLE EAST", field="war", place="RIYADH",
         pill="CONFIRMED", tag="80 FLOORS",
         head="Houthis hit Riyadh's tallest tower again",
         summ="Second strike on the PIF tower in a week; 11 hurt. Reuters",
         scene="tower", pin=(46.7, 24.7), bg=(58, 74, 96)),
    dict(num=5, region="MIDDLE EAST", field="energy", place="HORMUZ",
         pill="CLAIM", tag="4 TANKERS",
         head="Iran says 4 tankers hit by mines; strait shut",
         summ="Tehran claims mines set 4 tankers ablaze; JMIC: unverified. Reuters",
         scene="tanker", pin=(56.5, 26.5), bg=(96, 58, 44)),
    dict(num=6, region="ASIA-PACIFIC", field="markets", place="SEOUL",
         pill="CONFIRMED", tag="+7.5%",
         head="Asia rebounds: Kospi +7.5%, Nikkei +3.9%",
         summ="Taiex +9.1% as Wall Street's rally rolls on. Reuters",
         scene="chart", pin=(127.0, 37.5), bg=(30, 96, 66)),
    dict(num=7, region="AFRICA", field="sport", place="RABAT",
         pill="CONFIRMED", tag="AFCON",
         head="Sports court gives Senegal AFCON title",
         summ="CAS restores 1-0 final win; champions again. AP",
         scene="trophy", pin=(-6.8, 34.0), bg=(120, 96, 20)),
    dict(num=8, region="EUROPE", field="war", place="ZAPORIZHZHIA",
         pill="CONFIRMED", tag="04:00",
         head="Dawn glide-bomb strike kills 2, hurts 48",
         summ="10+ guided bombs hit homes; 15 freed from rubble. Reuters",
         scene="dawn", pin=(35.2, 47.8), bg=(70, 60, 92)),
    dict(num=9, region="MIDDLE EAST", field="war", place="GAZA CITY",
         pill="CONFIRMED", tag="AIR STRIKE",
         head="Israel kills Hamas security chief",
         summ="Naeem Abu Nahel dies in Gaza City air strike. Reuters",
         scene="smoke", pin=(34.5, 31.5), bg=(110, 74, 50)),
    dict(num=10, region="MIDDLE EAST", field="energy", place="KIRKUK",
         pill="OFFICIAL", tag="OIL FIELDS",
         head="Baghdad orders Kurdish oil takeover",
         summ="Kirkuk and 3 more provinces; Erbil says no. Reuters",
         scene="derrick", pin=(44.4, 35.5), bg=(92, 70, 30)),
    dict(num=11, region="AMERICAS", field="elections", place="WASHINGTON",
         pill="CONFIRMED", tag="259 SEATS",
         head="Democrats lock 259 House seats — most since 1990",
         summ="Tennessee flip by under 400 votes; 48th flip. AP",
         scene="capitol", pin=(-77.0, 38.9), bg=(40, 70, 110)),
    dict(num=12, region="WORLD & SCIENCE", field="pharma", place="PARIS",
         pill="OFFICIAL", tag="$41BN DEAL",
         head="Sanofi to buy Insmed for $41bn",
         summ="Deal announced 05:30 UTC; $175 a share, cash. Sanofi",
         scene="flask", pin=(2.35, 48.85), bg=(16, 110, 110)),
    dict(num=13, region="ASIA-PACIFIC", field="space", place="BEIJING",
         pill="CONFIRMED", tag="TIANGONG",
         head="China names first foreign Tiangong astronaut",
         summ="Pakistan's Zeeshan Ali, 40, joins Shenzhou-24 crew. AP",
         scene="rocket", pin=(116.4, 39.9), bg=(24, 34, 74)),
]

# Briefs: one line each (<= ~66 chars incl. source), numbered 14-38.
# (region, field, text, source)
BRIEFS = [
    ("EUROPE", "defence", "NATO vows to defend itself in space — Rutte", "DSO"),
    ("EUROPE", "defence", "Germany first to get access to Ukraine's Delta", "K.Indep."),
    ("EUROPE", "diplomacy", "Zelensky meets Hungary PM Magyar in Uzhhorod", "h.ua"),
    ("EUROPE", "diplomacy", "Zelensky urges four-party talks 'as soon as possible'", "DSO"),
    ("EUROPE", "war", "Dymer toll climbs to 12 as rescued woman dies", "h.ua"),
    ("AFRICA", "diplomacy", "Tripoli seeks answers from Kyiv; UNSMIL urges probe", "UN News"),
    ("MIDDLE EAST", "sanctions", "UK sanctions Houthis + 4 senior officials", "DSO"),
    ("MIDDLE EAST", "war", "Saudi strike on bus, trucks in Yemen: 25 dead*", "Saba*"),
    ("MIDDLE EAST", "war", "Houthis 60 km from Aden, ready to strike", "DSO"),
    ("MIDDLE EAST", "health", "Gaza warns of meningitis epidemic: 272 cases", "DSO"),
    ("ASIA-PACIFIC", "politics", "Indonesia names two VP candidates to replace Gibran", "DSO"),
    ("ASIA-PACIFIC", "migration", "Malaysia to return thousands of migrants to Myanmar", "DSO"),
    ("ASIA-PACIFIC", "politics", "Hasina plans return to Bangladesh on 16 December", "DSO"),
    ("AMERICAS", "defence", "Pentagon scolds Canada over defence spend, F-35", "DSO"),
    ("AMERICAS", "crime", "El Chapo Isidro held with US drone help; Mexico to try him", "DSO"),
    ("ASIA-PACIFIC", "disaster", "Quake 5.6 shakes east Nepal; felt in Kathmandu", "The Hindu"),
    ("AFRICA", "health", "WHO Ebola team evacuated from Ituri hospital, DRC", "UN News"),
    ("EUROPE", "sport", "Champions League: Real Madrid 5-1 PSV", "Reuters"),
    ("MIDDLE EAST", "aviation", "Turkish air force helicopter crashes, 5 crew dead", "DSO"),
    ("ASIA-PACIFIC", "defence", "Russian jets enter South Korea's air defence zone", "DSO"),
    ("WORLD & SCIENCE", "climate", "COP31: post-failure analysis out Tuesday", "Smithsonian"),
    ("OCEANIA", "sport", "Cricket: England beat Australia by 8 wickets", "Reuters"),
    ("AMERICAS", "crime", "Cartagena supermarket siege: 25 held hostage", "DSO"),
    ("AMERICAS", "awards", "Trump gives Medal of Freedom to Giuliani, 82", "AP"),
    ("WORLD & SCIENCE", "technology", "Microsoft declares 'Code Red' after 24-hour outage", "Reuters"),
]

NUMBERS = [
    # (place, figure, label)
    ("BROOKLYN", "10 of 12", "counts: Huawei guilty"),
    ("RIYADH", "11", "hurt in tower strike"),
    ("PARIS · 05:30 UTC", "$41bn", "Sanofi bid for Insmed"),
    ("SEOUL", "+7.5%", "Kospi in a day"),
    ("ZAPORIZHZHIA · 04:00 LOCAL", "48", "hurt in dawn strike"),
    ("WASHINGTON", "259", "House seats, Democrats"),
]

DATECHECK = ("DATE CHECK — Left off as earlier news: ICJ Myanmar ruling (19 Nov) · "
             "FIFA Women's World Cup hosts (23 Nov) · Shenzhou-24 launch (25 Nov) · "
             "Nvidia +31.5% (Mon) · COP31 collapse (Sun/Mon) · Merkury sinking (Sun/Mon) · "
             "Poland missile incident (20 Nov) · GTA VI $3.79bn (Mon) · Nigeria boat (20 Nov)")

FOOTER = ("Every story happened or was first reported on Tuesday 24 Nov 2026, UTC. "
          "Times shown are UTC unless marked local. Sources named on each item · "
          "Original drawings, no photos.")

# ---------------------------------------------------------------- helpers
OVERFLOWS = []

def text_w(d, x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)

def wrap(s, font, width):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(d, x, y, s, font, width, leading, fill=INK, max_lines=None):
    """Draw wrapped text; record an overflow if it needs more lines than max."""
    lines = wrap(s, font, width)
    if max_lines is not None and len(lines) > max_lines:
        OVERFLOWS.append("'%s' needs %d lines, max %d" % (s[:40], len(lines), max_lines))
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * leading), ln, font=font, fill=fill)
    return len(lines)

def fit_size(s, font_fn, width, start, minimum=8):
    """Largest font size (<=start) at which s fits width; records overflow if < minimum."""
    sz = start
    while sz > minimum and font_fn(sz).getlength(s) > width:
        sz -= 1
    if font_fn(sz).getlength(s) > width:
        OVERFLOWS.append("cannot fit '%s' in %d px even at %d" % (s[:40], width, minimum))
    return sz

def pill(d, x, y, label, h=13):
    f = Fsans(8, bold=True)
    w = int(f.getlength(label)) + 10
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=PILL_FILL[label])
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w

def num_badge(d, cx, cy, n, r=11, fill=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=(255, 255, 255), width=2)
    f = Fsans(11, bold=True)
    t = str(n)
    d.text((cx - f.getlength(t) / 2, cy - 6), t, font=f, fill=(255, 255, 255))

def vgrad(d, box, top, bot):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, (y1 - y0 - 1))
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(x0, yy), (x1, yy)], fill=c)

# ---------------------------------------------------------------- scenes
def scene_shanghai(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (24, 34, 66), (214, 110, 60))
    # sun
    d.ellipse([x + w - 78, y + 14, x + w - 38, y + 54], fill=(240, 190, 90))
    # skyline silhouettes
    import random
    rnd = random.Random(7)
    bx = x + 6
    while bx < x + w - 14:
        bw = rnd.randint(12, 26)
        bh = rnd.randint(int(h * 0.30), int(h * 0.62))
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(22, 26, 44))
        for wy in range(y + h - bh + 6, y + h - 6, 10):
            for wx in range(bx + 3, bx + bw - 3, 7):
                if rnd.random() < 0.5:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(250, 200, 90))
        bx += bw + 4
    # Oriental Pearl Tower
    tx = x + w // 2
    d.line([(tx, y + 8), (tx, y + h)], fill=(30, 32, 52), width=4)
    d.ellipse([tx - 13, y + 26, tx + 13, y + 52], fill=(30, 32, 52))
    d.ellipse([tx - 9, y + 62, tx + 9, y + 80], fill=(30, 32, 52))
    # red investigation banner
    d.rectangle([x, y + h - 20, x + w, y + h], fill=RED)
    f = Fsans(10, bold=True)
    t = "UNDER INVESTIGATION"
    d.text((x + w / 2 - f.getlength(t) / 2, y + h - 16), t, font=f, fill=(255, 255, 255))

def scene_court(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (96, 66, 44), (52, 34, 22))
    # bench
    d.rectangle([x + 18, y + h - 46, x + w - 18, y + h - 8], fill=(40, 26, 16))
    d.rectangle([x + 18, y + h - 52, x + w - 18, y + h - 46], fill=(120, 84, 48))
    # scales of justice
    cx, cy = x + w // 2, y + 22
    d.line([(cx, cy), (cx, cy + 44)], fill=(232, 200, 120), width=3)
    d.line([(cx - 34, cy + 8), (cx + 34, cy + 8)], fill=(232, 200, 120), width=3)
    for sgn in (-1, 1):
        px = cx + sgn * 34
        d.line([(px, cy + 8), (px, cy + 26)], fill=(232, 200, 120), width=2)
        d.pieslice([px - 13, cy + 22, px + 13, cy + 40], 0, 180, fill=(232, 200, 120))
    # gavel
    d.rectangle([x + w - 62, y + h - 62, x + w - 30, y + h - 54], fill=(150, 104, 58))
    d.line([(x + w - 46, y + h - 54), (x + w - 46, y + h - 46)], fill=(150, 104, 58), width=4)
    # verdict badge (top-right, clear of the number badge)
    f = Fserif(20, bold=True)
    t = "10 OF 12"
    tw = f.getlength(t)
    d.rectangle([x + w - 18 - tw, y + 8, x + w - 10, y + 32], fill=(255, 255, 255))
    d.text((x + w - 14 - tw, y + 10), t, font=f, fill=DARKRED)

def scene_ship(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 30, 58), (8, 18, 38))
    # stars / radar arcs
    cx, cy = x + w - 52, y + 40
    for r in (34, 24, 14):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(90, 200, 160), width=2)
    # drones with trails
    for (dx, dy, ln) in ((x + 40, y + 26, 26), (x + 88, y + 16, 20), (x + 130, y + 34, 30)):
        d.line([(dx - ln, dy + 8), (dx, dy)], fill=(255, 190, 80), width=2)
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=(255, 210, 110))
    # sea
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(10, 40, 66))
    for wx in range(x + 8, x + w - 8, 26):
        d.line([(wx, y + h - 26), (wx + 14, y + h - 26)], fill=(70, 140, 180), width=2)
    # cargo ship
    sx, sy = x + 30, y + h - 52
    d.rectangle([sx, sy, sx + 190, sy + 20], fill=(28, 30, 40))
    for i, col in enumerate(((200, 60, 50), (40, 110, 160), (220, 170, 60))):
        d.rectangle([sx + 14 + i * 52, sy - 22, sx + 52 + i * 52, sy], fill=col)
    # bridge tower with a human figure in the lit window
    d.rectangle([sx + 196, sy - 44, sx + 224, sy], fill=(38, 42, 56))
    d.rectangle([sx + 200, sy - 40, sx + 220, sy - 22], fill=(250, 205, 110))
    fx = sx + 210
    d.ellipse([fx - 4, sy - 38, fx + 4, sy - 30], fill=(20, 20, 26))   # head
    d.rectangle([fx - 4, sy - 30, fx + 4, sy - 22], fill=(20, 20, 26))  # body
    d.line([(fx - 6, sy - 27), (fx + 6, sy - 27)], fill=(20, 20, 26), width=2)  # shoulders
    # mast + flag
    d.line([(sx + 210, sy - 44), (sx + 210, sy - 62)], fill=(200, 200, 200), width=2)
    d.polygon([(sx + 210, sy - 62), (sx + 226, sy - 58), (sx + 210, sy - 54)], fill=(220, 60, 50))

def card_scene(d, x, y, w, h, kind, tag, bg):
    d.rectangle([x, y, x + w, y + h], fill=bg)
    if kind == "tower":
        vgrad(d, (x, y, x + w, y + h), (70, 88, 120), (30, 38, 60))
        d.rectangle([x + w // 2 - 14, y + 8, x + w // 2 + 14, y + h], fill=(24, 26, 40))
        for wy in range(y + 12, y + h - 4, 8):
            d.rectangle([x + w // 2 - 10, wy, x + w // 2 - 4, wy + 4], fill=(250, 200, 90))
            d.rectangle([x + w // 2 + 4, wy, x + w // 2 + 10, wy + 4], fill=(250, 200, 90))
        d.ellipse([x + w - 34, y + 6, x + w - 8, y + 32], fill=(240, 150, 60))
    elif kind == "tanker":
        d.rectangle([x, y + h - 16, x + w, y + h], fill=(16, 44, 66))
        d.rectangle([x + 30, y + h - 30, x + w - 30, y + h - 16], fill=(40, 40, 48))
        d.rectangle([x + 46, y + h - 44, x + w - 46, y + h - 30], fill=(60, 60, 70))
        for fx in (x + 52, x + 96, x + 140):
            d.polygon([(fx, y + h - 44), (fx + 8, y + 8), (fx + 16, y + h - 44)], fill=(240, 130, 40))
            d.ellipse([fx + 2, y + 2, fx + 14, y + 16], fill=(250, 200, 80))
    elif kind == "chart":
        d.line([(x + 8, y + h - 12), (x + w // 3, y + h - 26), (x + 2 * w // 3, y + h - 18),
                (x + w - 14, y + 8)], fill=(255, 255, 255), width=4)
        d.polygon([(x + w - 22, y + 4), (x + w - 8, y + 8), (x + w - 16, y + 18)], fill=(255, 255, 255))
        for gy in range(y + 8, y + h - 8, 12):
            d.line([(x + 6, gy), (x + w - 6, gy)], fill=(255, 255, 255, 60), width=1)
    elif kind == "trophy":
        d.ellipse([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + 44], fill=(250, 205, 90))
        d.rectangle([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + 26], fill=(250, 205, 90))
        d.rectangle([x + w // 2 - 4, y + 40, x + w // 2 + 4, y + h - 8], fill=(250, 205, 90))
        d.rectangle([x + w // 2 - 16, y + h - 10, x + w // 2 + 16, y + h - 6], fill=(250, 205, 90))
        d.arc([x + w // 2 - 36, y + 10, x + w // 2 - 12, y + 34], 90, 270, fill=(250, 205, 90), width=4)
        d.arc([x + w // 2 + 12, y + 10, x + w // 2 + 36, y + 34], 270, 90, fill=(250, 205, 90), width=4)
    elif kind == "dawn":
        vgrad(d, (x, y, x + w, y + h), (40, 40, 70), (220, 120, 50))
        d.ellipse([x + w // 2 - 14, y + h - 30, x + w // 2 + 14, y + h - 2], fill=(250, 200, 90))
        for (bx, bh) in ((x + 12, 18), (x + 60, 26), (x + 150, 20)):
            d.rectangle([bx, y + h - bh, bx + 34, y + h], fill=(24, 22, 34))
    elif kind == "smoke":
        vgrad(d, (x, y, x + w, y + h), (120, 110, 100), (60, 56, 52))
        for (sx, sy, r) in ((x + 40, y + 14, 12), (x + 70, y + 8, 15), (x + 105, y + 16, 11),
                            (x + 140, y + 10, 13)):
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(90, 86, 84))
        d.polygon([(x + 90, y + h), (x + 110, y + 18), (x + 130, y + h)], fill=(240, 140, 50))
        d.rectangle([x + 12, y + h - 12, x + w - 12, y + h], fill=(30, 28, 26))
    elif kind == "derrick":
        d.line([(x + 40, y + h - 6), (x + 70, y + 6), (x + 100, y + h - 6)], fill=(30, 26, 22), width=4)
        d.line([(x + 52, y + h - 6), (x + 70, y + 20), (x + 88, y + h - 6)], fill=(30, 26, 22), width=3)
        d.rectangle([x + w - 48, y + h - 26, x + w - 22, y + h - 6], fill=(24, 22, 20))
        d.line([(x + w - 48, y + h - 19), (x + w - 22, y + h - 19)], fill=(120, 110, 100), width=2)
        d.line([(x + w - 48, y + h - 12), (x + w - 22, y + h - 12)], fill=(120, 110, 100), width=2)
        d.polygon([(x + w - 35, y + h - 26), (x + w - 30, y + h - 38), (x + w - 25, y + h - 26)], fill=(240, 140, 50))
    elif kind == "capitol":
        d.ellipse([x + w // 2 - 30, y + 6, x + w // 2 + 30, y + 30], fill=(235, 235, 225))
        d.rectangle([x + w // 2 - 34, y + 26, x + w // 2 + 34, y + h - 10], fill=(235, 235, 225))
        for cx in range(x + w // 2 - 28, x + w // 2 + 29, 12):
            d.line([(cx, y + 30), (cx, y + h - 12)], fill=(160, 160, 150), width=2)
        d.rectangle([x + w // 2 - 2, y + 0, x + w // 2 + 2, y + 8], fill=(235, 235, 225))
    elif kind == "flask":
        d.polygon([(x + w // 2 - 8, y + 8), (x + w // 2 + 8, y + 8),
                   (x + w // 2 + 26, y + h - 10), (x + w // 2 - 26, y + h - 10)],
                  fill=(220, 240, 245))
        d.rectangle([x + w // 2 - 30, y + h - 22, x + w // 2 + 30, y + h - 10], fill=(40, 160, 120))
        for (px, py, r) in ((x + w // 2 - 8, y + 22, 4), (x + w // 2 + 6, y + 16, 3),
                            (x + w // 2, y + 30, 5)):
            d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255))
    elif kind == "rocket":
        d.polygon([(x + w // 2, y + 4), (x + w // 2 + 12, y + 26),
                   (x + w // 2 + 12, y + h - 18), (x + w // 2 - 12, y + h - 18),
                   (x + w // 2 - 12, y + 26)], fill=(235, 235, 230))
        d.ellipse([x + w // 2 - 5, y + 12, x + w // 2 + 5, y + 24], fill=(60, 140, 200))
        d.polygon([(x + w // 2 - 12, y + h - 18), (x + w // 2 - 22, y + h - 6),
                   (x + w // 2 - 12, y + h - 8)], fill=(200, 60, 50))
        d.polygon([(x + w // 2 + 12, y + h - 18), (x + w // 2 + 22, y + h - 6),
                   (x + w // 2 + 12, y + h - 8)], fill=(200, 60, 50))
        d.polygon([(x + w // 2 - 5, y + h - 18), (x + w // 2 + 5, y + h - 18),
                   (x + w // 2, y + h - 2)], fill=(250, 180, 60))
    # tag chip, bottom-left
    f = Fsans(10, bold=True)
    tw = f.getlength(tag) + 12
    d.rectangle([x + 4, y + h - 20, x + 4 + tw, y + h - 4], fill=(255, 255, 255))
    d.text((x + 10, y + h - 18), tag, font=f, fill=INK)


# ---------------------------------------------------------------- map
# Equirectangular land grid: (lon, lat) of rough land cells, 5-degree step.
LAND = set()
for _lon in range(-170, 181, 5):
    for _lat in range(-55, 86, 5):
        _lon2, _lat2 = _lon, _lat
        on = False
        # North America
        if -168 <= _lon2 <= -52 and 15 <= _lat2 <= 72 and not (5 <= _lat2 <= 15 and _lon2 > -85):
            on = True
        if -60 <= _lon2 <= -52 and 5 <= _lat2 <= 15:
            on = True
        # South America
        if -80 <= _lon2 <= -35 and -55 <= _lat2 <= 10:
            on = True
        # Europe
        if -10 <= _lon2 <= 40 and 36 <= _lat2 <= 70:
            on = True
        # Africa
        if -18 <= _lon2 <= 50 and -35 <= _lat2 <= 35:
            on = True
        # Asia
        if 40 <= _lon2 <= 180 and 5 <= _lat2 <= 75:
            on = True
        if 95 <= _lon2 <= 145 and -10 <= _lat2 <= 5:
            on = True
        # Oceania
        if 112 <= _lon2 <= 154 and -40 <= _lat2 <= -10:
            on = True
        if 166 <= _lon2 <= 179 and -47 <= _lat2 <= -34:
            on = True
        if on:
            LAND.add((_lon2, _lat2))

def map_xy(mx, my, mw, mh, lon, lat):
    fx = (lon + 180.0) / 360.0
    fy = (84.0 - lat) / 144.0
    return mx + fx * mw, my + fy * mh

def draw_map(d, mx, my, mw, mh):
    vgrad(d, (mx, my, mx + mw, my + mh), NAVY, TEALDEEP)
    # graticule
    for glon in range(-150, 181, 30):
        gx, _ = map_xy(mx, my, mw, mh, glon, 0)
        d.line([(gx, my), (gx, my + mh)], fill=(255, 255, 255, 40), width=1)
    for glat in (-30, 0, 30, 60):
        _, gy = map_xy(mx, my, mw, mh, 0, glat)
        d.line([(mx, gy), (mx + mw, gy)], fill=(255, 255, 255, 40), width=1)
    # land dots
    for (lon, lat) in LAND:
        px, py = map_xy(mx, my, mw, mh, lon, lat)
        d.ellipse([px - 2.4, py - 2.4, px + 2.4, py + 2.4], fill=GOLD)
    # pins: heroes 1-3 + cards 4-13
    pins = [(h["num"], h["pin"]) for h in HEROES] + [(c["num"], c["pin"]) for c in CARDS]
    # fan-out offsets for the crowded Europe / Near-East cluster (dx, dy px)
    fan = {1: (18, 22), 2: (-24, -18), 3: (26, -26), 6: (22, -18), 8: (34, 20),
           9: (-30, 18), 10: (30, -14), 12: (-34, -20), 13: (-22, -14), 5: (24, 22)}
    for n, (lon, lat) in pins:
        px, py = map_xy(mx, my, mw, mh, lon, lat)
        dx, dy = fan.get(n, (0, 0))
        bx, by = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line([(px, py), (bx, by)], fill=(20, 20, 20), width=4)
            d.line([(px, py), (bx, by)], fill=(255, 255, 255), width=2)
            d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=(255, 255, 255))
        r = 8
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=PINRED, outline=(255, 255, 255), width=2)
        f = Fsans(8, bold=True)
        t = str(n)
        d.text((bx - f.getlength(t) / 2, by - 5), t, font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # top rule
    d.rectangle([0, 0, W, 5], fill=INK)

    # --- header line
    y = 12
    text_w(d, 8, y, "ONE DAY OF WORLD NEWS", Fsans(12, bold=True), fill=RED)
    hdr = "38 STORIES \u00b7 7 REGIONS \u00b7 20 FIELDS \u00b7 EVERY ONE FROM TUESDAY 24 NOVEMBER 2026"
    text_w(d, W - 8, y, hdr, Fsans(11, bold=True), anchor="ra")

    # --- masthead
    y = 30
    sz = fit_size("Tuesday 24 November 2026", lambda s: Fserif(s, bold=True), W - 16, 62, 40)
    f = Fserif(sz, bold=True)
    text_w(d, W // 2, y, "Tuesday 24 November 2026", f, anchor="ma")
    # --- dek
    y = 30 + sz + 8
    dek = ("China puts Shanghai's party chief under investigation \u00b7 "
           "US jury finds Huawei guilty \u00b7 War widens beyond Ukraine")
    dsz = fit_size(dek, lambda s: Fserif_it(s), W - 40, 17, 12)
    text_w(d, W // 2, y, dek, Fserif_it(dsz), fill=RED, anchor="ma")

    # --- region tabs
    y = 128
    counts = {}
    for h in HEROES:
        counts[h["region"]] = counts.get(h["region"], 0) + 1
    for c in CARDS:
        counts[c["region"]] = counts.get(c["region"], 0) + 1
    for i, (region, _, _, _) in enumerate(BRIEFS):
        counts[region] = counts.get(region, 0) + 1
    total = sum(counts.values())
    fields = set()
    for h in HEROES:
        fields.add(h["field"])
    for c in CARDS:
        fields.add(c["field"])
    for (_, f2, _, _) in BRIEFS:
        fields.add(f2)
    assert total == 38, "story total %d != 38" % total
    assert len(REGIONS) == 7
    assert len(fields) == 20, "fields %d != 20: %s" % (len(fields), sorted(fields))
    tab_w = W // 7
    for i, (name, col) in enumerate(REGIONS):
        x0 = i * tab_w
        d.rectangle([x0 + 2, y, x0 + tab_w - 2, y + 22], fill=col)
        f = Fsans(10, bold=True)
        t = "%s %d" % (name, counts.get(name, 0))
        text_w(d, x0 + tab_w // 2, y + 5, t, f, fill=(255, 255, 255), anchor="ma")

    # --- numbers strip
    y = 156
    d.rectangle([8, y, 8 + 92, y + 62], fill=INK)
    f = Fsans(10, bold=True)
    text_w(d, 54, y + 12, "THE DAY", f, fill=(255, 255, 255), anchor="ma")
    text_w(d, 54, y + 26, "IN NUMBERS", f, fill=(255, 255, 255), anchor="ma")
    text_w(d, 54, y + 42, "TUESDAY", Fsans(8), fill=(200, 200, 200), anchor="ma")
    cw = (W - 16 - 100) // 6
    for i, (place, fig, label) in enumerate(NUMBERS):
        x0 = 108 + i * cw
        if i:
            d.line([(x0 - 4, y + 4), (x0 - 4, y + 58)], fill=LINE, width=1)
        text_w(d, x0, y + 2, place, Fsans(8, bold=True), fill=GREY)
        fsz = fit_size(fig, lambda s: Fserif(s, bold=True), cw - 8, 28, 16)
        text_w(d, x0, y + 14, fig, Fserif(fsz, bold=True), fill=RED)
        draw_wrapped(d, x0, y + 44, label, Fsans(9), cw - 8, 11, max_lines=2)

    # --- heroes
    y = 226
    hw = (W - 16 - 16) // 3
    for i, h in enumerate(HEROES):
        x0 = 8 + i * (hw + 8)
        sc = {"shanghai": scene_shanghai, "court": scene_court, "ship": scene_ship}[h["scene"]]
        sc(d, x0, y, hw, 118)
        num_badge(d, x0 + 14, y + 14, h["num"], r=12)
        # place tag + pill
        yy = y + 124
        text_w(d, x0, yy, h["place"], Fsans(10, bold=True), fill=RED)
        pill(d, x0 + hw - 62, yy - 1, h["pill"])
        # headline
        yy += 16
        draw_wrapped(d, x0, yy, h["head"], Fserif(19, bold=True), hw, 21, max_lines=2)
        yy += 44
        draw_wrapped(d, x0, yy, h["summ"], Fsans(11), hw, 14, max_lines=3)
    y = 226 + 124 + 16 + 44 + 42

    # --- cards, 2 rows x 5
    cw2 = (W - 16 - 4 * 8) // 5
    ch = 114
    for row in range(2):
        for col in range(5):
            c = CARDS[row * 5 + col]
            x0 = 8 + col * (cw2 + 8)
            y0 = y + row * (ch + 8)
            card_scene(d, x0, y0, cw2, 52, c["scene"], c["tag"], c["bg"])
            num_badge(d, x0 + 13, y0 + 13, c["num"], r=10)
            yy = y0 + 56
            text_w(d, x0, yy, c["place"], Fsans(9, bold=True), fill=RED)
            pill(d, x0 + cw2 - 62, yy - 1, c["pill"])
            yy += 13
            draw_wrapped(d, x0, yy, c["head"], Fserif(13, bold=True), cw2, 15, max_lines=2)
            yy += 30
            draw_wrapped(d, x0, yy, c["summ"], Fsans(10), cw2, 12, max_lines=2)
    y = y + 2 * (ch + 8)

    # --- briefs header
    d.line([(8, y + 4), (W - 8, y + 4)], fill=INK, width=2)
    text_w(d, 8, y + 10, "ALSO ON TUESDAY 24 NOVEMBER \u2014 25 MORE, BY REGION",
           Fsans(11, bold=True))
    text_w(d, W - 8, y + 10, "Sources in brackets \u00b7 * = one side's claim",
           Fsans(9), fill=GREY, anchor="ra")
    y = y + 30

    # --- briefs (2 cols) + map
    by = y
    bw = 322
    for col in range(2):
        items = BRIEFS[col * 13:(col + 1) * 13] if col == 0 else BRIEFS[13:25]
        x0 = 8 + col * (bw + 8)
        for j, (region, _, txt, src) in enumerate(items):
            n = 14 + col * 13 + j
            yy = by + j * 19
            f = Fsans(10, bold=True)
            d.text((x0, yy), str(n), font=f, fill=INK)
            d.ellipse([x0 + 20, yy + 3, x0 + 28, yy + 11], fill=RHEX[region])
            line = "%s (%s)" % (txt, src)
            f2 = Fsans(10)
            if f2.getlength(line) > bw - 34:
                # shrink to fit one line
                sz = 10
                while sz > 8 and Fsans(sz).getlength(line) > bw - 34:
                    sz -= 1
                f2 = Fsans(sz)
                if f2.getlength(line) > bw - 34:
                    OVERFLOWS.append("brief %d too long even at 8px" % n)
            d.text((x0 + 32, yy), line, font=f2, fill=INK)
    # map
    mx, my, mw, mh = 668, by - 4, W - 8 - 668, 244
    text_w(d, mx, my, "WHERE IT HAPPENED \u00b7 PINS 1\u201313", Fsans(11, bold=True))
    draw_map(d, mx, my + 20, mw, mh - 62)
    # map legend
    ly = my + mh - 38
    lx = mx
    for name, col in REGIONS:
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=col)
        t = "%s %d" % (name, counts.get(name, 0))
        f = Fsans(8)
        d.text((lx + 11, ly - 1), t, font=f, fill=INK)
        lx += int(f.getlength(t)) + 26
        if lx > mx + mw - 90:
            lx = mx
            ly += 13
    y = by + 248

    # --- DATE CHECK
    d.rectangle([8, y, W - 8, y + 26], fill=RED)
    f = Fsans(10, bold=True)
    t = DATECHECK
    if len(wrap(t, f, W - 28)) > 2:
        OVERFLOWS.append("DATE CHECK needs >2 lines")
    draw_wrapped(d, 14, y + 3, t, f, W - 28, 12, fill=(255, 255, 255), max_lines=2)

    # --- footer
    y = y + 28
    text_w(d, W // 2, y, FOOTER, Fsans(8), fill=GREY, anchor="ma")

    if OVERFLOWS:
        print("OVERFLOWS (%d):" % len(OVERFLOWS))
        for o in OVERFLOWS:
            print("  -", o)
    else:
        print("no overflows")
    print("counts:", {k: counts[k] for k, _ in REGIONS}, "total", total, "fields", len(fields))
    img.save(OUT, optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    build()
