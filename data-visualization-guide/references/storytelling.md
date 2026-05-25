# Data Storytelling & Presenting

A chart informs; a *story* drives a decision. For business and analytics work the deliverable is
usually not a chart but a recommendation a chart supports. This file covers turning analysis into a
narrative — for a slide, a report, or a live presentation. Grounded in Knaflic *Storytelling with
Data*, Dykes *Effective Data Storytelling*, Berinato *Good Charts*, and Duarte *Resonate*.

## The equation (Dykes)

> Data storytelling = Data + Narrative + Visuals

- **Data** alone informs but doesn't move anyone.
- **Data + visuals** enlightens (a good chart).
- **Data + narrative** engages but may not stick without proof.
- **All three** drives *change* — which is the actual goal.

The narrative is the connective tissue: it tells the audience *why these numbers matter* and *what
to do*. If your output is a wall of charts with no through-line, you've stopped at "enlighten."

## Start from the audience and the ask (Knaflic, lesson 1)

Before designing anything, answer:

1. **Who** is the audience? (Their role, what they care about, what they already believe.)
2. **What** do you need them to know or do? State it as an action: "approve the budget,"
   "reprioritize the roadmap," "stop the campaign."
3. **How** does the data support that?

Knaflic's **3-minute story / Big Idea** test: can you state, in one sentence, the single thing the
audience must take away? Duarte calls this the **Big Idea** — it must (a) articulate your point of
view, (b) convey what's at stake, and (c) be a complete sentence. If you can't write it, the
presentation has no spine yet.

## Exploratory vs. explanatory (the key distinction)

- **Exploratory** analysis is for *you* — finding what's interesting. Many charts, fast, ugly is
  fine. (Berinato's "visual discovery" / "idea generation" quadrants.)
- **Explanatory** communication is for *them* — presenting the one or few things worth their
  attention. Few polished charts, each making a point.

The cardinal error is showing your audience the exploratory pile. *You did the work of looking at 50
charts so they don't have to.* Pick the few that make the case and discard the rest. Berinato's 2×2
(conceptual vs. data-driven × declarative vs. exploratory) is a useful map: most business
deliverables are **declarative + data-driven** = "everyday dataviz," where clarity and a single
point matter most.

## Narrative structure

Borrow the shape of a story:

- **Setup / context** — the situation, the relevant baseline, why we're looking.
- **Tension / insight** — what changed, what's surprising, the gap between expectation and reality.
  This is the heart; lead with it if the audience is impatient (the "BLUF" — bottom line up front).
- **Resolution / call to action** — what it means and what to do.

Duarte's contrast structure ("what is" vs. "what could be," repeated) builds momentum toward the
call to action. For executive audiences, invert to **answer-first**: state the recommendation, then
support it — they'll ask for the backup, not the buildup.

## Make each chart carry its message

- **Title = takeaway.** Write the conclusion as the title: "Onboarding time dropped 40% after the
  redesign," not "Onboarding time by month." The reader should get the point from the title alone;
  the chart proves it.
- **One message per chart.** If a slide needs two takeaways, split it.
- **Annotate the insight.** Add a short text note pointing at the exact bar/point that matters
  ("← launch"). The annotation layer is where narrative meets the data.
- **Highlight with color, mute the rest.** Use the preattentive "one thing pops" technique
  (see [perception-and-encoding.md](perception-and-encoding.md)) so the eye lands on the point.
- **Direct-label** instead of legends so the audience never has to decode while you talk.
- **Pace the reveal** in live presentations: build a chart up (show context, then add the
  highlighted series) so attention follows your words rather than racing ahead.

## Titles, labels, and legends (best practices)

The text on a chart is part of the message, not afterthought. Get these right and the chart reads
itself.

**Titles & subtitles**

- Make the **title the takeaway**, phrased as a complete sentence with the direction and the number
  ("Revenue fell 12% after the May price change"). A label-style title ("Revenue by month") wastes
  the most-read line on the chart.
- Use a **subtitle** for the supporting context the title can't carry — the metric definition, units,
  time range, or population ("Monthly recurring revenue, USD, all paid plans").
- Add a small, muted **source/footnote line** ("Source: billing system, pulled 2026-05-01;
  excludes refunds"). Credibility and reproducibility cost one grey line.
- **Left-align** the title block. Readers scan from the left edge; centered titles drift away from
  where the eye starts.

**Legends vs. direct labeling**

- **Prefer direct labels** on the data — at the end of each line, inside or beside each bar. A legend
  forces the eye to ping-pong between a key and the marks and to hold a color→name mapping in working
  memory (Hick's/Miller's load). Direct labels remove both.
- When a legend is unavoidable (e.g. a scatter with many categories), **place it close to the data**
  and **order it to match the visual order** of the series — top-to-bottom in the same order the
  lines end, not alphabetically. A legend whose order contradicts the chart adds a decoding step.
- **Color the legend text** (or the label) to match its series, so the link is preattentive rather
  than positional.

**Annotation layer**

- The annotation layer is where narrative meets the data. Add a **short callout on the specific mark
  that matters** ("← price change"), a **reference/target line** with a label, or a shaded band for
  a period (a recession, a campaign window — Gestalt enclosure).
- Annotate the *insight*, not everything. One or two notes guide; ten notes are clutter.

## Slides and reports

- Slides are **projected, glanced at, and talked over** — bigger fonts, fewer elements, one chart
  per slide, the takeaway as the slide title. Garr Reynolds / Duarte: the slide supports the
  speaker, it is not the document.
- Reports are **read alone** — they can carry more density, footnotes, and a methods note, because
  there's no narrator. A chart that works on a slide may be too sparse for a standalone report and
  vice versa. Design for the medium.
- Either way, **end on the action**, not the last chart.

## Worked micro-example

Raw finding: "Q3 churn was 5.2%, up from 4.1% in Q2; most of the increase came from the SMB tier."

- **Weak:** a slide titled "Churn by Quarter and Segment" with a grouped bar chart, legend on the
  right, all bars colored, no annotation. The audience has to find the story.
- **Strong:** a slide titled "SMB churn drove a 27% jump in Q3 — recommend a retention play there."
  A small-multiples panel by segment with the SMB panel's Q3 bar in red and the rest grey, a one-
  line annotation on that bar, and a closing line stating the recommended action. Same data; now it
  drives a decision.

## Checklist

```
[ ] Audience and the specific action they should take are named?
[ ] Big Idea written as one complete sentence?
[ ] Showing the few explanatory charts, not the exploratory pile?
[ ] Each chart's title states its takeaway?
[ ] One message per chart; insight annotated; emphasis via color?
[ ] Structure leads to a call to action (answer-first for execs)?
[ ] Designed for the medium (slide vs. read-alone report)?
```

Sources: Knaflic *Storytelling with Data* (audience, Big Idea, explanatory vs. exploratory);
Dykes *Effective Data Storytelling* (data+narrative+visuals); Berinato *Good Charts* (the 2×2
typology); Duarte *Resonate* (Big Idea, contrast structure).
