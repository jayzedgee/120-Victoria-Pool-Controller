# 120 Pool Controller — Design Plan

**Status:** Draft for approval · 4 November 2026
**Supersedes:** the earlier C-Bus / AC2 plan (dropped, see §1.3)

---

## 0. Summary

- A **self-contained controller at the pool equipment pad**. Home Assistant (HA) is the user interface and can request overrides such as "spa on for 90 minutes". Every safety interlock and the base filtration schedule run **on the controller**, so it keeps working safely with HA, the network or the internet down.
- **Brain:** Waveshare ESP32-S3-ETH-8DI-8RO (programmable ESP32-S3, Ethernet, 8 relays, 8 digital inputs, isolated RS485, real-time clock), running ESPHome with a custom C++ interlock component.
- **Expansion** on the brain's isolated RS485 bus (Modbus RTU):
  - 2 × Waveshare Modbus RTU Relay (D): 8 relays + 8 digital inputs each
  - 1 × Waveshare Modbus RTU Analog Input 8CH: 4–20 mA temperature transmitters
- **Capacity:** 24 relay outputs (20 used: 17 loads, a JVA supply relay and 2 top-up valves), 24 digital inputs (DIs; 8 allocated), 8 analogue inputs (AIs; all 8 used: 6 temperatures, 2 water levels).
- **Auto top-up for both pools.** Level is measured from the plant room by pressure transmitters on the filter suction pipes, read while the pumps are off (§5.9).
- **Shopping list and indicative prices:** [SHOPPING-LIST.md](SHOPPING-LIST.md).
- **Drawings:** [E-01 control interconnection](drawings/E-01-control-interconnection.svg) and [P-01 piping & instrumentation](drawings/P-01-piping-instrumentation.svg) (see [drawings/README.md](drawings/README.md)).
- **No mains through the Waveshare boards.** Their relays only switch extra-low-voltage (ELV) control circuits: the coils of the existing contactors, the gas heaters' enable loops and the 24 VAC Jandy Valve Actuators (JVAs).
- **Hardware safety backstops that don't depend on software:** the heaters' own pressure switch and high limit, a hardwired "pump running" contact in series with each heater enable, the contactors' overloads, and relay states that fail safe.

---

## 1. Scope

### 1.1 Equipment (as described)

**Indoor pool (very small)**
1. Filter pump
2. Gas heater
3. Spa jet pump
4. Blower

**Outdoor pool**
5. Filter pump
6. Cleaner booster pump
7. Gas heater (shared with the spa)
8. Solar pump
9. Swim jet 1
10. Swim jet 2
11. Feature pump
12. JVA 1
13. JVA 2
14. JVA 3

**Outdoor in-pool spa**
15. Spa filter pump (small; only used in spa mode)
16. Spa jet pump
17. Spa blower

That's 17 controlled loads.

The spa overflows into the pool when the pool filter runs. In spa mode the 3 JVAs isolate it.

**Water level (new):** auto top-up for both pools. This replaces the old leveller, whose float sensors sit in the skimmer boxes; the outdoor one has failed. Level is measured from the plant room, which is below the pools (§5.9).

### 1.2 Existing installation

- The old Jandy/Aquatech controller is being replaced. Its **contactors stay** and switch the motors. The new controller drives their coils.
- The owner will rewire the contactor coils to the new low-voltage relays.

### 1.3 Change from the previous plan

- C-Bus and the SpaceLogic Application Controller (AC2) are dropped. The controller now lives at the pad and talks to HA directly.
- **Two corrections to earlier advice:**
  1. **JVA limit switches are not feedback contacts.** The JVA's cam-operated microswitches cut its own motor at end of travel. They aren't wired out as position signals. Position confirmation is handled in §5.3.
  2. **Water temperature sensors must sit upstream of the heater**, at the heater inlet, not after it. A sensor after the heater reads heated water and would make the thermostat cut out early. Outlet sensors are still useful, but only for diagnostics (§5.5).

---

## 2. What we take from Pentair

There is no "Pentair D10". The reference is the **IntelliCenter i10D** (dual-body) plus Pentair's IntelliConnect and SolarTouch documentation.

| Pentair behaviour | Pentair default | Our default |
|---|---|---|
| Heater cool-down: pump keeps running after the heater stops | 0–10 min, default 5 min | 300 s |
| Valve delay: filter pump off while pool/spa valves rotate | 30 s | ≥ 30 s, plus JVA motion confirmation |
| Flow-dependent equipment (booster etc.) waits for the filter pump | 2 min | 120 s |
| Heater stops 5 min before the end of a filtration cycle | 5 min | 300 s before window end |
| Pressure cleaner pump paused when solar starts, to purge air from the collectors | 5 min | 300 s booster pause |
| Solar start / stop temperature difference | 6 °F / 3 °F | 3.3 °C / 1.7 °C |
| "Egg timer" auto-off for manually started circuits | per circuit | per-output maximum run times (§9) |

---

## 3. What "Waveshare Industrial" means

Waveshare is a Shenzhen maker of development boards and modules. Products it labels **"Industrial"** share these design features:

- 35 mm DIN-rail ABS enclosure
- Wide 7–36 V DC supply input
- Isolated RS485 port (isolated power plus magnetic/digital signal isolation)
- Optocouplers between the microcontroller and the relay drivers
- Transient-voltage-suppression (TVS) diodes, resettable fuses and reverse-polarity protection
- Optocoupler-isolated digital inputs that accept NPN, PNP or dry contacts

Those are the same protection practices real industrial I/O modules use. This is the correct Waveshare tier for this job, rather than their bare boards and HATs.

**What it isn't:** a certified industrial controller. Waveshare generally doesn't publish the certifications (e.g. IEC 61131-2), environmental ratings, mean-time-between-failure (MTBF) figures or long-term product support that programmable logic controller (PLC) vendors do.

**The certified alternative** is a small PLC such as the Siemens LOGO! 8, with relay expansion and a resistance temperature detector (RTD) input module. It is very robust and designed for exactly this kind of plant. The trade-offs:
- It costs several times as much.
- Logic is written in the vendor's function-block tool.
- HA integration is via Modbus TCP rather than native.

**Recommendation:** use the Waveshare Industrial line, for four reasons:
1. The life-safety backstops are in hardware (§5.2), so the controller does sequencing and convenience, not last-line protection.
2. ESPHome gives first-class, local HA integration.
3. Spares are cheap enough to keep a complete set on the shelf.
4. The interlock logic is unit-tested on a PC before it ever touches equipment (§12).

---

## 4. Hardware selection

### 4.1 Options considered

