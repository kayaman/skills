---
name: data-visualization-guide
description: >
  Guidance for designing charts, graphs, plots, dashboards, and data visualizations that
  communicate clearly and persuade. Use when creating or reviewing a visualization, choosing a
  chart type, picking a color palette, decluttering a busy graphic, fixing misleading axes or
  proportions, building a dashboard, annotating a figure, or turning data into a presentation,
  report, or data-driven story. Grounded in the standard data-visualization literature (Knaflic,
  Tufte, Cleveland & McGill, Cairo, Wilke, Munzner, Few, Berinato). Covers chart selection,
  graphical perception and encoding, color and accessibility, decluttering, graphical integrity,
  dashboards, and narrative. Does NOT cover building data pipelines or ETL, statistical modeling
  or analysis methods, BI tool/vendor selection, or general UI/UX layout (see ux-design-principles).
  Tool-agnostic, with optional Python recipes.
license: MIT
metadata:
  author: kayaman
  version: "1.1.0"
  type: knowledge
  domain: data-visualization
---

# Data Visualization Guide

A decision framework for turning data into graphics that communicate. Optimized for **business and
analytics** work — reports, dashboards, slides, and the exec-facing "what should we do?" chart —
but the principles are tool-agnostic and apply in Tableau, Python, R, JavaScript, or a spreadsheet.

The guidance distills the standard literature on the subject. See [references/BOOKS.md](references/BOOKS.md)
for the fifteen books behind it (Knaflic, Wilke, Munzner, Cairo ×2, Dykes, Berinato, Camões,
Setlur & Cogley, Meirelles, Krum, Duarte, Dougherty & Ilyankou, Khan, Kirk) and which file draws
on each.

These are principles of human perception and communication, not chart-tool trends. They hold
regardless of library or era.

## When to use

- Creating a chart, graph, plot, map, or infographic from data
- Reviewing or critiquing an existing visualization
- Choosing *which* chart type fits a question and a dataset
- Picking or fixing colors, axes, scales, labels, or annotations
- Designing a dashboard or a single-screen monitoring view
- Turning analysis into a presentation, report, or data story that drives a decision

## When NOT to use

- Building data pipelines, ETL, or wrangling raw data into shape
- Statistical modeling, hypothesis testing, or choosing analysis methods
- Selecting a BI platform or visualization vendor
- General interface layout, navigation, or interaction design — use `ux-design-principles`

## The core idea

