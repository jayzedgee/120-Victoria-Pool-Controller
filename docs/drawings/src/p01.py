"""P-01 Indicative piping & instrumentation diagram (sensor and valve locations)."""
import sys
from svgkit import SVG, COL, title_block

OUT = sys.argv[1]
W, H = 2100, 1540
s = SVG(W, H)
PIPE = 2.2


# ---------------------------------------------------------------- symbols
def pipe(pts, dash=None, col=COL["ink"], sw=PIPE):
    s.poly(pts, stroke=col, sw=sw, dash=dash)


def flow(x, y, d="r", col=COL["ink"]):
    k = 7
    tri = {
        "r": [(x - k, y - k + 2), (x - k, y + k - 2), (x + k, y)],
        "l": [(x + k, y - k + 2), (x + k, y + k - 2), (x - k, y)],
        "u": [(x - k + 2, y + k), (x + k - 2, y + k), (x, y - k)],
        "d": [(x - k + 2, y - k), (x + k - 2, y - k), (x, y + k)],
    }[d]
    s.poly(tri, stroke=col, fill=col, sw=1, closed=True)


def pump(cx, cy, tag, sub, d="r", lab="below"):
    s.circle(cx, cy, 19, sw=1.8)
    if d == "r":
        s.poly([(cx - 8, cy - 10), (cx - 8, cy + 10), (cx + 11, cy)], sw=1.4, closed=True)
    else:  # up
        s.poly([(cx - 10, cy + 8), (cx + 10, cy + 8), (cx, cy - 11)], sw=1.4, closed=True)
    if lab == "below":
        s.text(cx, cy + 36, tag, size=11, weight="bold", anchor="middle")
        s.text(cx, cy + 50, sub, size=10, anchor="middle", fill=COL["grey"])
    else:  # right
        s.text(cx + 28, cy - 2, tag, size=11, weight="bold")
        s.text(cx + 28, cy + 12, sub, size=10, fill=COL["grey"])


def blower(cx, cy, tag, sub):
    s.circle(cx, cy, 17, sw=1.6)
    s.text(cx, cy + 4, "B", size=12, weight="bold", anchor="middle")
    s.text(cx + 26, cy - 2, tag, size=11, weight="bold")
    s.text(cx + 26, cy + 12, sub, size=10, fill=COL["grey"])


def filt(cx, cy, tag, sub):
    s.rect(cx - 17, cy - 38, 34, 76, sw=1.8, fill="white", rx=8)
    for k in range(-24, 30, 12):
        s.line(cx - 13, cy + k, cx + 13, cy + k - 8, sw=0.8, stroke=COL["grey"])
    s.text(cx, cy + 56, tag, size=11, weight="bold", anchor="middle")
    s.text(cx, cy + 70, sub, size=10, anchor="middle", fill=COL["grey"])


def heater(x, y, w, h, tag, sub1, sub2):
    s.rect(x, y, w, h, sw=1.8, fill="#fff7ed")
    zz = [(x + 10, y + h / 2)]
    n = 8
    for i in range(1, n + 1):
        zz.append((x + 10 + i * (w - 20) / n, y + (12 if i % 2 else h - 12)))
    s.poly(zz, sw=1.2, stroke=COL["mains"])
    s.text(x + w / 2, y + h + 18, tag, size=11, weight="bold", anchor="middle")
    s.text(x + w / 2, y + h + 32, sub1, size=10, anchor="middle", fill=COL["grey"])
    s.text(x + w / 2, y + h + 46, sub2, size=10, anchor="middle", fill=COL["grey"])


