"""E-01 Control system interconnection (block wiring diagram)."""
import sys
from svgkit import SVG, COL, title_block

OUT = sys.argv[1]
W, H = 2100, 1620
s = SVG(W, H)

# ---------------------------------------------------------------- geometry
PX0, PX1, PY0, PY1 = 500, 1500, 150, 1385      # panel boundary
BX0, BW = 830, 360                             # module column
BX1 = BX0 + BW
AX0, AX1 = 30, 470                             # field inputs column
CX0, CX1 = 1530, 2070                          # field outputs column
LZ0, LZ1 = 560, 790                            # panel left zone (in-panel devices)
HDR, PITCH, FIRST = 44, 22, 55


def rows_y(y0):
    return [y0 + FIRST + i * PITCH for i in range(8)]


def module(y0, tag, name, sub, left, right):
    """Draw a module box; left/right = list of (label) strings or None."""
    h = HDR + 8 * PITCH + 8
    s.rect(BX0, y0, BW, h, sw=1.6, fill="white")
    s.rect(BX0, y0, BW, HDR - 6, sw=0, fill=COL["light"])
    s.line(BX0, y0 + HDR - 6, BX1, y0 + HDR - 6, sw=0.8)
    s.text(BX0 + 10, y0 + 17, f"{tag} · {name}", size=13, weight="bold")
    s.text(BX0 + 10, y0 + 32, sub, size=10, fill=COL["grey"])
    ys = rows_y(y0)
    for i, y in enumerate(ys):
        if left and left[i] is not None:
            lab, txt = left[i]
            spare = txt == "spare"
            s.circle(BX0, y, 3, fill="white", stroke=COL["grey"] if spare else COL["ink"])
            s.text(BX0 + 10, y + 4, lab, size=10.5, weight="bold", fill=COL["grey"] if spare else COL["ink"])
            s.text(BX0 + 44, y + 4, txt, size=10.5, fill=COL["grey"] if spare else COL["ink"])
        if right and right[i] is not None:
            lab, txt = right[i]
            spare = txt == "spare"
            s.circle(BX1, y, 3, fill="white", stroke=COL["grey"] if spare else COL["ink"])
            s.text(BX1 - 10, y + 4, lab, size=10.5, weight="bold", anchor="end", fill=COL["grey"] if spare else COL["ink"])
            s.text(BX1 - 44, y + 4, txt, size=10.5, anchor="end", fill=COL["grey"] if spare else COL["ink"])
    return ys, y0 + h


def field_box(x0, x1, y, tag, desc, note="", dash=None, stroke=COL["ink"], align_right=False):
    s.rect(x0, y - 9, x1 - x0, 18, sw=1.0, dash=dash, stroke=stroke, fill="white")
    s.text(x0 + 6, y + 4, tag, size=10.5, weight="bold", fill=stroke)
    s.text(x0 + 62, y + 4, desc, size=10.5, fill=stroke)
    if note:
        s.text(x1 - 6, y + 4, note, size=9.5, anchor="end", fill=COL["grey"], italic=True)


def panel_box(x0, x1, y, tag, desc, dash=None, stroke=COL["ink"]):
    s.rect(x0, y - 9, x1 - x0, 18, sw=1.0, dash=dash, stroke=stroke, fill=COL["light"])
    s.text(x0 + 5, y + 4, tag, size=10, weight="bold", fill=stroke)
    s.text(x0 + 46, y + 4, desc, size=9.5, fill=stroke)


def terminal(x, y, col=COL["ink"]):
    s.circle(x, y, 2.6, fill="white", stroke=col, sw=1.0)


# ---------------------------------------------------------------- frame & headings
s.rect(10, 10, W - 20, H - 20, sw=2)
s.text(30, 44, "120 POOL CONTROLLER — CONTROL SYSTEM INTERCONNECTION (BLOCK WIRING DIAGRAM)", size=20, weight="bold")
s.text(30, 66, "Every relay, digital input and analogue channel from PLAN §6, wired to its field device. Indicative — confirm tags and coil voltage at site survey.", size=12, fill=COL["grey"])

