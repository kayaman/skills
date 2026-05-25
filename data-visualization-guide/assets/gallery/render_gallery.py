#!/usr/bin/env python3
"""Render every example in references/chart-gallery.md.

Each function below is the *exact* source for one gallery image; the markdown
reproduces these bodies verbatim. Run from anywhere:

    python3 render_gallery.py        # writes PNGs next to this file

All examples apply the skill's own defaults: grey by default with a single
highlight color, zero baseline for bars, direct labels over legends,
decluttered spines, and a takeaway title.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
GREY, ACCENT, INK = "#bdbdbd", "#c0392b", "#333333"


def style(ax, title, drop=("top", "right")):
    """Shared decluttering: drop frame spines, mute ticks, takeaway title."""
    for s in drop:
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    ax.set_title(title, loc="left", fontsize=13, weight="bold", color=INK)


# 1 — Compare values across categories -> sorted horizontal bar
def comparison_bar():
    cats = ["Email", "Organic", "Paid social", "Referral", "Direct", "Affiliate"]
    rev = [820, 760, 540, 410, 360, 120]  # $K
    order = np.argsort(rev)               # ascending -> largest on top in barh
    cats = [cats[i] for i in order]
    rev = [rev[i] for i in order]
    colors = [ACCENT if c == "Email" else GREY for c in cats]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(cats, rev, color=colors)
    ax.set_xlim(0, max(rev) * 1.12)       # bars start at zero
    for y, v in enumerate(rev):
        ax.text(v + 12, y, f"${v}K", va="center", fontsize=10, color=INK)
    ax.set_xticks([])
    style(ax, "Email drives the most revenue of any channel", drop=("top", "right", "bottom"))
    fig.tight_layout(); fig.savefig(f"{OUT}/comparison-bar.png", dpi=120); plt.close(fig)


# 2 — Change over time -> line with direct end-labels
def trend_line():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    series = {"New": [40, 44, 48, 53, 61, 72], "Returning": [60, 59, 58, 57, 56, 55]}
    fig, ax = plt.subplots(figsize=(8, 4))
    for name, vals in series.items():
        color = ACCENT if name == "New" else GREY
        ax.plot(months, vals, lw=2.5, color=color)
        ax.text(len(months) - 0.9, vals[-1], f"  {name}", va="center", color=color, weight="bold")
    ax.margins(x=0.02)
    style(ax, "New customers overtook returning in May")
    fig.tight_layout(); fig.savefig(f"{OUT}/trend-line.png", dpi=120); plt.close(fig)


# 3 — Part-to-whole -> stacked bars (composition over time)
def part_to_whole():
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    seg = {"Enterprise": [30, 34, 40, 46], "Mid-market": [40, 41, 39, 38], "SMB": [30, 25, 21, 16]}
    palette = {"Enterprise": ACCENT, "Mid-market": "#7f8c8d", "SMB": "#cfd2d4"}
    fig, ax = plt.subplots(figsize=(8, 4))
    bottom = np.zeros(len(quarters))
    for name, vals in seg.items():
        ax.bar(quarters, vals, bottom=bottom, color=palette[name], width=0.6, label=name)
        for i, v in enumerate(vals):                       # direct in-segment labels
            ax.text(i, bottom[i] + v / 2, f"{v}%", ha="center", va="center",
                    color="white" if name == "Enterprise" else INK, fontsize=9)
        bottom += np.array(vals)
    ax.set_ylim(0, 100); ax.set_yticks([])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=3, frameon=False)
    style(ax, "Enterprise is taking a growing share of revenue")
    fig.tight_layout(); fig.savefig(f"{OUT}/part-to-whole.png", dpi=120); plt.close(fig)


# 4 — Rank items -> ordered lollipop
def ranking_lollipop():
    items = ["Checkout", "Search", "Onboarding", "Billing", "Profile",
             "Notifications", "Reports", "Export", "Settings", "Help"]
    score = [92, 88, 81, 67, 63, 58, 55, 49, 41, 38]
    order = np.argsort(score)
    items = [items[i] for i in order]; score = [score[i] for i in order]
    colors = [ACCENT if s < 50 else GREY for s in score]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hlines(items, 0, score, color=colors, lw=2)
    ax.plot(score, items, "o", color="none")
    for i, (s, c) in enumerate(zip(score, colors)):
        ax.plot(s, i, "o", color=c, ms=9)
        ax.text(s + 1.5, i, str(s), va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 100); ax.set_xticks([])
    style(ax, "Three features score below 50 on satisfaction", drop=("top", "right", "bottom"))
    fig.tight_layout(); fig.savefig(f"{OUT}/ranking-lollipop.png", dpi=120); plt.close(fig)


# 5 — Distribution of one variable -> histogram
def distribution_histogram():
    rng = np.random.default_rng(7)
    data = np.concatenate([rng.normal(45, 8, 600), rng.normal(78, 6, 220)])  # bimodal
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(data, bins=30, color=GREY, edgecolor="white")
    ax.axvline(float(np.median(data)), color=ACCENT, lw=2)
    ax.text(float(np.median(data)) + 1, ax.get_ylim()[1] * 0.9, "median",
            color=ACCENT, weight="bold")
    ax.set_xlabel("Response time (ms)")
    style(ax, "Response times are bimodal — a fast and a slow cluster")
    fig.tight_layout(); fig.savefig(f"{OUT}/distribution-histogram.png", dpi=120); plt.close(fig)


# 6 — Compare distributions across groups -> box + jittered points
def distribution_box():
    rng = np.random.default_rng(3)
    groups = ["Control", "Variant A", "Variant B"]
    data = [rng.normal(m, s, n) for m, s, n in [(50, 10, 80), (54, 11, 80), (62, 9, 80)]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bp = ax.boxplot(data, vert=True, patch_artist=True, widths=0.5,
                    medianprops=dict(color=INK), showfliers=False)
    for i, box in enumerate(bp["boxes"]):
        box.set(facecolor=ACCENT if i == 2 else GREY, edgecolor=INK, alpha=0.85)
    for i, d in enumerate(data):                        # jittered raw points
        x = rng.normal(i + 1, 0.05, len(d))
        ax.plot(x, d, "o", ms=3, color=INK, alpha=0.25)
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels(groups)
    ax.set_ylabel("Conversion (%)")
    style(ax, "Variant B lifts conversion and the whole distribution shifts up")
    fig.tight_layout(); fig.savefig(f"{OUT}/distribution-box.png", dpi=120); plt.close(fig)


# 7 — Relationship between two measures -> scatter (with overplotting handled)
def relationship_scatter():
    rng = np.random.default_rng(11)
    x = rng.gamma(4, 350, 1200)
    y = 20 + 0.02 * x + rng.normal(0, 6, 1200)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(x, y, s=14, color=ACCENT, alpha=0.18, edgecolors="none")  # alpha for overplot
    ax.set_xlabel("Monthly spend ($)"); ax.set_ylabel("Engagement score")
    style(ax, "Engagement rises steadily with monthly spend")
    fig.tight_layout(); fig.savefig(f"{OUT}/relationship-scatter.png", dpi=120); plt.close(fig)


# 8 — Deviation from a target -> diverging bar around zero
def deviation_diverging():
    regions = ["West", "North", "Central", "South", "East", "APAC"]
    delta = [-8, -3, 1, 4, 9, 12]   # percentage points vs target
    order = np.argsort(delta)
    regions = [regions[i] for i in order]; delta = [delta[i] for i in order]
    colors = [ACCENT if d < 0 else "#7f8c8d" for d in delta]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(regions, delta, color=colors)
    ax.axvline(0, color=INK, lw=1)
    for y, d in enumerate(delta):
        ax.text(d + (0.4 if d >= 0 else -0.4), y, f"{d:+d}", va="center",
                ha="left" if d >= 0 else "right", fontsize=9, color=INK)
    ax.set_xticks([])
    style(ax, "Two regions are below target; West trails by 8 points",
          drop=("top", "right", "bottom"))
    fig.tight_layout(); fig.savefig(f"{OUT}/deviation-diverging.png", dpi=120); plt.close(fig)


# ---------------------------------------------------------------------------
# Anti-examples: the same data shown wrong (left) vs. right (right).
# ---------------------------------------------------------------------------

# A1 — Truncated bar baseline exaggerates a tiny difference
def integrity_truncated_axis():
    teams = ["A", "B", "C", "D"]
    vals = [96, 94, 97, 95]
    fig, (bad, good) = plt.subplots(1, 2, figsize=(10, 4))
    bad.bar(teams, vals, color=ACCENT)
    bad.set_ylim(90, 98)                       # the lie: baseline at 90
    bad.set_title("Misleading: y-axis starts at 90", loc="left", color=ACCENT, weight="bold")
    good.bar(teams, vals, color=GREY)
    good.set_ylim(0, 100)                       # honest: bars encode length from zero
    good.set_title("Honest: zero baseline", loc="left", color=INK, weight="bold")
    for ax in (bad, good):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
    fig.suptitle("Bars must start at zero — length IS the value", x=0.02, ha="left",
                 fontsize=13, weight="bold", color=INK)
    fig.tight_layout(); fig.savefig(f"{OUT}/integrity-truncated-axis.png", dpi=120); plt.close(fig)


# A2 — Dual axes manufacture a correlation; index to 100 instead
def integrity_dual_axis():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    revenue = [120, 130, 125, 140, 150, 160]       # $K, +33%
    visits = [800, 870, 890, 1020, 1100, 1180]     # site visits, +47% — same data in both panels
    fig, (bad, good) = plt.subplots(1, 2, figsize=(10, 4))
    # BAD: dual axes; each axis auto-scales to its own range, overlaying the lines so two
    # series that grow at *different* rates look like they move in lockstep ("proving" a link).
    bad.plot(months, revenue, color=ACCENT, lw=2.5)
    twin = bad.twinx()
    twin.plot(months, visits, color="#2c7fb8", lw=2.5)
    bad.set_title("Misleading: dual axes 'prove' a link", loc="left", color=ACCENT, weight="bold")
    # GOOD: index both to 100 at the start, one axis — the different slopes become visible.
    rev_idx = [100 * v / revenue[0] for v in revenue]
    vis_idx = [100 * v / visits[0] for v in visits]
    good.plot(months, rev_idx, color=ACCENT, lw=2.5)
    good.plot(months, vis_idx, color="#2c7fb8", lw=2.5)
    good.text(5, rev_idx[-1], "  Revenue", color=ACCENT, va="center", weight="bold")
    good.text(5, vis_idx[-1], "  Visits", color="#2c7fb8", va="center", weight="bold")
    good.axhline(100, color=GREY, lw=1)
    good.margins(x=0.12)
    good.set_title("Honest: indexed to 100, one axis", loc="left", color=INK, weight="bold")
    for ax in (bad, twin, good):
        ax.spines["top"].set_visible(False)
        ax.tick_params(length=0)
    fig.tight_layout(); fig.savefig(f"{OUT}/integrity-dual-axis.png", dpi=120); plt.close(fig)


# A3 — Rainbow (jet) invents bands; viridis is perceptually uniform
def color_jet_vs_viridis():
    x = np.linspace(-3, 3, 200)
    field = np.exp(-(x[:, None] ** 2 + x[None, :] ** 2) / 4)   # smooth gradient, no real bands
    fig, (bad, good) = plt.subplots(1, 2, figsize=(10, 4.2))
    bad.imshow(field, cmap="jet"); bad.set_title("Misleading: 'jet' invents bands",
                                                  loc="left", color=ACCENT, weight="bold")
    good.imshow(field, cmap="viridis"); good.set_title("Honest: 'viridis' is uniform",
                                                        loc="left", color=INK, weight="bold")
    for ax in (bad, good):
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Same smooth gradient — rainbow fabricates edges that aren't in the data",
                 x=0.02, ha="left", fontsize=13, weight="bold", color=INK)
    fig.tight_layout(); fig.savefig(f"{OUT}/color-jet-vs-viridis.png", dpi=120); plt.close(fig)


# A4 — Chartjunk vs. decluttered: identical data
def declutter_before_after():
    cats = ["North", "South", "East", "West", "Central"]
    vals = [118, 109, 104, 92, 101]
    fig, (bad, good) = plt.subplots(1, 2, figsize=(10, 4.2))
    # BAD: rainbow bars, heavy grid, dark frame, redundant legend, 3-D-ish edges
    palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
    bad.bar(cats, vals, color=palette, edgecolor="black", linewidth=1.5, hatch="//",
            label="quota %")
    bad.grid(True, color="grey", linewidth=1.2)
    bad.set_facecolor("#eaeaea")
    bad.legend(loc="upper right")
    bad.set_title("Cluttered", loc="left", color=ACCENT, weight="bold")
    # GOOD: sorted, grey + one highlight, direct labels, zero baseline, decluttered
    order = np.argsort(vals)
    c2 = [cats[i] for i in order]; v2 = [vals[i] for i in order]
    colors = [ACCENT if c == "West" else GREY for c in c2]
    good.barh(c2, v2, color=colors)
    good.axvline(100, color="#666666", lw=1)
    for y, v in enumerate(v2):
        good.text(v + 1, y, f"{v}%", va="center", fontsize=9, color=INK)
    good.set_xlim(0, max(v2) * 1.12); good.set_xticks([])
    for s in ("top", "right", "bottom"):
        good.spines[s].set_visible(False)
    good.tick_params(length=0)
    good.set_title("Decluttered: West missed quota", loc="left", color=INK, weight="bold")
    fig.tight_layout(); fig.savefig(f"{OUT}/declutter-before-after.png", dpi=120); plt.close(fig)


if __name__ == "__main__":
    for fn in (comparison_bar, trend_line, part_to_whole, ranking_lollipop,
               distribution_histogram, distribution_box, relationship_scatter,
               deviation_diverging,
               integrity_truncated_axis, integrity_dual_axis,
               color_jet_vs_viridis, declutter_before_after):
        fn()
        print("rendered", fn.__name__)
