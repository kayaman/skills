# Chart Selection

Pick a chart by answering two questions in order: **what relationship am I showing?** (intent) and
**what shape is the data?** Intent dominates — the same dataset becomes a different chart depending
on the point you're making. This taxonomy follows the *Financial Times* Visual Vocabulary and
Andy Kirk's "trifecta" of intent, plus Wilke's chart directory and Berinato's typology.

> For a rendered example and the exact code for each situation below, see
> [chart-gallery.md](chart-gallery.md).

## Step 1 — Classify the intent

Most business charts answer one of nine questions. Find yours:

| Intent | The question | Go-to charts |
| --- | --- | --- |
| **Magnitude** | How big, comparing absolute sizes? | Bar (horizontal preferred), dot plot, lollipop |
| **Change over time** | How does it trend? | Line, area (single series), slope chart, candlestick |
| **Ranking** | What's the order, who's top/bottom? | Sorted bar, ordered dot/lollipop, bump chart |
| **Part-to-whole** | What share of a total? | Stacked bar, bar of components, treemap; pie only for 2–3 parts |
| **Deviation** | How far above/below a reference? | Diverging bar, bullet graph, surplus/deficit fill |
| **Distribution** | How are values spread? | Histogram, box plot, violin, strip/beeswarm, ECDF |
| **Correlation / relationship** | Do two measures move together? | Scatter, bubble, connected scatter, heatmap |
| **Spatial** | Where, geographically? | Choropleth, symbol/proportional-symbol map, cartogram |
| **Flow** | How do things move between states? | Sankey, chord, network, alluvial |

> If you can't name the intent in one sentence, you're not ready to chart. Two intents = two charts.

## Step 2 — Confirm the data shape fits

| Data shape | Natural encodings | Watch out for |
| --- | --- | --- |
| 1 categorical + 1 quantity | Bar, dot plot | Sort by value; don't sort alphabetically unless the category has a natural order |
| 1 quantity over time | Line | Even time spacing; don't connect across gaps you didn't measure |
| 2 quantities | Scatter | Overplotting at scale; aspect ratio (see "banking" below) |
| 1 quantity, many observations | Histogram, box, violin | Bin width changes the story; show or justify it |
| 2 categoricals + 1 quantity | Heatmap, grouped/stacked bar | Too many cells become unreadable; consider small multiples |
| Nested categories + quantity | Treemap, sunburst, grouped bar | Hard to compare non-adjacent areas — prefer bars if precision matters |
| Geographic + quantity | Choropleth (rates), symbol map (counts) | Choropleth of raw counts just maps population; normalize to a rate |

## Step 3 — Apply the defaults and the exceptions

**Bar charts** are the workhorse because length on a common scale is the most accurately perceived
encoding (see [perception-and-encoding.md](perception-and-encoding.md)). Default to **horizontal** bars when category labels are
long or there are many categories — labels stay readable and the eye compares lengths easily.

**Line charts** for time, because the slope between adjacent points is the signal. Direct-label the
end of each line rather than using a legend. Limit to ~4–6 lines before it becomes a "spaghetti"
chart; for more series use small multiples (one mini-panel per series, shared axes).

**Pie / donut charts**: acceptable only for 2–3 categories where you're making a rough "about half"
point. Beyond that, angle and area defeat accurate comparison — use a sorted bar. Never explode,
3-D, or stack many thin slices.

**Scatter plots** for relationships. Add a regression/trend line *only* when you intend a claim
about the relationship, and remember correlation is not causation. For dense data, switch to
transparency, **hexbin**, or 2-D density.

**Small multiples** (a.k.a. trellis/facets) are the single most underused idiom: repeat the same
small chart across categories with shared scales. The eye compares panels effortlessly, and it
scales where overlaying series fails. Reach for this whenever a single chart is getting crowded.

## Maps & geospatial

Put data on a map only when **location is the point** — when the question is genuinely "where?"
Otherwise a sorted bar chart compares regions far more accurately than a map (which encodes value by
color or area, both low on the perception ranking). When geography *is* the message:

- **Choropleth (shaded regions): map rates, not counts.** A choropleth of raw counts mostly maps
  population — big or populous regions dominate regardless of the metric. Normalize to a rate or
  per-capita value first. Use a sequential palette (or diverging around a meaningful midpoint).
- **Proportional-symbol map for counts/totals.** When you must show absolute magnitudes, size a
  symbol by **area** (not radius — see [perception-and-encoding.md](perception-and-encoding.md)) over each location.
- **Classification changes the story.** How you bin values into color classes — equal-interval,
  quantile, or natural-breaks (Jenks) — can flip which regions look high or low. State the method;
  don't let a default quietly drive the conclusion.
- **Mind the projection and the area bias.** Map projections distort area (Mercator inflates high
  latitudes); large rural regions catch the eye even when little happens there. Consider a cartogram
  or tile/hex map when you need each unit to carry equal visual weight.

## Tables vs. charts

A **table** is the right choice when readers need to look up exact values, when there are very few
numbers, when units differ per row, or when the data will be *read* line by line. A **chart** wins
when the message is a pattern, comparison, or trend. Stephen Few's heuristic: use a table when the
display will be *read*; use a graph when it will be *perceived*.

When a table is right, format it so the numbers are scannable:

- **Right-align numbers and align on the decimal**, with a consistent number of decimals per column,
  so magnitudes line up vertically and the eye can compare digit columns. Left-align text.
- **Minimize rules and borders.** Whitespace and subtle row banding separate rows better than heavy
  gridlines (the same data-ink logic as charts — see [decluttering-and-integrity.md](decluttering-and-integrity.md)).
- **Sort meaningfully** (by the column that matters, not alphabetically) and keep a clear header;
  add a **summary/total row**, set off from the body.
- **Make it a hybrid where it helps:** embed **sparklines** (trend per row) or **in-cell bars /
  heat shading** (magnitude per cell) so an operational table is both lookup-able and perceivable.

## Avoid by default

- **Stacked area charts with many series** — only the bottom series has a flat baseline; the rest
  are nearly impossible to read.
- **Dual-axis charts** — see [decluttering-and-integrity.md](decluttering-and-integrity.md); the correlation is an artifact of your
  scale choices.
- **Radar/spider charts** — area is misleading and depends on the (arbitrary) ordering of axes.
- **Word clouds** — size encodes frequency by area and ignores meaning; almost never the best choice.
- **Gauges and speedometers on dashboards** — huge ink for one number; a bullet graph or a labeled
  number does it better (see [dashboards.md](dashboards.md)).

## Quick decision prompts

When unsure, ask yourself in order:
1. "Comparing categories?" → sorted bar.
2. "Over time?" → line.
3. "Relationship between two numbers?" → scatter.
4. "Spread of one number?" → histogram/box.
5. "Part of a whole, 2–3 parts?" → maybe pie; otherwise stacked bar.
6. "More than one of the above at once?" → split into multiple charts or small multiples.

Sources: Wilke *Fundamentals of Data Visualization* (chart directory); FT Visual Vocabulary lineage
via Kirk; Berinato *Good Charts*; Few on tables-vs-graphs; Cleveland on banking and small multiples.