s.text(AX0, 140, "FIELD INPUTS & NETWORK", size=13, weight="bold")
s.text(CX0, 140, "FIELD OUTPUTS — existing contactors & field devices", size=13, weight="bold")

# panel boundary
s.rect(PX0, PY0, PX1 - PX0, PY1 - PY0, sw=2, dash="10 5", fill=COL["panel"])
s.text(PX0 + 12, PY0 + 22, "CP-1  POOL CONTROL PANEL", size=14, weight="bold")
s.text(PX0 + 12, PY0 + 38, "IP66 enclosure · ELV section, segregated from mains", size=10.5, fill=COL["grey"])

# ---------------------------------------------------------------- network
s.rect(AX0, 175, 300, 44, sw=1.4, fill="white")
s.text(AX0 + 10, 193, "HA · Home Assistant server", size=12, weight="bold")
s.text(AX0 + 10, 210, "ESPHome native API (MQTT optional)", size=10.5, fill=COL["grey"])
s.rect(AX0, 250, 160, 30, sw=1.4, fill="white")
s.text(AX0 + 10, 270, "LAN switch", size=12, weight="bold")
s.line(AX0 + 80, 219, AX0 + 80, 250, sw=1.6)
s.poly([(AX0 + 160, 265), (850, 265), (850, 350 - 1)], sw=1.8)
s.text(560, 258, "Cat6 Ethernet", size=10.5)
terminal(PX0, 265)

# ---------------------------------------------------------------- power block
s.text(880, 168, "POWER", size=11, weight="bold", fill=COL["grey"])
s.poly([(930, 110), (930, 178)], stroke=COL["mains"], sw=1.8)
s.text(938, 118, "230 VAC supply (by electrician)", size=10.5, fill=COL["mains"])
terminal(930, PY0, COL["mains"])
s.rect(875, 178, 110, 40, sw=1.4, fill="white")
s.text(885, 195, "Q1", size=11, weight="bold")
s.text(885, 210, "2-pole MCB", size=10)
s.poly([(985, 198), (1030, 198)], stroke=COL["mains"], sw=1.6)
s.poly([(1005, 198), (1005, 258), (1030, 258)], stroke=COL["mains"], sw=1.6)
s.rect(1030, 178, 175, 40, sw=1.4, fill="white")
s.text(1040, 195, "PS1  24 VDC, 60 W", size=11, weight="bold")
s.text(1040, 210, "Mean Well HDR-60-24", size=10, fill=COL["grey"])
s.rect(1030, 238, 175, 40, sw=1.4, fill="white")
s.text(1040, 255, "TR1  24 VAC, ≥ 100 VA", size=11, weight="bold")
s.text(1040, 270, "JVAs + top-up valves", size=10, fill=COL["grey"])
# fuses
FX = 1240
fuses = [
    ("F1", "24 VDC → C1, M1, M2, M3", COL["ink"]),
    ("F2", "24 VDC → 4–20 mA loops, DI wetting", COL["ink"]),
    ("F3", "24 VAC → relay 1-7 (JVA supply)", COL["vac"]),
    ("F4", "24 VAC → relays 2-4, 2-5 (SV-1/2)", COL["vac"]),
    ("F5", "Coil supply (V TBC) → relay COMs", COL["ink"]),
    ("F6", "Spare", COL["grey"]),
]
s.rect(FX, 172, 245, 128, sw=1.2, fill="white")
for i, (t, d, c) in enumerate(fuses):
    y = 190 + i * 19
    s.text(FX + 8, y + 4, t, size=10.5, weight="bold", fill=c)
    s.text(FX + 34, y + 4, d, size=10, fill=c)
s.poly([(1205, 198), (1240, 198)], sw=1.4)
s.poly([(1205, 258), (1240, 258)], stroke=COL["vac"], sw=1.4)