def valve3(cx, cy, ports, act="down", tag="", sub="", dash=None):
    k, a = 13, 8
    tri = {
        "l": [(cx, cy), (cx - k, cy - a), (cx - k, cy + a)],
        "r": [(cx, cy), (cx + k, cy - a), (cx + k, cy + a)],
        "u": [(cx, cy), (cx - a, cy - k), (cx + a, cy - k)],
        "d": [(cx, cy), (cx - a, cy + k), (cx + a, cy + k)],
    }
    for p in ports:
        s.poly(tri[p], sw=1.6, fill="white", closed=True, dash=dash)
    sy = 1 if act == "down" else -1
    s.line(cx, cy, cx, cy + sy * 26, sw=1.2)
    by = cy + sy * 26 + (0 if sy > 0 else -16)
    s.rect(cx - 12, by, 24, 16, sw=1.4, fill="white")
    s.text(cx, by + 12, "M", size=10, weight="bold", anchor="middle")
    ty = by + 30 if sy > 0 else by - 20
    s.text(cx, ty, tag, size=11, weight="bold", anchor="middle", fill=COL["vac"])
    if sub:
        s.text(cx, ty + 14, sub, size=10, anchor="middle", fill=COL["grey"])


def ball(cx, cy, vertical=False):
    k, a = 9, 6
    if vertical:
        s.poly([(cx - a, cy - k), (cx + a, cy - k), (cx - a, cy + k), (cx + a, cy + k)], sw=1.4, fill="white", closed=True)
    else:
        s.poly([(cx - k, cy - a), (cx - k, cy + a), (cx + k, cy - a), (cx + k, cy + a)], sw=1.4, fill="white", closed=True)


def solenoid(cx, cy, tag, sub):
    ball(cx, cy)
    s.line(cx, cy, cx, cy - 14, sw=1.2)
    s.rect(cx - 9, cy - 28, 18, 14, sw=1.3, fill="white")
    s.text(cx, cy - 17, "S", size=10, weight="bold", anchor="middle")
    s.text(cx, cy + 22, tag, size=11, weight="bold", anchor="middle", fill=COL["vac"])
    s.text(cx, cy + 35, sub, size=10, anchor="middle", fill=COL["grey"])


def inst(cx, cy, tag, px, py, col=COL["ink"]):
    """ISA-style instrument bubble at (cx,cy), dashed lead to process point (px,py)."""
    s.line(px, py, cx, cy, sw=1.0, dash="3 2", stroke=col)
    s.circle(cx, cy, 17, sw=1.4, stroke=col)
    a, b = tag.split("-")
    s.text(cx, cy - 1, a, size=10, weight="bold", anchor="middle", fill=col)
    s.text(cx, cy + 11, b, size=10, anchor="middle", fill=col)


def pool(x, y, w, h, label, wl_off=18, wl_x=None):
    s.rect(x, y, w, h, sw=2, fill=COL["water"])
    s.line(x, y + wl_off, x + w, y + wl_off, stroke=COL["waterline"], sw=1.4)
    lx = (x + w - 6) if wl_x is None else wl_x
    s.text(lx, y + wl_off + 12, "▽ water line", size=9.5, fill=COL["waterline"], anchor="end")
    s.text(x + w / 2 - 40, y + h / 2 + 10, label, size=14, weight="bold", anchor="middle", fill=COL["waterline"])


def small(cx, cy, w, h, t):
    s.rect(cx - w / 2, cy - h / 2, w, h, sw=1.2, fill="white")
    s.text(cx, cy + 4, t, size=9.5, weight="bold", anchor="middle")


def note(x, y, t, col=COL["grey"], size=10, italic=True, anchor="start"):
    s.text(x, y, t, size=size, fill=col, italic=italic, anchor=anchor)


# ---------------------------------------------------------------- frame
s.rect(10, 10, W - 20, H - 20, sw=2)
s.text(30, 44, "120 POOL CONTROLLER — PIPING & INSTRUMENTATION DIAGRAM (INDICATIVE)", size=20, weight="bold")
s.text(30, 66, "Where each sensor, flow switch, valve actuator and top-up valve sits. Pipe routes, check valves and exact JVA functions to be confirmed at site survey (PLAN §14).", size=12, fill=COL["grey"])

# ================================================================ A. INDOOR
s.rect(25, 82, 1275, 540, sw=1.2, dash="8 4")
s.text(40, 104, "A · INDOOR POOL CIRCUIT", size=14, weight="bold")

