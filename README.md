# 120 Pool Controller

A self-contained pool and spa controller for a residence with two bodies of water:

- **Indoor pool:** filter pump, gas heater, spa jets, blower
- **Outdoor pool with in-pool spa:** filter pump, cleaner booster, shared gas heater, solar pump, 2 × swim jets, feature pump, 3 × Jandy Valve Actuators (JVAs), plus the spa's own filter pump, jets and blower

It sits at the equipment pad, enforces every safety interlock locally, and integrates with Home Assistant through ESPHome.

## Status

Design stage.

- **[docs/PLAN.md](docs/PLAN.md):** the full plan, I/O map, interlock rules, failure modes and open questions
- **[docs/SHOPPING-LIST.md](docs/SHOPPING-LIST.md):** staged shopping list with indicative prices and Australian stockists
- **[docs/drawings/](docs/drawings/README.md):** E-01 control-system interconnection, and P-01 piping & instrumentation (indicative)

## Hardware (proposed)

- Waveshare ESP32-S3-ETH-8DI-8RO: the controller ("brain")
- 2 × Waveshare Modbus RTU Relay (D): relay and digital-input expansion
- Waveshare Modbus RTU Analog Input 8CH: PT1000 temperatures via 4–20 mA transmitters, plus two pressure transmitters for pool water level (auto top-up)
- Existing contactors switch the motors. The Waveshare relays only switch low-voltage control circuits.
