# Decluttering & Graphical Integrity

Two disciplines that separate amateur charts from professional ones: **removing everything that
isn't communicating** (Tufte's data-ink, Knaflic's clutter), and **never letting the graphic say
something the data doesn't** (Tufte's graphical integrity, Cairo's truthfulness). The first is about
clarity; the second is about ethics. Both are non-negotiable for business reporting.

## Part 1 — Decluttering

### Data-ink ratio (Tufte)

> data-ink ratio = ink used to show data ÷ total ink

Maximize it, within reason. Every pixel that isn't data should justify itself; most don't. Tufte's
imperative: *erase non-data-ink, erase redundant data-ink, then revise.* The reasoning: each
non-data mark is something the reader's eye must process and discard, so clutter is a tax on
comprehension.

**Chartjunk** is the name for the worst offenders — decorative elements that add no information and
often distort: 3-D effects, drop shadows, gradient fills, background images, heavy gridlines, moiré
patterns, clip-art "infographic" icons sized to encode numbers.

### What to remove (in order)

1. **3-D, shadows, bevels, gradients** — pure distortion and noise.
2. **Heavy or dark gridlines** — make them faint grey or remove them; closure (perception file) means
   the eye doesn't need a full grid.
3. **Chart borders and plot frames** — usually unnecessary.
4. **Redundant axes/labels** — if bars are directly labeled with values, you may not need the axis at
   all.
5. **Legends** — replace with direct labels on the data wherever possible; a legend forces the eye to
   travel and translate.
6. **Tick marks and excessive precision** — "$1,234,567.89" where "$1.2M" communicates.
7. **Redundant data-ink** — e.g. a bar that's also labeled and also gridline-pinned; pick one.

The test for any element: *if I delete this, is any information lost?* If not, delete it.

### Decluttering is not minimalism for its own sake

The goal is clarity, not the lowest possible ink. Keep annotations, reference lines, and direct
labels that *help* the reader — those are high-value ink. Setlur & Cogley's "functional aesthetics"
point: beauty and function reinforce each other when the styling serves comprehension; strip the
decorative, keep the communicative.

## Part 2 — Graphical integrity

Cairo's first quality of a great visualization is **truthful**. A chart can be technically accurate
in every data point and still mislead through framing. Tufte's **Lie Factor** quantifies it:

> Lie Factor = (size of effect shown in graphic) ÷ (size of effect in the data)

A lie factor far from 1.0 means the graphic exaggerates or understates. Common ways it goes wrong:

### Axis manipulation

- **Truncated bar baseline.** Bars encode value as *length*, so the baseline must be **zero** — start
  a bar axis at 90 and a 91-vs-99 difference looks 9× bigger than it is. This is the most common
  integrity failure in business decks.
- **Line charts are the opposite.** They encode *position/slope*, not length, so a non-zero baseline
  is legitimate and often necessary — forcing a line axis to zero can flatten a real, decision-
  relevant trend into a flat line. Choose the range honestly for the question.
- **Inverted or broken axes.** Reversing an axis or inserting a break can flip the apparent story;
  use only with an unmistakable visual cue, and rarely.

### Dual axes

Plotting two series against two different y-scales lets you "prove" a correlation by sliding the
scales until the lines track. Readers can't see that you chose the alignment. Prefer: index both
series to 100 at a common start point and plot on one axis, or use two stacked panels (small
multiples) sharing the x-axis.

### Proportion and area

- **Area/bubble by radius** doubles the radius for a 2× value and shows a 4× blob — see
  perception-and-encoding.md. Scale by area.
- **Pictographs sized by height** but drawn as 2-D images grow in area too, exaggerating the same way.

### Scale and selection

- **Cherry-picked time ranges** — starting a trend at a convenient peak or trough. Show enough
  context that the reader sees the real baseline.
- **Unlabeled log scales** — legitimate for wide-ranging or multiplicative data, but a log axis read
  as linear wildly misleads. Label it clearly.
- **Per-capita vs. raw counts** — a choropleth of raw counts mostly maps population; normalize to a
  rate when comparing places or groups.
- **Correlation presented as causation** — a trend line or two adjacent series implies a causal claim
  you may not have earned. Say what you actually know.

## Integrity checklist

```
[ ] Bar charts start at zero; line-chart range chosen honestly (not forced to zero, not cherry-picked)?
[ ] No dual axes (or replaced with indexed series / small multiples)?
[ ] Quantities by length/position, not area/volume; any area scaled by area not radius?
[ ] Time range / data selection shows enough context to be fair?
[ ] Log or non-linear scales clearly labeled?
[ ] Counts normalized to rates where comparing populations?
[ ] No causal language the data doesn't support?
[ ] Lie Factor ≈ 1: the visual magnitude of the effect matches the real one?
```

Sources: Tufte *The Visual Display of Quantitative Information* (data-ink ratio, chartjunk, lie
factor — foundational, referenced via the survey literature); Knaflic *Storytelling with Data*
(declutter, cognitive load); Cairo *The Truthful Art* / *The Functional Art* (truthfulness as the
first quality); Setlur & Cogley *Functional Aesthetics for Data Visualization*.