| # | Waveshare product | Relays | DIs | Programmable | Verdict |
|---|---|---|---|---|---|
| 1 | Modbus RTU Relay 32CH | 32 | 0 | No (slave) | Rejected: needs a separate master and has no DIs |
| 2 | Modbus RTU Relay 16CH | 16 | 0 | No (slave) | Rejected: 5 V supply only, no DIs |
| 3 | Modbus POE ETH Relay 16CH | 16 | 0 | No (fixed firmware: Modbus TCP/MQTT/HTTP) | Rejected: HA would become the controller, and interlocks must not live there |
| 4 | ESP32-S3-POE-ETH-8DI-8DO | 0 (8 transistor outputs) | 8 | Yes | Rejected: JVAs need 24 VAC changeover contacts and heater loops need isolated dry contacts |
| 5 | Modbus RTU IO 8CH | 0 (8 transistor outputs) | 8 | No | Rejected for the same reason |
| 6 | **ESP32-S3-ETH-8DI-8RO** | 8 | 8 | **Yes** | **Chosen as the brain** |
| 7 | **Modbus RTU Relay (D)** | 8 | 8 | No (slave) | **Chosen as expansion (×2)** |
| 8 | **Modbus RTU Analog Input 8CH** | — | — | No (slave) | **Chosen for temperatures** |

**About digital inputs and temperatures:** DIs are on/off only. They read contacts: flow switches, current switches, key switches, buttons. Temperatures are analogue and come in through the AI module over RS485. They don't use DIs.

### 4.2 Architecture

```
                    Home Assistant  (ESPHome native API over Ethernet)
                          │
┌─────────────────────────┴─────────────────────────────────────────────┐
│  BRAIN: ESP32-S3-ETH-8DI-8RO                                          │
│   • interlock engine, schedules, RTC (battery-backed)                 │
│   • 8 onboard relays  → heaters + loads that must stop if brain resets│
│   • 8 onboard DIs     → flow switches, JVA motion, service key        │
│   • isolated RS485 master ─────────────────────────────┐              │
└────────────────────────────────────────────────────────│──────────────┘
                                                         │  Modbus RTU
        ┌────────────────────────┬───────────────────────┼───────────────┐
        │                        │                       │               │
  Relay (D) addr 1         Relay (D) addr 2       Analog In 8CH addr 3   │
  "Circulation"            "Features"             6 × PT1000 → 4–20 mA   │
  filter pumps + JVAs      swim jets, feature                         120 Ω
  8 DIs (spare)            8 DIs (spare)                          termination
```

### 4.3 Why outputs are split this way

Outputs are grouped by **what should happen when something fails**.

| Group | Location | On brain reset (incl. OTA update) | On RS485 bus failure |
|---|---|---|---|
| Heaters, plus loads that must stop immediately (booster, jets, blowers, solar) | Brain onboard relays | Switched off at boot | Brain is alive and switches them off at once |
| Filter pumps | Module 1, "long deadman" | Keep running up to 360 s, so heater cool-down is preserved, then stop | Same |
| JVAs | Module 1: direction relays latched, supply relay powered only during a move with a hardware time limit (§5.3) | Hold position (unpowered) | Hold position (unpowered) |
| Swim jets, feature pump | Module 2, "short deadman" | Stop within 10 s | Stop within 10 s |
| Top-up solenoids | Module 2, one flash-on pulse per fill | Close when the pulse ends (≤ 15 min) | Same |

**How the deadman works:** the Modbus Relay (D) supports "flash-on". Writing a duration to register `0x0200 + channel` (units of 100 ms) switches the relay on for that time, then off. The brain keeps re-arming flash-on instead of latching the output. If the brain or the bus dies, the module drops those outputs on its own. Whether re-arming restarts the timer cleanly, without a glitch, is **Bench gate B2** (§15).

**Why this matters day to day:** an over-the-air (OTA) firmware update reboots the brain. With this split, a reboot while heating behaves like a controlled heater stop with cool-down, not like a power cut.

---

## 5. Interfacing to the existing equipment

### 5.1 Contactor coils

The coil voltage of the existing contactors/relays is **unknown** (Open question Q1).

| Coil type | What we do |
|---|---|
| 24 VAC or 24 VDC | Waveshare relay contact switches the coil supply directly. Ideal. |
| 12 VDC | Same, with a 12 VDC supply. |
| 230 VAC | This would put mains through the Waveshare relays, which we want to avoid. Two options: fit 24 V interposing relays (DIN, 24 V coil, mains contact) between controller and contactor, or replace the contactors with 24 VAC/DC-coil versions. |

- Fit a suppressor across each contactor coil: an RC snubber for AC coils, a diode for DC coils. It protects the Waveshare contacts and reduces electrical noise.
- **Keep the motor overloads.**

### 5.2 Gas heaters: enable loop and hardwired interlock

- Each heater has a remote-enable loop ("fireman's switch" or remote thermostat terminals). The controller's heater relay is a dry contact in that loop.
- **Hardwired pump-proof interlock:**
  - Put a normally-open (NO) **auxiliary contact on the filter pump contactor** in series with the controller's heater relay. The heater then physically cannot be enabled unless the pump contactor is pulled in, whatever the software does.
  - Outdoor heater: wire the aux contacts of the outdoor filter pump and the spa filter pump **in parallel**, then in series with the heater relay. This assumes spa-mode flow through the heater comes from the spa filter pump (Q3).
  - If the contactors have no aux contacts, add clip-on auxiliary blocks for that contactor family.
- **Set each heater's own thermostat to the highest temperature you'd ever accept.** Pentair's own guidance says the heater's panel setpoint must be at or above the controller's setpoint. It also acts as a backstop cap.
- **Millivolt heaters:** older standing-pilot heaters use a millivolt circuit. General-purpose power relay contacts can be unreliable at such low voltages and currents. If either heater is millivolt (Q2), use a relay with gold-flash contacts, or reuse the old controller's heater relay, driven by our channel.
- **Never bypass the heater's internal pressure/flow switch or high limit.**

### 5.3 JVAs

**Wiring.** The JVA is 24 VAC, about 0.75 A, with 3 wires:
- black: common
- red and white: one for each direction

Applying 24 VAC to one leg drives the actuator that way until its internal cam microswitch opens. **That microswitch is the only thing that stops the motor.** If its contacts are dirty or welded and don't open, the actuator keeps turning indefinitely. Old controllers leave 24 VAC applied permanently, so nothing notices. (This has happened here before.)

So each JVA gets a changeover relay for **direction**, and a shared relay controls **supply**:

```
24 VAC ──► JVA SUPPLY relay (1-7, NO) ──┬──► JVA1 direction relay COM ─┬─ NC ──► leg → POOL  (de-energised)
                                        │                              └─ NO ──► leg → SPA   (energised)
                                        ├──► JVA2 direction relay COM ...
                                        └──► JVA3 direction relay COM ...
JVA black (common) ──► 24 VAC return   (current switch on each JVA's common: DI5–DI7)
```

