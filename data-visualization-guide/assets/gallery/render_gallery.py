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


if __name__ == "__main__":
    for fn in (comparison_bar, trend_line, part_to_whole, ranking_lollipop,
               distribution_histogram, distribution_box, relationship_scatter,
               deviation_diverging):
        fn()
        print("rendered", fn.__name__)
