# Shopping List — 120 Pool Controller

**Status:** indicative, 4 November 2026. Companion to [PLAN.md](PLAN.md).

**About the prices:**
- All prices are AUD, including GST.
- **Checked:** read from the linked stockist page on 4 November 2026.
- **Converted:** a Waveshare US-dollar list price, converted to AUD with an allowance for shipping and GST on import.
- **Estimate:** a planning figure; confirm before ordering.
- Prices and stock change, so check before buying.

**Buy in three stages:**
- **Stage 1** is a bench kit, to prove the risky parts (bench gates B1–B6 in PLAN §15) before spending the rest.
- **Stage 2** waits for the site survey (PLAN §14).
- **Stage 3** is shelf spares.

**Assumptions behind quantities.** Confirm these at the survey; they mostly affect cable, saddles and fittings.
- Pool pipework is 50 mm PVC.
- The new panel sits beside the old contactor panel.
- Plant-room cable runs are about 5 m each.
- The run to the solar collector on the roof is about 25 m.

---

## Stage 1 — Bench kit (buy first)

### 1A. Modules and sensors

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis | Where |
|---|---|---|---|---|---|---|---|
| 1 | Waveshare **ESP32-S3-ETH-8DI-8RO** (controller) | Standard-Ethernet version (not PoE). 8 relays, 8 DIs, isolated RS485, RTC. Check the wiki for the RTC backup cell type, and fit one if it isn't supplied. | 1 | 75.00 | 75.00 | Converted (US$43.99) | Waveshare direct; Waveshare store on AliExpress |
| 2 | Waveshare **Modbus RTU Relay (D)** | 8 relays + 8 DIs, 7–36 V supply, product code WS-26517 | 1 | 61.80 | 61.80 | Checked | Core Electronics (Little Bird $69.07) |
| 3 | Waveshare **Modbus RTU Analog Input 8CH** | The **current-input** version (0–20 / 4–20 mA) | 1 | 40.00 | 40.00 | Converted (US$24.99) | Waveshare direct |
| 4 | **Mean Well HDR-60-24** DIN power supply | 24 VDC, 2.5 A, 60 W | 1 | 45.00 | 45.00 | Estimate | Altronics M8395; RS 145-7873 |
| 5 | Isolated **USB-to-RS485 converter** | For setting module addresses and watching the bus from a laptop. Waveshare industrial isolated type. | 1 | 40.00 | 40.00 | Estimate | Core Electronics; Waveshare direct |
| 6 | **Gauge pressure transmitter** (level, first of two) | **0–40 kPa (0–0.4 bar) gauge**, 4–20 mA 2-wire, **vacuum-resistant (−1 bar)**, overpressure ≥ 2× range, stainless, ¼" or ½" BSP. Accuracy ≤ 0.25 % of span, with a stated temperature error. | 1 | 200.00 | 200.00 | Estimate (note A) | RS; industrial suppliers |
| 7 | **PT1000 probe** (first of six) | 3-wire, 6 mm × 50 mm stainless sheath, class A or B, 2–5 m lead | 1 | 15.00 | 15.00 | Estimate | Industrial suppliers |
| 8 | **PT1000 → 4–20 mA transmitter** (first of six) | DIN-rail, 3-wire PT1000 input, range 0–50 °C, loop-powered from 24 VDC | 1 | 40.00 | 40.00 | Estimate (note B) | Industrial suppliers |
| | **Subtotal 1A** | | | | **516.80** | | |

### 1B. Bench test sundries

| # | Item | Purpose | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 9 | DIN rail, 35 mm × 1 m | Bench mounting; moves into the panel later | 1 | 10.00 | 10.00 | Estimate |
| 10 | DIN terminals, RS PRO 2.5 mm² feed-through | Bench wiring; move into the panel later (60 in total with item 33) | 20 | 2.91 | 58.20 | Checked (10–40 qty price) |
| 11 | 24 V indicator LEDs | Stand-in for each relay load under test | 8 | 3.00 | 24.00 | Estimate |
| 12 | Toggle switches | Fake flow switches and other DIs | 4 | 4.00 | 16.00 | Estimate |
| 13 | 0.1 % resistors, 2 × 1000 Ω and 2 × 1100 Ω | Fake a PT1000 at 0 °C and ≈ 26 °C (gate B4) | 4 | 2.00 | 8.00 | Estimate |
| 14 | Level test rig: ≈ 1.5 m clear vinyl hose, ½" BSP adapter, scale on a board | Gate B6: resolve a 5 mm change, measure drift | 1 | 25.00 | 25.00 | Estimate |
| 15 | Hook-up wire (0.75 mm²) and bootlace ferrules | Bench wiring. Add ≈ AU$40 for a ferrule crimper if you don't have one. | lot | — | 30.00 | Estimate |
| 16 | Mains lead / IEC inlet for the bench power supply | Bench power | 1 | 10.00 | 10.00 | Estimate |
| | **Subtotal 1B** | | | | **181.20** | |