pool(90, 170, 250, 130, "INDOOR POOL")
small(107, 187, 26, 18, "SK")
small(215, 292, 26, 14, "MD")
# skimmer + main drain suction
pipe([(94, 187), (60, 187), (60, 470), (1235, 470)])
pipe([(215, 299), (215, 470)])
flow(60, 330, "d"); flow(140, 470, "r"); flow(215, 400, "d")
# LT-2 level tap
pipe([(400, 470), (400, 520)], sw=1.4)
ball(400, 505, vertical=True)
inst(400, 560, "LT-2", 400, 520, COL["loop"])
note(424, 552, "Level tap: pool-only suction, pool side of any check valve.", COL["loop"], 10, False)
note(424, 566, "Read with P-1 off ≥ 120 s · 0–40 kPa gauge · → M3 AI8", COL["loop"], 10, False)
# equipment train
pump(560, 470, "P-1", "K1 · indoor filter")
filt(680, 470, "F-1", "filter")
flow(735, 470, "r")
inst(790, 418, "FS-2", 790, 470)
inst(890, 418, "TE-1", 890, 470, COL["loop"])
heater(950, 445, 130, 50, "HTR-2  indoor gas heater", "enable ← R2", "via K1-aux (hardwired)")
inst(1150, 418, "TE-2", 1150, 470, COL["loop"])
# return
pipe([(1235, 470), (1235, 132), (265, 132), (265, 170)])
flow(1235, 300, "u"); flow(750, 132, "l"); flow(265, 155, "d")
note(1243, 300, "return", COL["grey"], 10)
# jets loop P-2
pipe([(340, 278), (452, 278)])
pump(472, 278, "P-2", "K2 · spa jets", d="u", lab="right")
pipe([(472, 259), (472, 222), (340, 222)])
flow(400, 222, "l"); flow(400, 278, "r")
note(350, 214, "jets", COL["grey"], 10)
# blower
blower(640, 196, "B-1", "K3 · blower")
pipe([(623, 196), (340, 196)], dash="5 3", col=COL["air"], sw=1.6)
flow(560, 196, "l", COL["air"])
note(350, 190, "air", COL["air"], 10)
# top-up SV-2
note(100, 118, "Mains water via backflow device → SV-2 (relay 2-5)", COL["waterline"], 10, False)
pipe([(30, 156), (160, 156), (160, 170)], col=COL["waterline"], sw=1.6)
solenoid(75, 156, "", "")
s.text(62, 144, "SV-2", size=10.5, weight="bold", fill=COL["vac"], anchor="end")
flow(160, 165, "d", COL["waterline"])

# ================================================================ symbol legend (right of A)
LX, LY = 1320, 82
s.rect(LX, LY, 755, 540, sw=1.2)
s.text(LX + 14, LY + 22, "SYMBOLS", size=13, weight="bold")
ly = LY + 52
pump(LX + 40, ly, "", "")
s.text(LX + 75, ly + 4, "Pump (tag P-n, driven by contactor Kn)", size=10.5)
filt(LX + 40, ly + 82, "", "")
s.text(LX + 75, ly + 86, "Filter", size=10.5)
s.rect(LX + 18, ly + 140, 46, 26, sw=1.6, fill="#fff7ed")
s.text(LX + 75, ly + 157, "Gas heater (enable loop from controller)", size=10.5)
valve3(LX + 40, ly + 206, "lru", act="down")
s.text(LX + 75, ly + 210, "3-way valve with JVA actuator (M)", size=10.5)
ball(LX + 40, ly + 270)
s.text(LX + 75, ly + 274, "Ball / isolation valve", size=10.5)
solenoid(LX + 40, ly + 322, "", "")
s.text(LX + 75, ly + 318, "Solenoid valve (top-up, 24 VAC)", size=10.5)
blower(LX + 40, ly + 372, "", "")
s.text(LX + 75, ly + 376, "Air blower", size=10.5)
c2 = LX + 400
inst(c2, ly, "TE-n", c2, ly, COL["loop"])
s.text(c2 + 30, ly + 4, "TE = PT1000 temperature element (in thermowell)", size=10.5)
inst(c2, ly + 50, "LT-n", c2, ly + 50, COL["loop"])
s.text(c2 + 30, ly + 54, "LT = level transmitter (gauge pressure)", size=10.5)
inst(c2, ly + 100, "FS-n", c2, ly + 100)
s.text(c2 + 30, ly + 104, "FS = flow switch (dry contact)", size=10.5)
s.line(c2 - 20, ly + 150, c2 + 20, ly + 150, sw=PIPE)
s.text(c2 + 30, ly + 154, "Process pipe", size=10.5)
s.line(c2 - 20, ly + 180, c2 + 20, ly + 180, sw=PIPE, dash="7 4")
s.text(c2 + 30, ly + 184, "Pipe route / function to be confirmed", size=10.5)
s.line(c2 - 20, ly + 210, c2 + 20, ly + 210, sw=1.6, dash="5 3", stroke=COL["air"])
s.text(c2 + 30, ly + 214, "Air line", size=10.5)
s.line(c2 - 20, ly + 240, c2 + 20, ly + 240, sw=1.6, stroke=COL["waterline"])
s.text(c2 + 30, ly + 244, "Mains water (top-up)", size=10.5)
s.line(c2 - 20, ly + 270, c2 + 20, ly + 270, sw=1.0, dash="3 2")
s.text(c2 + 30, ly + 274, "Instrument connection", size=10.5)
flow(c2, ly + 300, "r")
s.text(c2 + 30, ly + 304, "Flow direction", size=10.5)

