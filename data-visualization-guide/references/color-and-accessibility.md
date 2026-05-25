# Color & Accessibility

Color is the most abused channel in data visualization: it is preattentive and emotionally
powerful, but it carries no natural magnitude and roughly 1 in 12 men (8%) and 1 in 200 women have
some color-vision deficiency. Treat color as a deliberate encoding with a job, not as decoration.
Grounded in Wilke's color chapters, Few's palette guidance, and accessibility practice.

## Three palette types — match to data type

The single most common color error is using the wrong *type* of palette for the data. There are
exactly three, mapped to the three data types from perception-and-encoding.md:

| Data type | Palette type | What it looks like | Examples |
| --- | --- | --- | --- |
| Categorical (no order) | **Qualitative** | Distinct hues, similar lightness | Set2, Tableau 10, Okabe-Ito |
| Ordered / sequential | **Sequential** | One hue, light → dark | viridis, Blues, cividis |
| Diverging from a midpoint | **Diverging** | Two hues meeting at a neutral middle | RdBu, BrBG, PiYG |

- **Qualitative** palettes must not imply order — keep lightness roughly constant so no category
  looks "bigger." Cap at ~7 colors; beyond that, hues become indistinguishable. If you have more
  categories, group the long tail into "Other" or switch to small multiples.
- **Sequential** for quantities/ranks. Higher value = darker (or lighter) — monotonic in lightness
  so the eye reads magnitude. Use **perceptually uniform** maps (viridis, magma, cividis) where
  equal data steps look like equal color steps.
- **Diverging** only when there is a meaningful midpoint (zero, a target, an average). The neutral
  center must sit at that value, or the chart lies about which side things fall on.

## Recommended palettes (safe defaults)

When you don't have a brand palette to honor, reach for these — all are colorblind-safe and widely
available in matplotlib, ggplot, Tableau, Vega, and D3:

| Use | First choice | Alternatives |
| --- | --- | --- |
| Sequential (low→high) | `viridis` | `cividis`, `magma`, single-hue `Blues`/`Greens` |
| Diverging (−/0/+) | `RdBu` (red–blue) | `BrBG`, `PiYG` — avoid red–green |
| Qualitative (categories) | Okabe-Ito (8-color, CVD-safe) | `tab10`, Vega/Tableau "Safe" set |
| Highlight on grey | one accent (e.g. a strong red/blue) | brand accent |

**Single-hue vs. multi-hue sequential.** Single-hue ramps (light→dark blue) read as "more of one
thing" and are the safe default. Multi-hue perceptually-uniform ramps (viridis) give more
discriminable steps across a wide range — use them for heatmaps and continuous fields where fine
distinctions matter. Don't build your own multi-hue ramp by hand; you'll reintroduce the rainbow's
non-uniform bands.

**The highlight pattern.** The most useful palette in business reporting is *grey plus one*: render
everything in neutral grey and give the one series/bar/point that carries the message a single
accent color. This is the preattentive "one thing pops" technique (perception-and-encoding.md) and
is how every example in [chart-gallery.md](chart-gallery.md) directs the eye.

## Avoid rainbow / jet

The classic rainbow (jet) colormap is **not perceptually uniform**: it has bright bands (yellow,
cyan) that create the illusion of edges or features in the data that don't exist, and it's
unreadable in grayscale or with color blindness. It remains common in legacy scientific tools —
replace it with viridis/cividis. This is a correctness issue, not taste: rainbow maps have caused
misreadings of medical and climate data in published work.

## Colorblind safety

- **Never encode meaning by color alone.** Pair color with a second channel — direct labels,
  position, shape, or texture — so the chart survives in grayscale. The red/green of "bad/good" is
  exactly the pair most deuteranopes can't distinguish.
- Prefer **colorblind-safe palettes**: viridis family (sequential), Okabe-Ito or Tableau 10
  (qualitative), RdBu/BrBG (diverging — blue/orange survives most CVD; red/green does not).
- **Test it.** Simulate deuteranopia/protanopia/tritanopia, or just render in grayscale — if
  categories collapse, the palette fails.

## Contrast and legibility

- Text and key marks need sufficient contrast against the background (WCAG ≥ 4.5:1 for body text,
  ≥ 3:1 for large text and meaningful graphical objects). Light-grey-on-white axis labels are a
  common failure.
- Don't rely on thin colored lines on colored backgrounds; thin marks lose contrast fastest.
- On dashboards and slides, account for projectors and cheap monitors that crush dark tones —
  test on the actual medium.

## Using color with restraint

Few's principle: a chart's default state should be **mostly grey**. Color is then free to mean
something. Reserve saturated color for the data you want noticed; render context, gridlines, and
secondary series in neutral grey. A chart where everything is colorful has spent its entire
attention budget and can highlight nothing.

**Semantic color**: lean on conventions where they exist (red = loss/danger, green = gain/ok, but
see colorblind note; brand colors for brand entities; political/team colors). Override conventions
only with a reason, and never invert them (green for loss will misread).

## Accessibility checklist

```
[ ] Palette type matches data type (qualitative / sequential / diverging)?
[ ] Sequential/diverging maps are perceptually uniform (viridis family)?
[ ] No rainbow/jet?
[ ] Meaning never conveyed by color alone — second channel present?
[ ] Passes a grayscale / colorblind simulation?
[ ] Text contrast ≥ 4.5:1; readable on the target medium (print/projector/screen)?
[ ] Most of the chart is neutral; saturated color reserved for the message?
```

Sources: Wilke *Fundamentals of Data Visualization* (color chapters); Few on grey-by-default and
restraint; viridis/perceptual-uniformity research; Okabe-Ito colorblind-safe palette; WCAG contrast
guidance.