**Stage 1 total:** 516.80 + 181.20 = **AU$698.00**

---

## Stage 2 — Installation (after the site survey)

### 2A. Control and I/O

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 17 | Waveshare **Modbus RTU Relay (D)** | Second expansion module, as item 2 | 1 | 61.80 | 61.80 | Checked |
| | **Subtotal 2A** | | | | **61.80** | |

### 2B. Temperature

Six sensors: indoor heater in/out, outdoor heater in/out, solar collector, air.

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 18 | **PT1000 probes** | As item 7 (5 here + 1 from Stage 1 = 6). The solar probe needs a long lead or a joint box. | 5 | 15.00 | 75.00 | Estimate |
| 19 | **PT1000 → 4–20 mA transmitters** | As item 8. Ranges: outlets 0–100 °C, solar −20…+120 °C, air −20…+60 °C. | 5 | 40.00 | 200.00 | Estimate (note B) |
| 20 | **Thermowells** | 316 stainless, ½" BSP male, 6 mm bore, 50 mm insertion. 4 water + 1 solar; the air probe needs none. | 5 | 15.00 | 75.00 | Estimate |
| 21 | **Tapping saddles** | ½" BSP female outlet, to suit pipe size (50 mm PVC assumed) | 5 | 12.00 | 60.00 | Estimate |
| 22 | Thermal paste and PTFE tape | Probe-to-well contact; thread sealing | lot | — | 15.00 | Estimate |
| 23 | Air-sensor radiation shield | Or a shaded, vented box | 1 | 20.00 | 20.00 | Estimate |
| | **Subtotal 2B** | | | | **445.00** | |

### 2C. Water level (both pools)

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 24 | **Gauge pressure transmitter** (second) | Same model as item 6, once it has passed gate B6 | 1 | 200.00 | 200.00 | Estimate (note A) |
| 25 | Level tap fittings, per pool | ½" BSP tapping saddle (12), ½" ball valve (15), ¼" bleed/needle valve (15), nipples and adapters (10) | 2 | 52.00 | 104.00 | Estimate |
| | **Subtotal 2C** | | | | **304.00** | |

### 2D. Flow and valve monitoring

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 26 | **Flow switches** with tees | Paddle/reed type, dry contact, rated for pool water. Outdoor filter, indoor filter, spa filter. | 3 | 100.00 | 300.00 | Estimate (note C) |
| 27 | **AC current switches** (JVA motion) | Current-transformer type, normally-open output, adjustable trip down to ≈ 0.2 A, works on 24 VAC. Loop the JVA common wire 2–3 turns through it. | 3 | 50.00 | 150.00 | Estimate |
| | **Subtotal 2D** | | | | **450.00** | |

### 2E. Contactor interface

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 28 | **Auxiliary contact blocks** | To suit the existing contactor make (survey Q1). On the outdoor filter, spa filter and indoor filter contactors; they form the hardwired heater interlock. | 3 | 25.00 | 75.00 | Estimate |
| 29 | **Coil suppressors** | RC snubbers for AC coils, one per contactor. Use diodes (≈ AU$0.50 each) if the coils are DC. | 12 | 6.00 | 72.00 | Estimate |
| | **Subtotal 2E** | | | | **147.00** | |

### 2F. Panel (enclosure and hardware)