# elevation inset
EX, EY = c2 - 20, ly + 330
s.text(EX, EY + 6, "Level measurement (elevation)", size=11, weight="bold")
s.rect(EX, EY + 18, 150, 40, sw=1.4, fill=COL["water"])
s.line(EX, EY + 26, EX + 150, EY + 26, stroke=COL["waterline"], sw=1.2)
s.text(EX + 4, EY + 50, "pool", size=10, fill=COL["waterline"])
pipe([(EX + 120, EY + 58), (EX + 120, EY + 130), (EX + 200, EY + 130)], sw=1.6)
s.line(EX - 10, EY + 140, EX + 260, EY + 140, sw=1.2)
s.text(EX + 205, EY + 152, "basement floor", size=9.5, fill=COL["grey"])
s.circle(EX + 150, EY + 130, 6, stroke=COL["loop"], fill="white", sw=1.4)
s.text(EX + 160, EY + 122, "LT", size=9.5, weight="bold", fill=COL["loop"])
s.line(EX + 70, EY + 26, EX + 70, EY + 130, sw=1, end="arr", start="arr")
s.text(EX + 76, EY + 82, "h ≈ 3 m", size=10.5, weight="bold")
s.text(EX + 76, EY + 96, "P = ρgh", size=10, fill=COL["grey"])

# ================================================================ B. OUTDOOR
s.rect(25, 640, 2050, 700, sw=1.2, dash="8 4")
s.text(40, 662, "B · OUTDOOR POOL & IN-POOL SPA CIRCUIT", size=14, weight="bold")
s.text(390, 662, "JVA functions and the spa-filter connection are indicative — confirm at survey (PLAN §14 Q3).", size=11, fill=COL["grey"], italic=True)

pool(90, 720, 470, 170, "OUTDOOR POOL", wl_x=400)
# spa inside pool
s.rect(420, 738, 128, 102, sw=2.4, fill="#c7ddf7")
s.text(484, 800, "SPA", size=13, weight="bold", anchor="middle", fill=COL["waterline"])
s.line(420, 752, 392, 770, sw=1.4, stroke=COL["waterline"], end="arrb")
note(250, 790, "spillover (pool mode)", COL["waterline"], 10)
small(107, 737, 26, 18, "SK")
small(230, 882, 26, 14, "MD")