- **Power on demand.** The JVAs are only powered while a move is in progress. Each move goes like this:
  1. Set the direction relays.
  2. Pulse the supply relay with the module's **flash-on** command for `T_JVA_POWER` (default 90 s).
  3. Confirm motion started and stopped.
  4. Remove supply.

  The flash-on timer runs **on the relay module itself**, so supply is cut after `T_JVA_POWER` even if the brain crashes mid-move. A failed limit switch can therefore never spin a valve for more than that window.
- **At rest the JVAs are unpowered.** Their gearboxes hold position, as they do during a power cut today.
- **The direction relay is never switched while supply is on.** Changing direction under power would reverse a moving motor.
- **At power-up** the valves stay where they are. The brain then makes a "re-assert" move to the position the current mode requires, with pumps off. It does the same before every pool/spa transition, which also corrects a valve that was moved by hand.
- Set the JVA's own selector/toggle to the automatic position and confirm the rotation direction for each valve at commissioning.

**Position confirmation.** JVAs have no position output, so this design detects **motion** instead:
- Put an AC current switch (current-transformer type, NO output) on each JVA's common wire, wired to a DI.
- The current is about 0.75 A, so loop the wire 2–3 turns through the sensor to get above the trip point reliably.
- Logic for each move, per actuator:
  - **No start:** motion must start within 5 s, otherwise fault. Causes: actuator switched off or unplugged, toggle wrong, dirty contact in the motor path. A re-assert move to a position the valve is already at legitimately shows no motion, so that case is logged, not faulted.
  - **No stop (runaway):** motion must stop within `T_JVA_MAX`, otherwise fault. Causes: limit switch not opening, or valve jammed. The brain cuts supply at once; the module's flash-on window is the hardware backstop.
  - **Bounce:** current reappears after the stop within the same move. Logged as a "limit-contact bounce" event, which is an early sign of dirty contacts.
  - **Trend:** each move's travel time (current on → current off) is published to HA. An alert fires if it exceeds the actuator's commissioned baseline by 30 %. Dirty contacts tend to open late before they fail outright, so this can catch the problem weeks early.
  - Set `T_JVA_MAX` to about 1.5 × the measured 180° travel time. That is well under one full revolution. Default 90 s until measured.
- **After a runaway or no-stop fault:** the valve's position is unknown. It could be routing suction from the spa only, and draining the spa into the pool. All outdoor pumps stay locked out until someone inspects the valve and clears the fault in HA.
- **Fallback if current switches aren't fitted:** fixed travel time plus proof-of-flow on the spa filter circuit. The supply time limit still prevents endless spinning, but nothing can detect that it happened, or that an actuator never moved.

### 5.4 Flow switches

Recommended, three of them:
- outdoor filter
- indoor filter
- spa filter

A paddle/reed flow switch screwed into a tee, dry contact to a DI. The Hayward GLX-FLO style made for salt chlorinators is cheap and proven. Buy genuine parts; reviews of some knock-offs report unreliable contacts.

What they add on top of the heater's own pressure switch:
- proof of flow before the heater is enabled, and loss of flow while it's running
- detection of a pump that has lost prime or has a blocked basket, so it can be stopped before it runs dry
- confirmation that a pool/spa transition actually produced flow

They're not strictly mandatory, because the heater protects itself. They're the cheapest robustness upgrade in this design.

### 5.5 Temperature sensors

**Chosen approach:** 3-wire PT1000 probes (platinum resistance sensors, 1000 Ω at 0 °C) in thermowells, wired to DIN-rail PT1000→4–20 mA transmitters, wired to the Waveshare Analog Input 8CH (current version).
- 3-wire wiring cancels cable resistance, which matters for the long run to the roof.
- 4–20 mA is immune to cable length and noise.
- A broken wire or failed sensor shows up as a current outside 3.8–20.5 mA. That's flagged as a sensor fault, and the heater fails to "no heat".
- The module is 12-bit with ≤ 0.3 % accuracy. Over a 0–50 °C span that is ≈ 0.015 °C resolution. Overall accuracy is about ±0.5 °C, dominated by the probe class. That's fine for pool control.

| Ch | Sensor | Location | Transmitter range |
|---|---|---|---|
| AI1 | Indoor water | Indoor heater **inlet** (after filter, before heater) | 0–50 °C |
| AI2 | Indoor heater outlet | After indoor heater (diagnostic ΔT) | 0–100 °C |
| AI3 | Outdoor water | Outdoor heater **inlet**, on the path common to pool-mode and spa-mode flow (Q3) | 0–50 °C |
| AI4 | Outdoor heater outlet | After outdoor heater (diagnostic ΔT) | 0–100 °C |
| AI5 | Solar collector | At the collector outlet/top header on the roof, in the sun | −20…+120 °C |
| AI6 | Air | Shaded, outdoors | −20…+60 °C |
| AI7 | Outdoor pool level | Gauge pressure transmitter on the outdoor pool suction pipe, before the JVAs (§5.9) | 0–40 kPa |
| AI8 | Indoor pool level | Gauge pressure transmitter on the indoor filter suction pipe (§5.9) | 0–40 kPa, if the head is under ≈ 3.8 m |

That's 6 temperatures plus 2 levels: all 8 channels used.

**Mounting** is as previously advised: ½" BSP stainless thermowell, 6 mm bore, 50 mm insertion, in a tee or saddle, with thermal paste and PTFE tape. Use 316 stainless if the pool uses salt chlorination. Only the **locations** change (inlet, not outlet).

**Water readings are only trusted after the pump has run for `T_PRERUN`** (120 s). With no flow, an in-pipe sensor reads plant-room temperature.

**Budget alternative:** an 8-channel DS18B20 RS485 Modbus module (unbranded, ≈ AU$40–60) with DS18B20 probes in the same thermowells. It saves ≈ AU$230, but uses an unbranded board and gives weaker fault detection.

### 5.6 Power

- **24 VDC DIN power supply, 60 W** (e.g. Mean Well HDR-60-24). It feeds the brain, both relay modules, the AI module, the transmitter loops and the DI wetting. Total load is well under 30 W.
- **24 VAC transformer** for the JVAs and the 2 top-up solenoids. The JVAs draw 3 × 0.75 A × 24 V = 54 VA while moving, plus the solenoids (check their rating, typically under 10 VA each), so use ≥ 100 VA. Reuse the old controller's if it is adequate. Fuse the secondary.
- A separate ELV supply for the contactor coils if their voltage differs (§5.1).
- Fit the RTC backup cell on the brain, so schedules survive a power cut without the network.

### 5.7 Enclosure and environment

- IP65 or better enclosure, with ELV wiring segregated from mains.
- Pool plant rooms have chlorine-laden air that corrodes copper and PCBs. Keep chemicals away from the enclosure, use sealed glands, consider a desiccant and conformal-coated spares.
- Leave room on the DIN rail for spares and labelling.

