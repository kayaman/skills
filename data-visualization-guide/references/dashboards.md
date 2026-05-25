# Dashboards & Monitoring Views

A dashboard is not a report and not a collection of charts — it is a **single-screen, at-a-glance
display of the information needed to monitor something and act**. Most "dashboards" fail because
they're really cluttered report dumps. Grounded in Stephen Few's dashboard work, Khan's *Visual
Analytics for Dashboards*, and Shneiderman's interaction mantra.

## Few's definition and the core constraint

> A dashboard is a visual display of the most important information needed to achieve one or more
> objectives, consolidated on a single screen so it can be monitored at a glance.

Three load-bearing words:

- **Single screen** — if the user must scroll or page to see it all, the at-a-glance property is
  gone. Ruthlessly prioritize; everything competes for one screen.
- **At a glance** — the design must yield its message in seconds, which forces high data-ink, no
  decoration, and strong visual hierarchy.
- **Monitor / act** — a dashboard exists to prompt action (notice a problem, drill in). If nothing
  on it would ever change a decision, it's a vanity display.

## Decide the type first

- **Strategic** (exec/KPI): a few high-level metrics, trend + comparison to target, low interactivity,
  refreshed daily/weekly.
- **Operational** (monitoring): real-time, alerting, "is anything on fire right now," needs fast
  noticing of out-of-range values.
- **Analytical** (exploration): supports drill-down, filtering, comparison; more interactivity, the
  user investigates *why*.

The type sets density, refresh rate, and how much interaction to build. Mixing them on one screen is
a common failure.

## Layout and hierarchy

- **Most important, top-left.** Reading order (in LTR cultures) is top-left to bottom-right; put the
  headline metric where the eye lands first. Khan and Few both stress an explicit visual hierarchy.
- **Group related metrics** using proximity and enclosure (see perception-and-encoding.md), not heavy
  borders. White space is the primary structuring tool.
- **Consistent encodings across tiles** — the same color means the same thing everywhere on the
  dashboard, or the at-a-glance reading breaks.
- **Provide context, not bare numbers.** "Sales: $1.2M" is nearly useless; "$1.2M, 8% below target,
  trending down 3 weeks" prompts action. Pair each metric with comparison (vs. target / prior period)
  and a micro-trend.

## Use compact, high-density widgets

Few designed several idioms specifically for dashboards:

- **Sparklines** — word-sized line charts showing trend without axes; ideal next to a KPI number.
- **Bullet graphs** — a compact bar + target marker + qualitative bands; replace gauges and
  speedometers, which waste enormous space for one value.
- **Small multiples** — repeated mini-charts for comparing many series in little space.
- **In-cell bars / heat-tables** — tables augmented with embedded magnitude cues for operational
  lookups.

Avoid the dashboard anti-patterns Few is famous for criticizing: **gauges, speedometers, traffic
lights as the main display, 3-D, gratuitous color, and decorative skeuomorphism.** They consume
pixels and attention far out of proportion to the single number they convey.

## Interaction (Shneiderman's mantra)

For analytical dashboards, structure interaction as:

> **Overview first, zoom and filter, then details on demand.**

Show the whole picture, let the user narrow (filter, brush, select a range), and reveal detail
(tooltips, drill-through) only when requested — rather than dumping everything up front. This keeps
the default view at-a-glance while supporting investigation.

## Alerting and exceptions

Operational dashboards should make out-of-range values *pop* via a single preattentive cue (color,
position), with everything in-range muted. Don't color every cell by status — if everything is
red/amber/green, nothing stands out. Encode "needs attention" sparingly so it retains meaning.

## Checklist

```
[ ] Type chosen (strategic / operational / analytical) and design matched to it?
[ ] Fits one screen without scrolling for the core view?
[ ] Most important metric top-left; clear visual hierarchy?
[ ] Each metric paired with context (target, prior period, trend)?
[ ] Compact widgets (sparklines, bullet graphs) instead of gauges/3-D?
[ ] Consistent color meaning across all tiles?
[ ] Exceptions pop via one preattentive cue; in-range muted?
[ ] Interaction follows overview → zoom/filter → details on demand?
```

Sources: Stephen Few, *Information Dashboard Design* (definition, bullet graphs, sparklines,
anti-patterns); Khan *Visual Analytics for Dashboards* (types, layout, hierarchy); Shneiderman's
visual-information-seeking mantra.