# pool suction main
pipe([(94, 737), (60, 737), (60, 1080), (507, 1080)])
pipe([(230, 889), (230, 1080)])
flow(60, 900, "d"); flow(150, 1080, "r"); flow(230, 990, "d")
# LT-1 tap
pipe([(380, 1080), (380, 1128)], sw=1.4)
ball(380, 1112, vertical=True)
inst(380, 1166, "LT-1", 380, 1128, COL["loop"])
note(404, 1160, "Level tap on pool-only suction, before JVA-1, pool side of any check valve.", COL["loop"], 10, False)
note(404, 1174, "Reads the pool even in spa mode · read with P-4 off ≥ 120 s · → M3 AI7", COL["loop"], 10, False)
# spa suction to JVA-1
pipe([(530, 840), (530, 1067)])
flow(530, 960, "d")
note(538, 930, "spa suction", COL["grey"], 10)
valve3(530, 1080, "lru", act="down", tag="JVA-1", sub="suction: pool / spa")
pipe([(543, 1080), (621, 1080)])
pump(640, 1080, "P-4", "K4 · outdoor filter")
pipe([(659, 1080), (1217, 1080)])
filt(760, 1080, "F-2", "filter")
inst(850, 1030, "FS-1", 850, 1080)
# booster branch
pipe([(910, 1080), (910, 1154)])
pump(910, 1173, "P-5", "K5 · booster", d="r", lab="right")
pipe([(929, 1173), (1010, 1173)])
flow(1003, 1173, "r")
note(1016, 1177, "to cleaner", COL["grey"], 10, False)
# solar branch
pipe([(980, 1080), (980, 1019)], dash="7 4")
pump(980, 1000, "P-6", "K6 · solar", d="u", lab="right")
pipe([(980, 981), (980, 940)], dash="7 4")
s.rect(970, 880, 180, 60, sw=1.6, fill="#eef2ff")
for k in range(1, 6):
    s.line(970 + k * 30, 880, 970 + k * 30, 940, sw=0.8, stroke=COL["grey"])
s.text(1060, 872, "SC-1  solar collectors (roof)", size=11, weight="bold", anchor="middle")
pipe([(1150, 910), (1180, 910), (1180, 1080)], dash="7 4")
flow(1180, 1000, "d")
inst(1218, 960, "TE-5", 1180, 960, COL["loop"])
note(1240, 990, "solar circuit indicative (Q6)", COL["grey"], 10)
# spa filter loop P-10 -> FS-3 -> JVA-3 (heater inlet select)
pipe([(548, 800), (681, 800)], dash="7 4")
pump(700, 800, "P-10", "K10 · spa filter", d="r", lab="below")
pipe([(719, 800), (1230, 800), (1230, 1067)], dash="7 4")
flow(1000, 800, "r"); flow(1230, 1020, "d")
inst(790, 752, "FS-3", 790, 800)
note(820, 792, "spa filter discharge → heater (TBC Q3)", COL["grey"], 10)
valve3(1230, 1080, "lru", act="down", tag="JVA-3", sub="heater feed: pool / spa (TBC)", dash="3 2")
# heater train
pipe([(1243, 1080), (1350, 1080)])
inst(1300, 1030, "TE-3", 1300, 1080, COL["loop"])
heater(1350, 1055, 130, 50, "HTR-1  outdoor gas heater (shared)", "enable ← R1", "via K4-aux ∥ K10-aux")
pipe([(1480, 1080), (1627, 1080)])
inst(1550, 1030, "TE-4", 1550, 1080, COL["loop"])
valve3(1640, 1080, "lru", act="down", tag="JVA-2", sub="return: pool / spa")
# returns
pipe([(1653, 1080), (1780, 1080), (1780, 690), (150, 690), (150, 720)])
pipe([(1640, 1067), (1640, 708), (500, 708), (500, 738)])
flow(1780, 900, "u"); flow(1000, 690, "l"); flow(150, 707, "d")
flow(1640, 900, "u"); flow(1000, 708, "l"); flow(500, 725, "d")
note(1772, 900, "pool returns", COL["grey"], 10, anchor="end")
note(1648, 940, "spa returns", COL["grey"], 10)
# top-up SV-1
note(100, 682, "Mains water via backflow device → SV-1 (relay 2-4)", COL["waterline"], 10, False)
pipe([(30, 708), (120, 708), (120, 720)], col=COL["waterline"], sw=1.6)
solenoid(75, 708, "", "")
s.text(62, 696, "SV-1", size=10.5, weight="bold", fill=COL["vac"], anchor="end")