### 5.8 Compliance

- Mains work, contactor rewiring and any mains coil circuits must be done by a licensed electrician to AS/NZS 3000. That includes pool-zone requirements and RCD (residual current device) protection.
- Every pump needs a local mains isolator. The software "service lockout" (§7.1) is **not** a substitute for electrical isolation.
- Mains-water top-up (§5.9) must keep a compliant backflow arrangement to AS/NZS 3500: an air gap, or a backflow prevention device. Any change to it is licensed-plumber work.

### 5.9 Water level and auto top-up (both pools)

**Existing setup.** The old leveller used float sensors inside the skimmer boxes. The outdoor one has failed and is awkward to replace. There are no dedicated level lines to the plant room. So the new design measures level on the **existing suction pipework**, with nothing to service in the skimmers. The old floats can be removed or left disconnected.

**How we measure from the plant room: hydrostatic pressure, with the pump off.** The plant room is below the pools; it's ≈ 3 m from the outdoor pool's water line to the basement floor. When a filter pump has stopped, its suction pipe (skimmer and main drain) is a still column of water connected to the pool. A **gauge pressure transmitter** tapped into that pipe measures:

```
P = ρ · g · h      ρ ≈ 996 kg/m³ (pool water at ~28 °C), g = 9.81 m/s²
1 mm of level change → ≈ 9.8 Pa
```

Here h is the height of the pool surface above the transmitter's sensing point. A gauge (vented) transmitter references the local atmosphere. Weather changes in barometric pressure act on the pool surface and on the sensor equally, so they cancel.

```
   pool surface ─────────────────────── ▲
   skimmer / main drain                 │ h ≈ 2–3 m outdoor (surface to transmitter)
   │ suction pipe (still water          │
   │ whenever the filter pump is off)   │
   └────────┬──────── plant room ───────▼
      ball valve ─ tee ─ bleed valve      ← on the pool side of any check valve,
                    │                        and (outdoor) before the JVAs
            gauge pressure transmitter (4–20 mA → AI7 / AI8)
```

**When readings are valid:**
- Only when that pool's filter pump has been off ≥ `T_LEVEL_SETTLE` (120 s).
- For the outdoor pool, also not while the JVAs are moving.

While the pump runs the pipe is under suction, below atmospheric pressure. Those readings are ignored rather than treated as a sensor fault. **Top-up therefore only happens in pump-off periods.**

**Where to tap:**
- **Outdoor:** on the pool-only suction pipe, **before** the JVAs. In spa mode the outdoor filter pump is off and the spa runs on its own filter, so this pipe still sits static against the pool. Level readings and top-ups can therefore also happen during spa sessions.
- **Indoor:** on the indoor filter pump's suction pipe.
- On the **pool side of any check valve**.
- Any isolation valves between the pool and the tap must stay open. Label them.
- Not on a pipe that another running pump draws through.
- Fit a ball valve and a bleed valve at the tee, so the transmitter can be isolated, purged of air and swapped. A flooded suction line below pool level stays full once bled.

**Transmitter choice:**
- **Type:** gauge (relative), 4–20 mA 2-wire, stainless wetted parts, ¼" or ½" BSP.
- **Range 0–40 kPa (0–0.4 bar),** good for up to ≈ 4.1 m of head. That fits the outdoor pool's ≈ 3 m with margin. Use the same range for the indoor pool if its head is under ≈ 3.8 m, so the two units are interchangeable.
- **Must be vacuum-resistant** (rated to −1 bar), because the pipe goes below atmospheric when the pump runs. Overpressure rating ≥ 2 × range, for the water-hammer spike when a pump stops.
- **Accuracy:** aim for ≤ 0.25 % of span, with a stated temperature error. The offset is calibrated out at commissioning, so what matters is repeatability and drift. At 0–40 kPa the AI module resolves about 12 Pa ≈ 1.2 mm.
- A seasonal temperature swing in the plant room can shift the reading by a few millimetres. Bench gate B6 measures this, and HA has a "set current level as target" button for re-zeroing.

**Do you need the exact head?** No. Knowing it to ±0.5 m is enough to choose the range. Once installed, the transmitter measures the head itself, and the target is set by calibrating against the normal water line. A tape measure from the coping down to the basement is enough for the indoor pool; no hose is needed.

**Other details:**
- Water density varies by ≈ 0.25 % between 20 °C and 30 °C, which is ≈ 5–7 mm at 2–3 m head. Readings are compensated using that body's water temperature (AI1 / AI3).
- **Fill in bursts:** about 5 min filling, then 2 min paused with a static reading, repeat. Water flowing in through a skimmer can briefly sit a few millimetres above pool level.
- The same principle (pool level from suction-side plumbing while the pump is off) is described in a Pentair-assigned patent, US9513638.

**Top-up control (each pool):**
- **Filtering:** the level is the median of readings over 60 s, to reject waves and swimmers.
- **Start / stop:** fill when level < target − 10 mm; stop at target.
- **Hardware-timed valve:** each fill command is a **flash-on pulse** (default 15 min) on the solenoid's relay. A crashed controller or a lost bus can never leave the water running.
- **Fill must work:**
  - Level must rise ≥ 3 mm per 15 min of filling, otherwise fault: supply off, valve stuck closed or blocked.
  - Daily cap of 60 min of filling. Hitting it means a fault and an alert: possible leak, or valve not closing.
- **Stuck-open valve:** level rising > 10 mm with the valve off and no rain → alarm. Optionally fit a pulse water meter on the shared top-up supply, which confirms the valve is closed and logs litres per pool. The controller opens only one solenoid at a time, so a single meter can attribute the flow.
- **High level** (rain): level > target + 30 mm → alert. Auto pump-out is possible later.
- **Leak trend:** daily top-up volume is published to HA. A sustained rise above normal evaporation is the earliest sign of a leak.

---

## 6. I/O allocation (proposed)

### 6.1 Relay outputs: 24 available, 20 used

**Brain onboard: switched off on brain reset**

| Relay | Load | Notes |
|---|---|---|
| R1 | Outdoor heater enable | Dry contact, in series with pump aux contacts (§5.2) |
| R2 | Indoor heater enable | Dry contact, in series with pump aux contact |
| R3 | Cleaner booster pump | Contactor coil |
| R4 | Outdoor spa jet pump | Contactor coil |
| R5 | Outdoor spa blower | Contactor coil |
| R6 | Indoor spa jet pump | Contactor coil |
| R7 | Indoor blower | Contactor coil |
| R8 | Solar pump | Contactor coil |

**Module 1 (addr 1), "Circulation"**

