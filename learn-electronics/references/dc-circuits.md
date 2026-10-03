# Linear DC circuits

## Contents

- Core quantities and laws
- Sources and reference nodes
- Series and parallel networks
- Systematic nodal analysis
- Useful transformations
- Opens, shorts, loading, and transfer

## Core quantities and laws

- Charge `q` is measured in coulombs.
- Current is charge flow rate: `i = dq/dt`, measured in amperes.
- Voltage is energy per unit charge: `v = dw/dq`, measured in volts.
- Resistance relates voltage and current for an ohmic element: `v = iR`.
- Power: `p = vi = i^2R = v^2/R` for a resistor.

Always define voltage polarity and current direction. Use the passive sign convention when convenient: current enters the terminal marked positive.

## Sources and reference nodes

An ideal voltage source fixes terminal voltage and can theoretically supply any current; an ideal current source fixes current and can theoretically develop any voltage. Real sources have current, voltage, power, and thermal limits plus internal impedance.

Ground is the selected zero-volt node for measuring other node voltages. It may or may not connect to protective Earth, chassis, or another system's ground.

## Series and parallel networks

Series elements share the same current because their connecting node has no other branch. `R_series = sum(Rk)`.

Parallel elements share both endpoint nodes and therefore the same voltage. `1/R_parallel = sum(1/Rk)`. For two resistors: `R = R1 R2 / (R1 + R2)`.

Voltage divider with unloaded output across `R2`:

`Vout = Vin * R2/(R1 + R2)`

If a load `RL` is attached, replace `R2` with `R2 || RL`. Never ignore loading without checking it.

## Kirchhoff laws

KCL: the algebraic sum of currents at a node is zero. This follows from charge conservation.

KVL: the algebraic sum of voltage changes around a closed loop is zero under the lumped-element model.

## Systematic nodal analysis

1. Choose a reference node.
2. Name every other essential node.
3. Express each branch current from node voltages and element laws.
4. Write one KCL equation per unknown node, excluding redundant equations.
5. Handle a voltage source between two unknown nodes with a supernode plus its voltage constraint.
6. Solve, then back-calculate branch currents and power.
7. Verify KCL and check that total delivered and absorbed power balance within rounding.

## Useful transformations

Superposition applies only to linear circuits. Evaluate one independent source at a time: replace ideal voltage sources with shorts and ideal current sources with opens. Keep dependent sources active. Add voltages or currents, not powers.

Thevenin equivalent at a port: voltage source `Vth` in series with `Rth`. Norton equivalent: current source `In = Vth/Rth` in parallel with `Rth`.

Find `Vth` as open-circuit port voltage. Find `Rth` by deactivating independent sources and looking into the port; if dependent sources remain, apply a test source and compute `Rth = Vtest/Itest`. Alternatively, where valid, `Rth = Voc/Isc`.

Maximum power transfer for a resistive DC source occurs at `RL = Rth`; efficiency is only 50%, so this is not usually the goal for power delivery. For signal transfer, choose impedances to avoid loading according to the application.

## Opens, shorts, loading, and transfer

An ideal open circuit carries zero current but can have voltage across it. An ideal short has zero voltage across it but can carry current limited by the rest of the circuit. Shorting a low-impedance source can create destructive current.

Input resistance and output resistance predict interstage loading. For voltage transfer, a receiving stage usually needs input resistance much larger than the source output resistance.

Dependent sources model behavior controlled by another circuit variable. Preserve them during superposition and equivalent-resistance calculations.