# ---------------------------------------------------------------- modules
c1_left = [("DI1", "Outdoor filter flow"), ("DI2", "Indoor filter flow"), ("DI3", "Spa filter flow"),
           ("DI4", "Service key switch"), ("DI5", "JVA-1 motion"), ("DI6", "JVA-2 motion"),
           ("DI7", "JVA-3 motion"), ("DI8", "Top-up meter (opt.)")]
c1_right = [("R1", "Outdoor heater enable"), ("R2", "Indoor heater enable"), ("R3", "Booster pump"),
            ("R4", "Outdoor spa jets"), ("R5", "Outdoor spa blower"), ("R6", "Indoor spa jets"),
            ("R7", "Indoor blower"), ("R8", "Solar pump")]
m1_left = [("DI1", "Spa-side button (opt.)"), ("DI2", "K4 aux proof (opt.)"), ("DI3", "K1 aux proof (opt.)"),
           ("DI4", "K10 aux proof (opt.)"), ("DI5", "spare"), ("DI6", "spare"), ("DI7", "spare"), ("DI8", "spare")]
m1_right = [("1-1", "Outdoor filter pump"), ("1-2", "Indoor filter pump"), ("1-3", "Spa filter pump"),
            ("1-4", "JVA-1 direction"), ("1-5", "JVA-2 direction"), ("1-6", "JVA-3 direction"),
            ("1-7", "JVA 24 VAC supply"), ("1-8", "spare")]
m2_left = [("DI1–8", "spare")] + [None] * 7
m2_right = [("2-1", "Swim jet 1"), ("2-2", "Swim jet 2"), ("2-3", "Feature pump"),
            ("2-4", "Top-up valve, outdoor"), ("2-5", "Top-up valve, indoor"),
            ("2-6", "spare"), ("2-7", "spare"), ("2-8", "spare")]
m3_left = [("AI1", "Indoor heater inlet"), ("AI2", "Indoor heater outlet"), ("AI3", "Outdoor heater inlet"),
           ("AI4", "Outdoor heater outlet"), ("AI5", "Solar collector"), ("AI6", "Air"),
           ("AI7", "Outdoor pool level"), ("AI8", "Indoor pool level")]

C1Y, M1Y, M2Y, M3Y = 350, 610, 870, 1130
c1y, c1b = module(C1Y, "C1", "Controller", "Waveshare ESP32-S3-ETH-8DI-8RO · ESPHome · RTC", c1_left, c1_right)
m1y, m1b = module(M1Y, "M1", "Relay (D) · Modbus addr 1 · “Circulation”", "Waveshare Modbus RTU Relay (D) · 8 relays + 8 DIs", m1_left, m1_right)
m2y, m2b = module(M2Y, "M2", "Relay (D) · Modbus addr 2 · “Features”", "Waveshare Modbus RTU Relay (D) · 8 relays + 8 DIs", m2_left, m2_right)
m3y, m3b = module(M3Y, "M3", "Analog Input 8CH · Modbus addr 3", "Waveshare Modbus RTU Analog Input 8CH · 4–20 mA", m3_left, None)

# relay-group annotations (inside panel, right of module column)
s.text(BX1 + 14, C1Y + 18, "Onboard relays: OFF on controller reset", size=9.5, fill=COL["grey"], italic=True)
s.text(BX1 + 14, M1Y + 18, "Pumps: deadman 360 s · JVAs: latched", size=9.5, fill=COL["grey"], italic=True)
s.text(BX1 + 14, M2Y + 18, "Loads: deadman 10 s · Valves: flash-on", size=9.5, fill=COL["grey"], italic=True)

# ---------------------------------------------------------------- RS485 bus
BUSX = 1010
for (a, b) in [(c1b, M1Y), (m1b, M2Y), (m2b, M3Y)]:
    s.line(BUSX, a, BUSX, b, stroke=COL["bus"], sw=3.2)
