# Teaching and visual communication

## Contents

- Lesson pattern
- Worked-example pattern
- Visual hierarchy
- Build-guide format
- Simulation exercises

## Lesson pattern

Teach in this order:

1. Goal: what the learner will predict or build.
2. Intuition: physical analogy with its limits stated.
3. Model: circuit diagram, nodes, directions, and assumptions.
4. Rule: equation with variable definitions and units.
5. Worked example: symbolic solution, numbers, and checks.
6. Try it: one small change predicted before calculating.
7. Verify: expected simulation or measurement results.
8. Reflect: connect the result to a broader concept.

Avoid analogies that replace the electrical model. Use them as bridges, then return to charge, energy, fields, and circuit laws.

## Worked-example pattern

Present given values and unknowns, assumptions, labeled topology, qualitative prediction, governing equations, algebraic solution, numeric substitution with units, sanity and power checks, and expected measured values.

Round only at the end. Preserve enough significant digits to show reasoning without implying unrealistic component precision.

## Visual hierarchy

- Proper schematic: exact electrical connectivity.
- Connection table: physical wiring and pin mapping.
- Block diagram: functional stages and signal flow.
- Plot: voltage/current versus time or a sweep.
- Table: BOM, node voltages, tolerance corners, or comparison.

Do not use a block diagram or flowchart as a substitute for a schematic. If no schematic-rendering tool is available, provide a node-based netlist/connection table that is electrically unambiguous. Use consistent identifiers across every representation.

## Build-guide format

Include supply limits and current limit, BOM with ratings, pinout/orientation source, numbered wiring table, pre-power checks, staged power-up, expected node readings, and troubleshooting decision points.

## Simulation exercises

Ask the learner to predict before simulating. Change one parameter at a time. Compare the result to an equation and explain any model discrepancy.

Useful sweeps include resistance ratios, load resistance, source resistance, supply voltage, tolerance corners, and op-amp bandwidth or output limits. Never treat a successful ideal simulation as proof that a real component will survive or behave identically.
