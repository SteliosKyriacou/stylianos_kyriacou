"""Redraw the AlphaForge agent-ablation box plots in the site's dark theme.

Output: assets/blog/bootstrapped_reasoning_ablation.png

The box statistics below are declared explicitly rather than recomputed from the
bootstrap arrays, so the figure is a pure restyle. Provenance of each number:

  * Medians are the values quoted in the post text (the authoritative source).
  * IQRs were recovered from the original 512x231 chart by pixel calibration
    against its gridlines, accurate to roughly +/-0.02.
  * Whiskers use the matplotlib 1.5*IQR convention. This reproduces the post's
    statement that the Opus 5 lower whisker "reaches down toward 0.55" (it
    lands at 0.548), which is a good independent check on the recovered IQRs.

If you still have the bootstrap arrays, prefer them: drop the SERIES medians and
iqrs, and pass the raw samples to ax.boxplot(...) with the same styling block.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- site design tokens -----------------------------------------------------
SURFACE = "#050505"  # matches body background in style.css
INK = "#f2f2f2"  # primary
INK_2 = "#a0a0a0"  # --text-secondary
GRID = "#232323"
AXIS = "#333333"

ACCENT = "#00f2fe"  # AlphaForge, full board  (site accent)
ACCENT_DIM = "#12879b"  # AlphaForge, ablated     (same hue, darker step)
NEUTRAL = "#898781"  # unassisted frontier models (de-emphasis gray)

CHANCE = 0.50

# label, colour, {metric: (median, iqr)}
SERIES = [
    ("AlphaForge (all agents)", ACCENT, {"ap": (0.89, 0.023), "roc": (0.90, 0.018)}),
    ("AlphaForge (only Chemistry)", ACCENT_DIM, {"ap": (0.72, 0.041), "roc": (0.74, 0.037)}),
    ("Claude Opus 5 (high)", NEUTRAL, {"ap": (0.59, 0.046), "roc": (0.63, 0.041)}),
    ("Gemini 3.1 Pro", NEUTRAL, {"ap": (0.53, 0.041), "roc": (0.57, 0.037)}),
]

PANELS = [("ap", "Average precision (PRC)"), ("roc", "ROC AUC")]


def stats(median, iqr):
    q1, q3 = median - iqr / 2, median + iqr / 2
    return {
        "med": median,
        "q1": q1,
        "q3": q3,
        "whislo": q1 - 1.5 * iqr,
        "whishi": q3 + 1.5 * iqr,
        "fliers": [],
        "label": "",
    }


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Liberation Sans", "DejaVu Sans"],
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
    }
)

fig, axes = plt.subplots(1, 2, figsize=(8.6, 2.85), sharey=True, dpi=200)
fig.subplots_adjust(left=0.235, right=0.985, top=0.875, bottom=0.155, wspace=0.10)

# top row = best performer
positions = list(range(len(SERIES), 0, -1))

for ax, (metric, panel_title) in zip(axes, PANELS):
    # gridlines stop short of 0.50 — the dashed chance rule already marks it
    for gx in (0.6, 0.7, 0.8, 0.9):
        ax.axvline(gx, color=GRID, lw=0.8, zorder=0)
    ax.axvline(CHANCE, color=NEUTRAL, lw=1.0, ls=(0, (4, 3)), zorder=1)

    for pos, (_, colour, values) in zip(positions, SERIES):
        bp = ax.bxp(
            [stats(*values[metric])],
            positions=[pos],
            vert=False,
            widths=0.42,
            patch_artist=True,
            showfliers=False,
            showcaps=True,
            zorder=3,
        )
        for patch in bp["boxes"]:
            patch.set(facecolor=colour, alpha=0.40, edgecolor=colour, linewidth=1.6)
        for part in ("whiskers", "caps"):
            for artist in bp[part]:
                artist.set(color=colour, linewidth=1.3)
        for line in bp["medians"]:
            line.set(color=INK, linewidth=1.5, solid_capstyle="butt")

        # static export has no tooltip, so every median is directly labelled
        ax.text(
            values[metric][0] + values[metric][1] / 2 + 1.5 * values[metric][1] + 0.012,
            pos,
            f"{values[metric][0]:.2f}",
            va="center",
            ha="left",
            fontsize=8.5,
            color=INK_2,
        )

    ax.set_title(panel_title, color=INK, fontsize=10.5, fontweight="600", pad=9, loc="left")
    ax.set_xlim(0.42, 1.005)
    ax.set_ylim(0.45, len(SERIES) + 0.75)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9])
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.1f}")
    ax.tick_params(axis="x", colors=INK_2, labelsize=8.5, length=0, pad=5)
    ax.tick_params(axis="y", length=0, pad=9)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(0.8)

axes[0].set_yticks(positions)
axes[0].set_yticklabels([s[0] for s in SERIES], color=INK, fontsize=9.5, ha="right")

# annotate the chance rule once, in the empty band above the top box
axes[0].text(
    CHANCE + 0.012,
    len(SERIES) + 0.5,
    "chance",
    ha="left",
    va="center",
    fontsize=8,
    color=NEUTRAL,
    style="italic",
)

# No overall title/subtitle on purpose: the post's <figcaption> already carries
# "Bootstrapped average precision and ROC AUC, 1,000 resamples, identical cohort
# and identical inputs for all four predictors." Repeating it in the image reads
# as a stutter. Add one back if the PNG needs to stand alone off-site.

out = "assets/blog/bootstrapped_reasoning_ablation.png"
fig.savefig(out, dpi=200)
print(f"wrote {out}")