| # | Item | What to look for | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 30 | **Enclosure** | IP66 powder-coated steel, 600 × 400 × 200 mm, mounting plate and gland plate included (Switches Plus FT604020). For polycarbonate, see note D. | 1 | 223.37 | 223.37 | Checked |
| 31 | DIN rail, 35 mm | Plus the 1 m from Stage 1 | 2 m | 10.00 | 20.00 | Estimate |
| 32 | Slotted cable duct, 40 × 40 mm | | 2 m | 12.00 | 24.00 | Estimate |
| 33 | DIN terminals, RS PRO 2.5 mm² | With the 20 from Stage 1: 60 in total, about 57 field and power terminations plus 10 % spare | 40 | 2.91 | 116.40 | Checked |
| 34 | End plates, end stops, jumper bars | | lot | — | 30.00 | Estimate |
| 35 | Earth terminals | | 3 | 5.00 | 15.00 | Estimate |
| 36 | Fuse terminals with fuses | One each for: 24 VDC controller and modules; 24 VDC sensor loops; 24 VAC JVAs; 24 VAC solenoids; contactor coil supply; spare | 6 | 6.00 | 36.00 | Estimate |
| 37 | 2-pole MCB for the panel's mains feed | The electrician may supply this | 1 | 20.00 | 20.00 | Estimate |
| 38 | IP68 cable glands, M20/M25 assorted | | 20 | 1.50 | 30.00 | Estimate |
| 39 | **Service key switch** | 22 mm, keyed, 2-position, NO contact (DI4) | 1 | 30.00 | 30.00 | Estimate |
| 40 | Labels, wire markers, cable ties | | lot | — | 30.00 | Estimate |
| 41 | Enclosure breather / desiccant | Against chlorine-laden plant-room air | 1 | 15.00 | 15.00 | Estimate |
| | **Subtotal 2F** | | | | **589.77** | |

### 2G. Cable