| Relay | Load | Mode |
|---|---|---|
| 1-1 | Outdoor filter pump | Long deadman, 360 s |
| 1-2 | Indoor filter pump | Long deadman, 360 s |
| 1-3 | Spa filter pump | Long deadman, 360 s |
| 1-4 | JVA 1 direction | Latched; NC = pool, NO = spa |
| 1-5 | JVA 2 direction | Latched |
| 1-6 | JVA 3 direction | Latched |
| 1-7 | JVA 24 VAC supply | Flash-on pulse per move, `T_JVA_POWER` (§5.3) |
| 1-8 | Spare | |

**Module 2 (addr 2), "Features"**

| Relay | Load | Mode |
|---|---|---|
| 2-1 | Swim jet 1 | Short deadman, 10 s |
| 2-2 | Swim jet 2 | Short deadman, 10 s |
| 2-3 | Feature pump | Short deadman, 10 s |
| 2-4 | Outdoor pool top-up solenoid (24 VAC) | Flash-on pulse per fill (§5.9) |
| 2-5 | Indoor pool top-up solenoid (24 VAC) | Flash-on pulse per fill (§5.9) |
| 2-6 … 2-8 | Spare (3) | e.g. pool lights, chlorinator |

Count: brain 8 (R1–R8) + module 1: 7 (1-1 to 1-7) + module 2: 5 (2-1 to 2-5) = **20 used** (17 loads + JVA supply + 2 top-up valves). Spares: 1 (1-8) + 3 (2-6 to 2-8) = **4**. Total 24.

### 6.2 Digital inputs: 24 available

**Brain onboard: fast, no bus dependency**

| DI | Signal |
|---|---|
| DI1 | Outdoor filter flow switch |
| DI2 | Indoor filter flow switch |
| DI3 | Spa filter flow switch |
| DI4 | Service lockout key switch (at the pad) |
| DI5 | JVA 1 motion (current switch) |
| DI6 | JVA 2 motion |
| DI7 | JVA 3 motion |
| DI8 | Top-up water meter pulses (optional; onboard so no pulses are missed) |

**Module 1 DIs (8):** spa-side "spa on/off" button (optional), plus optional contactor aux "proof of run" contacts for the 3 filter pumps. The rest are spare.
**Module 2 DIs (8):** spare.

### 6.3 Analogue inputs: 8 available, 8 used

See §5.5 (AI1–AI6, temperatures) and §5.9 (AI7–AI8, levels). No analogue spares remain; a second Analog Input 8CH (≈ AU$40) can be added to the bus if needed.

### 6.4 RS485 bus

- 3 slaves at addresses 1, 2 and 3. Set addresses one at a time on the bench.
- 19 200 or 38 400 baud, 8N1. The faster the bus, the shorter the poll cycle.
- Shielded twisted pair, daisy-chained, 120 Ω termination at the brain (jumper) and at the last module. All modules sit on the same DIN rail, so the bus is short.
- Poll cycle about 500 ms. A module is marked **offline** after 3 consecutive failed transactions.

---

## 7. Control modes and sequences

### 7.1 Who can ask for what (priority, highest first)

1. **Lockouts:** service key switch, or a latched critical fault. Nothing starts; running loads go through a safe shutdown.
2. **Service mode** (from HA): manual control of individual outputs, with every interlock still enforced. Auto-expires after 60 min.
3. **Spa session:** from HA, the spa-side button or a scene. Has a duration and a setpoint, and expires.
4. **HA overrides:** "filter now for N min", "pause filtration for N h", "boost heat to X °C until Y".
5. **On-device schedule:** filtration windows per body, plus booster and solar windows.
6. **Off.**

The controller treats every request as a **request**. HA never switches a relay directly. Whenever a request is blocked, the controller publishes the reason (e.g. "Waiting for pump pre-run, 45 s").

### 7.2 Outdoor pool/spa state machine

```
     ┌──────┐  schedule/override  ┌──────────┐    spa request     ┌──────────┐
     │ OFF  │ ──────────────────► │   POOL   │ ─────────────────► │ TO_SPA   │
     └──────┘ ◄────────────────── │ filtering│ ◄───────────┐      └────┬─────┘
        ▲      window end         └──────────┘             │           │
        │      (via COOLDOWN)                              │           ▼
        │                                            ┌─────┴────┐ ┌──────────┐
        └────────────────────────────────────────────│ TO_POOL  │◄│   SPA    │
                    no pool demand                   └──────────┘ └──────────┘
```

**Transitions are atomic.** Once a transition starts, it completes to a stable state before any new request is evaluated. The latest request is queued.

### 7.3 Pool → spa

1. Accept the request. Reject if locked out or faulted.
2. Switch off pool-only extras: booster, solar, swim jets, feature (Q5).
3. If the outdoor heater is on: heater off, filter pump keeps running for `T_COOLDOWN` (300 s).
4. Outdoor filter pump off. Wait `T_SPINDOWN` (10 s).
5. Set JVA 1–3 direction relays to spa, then pulse the JVA supply (§5.3). Wait until **all** JVAs report motion stopped **and** at least `T_VALVE` (30 s) has passed. Remove supply. Fault if not complete by `T_JVA_MAX`.
6. Start the spa filter pump. If the flow switch hasn't made within `T_FLOW_PROVE` (60 s), fault.
7. After `T_PRERUN` (120 s) with flow proven, the heater is allowed (thermostat, §7.6).
8. Spa jets are allowed. The blower is allowed `T_BLOWER_DELAY` (30 s) after the jets start.

### 7.4 Spa → pool

Triggered by session expiry, user request or fault.

1. Blower off. Jets keep running for `T_PURGE` (15 s), then jets off.
2. Heater off. The spa filter pump keeps running for `T_COOLDOWN`.
3. Spa filter pump off. Wait `T_SPINDOWN`.
4. JVAs to pool, with the same confirmation as step 5 above.
5. If the schedule calls for filtration, start the outdoor filter pump. Otherwise go to OFF.

### 7.5 Indoor body

Single body, no valves.

- **States:** OFF, FILTER, SPA. In SPA the jets and blower are allowed, the filter keeps running and the heater targets the spa setpoint.
- The same pre-run, cool-down, blower and auto-off rules apply.
- Jets need the indoor filter pump running for ≥ `T_PRERUN`, unless the jet pump has independent suction (Q10).

### 7.6 Heating (gas, both heaters)

The heater is enabled only when **all** of these are true:
- its pump has run ≥ `T_PRERUN` and flow is proven
- the water reading is valid
- no relevant fault
- inside an allowed heating window or session
- water < setpoint − 0.5 °C

It switches off at ≥ setpoint.

- Minimum off time 180 s (anti-short-cycle).
- **Setpoint caps:** spa 40 °C, pools 35 °C. These are hard limits in firmware, and can be lowered.
- **Software over-temperature:** water ≥ cap + 1 °C, or heater outlet ≥ `T_OUTLET_MAX` (default 52 °C; set from the heater manual), means heater off plus a latched alarm.
- **"Not firing" diagnostic:** heater enabled for 10 min with flow, but outlet − inlet < 1.5 °C, raises an alert. It doesn't shut anything down. Typical causes: gas off, ignition fault, heater's own thermostat set too low.
- **Schedule end:** the heater switches off `T_COOLDOWN` before the filtration window ends, so the pump still stops on time.

