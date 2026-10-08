# Foundations

## Contents

- Modeling and approximations
- Scale, logarithms, and decibels
- Complex numbers
- Linear and nonlinear systems
- Steady state and transient behavior
- Energy, equilibrium, and lumped elements

## Modeling and approximations

Start with the simplest model that answers the question, then add nonideal behavior only when it changes the conclusion. State the model boundary and neglected effects.

Use algebraic approximations only after identifying the small parameter. Validate by comparing the approximation with the unapproximated expression or by estimating relative error.

Track dimensions throughout. A valid equation must have compatible units on both sides. Use SI prefixes carefully: m = 10^-3, u = 10^-6, n = 10^-9, k = 10^3, M = 10^6.

## Scale, logarithms, and decibels

Use orders of magnitude for plausibility checks. A factor of ten is one decade.

- Power ratio: `dB = 10 log10(P2/P1)`
- Voltage or current ratio with equal impedances: `dB = 20 log10(V2/V1)`

State the reference for absolute units such as dBm or dBV.

## Complex numbers

Represent a sinusoid in steady state with a phasor only after frequency and sign convention are established. Use rectangular form for addition and polar form for multiplication/division. Do not apply DC-only resistor methods directly to reactive AC networks; use impedance.

## Linear and nonlinear systems

A linear system satisfies scaling and superposition. Resistors with constant resistance and ideal linear sources form linear networks. Diodes, saturated amplifiers, switching devices, and temperature-dependent behavior are generally nonlinear.

Use local linearization only around a declared operating point and over a stated small-signal range.

## Steady state and transients

Steady state describes behavior after transients settle or a repeating periodic condition is reached. A transient is the time-dependent response to switching, startup, or disturbance.

Ask whether the requested value is at `t = 0+`, during the transition, or after settling. Initial energy in capacitors and inductors can matter.

## Energy, equilibrium, and lumped elements

The lumped-element model assumes circuit dimensions are small relative to relevant electromagnetic wavelengths and propagation delay is negligible. It becomes unreliable for sufficiently fast edges, long interconnects, or high frequencies.

Power is the rate of energy transfer: `p = v i`. Positive power under the passive sign convention means an element absorbs energy; negative power means it delivers energy.