s.text(BUSX + 10, c1b + 21, "RS485 A/B · shielded twisted pair · 38 400 8N1", size=10, fill=COL["bus"], weight="bold")
s.text(BUSX - 10, c1b + 21, "120 Ω (C1 jumper)", size=9.5, fill=COL["bus"], anchor="end")
s.line(BUSX, m3b, BUSX, m3b + 10, stroke=COL["bus"], sw=3.2)
s.rect(BUSX - 14, m3b + 10, 28, 12, stroke=COL["bus"], fill="white", sw=1.4)
s.text(BUSX + 22, m3b + 20, "120 Ω end termination", size=9.5, fill=COL["bus"])

# ---------------------------------------------------------------- outputs (right)
outs = {
    "C1": [
        ("HTR-1", "Outdoor gas heater — enable loop", "series: K4-aux ∥ K10-aux", None, COL["ink"]),
        ("HTR-2", "Indoor gas heater — enable loop", "series: K1-aux", None, COL["ink"]),
        ("K5", "Cleaner booster pump", "", None, COL["ink"]),
        ("K11", "Outdoor spa jet pump", "", None, COL["ink"]),
        ("K12", "Outdoor spa blower", "", None, COL["ink"]),
        ("K2", "Indoor spa jet pump", "", None, COL["ink"]),
        ("K3", "Indoor blower", "", None, COL["ink"]),
        ("K6", "Solar pump", "", None, COL["ink"]),
    ],
    "M1": [
        ("K4", "Outdoor filter pump", "aux → HTR-1 loop", None, COL["ink"]),
        ("K1", "Indoor filter pump", "aux → HTR-2 loop", None, COL["ink"]),
        ("K10", "Spa filter pump", "aux → HTR-1 loop", None, COL["ink"]),
        ("JVA-1", "Valve actuator 24 VAC", "NC = pool · NO = spa", None, COL["vac"]),
        ("JVA-2", "Valve actuator 24 VAC", "NC = pool · NO = spa", None, COL["vac"]),
        ("JVA-3", "Valve actuator 24 VAC", "NC = pool · NO = spa", None, COL["vac"]),
        None,
        "spare",
    ],
    "M2": [
        ("K7", "Swim jet 1 pump", "", None, COL["ink"]),
        ("K8", "Swim jet 2 pump", "", None, COL["ink"]),
        ("K9", "Feature pump", "", None, COL["ink"]),
        ("SV-1", "Top-up solenoid 24 VAC — outdoor", "≤ 15 min per pulse", None, COL["vac"]),
        ("SV-2", "Top-up solenoid 24 VAC — indoor", "≤ 15 min per pulse", None, COL["vac"]),
        "spare", "spare", "spare",
    ],
}
for key, ys in (("C1", c1y), ("M1", m1y), ("M2", m2y)):
    for y, item in zip(ys, outs[key]):
        if item is None:
            continue
        if item == "spare":
            s.line(BX1, y, BX1 + 40, y, stroke=COL["grey"], sw=1, dash="4 3")
            continue
        tag, desc, note, dash, col = item
        s.line(BX1, y, CX0, y, stroke=col, sw=1.3)
        terminal(PX1, y, col)
        field_box(CX0, CX1, y, tag, desc, note, dash=dash, stroke=col)

# JVA supply link (1-7 feeds COM of 1-4..1-6)
y17 = m1y[6]
s.line(BX1, y17, BX1 + 22, y17, stroke=COL["vac"], sw=1.6)
s.circle(BX1 + 25, y17, 3, stroke=COL["vac"], fill=COL["vac"])
s.text(BX1 + 34, y17 + 4, "→ COM of 1-4, 1-5, 1-6 (flash-on ≤ 90 s per move)", size=9.5, fill=COL["vac"])