### 7.7 Solar (outdoor pool; spa only if Q6 says so)

- **Start** when collector − water ≥ 3.3 °C for 2 min, water < solar target, outdoor filter pump running ≥ `T_PRERUN`, and in POOL state.
- **Stop** when collector − water < 1.7 °C, or water ≥ solar target. Minimum run 5 min.
- **When solar starts,** pause the cleaner booster for 300 s while air purges from the collectors.
- If solar is running and the target is reached, gas doesn't fire. The order of preference (solar first, gas top-up) is configurable.

### 7.8 Schedules

- Each body has up to 2 daily filtration windows, editable from HA, stored on the device and backed by the RTC.
- The booster window sits inside the pool filtration window.
- **No valid time** (no RTC, no network): run failsafe filtration of 6 h after boot, with no heating. Alert.

---

## 8. Interlock rules (enforced on the controller)

**Heaters**
- **H1:** No heater without its pump running ≥ `T_PRERUN`, flow proven and a valid water reading. (Hardware backstop: pump aux contact in series.)
- **H2:** Heater off always comes first. The pump ignores stop requests until `T_COOLDOWN` has elapsed since the heater went off.
- **H3:** A stop request while heating means: heater off, cool-down, then pump off.
- **H4:** The outdoor heater is never enabled during a valve transition.

**Valves**
- **V1:** JVAs only move with all outdoor pumps off: filter, spa filter, booster, spa jets, solar, swim jets, feature.
- **V2:** The JVAs move as a set, and the transition must be confirmed (§5.3) before any pump restarts.
- **V3:** Spa-mode equipment (spa filter, spa jets, spa blower) requires all JVAs confirmed at spa.
- **V4:** The outdoor filter pump and the spa filter pump are never on together.
- **V5:** JVAs are powered only during a move, for at most `T_JVA_POWER`, which is enforced by the relay module's own timer. Direction relays never change while supply is on.

**Flow-dependent equipment**
- **F1:** Booster, solar, swim jets and feature (if on the filter circuit) need the outdoor filter pump running ≥ `T_PRERUN`, POOL state and flow proven.
- **F2:** Indoor jets need the indoor filter pump running ≥ `T_PRERUN` (unless Q10 says the jet pump has its own suction).
- **F3:** Loss of flow means the heater goes off immediately and dependent loads go off. The pump stops after `T_NOFLOW_STOP` (180 s) if flow isn't restored.

**Blowers**
- **B1:** Blower only starts ≥ `T_BLOWER_DELAY` after the jets.
- **B2:** On shutdown the blower stops first, and the jets purge for `T_PURGE`.

**System**
- **S1:** At power-up everything is off. Spa sessions don't resume. Heaters require a fresh pre-run. Pump starts are staggered 3 s apart to limit inrush.
- **S2:** Every manually started load has a maximum run time (§9).
- **S3:** Interlocks apply in every mode, including service mode.

**Water level**
- **L1:** Top-up only with a valid level reading: that pool's filter pump off ≥ `T_LEVEL_SETTLE`, and (outdoor) JVAs not moving.
- **L2:** Each fill is one hardware-timed flash-on pulse; no latched fill output exists.
- **L3:** One top-up valve open at a time, so a shared water meter can attribute flow.
- **L4:** Fill stops and locks out on: no level rise, daily cap reached, level sensor fault, or service lockout.

---

## 9. Timing and limits (defaults, all configurable)

| Constant | Default | Purpose |
|---|---|---|
| `T_PRERUN` | 120 s | Pump run before heater/dependents, and before water readings are trusted |
| `T_COOLDOWN` | 300 s | Pump run after heater off |
| `T_VALVE` | 30 s | Minimum pumps-off time for a valve transition |
| `T_JVA_MAX` | 90 s | JVA travel fault timeout (set to ≈ 1.5 × measured 180° travel time) |
| `T_JVA_POWER` | = `T_JVA_MAX` | Hardware-timed JVA supply window per move (flash-on on relay 1-7) |
| JVA travel-time alert | baseline + 30 % | Early warning of degrading limit contacts |
| `T_SPINDOWN` | 10 s | Pump stop before valves move |
| `T_FLOW_PROVE` | 60 s | Flow must make after pump start |
| `T_NOFLOW_STOP` | 180 s | Pump stopped if flow doesn't return |
| `T_BLOWER_DELAY` | 30 s | Jets before blower |
| `T_PURGE` | 15 s | Jets after blower stops |
| Heater minimum off | 180 s | Anti-short-cycle |
| Thermostat hysteresis | 0.5 °C | |
| Solar start / stop ΔT | 3.3 / 1.7 °C | |
| Solar minimum run | 300 s | |
| Booster pause on solar start | 300 s | |
| Spa session maximum | 120 min | |
| Jets / blowers maximum | 120 min | |
| Swim jets maximum | 120 min | |
| Feature maximum | 8 h | |
| Booster maximum | 4 h/day | |
| Setpoint caps | Spa 40 °C, pools 35 °C | |
| `T_OUTLET_MAX` | 52 °C | Set from heater manual |
| Short deadman | 10 s (refreshed every 3 s) | Module 2 loads |
| Long deadman | 360 s (refreshed every 30 s) | Filter pumps |
| Module offline | 3 failed polls (≈ 2 s) | |
| `T_LEVEL_SETTLE` | 120 s | Pump off before level readings are valid |
| Level filter | 60 s median | Rejects waves and swimmers |
| Top-up start / stop | target − 10 mm / target | |
| Top-up pulse | 15 min | Hardware-timed per fill command |
| Top-up minimum rise | 3 mm per 15 min | Else "fill not working" fault |
| Top-up daily cap | 60 min | Else "possible leak / valve" fault |
| Uncommanded rise alarm | 10 mm | Level rising with valve off and no rain |
| High-level alert | target + 30 mm | |

---

## 10. Failure modes and responses