A visualization is an act of **communication, not decoration**. Before drawing anything, you owe
three answers (Munzner's *what / why / how*):

1. **Who is the audience and what decision or insight is this for?** ("Why")
2. **What is the shape of the data?** (quantities, categories, time, parts, relationships, geography) ("What")
3. **What encoding shows that relationship most accurately to the human eye?** ("How")

Get 1 and 2 right and the chart type often picks itself. Get the encoding right and the reader sees
the point without effort. Everything else in this skill serves those three questions.

> **Explain-the-why runs throughout.** Each rule is paired with the reason behind it, so you can
> apply it to cases this guide never anticipated. A rule you can't justify is one you'll
> misapply.

## Workflow

Use this loop when **producing** a visualization. Paste it and tick boxes for any non-trivial chart.

```
[ ] 1. State the question/decision in one sentence. Name the audience.
[ ] 2. Identify the data shape (see references/chart-selection.md).
[ ] 3. Pick the chart family from intent + data shape.
[ ] 4. Choose the encoding for accuracy (references/perception-and-encoding.md).
[ ] 5. Declutter: remove anything that isn't data or doesn't aid reading (references/decluttering-and-integrity.md).
[ ] 6. Direct attention: title states the takeaway; color/annotation highlight the point.
[ ] 7. Check integrity: axes, scales, proportions honest? (references/decluttering-and-integrity.md).
[ ] 8. Check accessibility: colorblind-safe, labeled, sufficient contrast (references/color-and-accessibility.md).
[ ] 9. Re-read as the audience. Is the message obvious in 5 seconds?
```

When **reviewing** a visualization, run the loop backwards as a critique: does the title carry a
message? Could a different encoding be read more accurately? Is any ink not earning its place? Is
anything misleading? Adopt a reviewer persona — *you are a data-viz editor whose job is to make the
single most important point land truthfully.*

## Reference map (load on demand)

Read the file that matches the task — don't load all of them at once.

| You need to… | Read |
| --- | --- |
| See the right chart for a situation, with a rendered example + code | [references/chart-gallery.md](references/chart-gallery.md) |
| Pick a chart type from the data and the question | [references/chart-selection.md](references/chart-selection.md) |
| Choose encodings the eye reads accurately; preattentive cues; Gestalt grouping | [references/perception-and-encoding.md](references/perception-and-encoding.md) |
| Choose a color palette; ensure colorblind safety and contrast | [references/color-and-accessibility.md](references/color-and-accessibility.md) |
| Strip clutter and keep the chart honest (axes, proportions) | [references/decluttering-and-integrity.md](references/decluttering-and-integrity.md) |
| Build a narrative, slide, or data story that drives action | [references/storytelling.md](references/storytelling.md) |
| Design a dashboard or single-screen monitoring view | [references/dashboards.md](references/dashboards.md) |
| Format titles & legends; annotate (titles/legends → storytelling; axes/numbers/gridlines/typography → decluttering; palettes → color) | [references/storytelling.md](references/storytelling.md), [references/decluttering-and-integrity.md](references/decluttering-and-integrity.md), [references/color-and-accessibility.md](references/color-and-accessibility.md) |
| Apply the principles in code (matplotlib / plotly / Vega-Lite) | [references/recipes-python.md](references/recipes-python.md) |
| See the source books and what each contributes | [references/BOOKS.md](references/BOOKS.md) |

## Fast defaults

When you have no time to read further, these defaults are right far more often than not. Each links
to the file that explains *why* and when to break it.

- **Comparing values across categories → horizontal bar chart**, sorted by value (not alphabetically).
  Bars encode magnitude as *length/position*, the most accurately read channel.
- **Change over time → line chart.** Time on x, one line per series; label lines directly instead of
  a legend.
- **Part-to-whole → stacked bar or just a bar chart of the parts.** Avoid pie charts beyond ~2–3
  slices; angle and area are read poorly (see perception file).
- **Relationship between two measures → scatter plot.** Add a trend line only if you mean it.
- **Distribution → histogram (one variable) or box/violin (comparing groups).**
- **Bar charts start at zero**, always — bar length *is* the value, so a clipped baseline lies.
  Line charts may use a non-zero baseline because they encode *position/slope*, not length.
- **One message per chart.** If it needs two takeaways, it's two charts.
- **The title is the takeaway**, written as a sentence ("Revenue fell 12% after the May price
  change"), not a label ("Revenue over time").
- **Default to a colorblind-safe, perceptually-uniform palette** (e.g. viridis for sequential).
  Never encode meaning by color alone.
- **Grey by default, one accent color** for the thing that matters; **direct-label** series instead
  of a legend; **round numbers** to what the decision needs ($1.2M, not $1,234,567); **faint or no
  gridlines.**

For a worked example of each situation above — rendered chart plus the exact code — see
[references/chart-gallery.md](references/chart-gallery.md).

## Known gotchas

Specific traps that look fine until someone is misled. Details and fixes in the linked files.

- **Truncated bar axis.** A bar chart not starting at zero exaggerates differences. (Line charts are
  the opposite — forcing zero can flatten a meaningful trend.) → [decluttering-and-integrity.md](references/decluttering-and-integrity.md)
- **Dual y-axes.** Two series on two scales invites readers to infer a correlation you manufactured
  by choosing the scales. Prefer indexed series or two stacked panels. → [decluttering-and-integrity.md](references/decluttering-and-integrity.md)
- **Rainbow / jet colormaps** create false boundaries and aren't perceptually uniform; the "bright
  band" looks like a feature in the data that isn't there. Use viridis/cividis. → [color-and-accessibility.md](references/color-and-accessibility.md)
- **Encoding quantity by area or radius.** Doubling a bubble's *radius* quadruples its area; readers
  under-read area by a known factor. Scale by area, and prefer length where you can. → [perception-and-encoding.md](references/perception-and-encoding.md)
- **Pie charts with many slices, or 3-D anything.** Angle, area, and volume sit at the bottom of the
  accuracy ranking; 3-D adds occlusion and perspective distortion for zero information. → [perception-and-encoding.md](references/perception-and-encoding.md)
- **Legends far from the data.** Forcing the eye to ping-pong between a legend and the plot adds
  cognitive load; label series directly. → [storytelling.md](references/storytelling.md)
- **Overplotting.** Thousands of opaque points become a blob. Use transparency, binning (hexbin),
  or sampling. → [chart-selection.md](references/chart-selection.md)
- **Cherry-picked ranges and unlabeled log scales.** Both are integrity failures even when each data
  point is accurate. → [decluttering-and-integrity.md](references/decluttering-and-integrity.md)

## A worked example (good vs. bad)

**Task:** "Show the board how our five regions performed against quota this quarter."

- **Bad:** A 3-D pie chart, one slice per region, rainbow colors, legend on the side, title "Regional
  Performance." The reader can't compare slice sizes (angle/area), the 3-D tilt distorts them
  further, and the title carries no message.
- **Good:** A horizontal bar chart, one bar per region showing *% of quota*, sorted descending, a
  reference line at 100%, the one region that missed quota colored to stand out and the rest in
  grey, every bar directly labeled, baseline at zero. Title: "Four of five regions beat quota; West
  missed by 8%." The encoding (length on a common scale) is the most accurate available, color
  directs attention to the single exception, and the title states the decision-relevant fact.

This is the whole method in miniature: right question → right data shape → most-accurate encoding →
declutter → direct attention → honest axis → takeaway title.