# contactor panel bracket
s.text(CX0, 160, "K1–K12 = existing contactors (coil voltage TBC, PLAN §5.1); motors & overloads unchanged.", size=9.5, fill=COL["grey"])
s.text(CX0, 173, "Fit RC snubber (AC) or diode (DC) across each coil. Spare relays: 1-8, 2-6, 2-7, 2-8.", size=9.5, fill=COL["grey"])

# ---------------------------------------------------------------- inputs (left)
def in_line(y, x_from, col=COL["ink"], dash=None):
    s.line(x_from, y, BX0, y, stroke=col, sw=1.3, dash=dash)

# C1 DIs
c1_in = [
    ("FS-1", "Flow switch — outdoor filter", "dry contact"),
    ("FS-2", "Flow switch — indoor filter", "dry contact"),
    ("FS-3", "Flow switch — spa filter", "dry contact"),
]
for y, (tag, d, n) in zip(c1y[:3], c1_in):
    field_box(AX0, AX1, y, tag, d, n)
    in_line(y, AX1)
    terminal(PX0, y)
# S1 key switch (panel door)
panel_box(LZ0, LZ1, c1y[3], "S1", "Service key switch (door)")
in_line(c1y[3], LZ1)
# CT-1..3 in panel on JVA commons
for i, y in enumerate(c1y[4:7]):
    panel_box(LZ0, LZ1, y, f"CT-{i+1}", f"Current sw. on JVA-{i+1} common", stroke=COL["ink"])
    in_line(y, LZ1)
# DI8 water meter optional
field_box(AX0, AX1, c1y[7], "FQ-1", "Pulse water meter — top-up supply", "optional", dash="4 3")
in_line(c1y[7], AX1, dash="4 3")
terminal(PX0, c1y[7])

# M1 DIs (optional)
m1_in = [
    ("HS-1", "Spa-side spa on/off button", "optional"),
    ("K4-aux", "Outdoor filter contactor aux", "optional proof"),
    ("K1-aux", "Indoor filter contactor aux", "optional proof"),
    ("K10-aux", "Spa filter contactor aux", "optional proof"),
]
for y, (tag, d, n) in zip(m1y[:4], m1_in):
    field_box(AX0, AX1, y, tag, d, n, dash="4 3")
    in_line(y, AX1, dash="4 3")
    terminal(PX0, y)

# M3 AIs: TE -> TT (in panel) -> AI
tes = [
    ("TE-1", "PT1000 — indoor heater inlet", "0–50 °C"),
    ("TE-2", "PT1000 — indoor heater outlet", "0–100 °C"),
    ("TE-3", "PT1000 — outdoor heater inlet (pool/spa common)", "0–50 °C"),
    ("TE-4", "PT1000 — outdoor heater outlet", "0–100 °C"),
    ("TE-5", "PT1000 — solar collector (roof, ≈ 25 m)", "−20…120 °C"),
    ("TE-6", "PT1000 — air (shaded)", "−20…60 °C"),
]
for i, (y, (tag, d, n)) in enumerate(zip(m3y[:6], tes)):
    field_box(AX0, AX1, y, tag, d, n)
    s.line(AX1, y, LZ0, y, sw=1.3)               # 3-wire RTD
    terminal(PX0, y)
    panel_box(LZ0, LZ1, y, f"TT-{i+1}", "PT1000 → 4–20 mA (DIN)", stroke=COL["loop"])
    s.line(LZ1, y, BX0, y, stroke=COL["loop"], sw=1.5)
s.text(PX0 + 8, m3y[0] - 14, "3-wire RTD", size=9.5, fill=COL["grey"])
lts = [
    ("LT-1", "Level — outdoor pool suction, before JVAs", "0–40 kPa gauge"),
    ("LT-2", "Level — indoor pool suction", "0–40 kPa gauge"),
]
for y, (tag, d, n) in zip(m3y[6:], lts):
    field_box(AX0, AX1, y, tag, d, n, stroke=COL["loop"])
    s.line(AX1, y, BX0, y, stroke=COL["loop"], sw=1.5)
    terminal(PX0, y, COL["loop"])
