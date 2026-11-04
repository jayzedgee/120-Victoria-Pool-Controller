# Pool and Spa Controller — Design Review

**Review date:** 4 November 2026 (Australia/Sydney)  
**Repository:** [jayzedgee/120-Victoria-Pool-Controller](https://github.com/jayzedgee/120-Victoria-Pool-Controller)  
**Branch reviewed:** `docs/initial-plan`  
**Commit:** [`757b2f5643cf497afe240380b287e7aff2ffc311`](https://github.com/jayzedgee/120-Victoria-Pool-Controller/tree/757b2f5643cf497afe240380b287e7aff2ffc311)  
**Scope:** Review of the design; no rewrite or changes to the plan.

## Five most important findings

1. **The heater’s hardwired interlock does not prove flow.** A pulled-in contactor can coexist with a failed motor, closed valve or blocked pipe. At approximately 3 m below pool level, static pressure can also defeat a heater pressure switch; Pentair’s Australian MasterTemp manual requires a flow switch beyond 1.2 m below water level. The actual heater models must determine the protection. [S1]

2. **“Onboard relays switch off on brain reset” is not established.** They are driven by a TCA9554, whose outputs are latched and whose reset depends on its own power supply. An ESP32 crash or reset can therefore leave a heater-enable relay energised unless another circuit removes permission. [S2] [S3]

3. **JVA current sensing cannot confirm valve position.** An unplugged actuator, interrupted supply, disengaged mechanism or incorrect cam setting can resemble successful completion. The startup exception accepting “no motion” is particularly problematic: the controller can start a pump with the plumbing in an unknown configuration.

4. **Top-up has no independent means of stopping a mechanical valve failure.** Flash-on limits an electrical command; it cannot close a jammed solenoid or interrupt welded relay contacts. For unattended operation—especially the indoor pool—an alarm alone is inadequate flood protection.

5. **The level-measurement accuracy is substantially overstated.** Waveshare currently publishes **≤3% accuracy**, not the plan’s **≤0.3%**. Separately, 0.25% of a 40 kPa transmitter span equals approximately **10 mm of water**, before other errors: the proposed 3 mm fill-progress test needs much stronger validation. [S4]

## Review basis and assessment

I reviewed these files at the commit above:

- [PLAN.md](https://github.com/jayzedgee/120-Victoria-Pool-Controller/blob/757b2f5643cf497afe240380b287e7aff2ffc311/docs/PLAN.md)
- [SHOPPING-LIST.md](https://github.com/jayzedgee/120-Victoria-Pool-Controller/blob/757b2f5643cf497afe240380b287e7aff2ffc311/docs/SHOPPING-LIST.md)
- [E-01 control interconnection](https://github.com/jayzedgee/120-Victoria-Pool-Controller/blob/757b2f5643cf497afe240380b287e7aff2ffc311/docs/drawings/E-01-control-interconnection.svg)
- [P-01 piping and instrumentation](https://github.com/jayzedgee/120-Victoria-Pool-Controller/blob/757b2f5643cf497afe240380b287e7aff2ffc311/docs/drawings/P-01-piping-instrumentation.svg)

**I rendered and viewed both Revision A SVGs**, as well as checking their labels. The branch contains design documents and drawing generators, rather than implemented controller firmware.

**My assessment: a sound architectural starting point, but not ready for installation.** Several claimed safety backstops currently depend on assumptions that the design itself has not resolved.

In the table, **V** means externally verified, **J** means engineering judgement or calculation, and **U** means behaviour remains unverified. Recommendations are engineering judgement. “Critical” identifies a potentially serious failure path; it does not assert that the existing installation already has that fault. Source references link to the source list at the end.

## All findings

| # | Severity | Plan section | Issue | Concrete failure scenario | Recommended fix | Confidence |
|---|---|---|---|---|---|---|
| 1 | **Critical** | §5.2–5.4; E-01 | **V/J — Contactor auxiliary contacts are not flow proof; basement static head matters.** See finding 1 above. [S1] | Contactor pulls in but motor does not circulate water. Static head keeps the heater pressure switch satisfied. | Make manufacturer-approved flow protection independent of ESPHome. Measure heater elevation and verify protection in both pool and spa configurations. Retain auxiliary contacts as additional permissives. | High |
| 2 | **Critical** | §4.3, §10, B1; E-01 | **V/U — MCU reset does not inherently reset the relay expander.** See finding 2 above. [S2] [S3] | ESP32 hangs while heating; the TCA9554 retains the heater command. Later, the circulation deadman expires. | Add an independently enforced heater-permit timeout/watchdog, driven by successful control cycles. Test MCU-only resets, hangs, I²C failure and bootloader operation with relay power maintained. | High |
| 3 | **Major** | §4.3, §9, §15 | **V/U — Flash-on exists, but uninterrupted retriggering remains unverified.** The Relay D documentation specifies function **0x05**, addresses `0x0200–0x0207`, and 100 ms units—not an ordinary holding-register write. Its FAQ does not establish glitch-free retriggering before expiry. [S5] | A refresh briefly drops a contactor, does not extend the timer, or a generic Modbus implementation sends the wrong function. | Keep B2 as a mandatory acceptance gate. Verify the exact command, timing and module firmware with electrical recordings. | High |
| 4 | **Critical** | §15 fallback | **J — Falling back to latched outputs defeats the failure strategy.** | Controller dies; pumps/features remain on indefinitely. A drained spa or blocked circuit continues running. | Remove this fallback from the acceptable production outcomes. Use a proven independent timeout or different output hardware if B2 fails. | High |
| 5 | **Major** | §4.3, §9–10 | **J — The 360 s deadman only conditionally preserves 300 s cooling.** With 30 s refreshes, nominal worst-case remaining time is **330 s**, before jitter and heater shutdown delay. | A delayed refresh, long watchdog interval or reboot recovery consumes the margin. A shared 24 VDC failure stops the relay module immediately. | Specify the complete timing inequality and failure domains. On recovery, actively renew any required pump run-on. Do not promise cooling through loss of the pump-control supply. | High |
| 6 | **Critical** | §5.3, V2/V3 | **J — Motor-current cessation is not endpoint confirmation.** | JVA is unplugged or mechanically disengaged; “already there” is accepted at startup; pumping starts through the wrong route. | Treat position as unknown after interrupted moves or uncertain startup. Use suitable position feedback, or a recovery procedure that establishes the hydraulic configuration before automatic operation. Retain current sensing as diagnostics. | High |
| 7 | **Major** | §5.3, §7.3, §9 | **J — Supply timeout can impersonate successful travel completion.** `T_JVA_POWER = T_JVA_MAX`. | A runaway actuator draws current until the supply timer expires. Current then disappears, and the same control cycle declares success. | Require valid completion **before** the deadline while supply is known available. Timer expiry is always a failed move. Track start/stop events per actuator. | High |
| 8 | **Major** | §5.3 | **J — The common JVA supply and its relay remain single failure points.** | Supply contact welds; a failed limit switch keeps the motor running. A later direction change occurs while supply is unexpectedly live. | Verify supply removal, provide appropriate branch protection, and consider a separate series timeout contact where bounded movement is relied upon for protection. | High |
| 9 | **Major** | §7.3–7.4; V1/V4 | **J — “Pump commanded off” is insufficient before moving valves.** | A contactor sticks or an old manual override keeps a pump running; the controller waits 10 s and rotates valves under flow. | Require observed stop/no-flow conditions. Add electrical mutual exclusion for the two circulation pumps where the confirmed plumbing requires it. | High |
| 10 | **Critical** | §7.2–7.4; H2/F3 | **J — Atomic transitions and unconditional cooling conflict with urgent faults.** | Flow is lost or someone activates a stop during transition, but the controller completes the sequence, runs a dry pump for cooling, or purges jets first. | Safety events must interrupt every state immediately. Distinguish normal shutdown, no-flow shutdown, unknown-valve shutdown and emergency stop. Cooling must not force continued hazardous pumping. | High |
| 11 | **Major** | §7.3; H2 | **J — Cooling is tested against “heater is on”, rather than recent heating.** | Thermostat turned the heater off seconds earlier; a spa request skips step 3 and attempts to stop circulation. H2 must rescue this inconsistency. | Enforce one authoritative “cooling required until” deadline for every pump stop and valve transition. | High |
| 12 | **Major** | §5.3, §10; S1 | **J — Reboot reconciliation is underspecified.** “Everything off”, retained pump operation and reasserting valves are different situations. | Brain reboots mid-move or while a remote pump remains energised, then initiates another valve move. | Establish a dedicated recovery state: heat inhibited, outputs read, old commands cancelled, movement assessed, required circulation reconciled, then normal requests accepted. | High |
| 13 | **Critical** | §5.9; L2; §10 | **J — Top-up timers cannot stop a mechanically stuck valve or welded contact.** | Indoor fill continues unattended despite an OFF command and alarm. | Provide an independent high-level shutdown operating a separate series shutoff, plus an adequate overflow route. A second valve controlled solely by the same software does not remove every common failure. | High |
| 14 | **Major** | §5.9, §10 | **J — Filling can persist after loss of valid level measurement.** The AI-offline response mentions heating but omits filling. | AI module fails, filter starts, or controller reboots while a 15 min fill pulse remains active. | Explicitly cancel filling whenever measurement validity is lost or pumping begins. Reconcile existing fill pulses on startup. Choose the hardware pulse limit from tolerable water volume. | High |
| 15 | **Major** | §5.9, §9 | **J — Fill limits are not tied to pool area, flow or overflow capacity.** Five-minute bursts also conflict with the default 15 min pulse. | A small pool overfills during one pulse; a large pool fails the 3 mm rise test despite normal filling. | Measure fill rate and surface area. Use `litres = area in m² × rise in mm`; define burst duration, maximum unattended volume and persistent daily limits accordingly. | High |
| 16 | **Major** | §5.9; §11 | **J — Stuck-open and volume diagnostics are overstated without a meter.** “No rain” has no specified local input. | Rain or swimmers create an alarm; a slow leak goes unnoticed while the pump runs; estimated minutes are presented as measured litres. | Fit the meter if these diagnostics matter. Detect flow with **both** fill valves commanded closed. Label time-derived volume as an estimate; do not depend on HA weather for protection. | High |
| 17 | **Major** | §5.5, §5.9; B4/B6 | **V/J — Analogue resolution is confused with accuracy.** The published ≤3% specification has no sufficiently clear error basis for this application. [S4] | Stable-looking, high-resolution readings are wrong enough to affect temperature control or filling. | Obtain a documented error specification or characterise the complete chain over input, temperature and supply variation. Calibration can remove some fixed errors, not unspecified drift. | High |
| 18 | **Major** | §5.9; Shopping note A | **V/J — Transmitter selection uses incomplete accuracy figures.** WIKA’s current A-10 sheet distinguishes BFSL non-linearity from total error; at 0.4 bar, listed maximum error is ±1.2% or ±0.7%, depending on option. [S6] | A “0.25%” purchase is assumed to provide 0.25% total measurement accuracy. | Specify repeatability, hysteresis, temperature effects, long-term drift and total error for the exact order code. Correct the shopping-list interpretation. | High |
| 19 | **Major** | §5.9; B6 | **J — The hydrostatic method is valid only when the actual pipe is static and connected to the intended body.** | Check valve traps pressure; isolation valve closes; solar drains back; another pump moves water through shared suction. A plausible but false level results. | Prove the tap against every operating mode. Require a stable pressure trace, not only 120 s elapsed. Test at actual static head and after repeated pump cycles. | High |
| 20 | **Major** | §5.5, §5.9 | **J — Density compensation can use the wrong temperature.** AI3 measures spa water in spa mode; pump-off pipe temperature is itself declared untrustworthy. | Hot spa temperature is applied to outdoor pool head, creating a false level shift comparable with the fill hysteresis. | Keep body-specific last-valid temperatures with age limits. Include water-column temperature uncertainty; do not compensate outdoor pool level from current spa temperature. | High |
| 21 | **Major** | §5.9 | **J — Atmospheric cancellation and operating pressure are assumed too broadly.** Basement air pressure can differ from pool-surface air pressure; flooded suction need not become sub-atmospheric while running. | Ventilation changes sensor reference pressure; 50 Pa becomes about 5 mm apparent level change. Air or a blocked vent adds drift. | Check reference ventilation, actual running pressure, vacuum tolerance and transients. Keep the reference dry and unobstructed. Validate level with ventilation operating. | Medium |
| 22 | **Major** | §5.4, §7.3; P-01 | **V/J — Generic circulation flow switches do not establish heater minimum flow.** Hayward’s cited style engages around **42 L/min**; the heater may require more. P-01 places FS-1 upstream of branches. [S7] | Flow goes to a booster/solar branch, or is merely above switch threshold, while heater flow is inadequate. | Prove flow through the heater’s actual path, at its required threshold. Follow switch orientation and straight-run requirements. | High |
| 23 | **Major** | §8 F3; §9–10 | **J — Waiting 180 s after no flow is not justified for these pumps.** | A dry or deadheaded pump runs for three minutes; cooling logic extends it further. | Set model-specific priming/no-flow limits. Distinguish startup priming from sudden flow loss; use a short commissioned dropout filter for the latter. | High |
| 24 | **Major** | §10–11 | **J — Acknowledgement must not override an active fault.** | User clears a stuck-flow-switch or unknown-valve alarm, and the system heats without re-establishing valid conditions. | Separate acknowledgement from reset permission. Require the cause to clear and the relevant proof sequence to pass; persist critical lockouts across reboot. | High |
| 25 | **Major** | §5.5, §7.7; P-01 | **J — TE-3 is downstream of solar heating in the drawing.** It therefore is not always representative pool temperature. | Solar-warmed return water makes the controller believe the pool has reached target and produces cycling or premature shutdown. | Place the controlling body-temperature measurement upstream of every heat addition, or provide a separate appropriate measurement. | High |
| 26 | **Major** | §5.5, §7.7; Shopping items 20–21 | **V/J — The solar sensor arrangement differs from the cited SolarTouch method.** Pentair specifies a sun-exposed surface sensor and explicitly excludes drilling it into solar pipe. [S8] | A drained header thermowell senses air/pipe temperature unpredictably; borrowed differentials give poor starts and stops. | Identify collector construction and drainback behaviour. Select the sensor location and differential together using the collector/controller requirements. | High |
| 27 | **Major** | §5.5; §10 | **J/U — 4–20 mA does not guarantee detection of every sensor fault.** Generic transmitters may clamp, saturate or retain a plausible value. | Broken RTD produces a credible cold reading; a frozen ADC continues answering Modbus requests. | Specify transmitter fault behaviour. Test opens, shorts, leakage, overrange and stale conversion. Add freshness and plausibility checks; preserve independent heater limits. | High |
| 28 | **Major** | Proposed thermistor reuse | **V/J — Reuse is feasible, but “10 kΩ NTC” is not a complete specification.** Voltage input requires per-channel hardware jumper and software changes. [S9] | Wrong curve, input loading or unstable excitation causes systematic temperature error. Leaving the current shunt connected heavily loads the divider. | Identify and test each sensor, characterise the complete divider/input chain, and implement explicit open/short detection. See assessment below. | High |
| 29 | **Major** | §1, §6; P-01 | **V/J — Chlorinator and chemical-dosing interlocks are deferred as optional spare loads.** [S10] | Existing sanitiser remains powered when its circulation path is stopped or diverted, allowing gas or concentrated chemical accumulation. | If fitted, include sanitiser power/enable, original flow protection and hydraulic path in the core design. Pentair explicitly requires pump-linked power and prohibits operation without circulation. | High |
| 30 | **Major** | §14 Q3–Q6; P-01 | **J — The hydraulic topology is still too uncertain to finalise sequencing.** | Small spa pump cannot meet heater flow; valves create an unwanted bypass; spa drains into pool; the drawn return selection does not produce the intended spillover. | Produce an as-found pipe survey and valve-port truth table for pool, spa, spillover, off and service. Show filters, check valves, bypasses, drains and heater minimum-flow path. | High |
| 31 | **Major** | §7.1; §8; P-01 | **V/J — Accessible emergency stopping and suction safety are missing.** [S11] [S12] | A bather needs jets stopped, but HA is unavailable and the basement service switch initiates delayed shutdown. | Provide an accessible local stop with defined immediate action. Check suction outlets/covers and combined pump flows against applicable recirculation requirements. NSW specifically advises knowing and labelling the filtration stop location. | High |
| 32 | **Major** | §11–12 | **V — ESPHome’s default API timeout conflicts with autonomous operation.** Default is reboot after 15 min without an authenticated API client. [S13] | HA outage produces repeated controller reboots, interrupted sessions and repeated recovery sequences. | Explicitly set `api.reboot_timeout: 0s`; audit equivalent options in any optional transports. Retain a controller-health watchdog independent of network availability. | High |
| 33 | **Major** | §7.8, §9, §11–12 | **J — Time validity, persistence and request validation need explicit rules.** | RTC fails and “6 h after boot” repeats after each restart—or runs once and never again. Daily fill allowance resets on reboot. A clock correction extends a session. | Use monotonic elapsed time for safety timers, Sydney civil time for schedules, bounded periodic fallback filtration, persistent fault/fill accounting and validated limits on every HA action. | High |
| 34 | **Major** | §6.4, §12 | **V/J — RS485 electrical details and worst-case latency are incomplete.** The Modbus guide includes a common conductor and defined biasing arrangements. [S14] | One dead slave occupies retries; short deadman refreshes are delayed. Undefined reference/bias produces intermittent errors. | Document isolated-side reference, shield and biasing; verify termination. Set per-transaction deadlines, data-age limits and priority for shutdown commands. Disable unwanted DI-to-relay linkage. Use one bus master. | High |
| 35 | **Major** | §5.1, §5.6; E-01 | **J — Electrical interface ratings and supply load are not yet established.** | Coil inrush damages contacts; an overloaded supply resets modules; one JVA short removes the shared actuator supply. | Obtain coil pickup/holding data, AC/DC inductive contact ratings, minimum switching load and suppression requirements. Budget simultaneous loads and fuse coordination. Use separate auxiliary poles for heater loops and DI wetting. | High |
| 36 | **Major** | §1.2, §5.8; E-01 | **V/J — ELV-only relay contacts do not complete the electrical compliance design.** §1.2 also assigns rewiring to the owner while §5.8 assigns it to an electrician. [S15] [S16] | Unknown 230 VAC coil wiring enters the ELV area; reused transformer lacks suitable separation; new water-contact metalwork is overlooked in bonding review. | Resolve work responsibility, protective separation, segregation, RCDs, isolators, earthing/bonding and testing in detailed electrical drawings. Check the actual installation against the applicable Wiring Rules. | High |
| 37 | **Major** | §5.8–5.9; P-01 | **V/J — “Air gap or backflow device” is too unspecific for construction.** [S17] | An unsuitable non-return device is treated as adequate protection of drinking water. | Specify the assessed hazard, approved device/air-gap arrangement, location, discharge provision and any testing obligations. NSW requires selection appropriate to hazard and backpressure/back-siphonage conditions. | High |
| 38 | **Major** | §5.7; §14; P-01 | **J — Basement flooding, blower water ingress and gas installation interfaces are absent.** | A pressure tap fails below pool level and gravity-drains water into the room; an air-line check valve leaks towards a low-mounted blower; ventilation equipment is inadvertently omitted during replacement. | Record drainage/sump capacity, leak detection, isolation access, blower loop/check arrangements and all existing heater ventilation/flue interlocks. Verify against the actual equipment manuals. | High |
| 39 | **Minor** | §2, §5.3, §9 | **V/J — Borrowed timing values and JVA ageing predictions are too authoritative.** Pentair’s guide gives a 5 min default but also says its gas heaters do not require that cooling delay. JVA documentation includes different cam arrangements. [S18] [S19] | Unnecessary delays are built in; a 90° actuator is treated as 180°; a failed contact is expected to provide weeks of warning. | Commission timing from actual equipment. Treat current/travel trends as diagnostics, not a predictive-maintenance guarantee. Confirm 50 Hz suitability of the actual actuator variant. | High |
| 40 | **Minor** | §5.7; Shopping §2F | **J — IP66 does not establish resistance to condensation or chlorine vapour.** | Moist air enters through breathing cycles; internal condensation corrodes terminals despite a sealed-looking enclosure. | Specify room conditions, corrosion-resistant materials, gland practice and condensation control. A breather/desiccant is not a chlorine-removal system. | High |
| 41 | **Major** | §12, §15; Shopping Stage 1 | **J — Existing bench gates are useful but do not cover the important common failures.** A 1.5 m standpipe does not reproduce approximately 3 m operating head. | Lamps pass every test, but real coils cause resets, a moving JVA loses power, or pressure hysteresis appears after pump operation. | Extend testing to real actuators/coils, independent supply failures, lost acknowledgements, interrupted moves, full-head level trials and fault persistence. | High |
| 42 | **Minor** | Shopping items 42–45; totals | **J — Cable and protection allowances are incomplete.** Twelve independent coil commands plus one shared return already need thirteen conductors. | The listed 12-core cable is insufficient; extra safety devices, terminals and enclosure space appear during installation. | Derive cable cores and quantities from terminal schedules. Add watchdog/timeout hardware, flood protection, appropriate flow protection and commissioning equipment before treating AU$3,033 as a project budget. | High |
| 43 | **Suggestion** | §3–4, §5.5; Shopping | **J — Some complexity offers little safety benefit.** Six separate RTD transmitters add cost and failure points; rejecting transistor-output hardware solely because loads need dry contacts ignores interposing relays. | Budget is spent on diagnostic temperature channels while independent shutdown protection remains unresolved. | Price alternatives by documented failure behaviour and maintainability. Reuse sound thermistors first; retain outlet sensors where their diagnostics justify them. A conventional PLC improves supportability but still needs the same equipment protections. | High |

## Thermistor reuse

**I would investigate this before purchasing six PT1000 assemblies.**

There is good precedent: Jandy’s AquaLink documentation gives **10.000 kΩ at 25 °C** and approximately **5.327 kΩ at 40 °C**. That supports your hypothesis, but does not identify the sensors actually installed. [S20]

The approach is technically reasonable with these conditions:

- **Identify the curve.** Measure disconnected sensors against a reference thermometer at approximately 20, 30 and 40 °C; cover the wider operating range for the roof sensor. Use the correct resistance table or fitted Steinhart–Hart coefficients.
- **Use only the old controller’s sensors.** Do not connect a divider in parallel with a sensor still serving the heater’s own thermostat or safety circuit.
- **Design the complete analogue circuit.** Use stable low-voltage excitation, a low-drift reference resistor, suitable filtering/protection and sufficiently high input impedance. Characterise loading or buffer the input.
- **Change both hardware and configuration.** The Waveshare module supports mixed voltage/current channels, but voltage channels require their current-sampling jumpers disconnected. The pressure channels can remain in current mode. [S9]
- **Detect electrical faults explicitly.** Check short circuit, open circuit, intermittent connection and moisture leakage. A partially faulty sensor can still give a believable temperature.
- **Validate end-to-end accuracy around the operating range.** A 0.1% divider resistor does not overcome an inadequately specified ADC. Measure repeatability, drift and absolute error with the real cable and module.

For a reference resistor above the thermistor, the ideal conversion is:

```text
R_NTC = R_ref × V_measured / (V_excitation − V_measured)
```

That expression assumes negligible input loading. Measuring excitation on another channel would consume capacity that the current eight-channel allocation does not have.

## Pressure-based level measurement

**The pressure-level method deserves a realistic trial, rather than outright rejection.** Hydrostatic pressure is a legitimate measurement principle. The difficulty is extracting a few millimetres of change from roughly 3 m of standing head in working suction plumbing.

Using the plan’s density:

| Level change | Pressure change | Change in a 4–20 mA signal spanning 40 kPa |
|---|---:|---:|
| 3 mm | 29 Pa | 11.7 µA |
| 5 mm | 49 Pa | 19.5 µA |
| 10 mm | 98 Pa | 39.1 µA |

These are calculations, not measured performance. A convincing trial must include the **transmitter, analogue module, wiring, temperature changes, pump cycles and actual tap arrangement**. A single zero adjustment cannot establish that performance.

## Claims not verified, and required tests

| Claim | Verification required |
|---|---|
| Flash-on refresh restarts the countdown without dropping the contact | Record the actual relay contact and contactor coil while refreshing at different points before expiry. Include lost replies, retries and a bus disconnection immediately before refresh. |
| A controller crash makes onboard outputs safe | Keep all supplies energised; test MCU reset, watchdog reset, stalled control execution, I²C failure, bootloader and failed OTA. Record physical contacts, not software state. |
| Remote module state survives or clears correctly through brownouts | Interrupt each module’s supply independently and restore it while other equipment remains energised. Verify outputs and configuration before accepting new commands. |
| JVA movement is correctly classified | Test already-at-endpoint, unplugged actuator, centre-OFF toggle, disengaged mechanism, interrupted power and simulated failed limit operation on a safe bench rig. Timeout must never count as successful arrival. |
| Generic transmitters provide the promised fault currents | Inject sensor open/short conditions and calibrated loop currents around the intended fault thresholds. Check whether the ADC reports, clips or mis-scales overrange values. |
| The level chain reliably detects 3–5 mm | Test around actual operating head, over temperature and repeated suction/pressure cycles, then compare against an independent physical level reference on site. |

The plan already proposes B1–B6; these tests strengthen those gates. **Passing the gates should be required before relying on the associated behaviour.**

## Cost assessment

The listed arithmetic reconciles to **AU$3,033.07**. I also verified the **AU$61.80** Relay D price and **AU$223.37 including GST** enclosure price. Those figures are credible. [S21] [S22]

The larger uncertainty is the specification behind the estimates: the AU$200 pressure transmitters and AU$40 temperature transmitters are not yet defined purchasable parts meeting the required performance. Safety additions, hydraulic corrections and commissioning could materially exceed savings on the controller modules.

The best economies are **reusing verified thermistors, existing sound wiring and suitable contactors**, and reducing unnecessary diagnostic channels. Saving money by accepting an unproven level chain or removing independent shutdown protection is poor value.

## Assumptions made

- The approximately 3 m dimension is to the basement floor; actual heater and transmitter elevations remain unknown.
- No existing independent flow, flood or sanitiser interlocks are credited unless documented.
- P-01 is indicative; I have not treated its guessed pipe routes as an as-built survey.
- Existing heater internal protections remain operational and are retained.
- The outdoor spa has a separate hydraulic state and temperature, even though it sits within the outdoor pool.
- This is a residential NSW installation. Standards comments identify design checks; I have not verified every applicable clause or amendment against licensed standards text.

## Questions for the owner before building

1. What are the exact models and installation heights of both heaters, including photographs of remote-enable terminals and existing flow/pressure protection?
2. What are every contactor’s coil voltage, auxiliary-contact arrangement and overload connections? Are there existing manual bypasses?
3. Can each pipe and all three JVA ports be traced through pool, spa and spillover operation?
4. What flow does the small spa circulation pump actually deliver through the shared heater?
5. What chlorinators, dosing equipment, ventilation systems and other interlocks currently depend on the old controller?
6. What are the pool surface areas, measured top-up flow rates, overflow destinations and basement drainage capacity?
7. What exact backflow protection and top-up valves are already installed?
8. Which original temperature sensors remain, where are they installed, and can their resistance be measured disconnected?
9. What caused the previous JVA runaway, and have its switches, cams and mechanical coupling been repaired?
10. Where can users stop jets/circulation immediately, and what must remain usable when HA is unavailable?

## Keep these parts of the design

- HA issuing bounded **requests**, with local authority over equipment.
- Local schedules, explicit priorities and published reasons for blocked requests.
- A deterministic, independently testable control core.
- Separation of heater shutdown from normal circulation run-on.
- Removing JVA power between moves and bounding movement duration.
- Retaining overloads, heater protections and physical electrical isolation.
- Staged purchasing, bench gates and documented commissioning.

The main correction is to make the claimed protections independent and testable, while keeping the existing control architecture.

## Sources

Sources were consulted for the original review on 4 November 2026. Product manuals establish requirements for their specified models; they do not identify equipment installed on this site. Chat citations have been converted to portable Markdown source links.

[S1]: https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/heaters/mastertemp/manual/MasterTemp_Australia_Pool_and_Spa_Heater_Operation_and_Installation_Manual_English.pdf
[S2]: https://www.waveshare.com/wiki/ESP32-S3-ETH-8DI-8RO
[S3]: https://www.ti.com/lit/ds/symlink/tca9554.pdf
[S4]: https://www.waveshare.com/modbus-rtu-analog-input-8ch.htm
[S5]: https://www.waveshare.com/wiki/Modbus_RTU_Relay_%28D%29
[S6]: https://www.wika.com/media/Data-sheets/Pressure/Pressure-sensors/ds_pe8160_en_co.pdf
[S7]: https://hayward.com/media/akeneo_connector/asset_files/A/Q/AQR159d_AquaRite_TSG_94ef.pdf
[S8]: https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/automation/solartouch/manual/SolarTouch_Solar_Controller_System_Installation_and_Users_Guide_English.pdf
[S9]: https://www.waveshare.com/wiki/Modbus_RTU_Analog_Input_8CH
[S10]: https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/sanitizers/intellichlor/intellichlor-installation-users-guide-ic15-ic20-ic40-ic60.pdf
[S11]: https://www.productsafety.gov.au/business/find-banned-products/swimming-pools-and-spas-with-unsafe-design-features-ban
[S12]: https://www.nsw.gov.au/housing-and-construction/building-or-renovating-a-home/pools-and-pool-safety/owner-obligations
[S13]: https://esphome.io/components/api/
[S14]: https://www.modbus.org/docs/Modbus_over_serial_line_V1_02.pdf
[S15]: https://www.nsw.gov.au/business-and-economy/licences-and-credentials/building-and-trade-licences-and-registrations/electrical
[S16]: https://www.wa.gov.au/government/multi-step-guides/electrical-safety-home/swimming-pools-and-spas-electrical-bonding
[S17]: https://www.nsw.gov.au/housing-and-construction/compliance-and-regulation/plumbers-and-drainers/standards-and-notes/cross-connection-and-backflow-control
[S18]: https://www.pentair.com/content/dam/extranet/nam/pentair-pool/residential/automation/intellicenter/manuals---user-docs/IntelliCenter_Quick_Ref_Guide.pdf
[S19]: https://www.jandy.com/-/media/zodiac/global/downloads/jandy/valves/h0570800.pdf
[S20]: https://www.jandy.com/-/media/zodiac/global/downloads/jandy/automation/6919.pdf?rev=b7abf41aa5ba459a87dc27862fd821ac
[S21]: https://core-electronics.com.au/industrial-modbus-rtu-8ch-relay-module-rs485.html
[S22]: https://switchesplus.com.au/Metal-Enclosure-600-x-400-x-200mm-IP66~1331

| Reference | Source | Relevant evidence |
|---|---|---|
| [S1] | Pentair MasterTemp Australian installation and user’s guide | Below-pool pressure-switch limitations; flow-switch requirement |
| [S2] | Waveshare ESP32-S3-ETH-8DI-8RO wiki | TCA9554 onboard relay-control expander |
| [S3] | Texas Instruments TCA9554 datasheet | Latched outputs and power-on reset behaviour |
| [S4] | Waveshare Analog Input 8CH product specifications | Published 12-bit resolution and ≤3% accuracy |
| [S5] | Waveshare Modbus RTU Relay D wiki | Flash-on command format, timing units and FAQ |
| [S6] | WIKA A-10 datasheet PE 81.60, February 2026 | Non-linearity versus maximum measured error, including 0.4 bar range |
| [S7] | Hayward AquaRite troubleshooting guide | Flow-switch engagement threshold and installation checks |
| [S8] | Pentair SolarTouch installation and user’s guide | Solar-sensor mounting instructions |
| [S9] | Waveshare Analog Input 8CH wiki | Per-channel voltage/current configuration and hardware jumpers |
| [S10] | Pentair IntelliChlor IC15/20/40/60 installation and user’s guide | Pump-linked power and circulation requirements |
| [S11] | ACCC Product Safety: unsafe pool and spa design features | Suction-outlet and entrapment risks |
| [S12] | NSW Government: pool and spa owner obligations | Clearly identified filtration on/off location |
| [S13] | ESPHome Native API component documentation | Default 15 min reboot timeout and disabling option |
| [S14] | Modbus serial-line specification and implementation guide V1.02 | Common conductor and physical bus arrangements |
| [S15] | NSW Government: electrical work | Licensing and applicable wiring framework |
| [S16] | WA Government: swimming pools and spas electrical bonding | AS/NZS 3000 bonding considerations; supporting guidance, not a NSW site assessment |
| [S17] | NSW Government: cross-connection and backflow control | Hazard-based backflow selection |
| [S18] | Pentair IntelliCenter quick reference guide | Cool-down and valve-delay settings and limitations of their applicability |
| [S19] | Jandy JVA 2444 installation and operation manual | Cam configurations, manual operation and actuator specifications |
| [S20] | Jandy AquaLink service documentation, document 6919 | Water-temperature sensor resistance table |
| [S21] | Core Electronics Relay D listing | AU$61.80 including GST at review |
| [S22] | Switches Plus FT604020 listing | AU$223.37 including GST at review |
