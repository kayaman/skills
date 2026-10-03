# Safety

## Contents

- Default operating envelope
- Pre-power checklist
- Batteries and stored energy
- Stop conditions
- Safety-critical boundaries

## Default operating envelope

Keep beginner physical projects at extra-low voltage using isolated, current-limited supplies. Prefer a bench supply with a conservative current limit or a protected low-power USB source when appropriate. Never imply that low voltage guarantees safety: high current, heat, fire, battery faults, and component rupture remain possible.

## Pre-power checklist

- Confirm source voltage, polarity, current limit, and connector pinout.
- Confirm all component orientations and IC pin 1.
- Check for shorts between supply and ground with power removed.
- Verify resistor values and power ratings.
- Verify electrolytic capacitor, diode, LED, transistor, and IC polarity/pinout.
- Ensure no loose conductors can bridge adjacent nodes.
- Use eye protection when components, batteries, or stored energy could fail violently.
- Power up in stages and stop if current, smell, heat, sound, or voltage is unexpected.

## Batteries and stored energy

Do not short batteries. Use appropriate fusing, protected cells, chargers, connectors, and wire gauge. Do not propose improvised charging of lithium cells. Treat large capacitors as energized until discharged through a suitable resistor and verified with a meter.

## Stop conditions

Stop and seek qualified supervision for direct mains, hazardous voltage, unknown stored energy, high-current packs, damaged lithium cells, wet or body-contact environments, safety functions, medical use, vehicles, machinery, regulatory certification, or uncertainty about isolation, protective Earth, oscilloscope grounding, or clearances.

Do not give procedural construction instructions for these conditions. Provide high-level concepts and safer simulation or extra-low-voltage analogues.

## Safety-critical boundaries

Do not design or validate circuits whose failure could cause death or serious injury. Simulation and educational calculations are not certification. State that qualified engineering review, hazard analysis, applicable standards, independent verification, and testing are required for real products.
