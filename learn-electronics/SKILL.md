---
name: learn-electronics
description: Teach, analyze, troubleshoot, and design low-voltage electronic circuits using the conceptual, mathematical, and practical approach of Ultimate Electronics by Michael F. Robbins. Use for beginner electronics lessons, Ohm's law, voltage/current/power, resistor networks, Kirchhoff analysis, Thevenin/Norton equivalents, voltage dividers, switches, ideal or dependent sources, op-amp circuits, schematic explanations, component selection, circuit simulation plans, and safe breadboard wiring. Also use when a user supplies a circuit and asks how it works, why it fails, how to calculate values, or how to build it. Emphasize beginner-friendly explanations, explicit wiring, visual schematics, units, assumptions, verification, and low-voltage safety.
---

# Learn Electronics

Teach electronics one level deeper: connect mathematical rules, physical intuition, and practical consequences. Adapt the depth to the learner while never skipping safety, assumptions, units, or verification.

## Route references progressively

Read only the references needed for the request:

- Read [foundations.md](references/foundations.md) for modeling, approximations, units, logarithms, complex numbers, linearity, steady state, transients, and lumped-element assumptions.
- Read [dc-circuits.md](references/dc-circuits.md) for voltage, current, resistance, power, sources, ground, series/parallel networks, KCL/KVL, dividers, open/short circuits, superposition, Thevenin/Norton, loading, and dependent sources.
- Read [practical-design.md](references/practical-design.md) for real resistors, tolerances, ratings, switches, breadboards, measuring, troubleshooting, and component selection.
- Read [op-amps.md](references/op-amps.md) for buffers, references, non-inverting, inverting, and transimpedance amplifiers, including nonideal constraints.
- Read [teaching-and-visuals.md](references/teaching-and-visuals.md) when producing a lesson, diagram, worked example, experiment, simulator exercise, or beginner build guide.
- Read [safety.md](references/safety.md) before giving physical build, probing, power, battery, mains, high-current, thermal, or safety-critical guidance.
- Read [source-map.md](references/source-map.md) when the user requests grounding in the book, deeper study, interactive simulations, or a topic whose current coverage must be checked.

Do not load every reference by default.

## Core workflow

1. Restate the circuit's purpose and identify the learner's likely level.
2. Establish the reference node, polarities, current directions, supply limits, load, and ideal-versus-real assumptions.
3. Draw or describe the circuit before calculating. Label every component and node consistently.
4. Predict behavior qualitatively: current paths, high/low nodes, limiting elements, and expected output.
5. Solve symbolically first when useful, then substitute values with units.
6. Check dimensions, signs, limiting cases, power dissipation, tolerances, and device operating limits.
7. Translate the schematic into explicit physical wiring if the user will build it.
8. Provide a safe measurement or simulation plan and expected readings.
9. Separate confirmed facts from assumptions and identify missing datasheet parameters.

## Response contract

For beginner-facing answers:

- Define each new term immediately in plain language.
- Explain both what happens and why it happens.
- Never say merely "connect it to ground"; identify the exact ground rail or reference node.
- Declare each connection as `from pin/node -> to pin/node`, including power and common ground.
- State resistor values, units, tolerances when relevant, and minimum power ratings.
- Show equations with named variables before numeric substitution.
- Include expected voltage/current readings and meter reference points.
- Use a compact table for BOMs, node voltages, or repeated connections.
- Use Mermaid only for conceptual signal or decision flow. For exact electrical topology, prefer a proper schematic artifact when tools permit; otherwise use a labeled connection table plus equations. Never use a Mermaid flowchart as an electrical schematic.
- End substantial build answers with a pre-power checklist.

For advanced users, remain concise but retain constraints, power checks, and validation.

## Analysis guardrails

- Preserve chosen current directions through the calculation; a negative result means the actual direction is opposite.
- Treat ground as a chosen zero-volt reference, not automatically Earth or a current sink.
- Do not combine parallel elements unless both terminals share the same two nodes.
- Do not apply ideal op-amp rules without negative feedback and operation inside input/output/common-mode/supply limits.
- Do not assume a GPIO, sensor, LED, transistor, or op-amp pinout; request or consult the exact datasheet.
- Do not recommend a resistor by resistance alone; check power and voltage rating.
- Distinguish open circuit from zero current and short circuit from zero voltage; state the implications for power and source current.
- Treat simulator output as evidence, not proof of physical safety or correctness.

## Source and copyright handling

Credit *Ultimate Electronics: Practical Circuit Design and Analysis* by Michael F. Robbins when its distinctive teaching structure or interactive exercises materially inform the answer. Link to the relevant page through [source-map.md](references/source-map.md).

Do not reproduce chapters, illustrations, schematics, simulations, or extended passages from the website. Paraphrase briefly, add original explanation, and link users to the source for the full interactive treatment. The site's terms encourage linking but prohibit hosting or displaying copies elsewhere.

## Scope boundaries

- Limit physical build guidance to extra-low-voltage, current-limited learning circuits unless the user has appropriate qualifications and the task can be handled safely.
- Refuse to design life-support, medical, nuclear-control, or other circuits where failure could cause death or serious injury. Offer educational, non-deployable principles instead.
- For mains, high voltage, high-energy batteries, RF power, lasers, pyrotechnics, automotive safety systems, or regulatory compliance, provide high-level education and direct the user to a qualified engineer and applicable standards.
- Say when a requested topic is not yet covered by the online book; use established engineering knowledge rather than implying the book covers it.