| Failure | Detection | Response |
|---|---|---|
| Brain reboot, crash or OTA update | Watchdog / boot | Onboard relays (heaters, booster, jets, blowers, solar) off. Filter pumps continue ≤ 360 s, preserving cool-down. JVAs hold. On boot the brain reads module 1's relay states and, if a pump is running, holds it for `T_COOLDOWN` before resuming. |
| Module 1 offline | Poll failures | Heaters and all dependents off immediately. Filter pumps stop when the 360 s deadman expires. JVAs hold position: they're unpowered at rest, and any move in progress is cut by the flash-on window. Alarm. |
| Module 2 offline | Poll failures | Its loads stop within 10 s (deadman). Alarm. |
| AI module offline | Poll failures | All temperatures invalid: heaters and solar off. Filtration continues. Alarm. |
| Temperature sensor fault | < 3.8 mA or > 20.5 mA, or implausible rate of change | That body's heater (or solar) off. Alarm. |
| No flow after pump start | DI not made within `T_FLOW_PROVE` | Heater and dependents blocked. Pump stopped after `T_NOFLOW_STOP`. Latched alarm. |
| Flow lost while running | DI drops | Same as above. Heater off immediately. |
| Flow switch stuck closed | Flow indicated with pump off | Heater blocked until acknowledged. Alarm. |
| JVA didn't move | No current within 5 s of a real move | Transition aborted, supply cut, outdoor pumps stay off, latched alarm. |
| JVA runaway / didn't stop (e.g. dirty limit contacts) | Current still flowing at `T_JVA_MAX` | Supply cut immediately (the flash-on window cuts it anyway if the brain is dead). Valve position unknown, so outdoor pumps are locked out until inspected and cleared. Latched alarm. |
| JVA limit contacts degrading | Travel time > baseline + 30 %, or bounce events | Alert only: clean or replace the actuator's microswitch before it fails. |
| Over-temperature | Water or outlet limit | Heater off, latched alarm. |
| Heater not firing | ΔT diagnostic | Alert only. |
| Contactor didn't pull in (if aux DIs fitted) | Aux contact vs command | Heater blocked, alarm. |
| Whole-site power cut | — | Everything stops (heaters are designed for this). On restore, JVAs stay put until the brain makes a re-assert move with pumps off. Staggered restart per schedule. |
| HA, network or internet down | API disconnect | No effect on control. Overrides run to expiry and the schedule continues. |
| Time invalid | RTC/SNTP | Failsafe filtration (§7.8). |
| Level transmitter fault | < 3.8 mA or > 20.5 mA, or a step change | No top-up for that pool. Alarm. |
| Top-up not raising level | < 3 mm rise per 15 min fill | Fill stopped and locked out. Alarm: supply off, valve stuck closed or blocked. |
| Top-up valve stuck open | Level rising with valve off (and meter flow, if fitted) | Alarm only; the controller can't close a stuck valve. Shut off the isolation valve. |
| Excessive top-up | Daily cap reached | Fill locked out. Alarm: possible leak. |
| Air at the level tap, or isolation valve shut | Level reads implausibly low, or doesn't change while filling | Alarm. Bleed at the tee; check valves are open. |
| Pump running | — | Level readings ignored (pipe under suction); not a fault. |

---

## 11. Home Assistant integration

**Transport:** ESPHome **native API**. It is encrypted, local, auto-discovered, supports custom actions and has no broker to fail. ESPHome can also publish over **MQTT** (Message Queuing Telemetry Transport) if you want the data in other systems. That's optional and doesn't replace the native API for HA.

**Entities exposed:**

| Type | Entities |
|---|---|
| Selects | Outdoor mode (Off / Auto / Pool / Spa), Indoor mode (Off / Auto / Filter / Spa) |
| Numbers | Pool, spa and indoor setpoints; solar target; spa session length; schedule window times; target water level per pool (and a "set current level as target" button) |
| Switches (requests) | Outdoor spa jets, outdoor spa blower, indoor jets, indoor blower, swim jets, feature, booster. The state shown is the **actual** output; a refused request snaps back and the reason is published. |
| Sensors | All temperatures and heater ΔT; water level relative to target (mm) for each pool; top-up minutes and litres per day; state-machine state; countdowns (cool-down, valve, pre-run, session remaining); next scheduled event |
| Binary sensors | Flow switches, JVA motion, each output (read-only), module online states, each fault |
| Text sensors | "Blocked because…", last fault |
| Buttons | Start spa session, end spa session, acknowledge/clear faults, end service mode |

**Actions for scripts and scenes:**
- `start_spa(duration_min, setpoint_c)`
- `end_spa()`
- `filter_now(body, duration_min)`
- `pause(body, duration_min)`
- `boost_heat(body, setpoint_c, until)`
- `service_mode(on)`

So a scene like "Spa night" can call `start_spa(90, 38)`. The controller sequences the valves, cool-downs and pre-runs itself and returns to the schedule when the session ends.

---

## 12. Firmware, repository and testing

**Firmware:**
- ESPHome YAML for the board: Ethernet, RS485, TCA9554 relay expander, DIs, RTC, buzzer, RGB status LED.
- An **external C++ component** that wraps a **pure C++ interlock engine** (`PoolCore`):
  - deterministic `tick(now_ms)` every 100 ms
  - inputs in, desired outputs out
  - no ESPHome or Arduino dependencies
- A small Modbus master inside the component handles the deadman refreshes, retries and offline detection. The alternative is ESPHome's `modbus_controller`; decide during build.

**Repository layout:**

```
120-pool-controller/
  README.md
  docs/
    PLAN.md                 ← this document
    SHOPPING-LIST.md        staged shopping list and prices
    drawings/               E-01 control interconnection, P-01 P&ID (+ generator scripts)
    wiring/                 terminal schedules, DIN layout, single-line (later)
    commissioning.md        interlock test checklist (later)
  firmware/
    pool-controller.yaml
    secrets.example.yaml
    components/pool_controller/   ESPHome external component
  core/                     PoolCore engine (pure C++)
  tests/                    host-side unit + scenario tests (simulated clock)
  ha/                       example dashboard, scripts, scenes
```

**Testing, in layers:**
1. **Unit and scenario tests on a PC**, with a simulated clock and I/O. For example:
   - spa request while heating (checks the cool-down)
   - flow loss mid-heat
   - module offline mid-transition
   - brain reboot during cool-down
   - JVA no-motion, JVA runaway (limit switch never opens), limit-contact bounce, travel-time drift
   - sensor open circuit
   - schedule end while heating
   - service lockout during spa
   - top-up: normal fill, no rise, daily cap, stuck-open valve, level sensor fault, suction-line fallback (pump-off readings only)
   - power-up with a stale spa request
2. **Bench hardware-in-the-loop:** real modules driving indicator lamps, a PT1000 replaced by resistors or a decade box, flow switches simulated by toggle switches.
3. **On-site commissioning:** one circuit at a time, working through a written interlock checklist.

---

## 13. Bill of materials

The itemised shopping list, with specifications, quantities, indicative prices, stockists and their contact details, is in **[SHOPPING-LIST.md](SHOPPING-LIST.md)**. Summary (AUD inc GST, indicative):

| Stage | ≈ AUD |
|---|---|
| 1 Bench kit (proves bench gates B1–B6 first) | 698 |
| 2 Installation: control and I/O 62, temperature 445, water level 304, flow and valve monitoring 450, contactor interface 147, panel 590, cable 338 | 2,335 |
| **Core total** | **≈ 3,033** |
| Conditional / optional (transformer, solenoids, water meter, spa button) | up to 330 |
| Shelf spares | 192 |