| # | Item | Run | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 42 | 3-core 0.5 mm² screened instrument cable (PT1000) | 5 probes × 5 m + 25 m to the roof | 50 m | 3.00/m | 150.00 | Estimate (note E) |
| 43 | Same cable, for the level transmitters | 2 × 5 m | 10 m | 3.00/m | 30.00 | Estimate |
| 44 | 2-core screened (flow switches) | 3 × 5 m | 15 m | 1.50/m | 22.50 | Estimate |
| 45 | 12-core 0.75 mm² control cable | To the contactor coils | 5 m | 8.00/m | 40.00 | Estimate |
| 46 | 3-core 0.75 mm² (JVA extensions, if the existing leads don't reach) | 3 × 5 m | 15 m | 2.00/m | 30.00 | Estimate |
| 47 | 2-core 0.75 mm² (top-up solenoids) | 2 × 5 m | 10 m | 1.50/m | 15.00 | Estimate |
| 48 | Panel hook-up wire, 0.75 mm², 4 colours | | lot | — | 40.00 | Estimate |
| 49 | Cat6 patch lead to the network | | 1 | 10.00 | 10.00 | Estimate |
| | **Subtotal 2G** | | | | **337.50** | |

### Stage 2 summary

| Group | ≈ AUD |
|---|---|
| 2A Control and I/O | 61.80 |
| 2B Temperature | 445.00 |
| 2C Water level | 304.00 |
| 2D Flow and valve monitoring | 450.00 |
| 2E Contactor interface | 147.00 |
| 2F Panel | 589.77 |
| 2G Cable | 337.50 |
| **Stage 2 total** | **2,335.07** |

Items 21, 25, 37 and parts of 2G may already be in the plumber's or electrician's quotes. Check, so they aren't paid for twice.

---

## Whole project by subsystem (Stages 1 + 2)

| Subsystem | Items | ≈ AUD |
|---|---|---|
| Controller and I/O modules | 1, 2, 3, 4, 5, 17 | 323.60 |
| Temperature (6 sensors) | 7, 8, 18–23 | 500.00 |
| Water level (2 pools) | 6, 24, 25 | 504.00 |
| Flow and valve monitoring | 26, 27 | 450.00 |
| Contactor interface | 28, 29 | 147.00 |
| Panel | 30–41 | 589.77 |
| Cable | 42–49 | 337.50 |
| Bench test sundries | 9–16 | 181.20 |
| **Core total** | | **3,033.07** |

Check: 323.60 + 500.00 + 504.00 + 450.00 + 147.00 + 589.77 + 337.50 + 181.20 = 3,033.07, which equals Stage 1 (698.00) + Stage 2 (2,335.07).

---

## Conditional and optional items

| # | Item | When needed | Qty | ≈ Each | ≈ Total | Basis |
|---|---|---|---|---|---|---|
| 50 | 24 VAC transformer, ≥ 100 VA | If the old controller's transformer can't be reused | 1 | 60 | 60 | Estimate |
| 51 | 24 VAC top-up solenoid valves | If the existing ones are unusable. Must be rated for your mains pressure. | 2 | 65 | 130 | Estimate |
| 52 | Pulse water meter on the shared top-up supply | Optional: litres per pool, stuck-valve confirmation | 1 | 60 | 60 | Estimate |
| 53 | Spa-side button kit (air button + air switch) | Optional | 1 | 80 | 80 | Estimate |
| 54 | 24 V interposing relays | Only if the contactor coils turn out to be 230 VAC (PLAN §5.1) | ≈ 12 | 25 | ≈ 300 | Estimate |

Excluding item 54: 60 + 130 + 60 + 80 = **≈ AU$330**.

---

## Stage 3 — Shelf spares (recommended)

| Item | Qty | ≈ Total |
|---|---|---|
| ESP32-S3-ETH-8DI-8RO | 1 | 75.00 |
| Modbus RTU Relay (D) | 1 | 61.80 |
| PT1000 probe + transmitter | 1 + 1 | 55.00 |

Total: 75.00 + 61.80 + 55.00 = **≈ AU$192**

---

## Totals

| | ≈ AUD |
|---|---|
| Stage 1 Bench kit | 698 |
| Stage 2 Installation | 2,335 |
| **Core total** | **≈ 3,033** |
| Conditional / optional (excluding interposing relays) | up to 330 |
| Shelf spares | 192 |

Not included: electrician, plumber, and the interposing relays (item 54) if needed.

### Why this is ≈ AU$850 more than the previous ≈ AU$2,180

Itemising showed the earlier lump sums were too low:

| Change | ≈ AUD |
|---|---|
| Panel: the enclosure alone is AU$223; terminals at the checked RS PRO price; fuses, MCB, duct, glands and breather added | +310 |
| Cable: priced per metre, including the 25 m roof run | +238 |
| Bench sundries: itemised | +101 |
| Temperature: pipe saddles, thermal paste and air-sensor shield added | +95 |
| Contactor interface: itemised | +67 |
| Water level: tap fittings itemised | +44 |
| **Total** | **+855** |

### Ways to bring it down

| Lever | ≈ Saving |
|---|---|
| Generic DIN terminals (≈ AU$1 each instead of AU$2.91, × 60) | −115 |
| DS18B20 temperature path instead of PT1000 + transmitters (note B) | −230 |
| Generic level transmitters (≈ AU$90 instead of AU$200, × 2) — only if they pass gate B6 | −220 |
| **All three** | **≈ −565, giving ≈ AU$2,470** |

---

## Notes on choices that move the price

**A. Level transmitters.** Prices vary enormously for the same job:
- Generic stainless 4–20 mA gauge transmitters: about AU$60–120 (estimate).
- WIKA A-10 at RS: AU$267.11 (checked, though that listing is a 0–40 bar unit; confirm a 0–0.4 bar gauge version exists). WIKA quotes it at ±0.5 % of span (best-fit straight line), < 0.25 % by limit-point calibration.
- SICK PFT 0–0.4 bar gauge at Schnap: AU$1,133.60 (checked).

A premium unit isn't needed. The offset is calibrated out, so repeatability and temperature drift are what count. Buy one for the bench, pass gate B6 (5 mm repeatable, drift measured over ~10 °C), then buy a second of the same model.

**B. Temperature transmitters.** Branded DIN-rail PT1000 transmitters cost far more than generic ones. For example, the LKMelectronic LKM223 at RS is AU$256.34 each (checked), which would add ≈ AU$1,300 for six. Generic units at ≈ AU$40 are the planning figure; gate B4 checks their accuracy. Cheaper alternatives:
- **DS18B20 path:** an 8-channel DS18B20 RS485 Modbus module (≈ AU$50) plus 6 stainless DS18B20 probes (≈ AU$8 each), in the same thermowells. That's ≈ AU$98 instead of 6 × (15 + 40) = AU$330, a saving of ≈ AU$230. It also frees 6 analogue channels.
- **RTD Modbus module:** an 8-channel PT100 RS485 Modbus module (e.g. eletechsup PTA8D08, or the Ebyte ME31 8-way PT100) with 3-wire PT100 probes. It removes the separate transmitters, but one listing quotes only "1 %" module accuracy, so bench-test it first.

**C. Flow switches.** Genuine Hayward GLX-FLO-RP switches sell for about US$95–190 overseas. Unbranded copies are much cheaper, but some reviews report unreliable contacts. Budget for a reputable part.

**D. Enclosure material.** Powder-coated steel (item 30, AU$223.37 with plate) is fine if the plant room is dry, chemicals are stored elsewhere and the enclosure is sealed with a breather. Polycarbonate resists chlorine corrosion better, but costs more and comes without a mounting plate:
- RS PRO 500 × 400 × 200 mm: AU$344.36 (checked)
- Fibox ARCA 600 × 400 × 210 mm: AU$619.70 at Schnap (checked)

**E. Cable.** AU$3/m is a retail by-the-metre estimate. 3-core 0.5 mm² screened instrument cable is cheaper per metre on a trade drum (Schnap sells Eltech ELT7303 in 100 m increments, about AU$1.80/m), but you'd be buying 100 m. Your electrician may have offcuts.

---

## Where to buy (Australian stockists)

| Stockist | For | Phone | Email | Address / notes |
|---|---|---|---|---|
| **Core Electronics** | Waveshare modules, USB-RS485 converter | (02) 4058 2818 | Via the forms at core-electronics.com.au/contacts | 40 Aruma Place, Cardiff NSW 2285 |
| **Little Bird Electronics** | Waveshare modules | Not listed (Mon–Fri 9–5 AEST) | hello@littlebird.com.au · support@littlebird.com.au | Online only |
| **RS Components Australia** | Mean Well power supply, transmitters, terminals, panel hardware | 1300 656 636 (Mon–Fri 8–5 AEST) | Via the contact form at au.rs-online.com | Online, trade |
| **Altronics** | Mean Well power supply (M8395), LEDs, switches, wire | Auburn NSW store (02) 8748 5388 | Not listed | Stores and online |
| **Switches Plus** | Steel enclosure (item 30) | — | Via switchesplus.com.au | Online |
| **Schnap Electric Products** | Polycarbonate enclosures, instrument cable | — | Via schnap.com.au | Online, trade |
| **Waveshare** (direct) | ESP32 controller, AI module | — | Via waveshare.com | Ships from China; allow for shipping and GST |
| Local pool / plumbing supplier | Saddles, valves, thermowells, flow switches, solenoids | — | — | Fitted by a licensed plumber |

---

## Sources for checked prices

- Modbus RTU Relay (D), Core Electronics (AU$61.80): https://core-electronics.com.au/industrial-modbus-rtu-8ch-relay-module-rs485.html
- Modbus RTU Relay (D), Little Bird (AU$69.07): https://littlebirdelectronics.com.au/products/industrial-modbus-rtu-8-channel-relay-module-d-with-digital-input-and-rs485-interface
- ESP32-S3-ETH-8DI-8RO, Waveshare (US$43.99 standard / US$49.99 PoE): https://www.waveshare.com/esp32-s3-eth-8di-8ro.htm
- Modbus RTU Analog Input 8CH, Waveshare (US$24.99): https://www.waveshare.com/modbus-rtu-analog-input-8ch.htm
- Mean Well HDR-60-24, Altronics M8395: https://altronics.com.au/p/m8395-meanwell-60w-24vdc-din-rail-switchmode-power-supply-hdr-60-24
- Mean Well HDR-60-24, RS 145-7873: https://au.rs-online.com/p/din-rail-power-supplies/1457873/
- RS PRO 2.5 mm² feed-through terminal (AU$2.91 each at 10–40; ≈ AU$2.39 at 50+): https://au.rs-online.com/web/p/din-rail-terminal-blocks/9131260
- Steel IP66 enclosure 600 × 400 × 200 with plate, Switches Plus FT604020 (AU$223.37): https://switchesplus.com.au/Metal-Enclosure-600-x-400-x-200mm-IP66~1331
- RS PRO polycarbonate wall box 500 × 400 × 200 (AU$344.36): https://au.rs-online.com/web/p/wall-boxes/2773602
- Fibox ARCA 600 × 400 × 210, Schnap (AU$619.70): https://www.schnap.com.au/wall-mount-electrical-enclosure-ip66-rated-polycarbonate-nhp-arca604021.html
- Eltech ELT7303 3-core screened instrument cable, Schnap: https://www.schnap.com.au/instrumentation-cable-3-core-0-5mm-overall-screened-black-pvc-eltech-elt7303.html
- WIKA A-10, RS (AU$267.11): https://au.rs-online.com/web/p/pressure-sensors/7255945
- SICK PFT 0–0.4 bar, Schnap (AU$1,133.60): https://www.schnap.com.au/pressure-transmitter-0-to-0-4-bar-ip65-sick-6043547.html
- LKMelectronic LKM223 PT1000 transmitter, RS (AU$256.34): https://au.rs-online.com/web/p/temperature-transmitters/2740302
- eletechsup PTA8D08 8-ch PT100 Modbus module manual: https://manuals.plus/ae/1005004974414347
- Hayward GLX-FLO-RP pricing (US): https://www.sunplay.com/collections/hayward/products/hayward-flow-switch-glx-flo-rp
- Stockist contacts: https://core-electronics.com.au/contacts · https://littlebirdelectronics.com.au/pages/contact · https://au.rs-online.com/web/content/support/contact-us · https://www.altronics.com.au/news/altronics-direct-phone-number-update
