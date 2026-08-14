# Practical design and troubleshooting

## Contents

- Resistor selection
- Potentiometers and switches
- Breadboard translation
- Measurement workflow
- Troubleshooting order

## Resistor selection

Choose a standard value that satisfies the functional requirement, then check tolerance, worst-case output, power, maximum working voltage, temperature coefficient, pulse rating, package, and availability.

Do not operate continuously at the nominal power limit. Unless the datasheet and thermal design justify otherwise, select a rating with meaningful margin and explain assumed ambient conditions. Measure unknown parts out of circuit when practical.

## Potentiometers and switches

A potentiometer has two end terminals and a wiper. Used as a divider, connect the ends across the reference voltage and take output from the wiper. Used as a rheostat, connect the wiper and one end; consider tying the unused end to the wiper for graceful contact failure where appropriate.

Identify switch topology, terminal mapping, voltage/current rating, bounce, and whether pull-up or pull-down resistance is required.

## Breadboard translation

Treat the schematic as the source of truth. Map by node, not by drawing position.

1. Declare the breadboard rail convention and verify whether long rails are split.
2. List every connection as `from -> to`.
3. Give integrated-circuit orientation and pin numbers from the exact datasheet.
4. Place a local decoupling capacitor near each IC supply pair when appropriate.
5. Establish common ground between interacting low-voltage modules.
6. Keep power disconnected while rewiring.
7. Inspect for unintended rail bridges before energizing.

## Measurement workflow

State meter mode, probe placement, expected range, and circuit power state.

- Measure voltage in parallel relative to a declared node.
- Measure resistance only with power removed and stored energy discharged; parallel paths may distort readings.
- Measure current by opening the path and inserting the meter in series. Start on a safe current range and correct jack. Never place a meter configured for current directly across a source.
- Use oscilloscope ground clips carefully; bench-scope grounds may be Earth-referenced.

## Troubleshooting order

1. Power off and inspect orientation, values, shorts, and rail continuity.
2. Check supply voltage, polarity, and current limit.
3. Verify reference ground continuity.
4. Measure node voltages from input toward output.
5. Compare each reading with a calculated or simulated expectation.
6. Isolate stages and substitute known inputs or loads.
7. Check thermal behavior and component ratings.
8. Change one variable at a time and record the result.