s.text(LZ0, m3y[7] + 26, "4–20 mA loops powered from F2 (24 VDC)", size=9.5, fill=COL["loop"])

# group labels on the left
s.text(AX0, c1y[0] - 22, "Digital inputs → C1", size=10.5, weight="bold", fill=COL["grey"])
s.text(AX0, m1y[0] - 22, "Digital inputs → M1 (optional)", size=10.5, weight="bold", fill=COL["grey"])
s.text(AX0, m3y[0] - 22, "Temperature & level → M3", size=10.5, weight="bold", fill=COL["grey"])

# ---------------------------------------------------------------- legend
LY = 1410
s.rect(30, LY, 470, 175, sw=1.2)
s.text(42, LY + 22, "LEGEND", size=12, weight="bold")
leg = [
    (COL["ink"], None, 1.4, "ELV control / signal wiring"),
    (COL["bus"], None, 3.2, "RS485 bus (Modbus RTU)"),
    (COL["loop"], None, 1.6, "4–20 mA analogue loop"),
    (COL["vac"], None, 1.6, "24 VAC (JVAs, top-up solenoids)"),
    (COL["mains"], None, 1.8, "230 VAC"),
    (COL["ink"], "4 3", 1.3, "Optional / to be confirmed"),
    (COL["grey"], "4 3", 1.0, "Spare channel"),
]
for i, (c, d, w, t) in enumerate(leg):
    y = LY + 44 + i * 18
    s.line(44, y, 104, y, stroke=c, sw=w, dash=d)
    s.text(116, y + 4, t, size=10.5)
s.circle(330, LY + 44, 2.6, fill="white", sw=1)
s.text(340, LY + 48, "Panel terminal", size=10.5)
s.rect(322, LY + 56, 40, 14, sw=1, fill="white")
s.text(370, LY + 67, "Field device", size=10.5)
s.rect(322, LY + 78, 40, 14, sw=1, fill=COL["light"])
s.text(370, LY + 89, "In-panel device (shaded)", size=10.5)

# ---------------------------------------------------------------- notes
NX = 520
s.rect(NX, LY, 990, 175, sw=1.2)
s.text(NX + 12, LY + 22, "NOTES", size=12, weight="bold")
notes = [
    "1. Waveshare relays switch extra-low-voltage control circuits only: contactor coils, heater enable loops, 24 VAC JVAs and solenoids. No mains through the boards.",
    "2. Hardwired interlock: each heater enable loop passes through its filter-pump contactor aux contact(s) in series with R1 / R2, independent of software.",
    "3. Fail-safe: R1–R8 switch OFF when C1 resets. M1 pump outputs drop 360 s after C1 stops refreshing (heater cool-down preserved);",
    "    M2 loads drop within 10 s. JVA supply (1-7) and top-up valves (2-4, 2-5) are timed pulses on the module itself.",
    "4. JVA motion is sensed by CT-1…3 on each actuator's common conductor (2–3 turns). Water readings valid only with flow; level readings only with the pump off.",
    "5. Device tags (K, FS, TE, LT, SV …) are indicative. Confirm at site survey (PLAN §14). Mains work by a licensed electrician (AS/NZS 3000).",
]
for i, n in enumerate(notes):
    ind = 18 if n.startswith("    ") else 0
    s.text(NX + 12 + ind, LY + 44 + i * 21, n.strip(), size=10.5)

# ---------------------------------------------------------------- title block
title_block(s, CX0, LY, CX1 - CX0, 175, [
    ("PROJECT", "120 Pool Controller", True),
    ("DRAWING", "Control system interconnection", True),
    ("DWG NO.", "E-01   ·   Sheet 1 of 2", False),
    ("REVISION", "A — DRAFT, not for construction", False),
    ("DATE", "4 November 2026", False),
    ("REFERENCE", "docs/PLAN.md §4–§6, §5.9", False),
])

s.save(OUT, "E-01 Control system interconnection")
print("wrote", OUT)