# spa jets & blower (stubs)
GX, GY = 1830, 760
s.rect(GX - 20, GY - 40, 245, 230, sw=1, dash="4 3")
s.text(GX - 8, GY - 22, "Spa jets & blower", size=11, weight="bold")
pump(GX + 60, GY + 30, "P-11", "K11 · spa jets", lab="right")
pipe([(GX, GY + 30), (GX + 41, GY + 30)]); note(GX - 6, GY + 14, "from spa", COL["grey"], 9.5)
pipe([(GX + 60, GY + 11), (GX + 60, GY - 6)]); flow(GX + 60, GY - 2, "u")
blower(GX + 60, GY + 120, "B-2", "K12 · spa blower")
pipe([(GX + 60, GY + 137), (GX + 60, GY + 165)], dash="5 3", col=COL["air"], sw=1.6)
flow(GX + 60, GY + 160, "d", COL["air"])
note(GX + 70, GY + 168, "air to spa", COL["air"], 9.5)
note(GX + 70, GY - 6, "to spa jets", COL["grey"], 9.5)

# swim jets & feature (stubs)
SX, SY = 130, 1255
s.rect(SX - 50, SY - 40, 790, 110, sw=1, dash="4 3")
s.text(SX - 8, SY - 22, "Swim jets & feature (own suction / return — TBC Q5)", size=11, weight="bold")
for i, (tag, sub, dest) in enumerate([("P-7", "K7 · swim jet 1", "swim jet 1"),
                                      ("P-8", "K8 · swim jet 2", "swim jet 2"),
                                      ("P-9", "K9 · feature", "feature")]):
    x = SX + 40 + i * 250
    pipe([(x - 70, SY + 10), (x - 19, SY + 10)])
    note(x - 70, SY - 2, "from pool", COL["grey"], 9.5)
    pump(x, SY + 10, tag, sub)
    pipe([(x + 19, SY + 10), (x + 90, SY + 10)])
    flow(x + 84, SY + 10, "r")
    note(x + 96, SY + 14, dest, COL["grey"], 9.5)

# ================================================================ notes + title
NY = 1360
s.rect(25, NY, 1500, 160, sw=1.2)
s.text(37, NY + 22, "NOTES", size=12, weight="bold")
notes = [
    "1. Indicative only. Pipe sizes, check valves, isolation valves and the exact functions of JVA-1…3 are to be confirmed at survey (PLAN §14 Q3–Q6).",
    "2. TE-1 / TE-3 sit at the heater inlets and give true water temperature (valid after 120 s of flow). TE-2 / TE-4 at the outlets are for ΔT diagnostics only.",
    "3. LT-1 / LT-2 tap the pool-only suction on the pool side of any check valve, with an isolation ball valve and bleed. Readings and top-up only with that pump off ≥ 120 s.",
    "4. FS-1…3 downstream of each filter pump prove flow. Heater enable is hardwired through the filter-pump contactor aux contacts (see E-01).",
    "5. Top-up valves SV-1 / SV-2 keep a compliant air gap or backflow device (AS/NZS 3500). Electrical tags and relay channels match E-01 and PLAN §6.",
]
for i, n in enumerate(notes):
    s.text(37, NY + 46 + i * 22, n, size=10.5)

title_block(s, 1545, NY, 530, 160, [
    ("PROJECT", "120 Pool Controller", True),
    ("DRAWING", "Piping & instrumentation (indicative)", True),
    ("DWG NO.", "P-01   ·   Sheet 2 of 2", False),
    ("REVISION", "A — DRAFT, not for construction", False),
    ("DATE", "4 November 2026", False),
    ("REFERENCE", "docs/PLAN.md §5.3–§5.5, §5.9", False),
])

s.save(OUT, "P-01 Piping and instrumentation (indicative)")
print("wrote", OUT)
