# Graphical Perception & Encoding

This is the scientific core of the field: charts work by mapping data to *visual channels*, and the
human visual system reads some channels far more accurately than others. Choosing the channel is the
single highest-leverage decision after choosing the chart. Grounded in Cleveland & McGill's
graphical-perception experiments (via Munzner and Wilke), preattentive-processing research, and the
Gestalt principles as applied by Knaflic.

## The accuracy ranking (Cleveland & McGill)

When a reader decodes a quantity, accuracy depends on the channel used to encode it. Ranked from
most to least accurate for **quantitative** data:

1. **Position along a common scale** (e.g. dots/bars on a shared axis) — best
2. **Position along non-aligned scales** (small multiples with separate axes)
3. **Length** (bar length, with a shared baseline)
4. **Angle / slope** (pie slices, line steepness)
5. **Area** (bubble size, treemap tiles)
6. **Volume / depth** (3-D charts) — worst
7. **Color saturation / density** — poor for precise values, fine for rough/ordinal

**Implication:** prefer encodings near the top. This is *why* a sorted bar chart beats a pie chart,
*why* a dot plot beats a bubble chart for precise comparison, and *why* 3-D charts are almost always
wrong — they push you down the ranking and add occlusion for nothing.

> Rule with reason: "Don't size circles to show quantity" isn't aesthetic snobbery — area sits at
> rank 5, and readers systematically *under*-estimate large areas. If you must use area (e.g. a
> proportional-symbol map), scale by area not radius, and add labels.

## Channels for different data types

Match the channel to whether the data is **quantitative**, **ordered**, or **categorical**:

| Data type | Best channels | Avoid |
| --- | --- | --- |
| Quantitative (how much) | Position, length | Hue (no natural order) |
| Ordered / ordinal (ranked) | Position, sequential color (light→dark), size | Categorical hue |
| Categorical (which kind) | Spatial region, hue, shape | Length/size (implies magnitude) |

Using a categorical channel for quantities (e.g. color hue to show "more") or a quantitative channel
for categories (e.g. bar height to show "type") both mislead, because the reader's eye infers the
wrong kind of relationship.

## Preattentive attributes — directing the eye

Some visual properties are processed *before* conscious attention, in milliseconds, in parallel
across the whole field: **color (hue/intensity), form (size, shape, orientation, length, width),
position, and motion.** A single value differing in one of these "pops out."

Use this deliberately: to highlight one bar, one line, or one point, give it *one* preattentive
difference (usually color) while everything else stays neutral grey. This is how you make "the
point" findable in under a second. The corollary: if *everything* is colored/bold, *nothing* pops —
emphasis is a budget, spend it on one thing.

## Gestalt principles — how the eye groups

The visual system imposes structure automatically. Knaflic's six (from *Storytelling with Data*),
each with a charting use:

- **Proximity** — things near each other read as a group. Use whitespace/gaps to group bars or
  separate clusters; tighten spacing within a group, widen between groups.
- **Similarity** — same color/shape/size read as related. Color a category consistently across all
  charts in a report so the eye links them.
- **Enclosure** — a shaded box or border binds elements into a unit. Use a light shaded band to mark
  a region (a target zone, a recession period) without heavy lines.
- **Closure** — the eye completes shapes; you rarely need full borders/gridlines around a plot.
  Remove the chart frame; the data implies it.
- **Continuity** — the eye follows lines and aligned edges. Align elements to invisible axes;
  ragged alignment reads as unrelated.
- **Connection** — connected elements read as most strongly related, stronger than similarity or
  proximity. A line *connecting* points groups them harder than coloring them the same; this is why
  connected scatter plots and slope charts are powerful.

## Banking to 45° (line/scatter aspect ratio)

The judged steepness of a trend depends on the chart's aspect ratio. Cleveland's finding: people
read slopes most accurately when the *average line segment* is oriented near 45°. A trend squeezed
into a tall narrow panel looks dramatic; stretched wide, it looks flat. Choose the aspect ratio
honestly for the comparison you want readers to make, and be aware that resizing a chart silently
changes the perceived message.

## Practical encoding checklist

```
[ ] Quantities encoded by position or length, not area/angle/volume?
[ ] At most one preattentive cue (usually color) carrying emphasis?
[ ] Everything not being emphasized rendered neutral (grey)?
[ ] Categorical = hue; ordered/quantitative = position/length/sequential color?
[ ] Gridlines/frames minimized (closure does the work)?
[ ] Aspect ratio chosen for honest slope perception, not drama?
```

Sources: Cleveland & McGill graphical-perception ranking (via Munzner *Visualization Analysis &
Design* and Wilke *Fundamentals of Data Visualization*); preattentive processing (Few, Ware);
Gestalt principles as applied in Knaflic *Storytelling with Data*; banking-to-45° (Cleveland).