Not included: electrician, plumber, and interposing relays if the contactor coils are 230 VAC (≈ AU$300; §5.1).

The biggest price levers are the level transmitters, the temperature transmitters and the terminals:
- generic DIN terminals: −115
- the DS18B20 temperature alternative (§5.5): −230
- generic level transmitters, if they pass bench gate B6: −220

Together these bring the core total to ≈ AU$2,470. See SHOPPING-LIST.md for the details.

---

## 14. Open questions (needed before detailed design)

1. **Contactors:** coil voltage, and whether aux contacts are fitted. Photos of the old panel and of the relay/contactor labels would answer this.
2. **Heaters:** make and model of both; type of enable circuit (24 VAC, millivolt or other); minimum flow rate; any status/fault output.
3. **Spa-mode plumbing:**
   - Does the spa filter pump's flow pass through the shared heater?
   - Does it meet the heater's minimum flow?
   - Where do the pool-filter and spa-filter paths merge? This decides the AI3 location.
4. **Spa jet pump and blower:** own suction? Allowed only in spa mode?
5. **Swim jets and feature pump:** independent suction/return, or on the filter circuit? Allowed in spa mode?
6. **Solar:**
   - Pool only, or spa as well?
   - Pump only, or a diverter valve too?
   - Collector location and cable route for AI5.
7. **Pumps:** single-speed or variable-speed? Variable-speed pumps may want a speed/enable interface later.
8. **Other loads** for the spare channels: pool lights, chlorinator, anything else?
9. **JVAs:** measured travel time; toggle positions; which leg is spa for each valve.
10. **Indoor jet pump:** independent suction, or dependent on the indoor filter?
11. **Pad controls:** service key switch (recommended); spa-side button wanted?
12. **Network:** is there Ethernet at the pad?
13. **Default schedules:** filtration hours per body for summer and winter.
14. **Water level:**
    - Outdoor head: answered, ≈ 3 m from water line to basement floor.
    - Indoor pool head: rough tape measure from the water line down to the basement floor.
    - Suction pipe layout in the plant room: a spot on each pool-only suction pipe, on the pool side of any check valve (and, outdoor, before the JVAs), where a ½" tapping can go.
    - Where does the top-up water enter each pool, and what valves does it use now (voltage, condition)? Is the backflow arrangement compliant?
    - Mains water pressure at the plant room, to check the solenoid rating.

---

## 15. Phases and bench gates

| Phase | Work | Exit criteria |
|---|---|---|
| 0 Survey | Answer §14; photos; measurements | Questions closed |
| 1 Bench | Buy the Stage 1 kit (SHOPPING-LIST.md); wire with indicator lamps | **B1** brain relays off at power-up and after reset; **B2** flash-on re-arm restarts the timer with no glitch, and a single flash-on pulse reliably times out (JVA supply); **B3** Modbus read/write and DIs at chosen baud; **B4** AI reads PT1000 resistances correctly; **B5** RTC holds time; **B6** a level transmitter on a test standpipe resolves a 5 mm change repeatably, and its drift is measured across a ~10 °C ambient change |
| 2 Core | `PoolCore` engine + scenario tests | All scenarios in §12 pass |
| 3 Integration | ESPHome component, HA entities and actions, dashboard | End-to-end on bench |
| 4 Panel | DIN layout, terminal schedule, labels; electrician review | Drawings approved |
| 5 Install | Staged commissioning against the interlock checklist | Checklist signed off |
| 6 Soak | Two weeks of logging and tuning | No unexplained faults |

**If Bench gate B2 fails** (flash-on can't be re-armed cleanly), modules 1 and 2 fall back to latched outputs. The brain then switches them off explicitly when it detects a problem. On brain death those loads would hold rather than stop, which is safe for pumps but means jets could run until noticed. Alternatively, move the short-deadman loads onto the brain's onboard relays and re-balance.

---

## Sources

- Pentair IntelliCenter Quick Reference Guide (cool-down 0–10 min, default 5; valve delay 30 s): https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/automation/intellicenter/manuals---user-docs/IntelliCenter_Quick_Ref_Guide.pdf
- Pentair IntelliConnect app guide (heater off 5 min before cycle end; booster waits 2 min for filter pump; heater panel setpoint): https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/automation/intelliconnect/manuals---user-documentation/users-guide/intelliconnect-link20-app-guide.pdf
- Pentair SolarTouch guide (cleaner pump off 5 min on solar start; differentials): https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/automation/solartouch/manual/SolarTouch_Solar_Controller_System_Installation_and_Users_Guide_English.pdf
- Waveshare ESP32-S3-ETH-8DI-8RO product page: https://www.waveshare.com/esp32-s3-eth-8di-8ro.htm
- Waveshare ESP32-S3-ETH-8DI-8RO wiki: https://www.waveshare.com/wiki/ESP32-S3-ETH-8DI-8RO
- ESPHome device config for the board (TCA9554 relays, GPIO DIs, W5500, RS485 pins): https://devices.esphome.io/devices/waveshare-esp32-s3-eth-8di-8ro/
- Waveshare Modbus RTU Relay (D) wiki: https://www.waveshare.com/wiki/Modbus_RTU_Relay_(D)
- Core Electronics, Modbus RTU Relay (D) (price): https://core-electronics.com.au/industrial-modbus-rtu-8ch-relay-module-rs485.html
- Waveshare Modbus RTU Relay 32CH wiki (flash-on/off registers 0x0200/0x0400, ×100 ms): https://www.waveshare.com/wiki/Modbus_RTU_Relay_32CH
- Waveshare Modbus RTU Relay 16CH (5 V supply): https://www.waveshare.com/modbus-rtu-relay-16ch.htm
- Waveshare Modbus RTU Analog Input 8CH: https://www.waveshare.com/modbus-rtu-analog-input-8ch.htm
- Jandy JVA operation (24 VAC on one leg; cam microswitch cuts motor at end of travel): https://www.troublefreepool.com/threads/signal-for-jandy-actuator.42637/
- Jandy JVA 2444 installation data (24 VAC, 0.75 A; black common, red/white legs): https://manualmachine.com/jandy/jva2444/8436109-operating-manual
- Hayward GLX-FLO-RP flow switch: https://poolsupply4less.com/Hayward-Flow-Switch-GLX-FLO-RP-p/glx-flo-rp.htm
- US9513638B2, "Automatic pool and spa water leveler on a non-static line" (level from suction-side plumbing when the pump is off; assignee listed as Pentair): https://patents.google.com/patent/US9513638
- Core Electronics contacts: https://core-electronics.com.au/contacts
- Little Bird Electronics contacts: https://littlebirdelectronics.com.au/pages/contact
