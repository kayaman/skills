# Op-amp circuits

## Contents

- Ideal model and validity
- Common configurations
- Nonideal checks
- Design workflow

## Ideal model and validity

The ideal op-amp has infinite open-loop gain, infinite input resistance, zero output resistance, and unlimited bandwidth. The familiar rules `V+ approximately V-` and zero input current are analysis consequences, not universal laws.

Apply the virtual-short approximation only when negative feedback exists and the amplifier is operating linearly rather than saturated. A virtual short means near-equal voltage, not a physical connection or equal currents.

## Common configurations

- Buffer: `Vout = Vin`; use to reduce loading, subject to input common-mode and output-drive limits.
- Non-inverting amplifier: `Vout/Vin = 1 + Rf/Rg`.
- Inverting amplifier: `Vout/Vin = -Rf/Rin`.
- Transimpedance amplifier: ideally `Vout = Vref - Iin Rf`, with sign determined by current direction.
- Voltage reference/buffer: distinguish generating a reference from buffering it; check source impedance and load current.

## Nonideal checks

Check the exact datasheet for supply range, input common-mode range, output swing and current, offset and bias current, gain-bandwidth, stability, slew rate, rail-to-rail conditions, noise, capacitive-load stability, pinout, and decoupling.

Estimate signal bandwidth and ensure noise gain is compatible with gain-bandwidth. Check resistor thermal noise and bias-current error when relevant. A DC gain calculation alone is insufficient for time-varying signals.

## Design workflow

1. Define input range, source impedance, output range, load, bandwidth, error budget, and supplies.
2. Choose topology and reference point.
3. Calculate nominal resistor ratios.
4. Select practical values that balance loading, noise, bias-current errors, and power.
5. Verify common-mode, output swing/current, stability, bandwidth, and slew rate.
6. Add decoupling and protection appropriate to the environment.
7. Evaluate min/typ/max behavior from datasheet limits.
8. Simulate useful corners, then measure the physical circuit.
