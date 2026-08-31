"""Loss trajectory and front contamination for the free-graph search run.

Output: assets/blog/freegraph/leak_trajectory.png

Numbers are transcribed directly from the two tables in cheat.md on the
cheating-agent branch of RWNN-LMM: per-generation best loss, Pareto front size,
and how many front members carry the acausal mean_reduce gate.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE, INK, INK_2 = "#050505", "#f2f2f2", "#a0a0a0"
GRID, AXIS = "#232323", "#333333"
HONEST, LEAK = "#00f2fe", "#d03b3b"

GEN    = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
LOSS   = [3.894, 3.801, 3.759, 3.759, 3.759, 3.629, 3.567, 3.368, 3.284, 3.284, 3.133, 3.032]
FRONT  = [2, 4, 6, 9, 7, 7, 10, 9, 9, 7, 9, 9]
LEAKED = [0, 0, 0, 0, 0, 1, 5, 8, 9, 7, 9, 9]

HONEST_FLOOR = 3.759          # the last generation with no leak on the front
FIRST_LEAK = 6

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Liberation Sans", "DejaVu Sans"],
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(8.6, 4.5), dpi=200, sharex=True,
    gridspec_kw={"height_ratios": [2.5, 1], "hspace": 0.18})
fig.subplots_adjust(left=0.085, right=0.975, top=0.87, bottom=0.115)


def chrome(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set(color=AXIS, linewidth=0.8)
    ax.tick_params(colors=INK_2, labelsize=8.5, length=0, pad=5)
    ax.set_axisbelow(True)


# shade the regime where the front is contaminated
for ax in (ax1, ax2):
    ax.axvspan(FIRST_LEAK - 0.5, 12.5, color=LEAK, alpha=0.07, zorder=0, lw=0)

# --- panel 1: best loss -----------------------------------------------------
for y in (3.0, 3.2, 3.4, 3.6, 3.8, 4.0):
    ax1.axhline(y, color=GRID, lw=0.8, zorder=1)
ax1.axhline(HONEST_FLOOR, color=INK_2, lw=1.0, ls=(0, (4, 3)), zorder=2)

split = GEN.index(FIRST_LEAK)
ax1.plot(GEN[:split + 1], LOSS[:split + 1], color=HONEST, lw=2.0, zorder=3)
ax1.plot(GEN[split:], LOSS[split:], color=LEAK, lw=2.0, zorder=3)
ax1.scatter(GEN[:split], LOSS[:split], s=42, color=HONEST, zorder=4,
            edgecolor=SURFACE, linewidth=1.6)
ax1.scatter(GEN[split:], LOSS[split:], s=42, color=LEAK, zorder=4,
            edgecolor=SURFACE, linewidth=1.6)

ax1.text(3.05, HONEST_FLOOR + 0.028, f"{HONEST_FLOOR}  last generation with a clean front",
         color=INK_2, fontsize=8, style="italic", va="bottom")
ax1.annotate(f"{LOSS[-1]:.3f}", (GEN[-1], LOSS[-1]), textcoords="offset points",
             xytext=(-11, -3), ha="right", color=LEAK, fontsize=9, fontweight="700")
ax1.text(3.0, 3.90, "causal", color=HONEST, fontsize=9, fontweight="700", ha="center")
ax1.text(9.5, 3.92, "front leaking the future", color=LEAK, fontsize=9,
         fontweight="700", ha="center")

ax1.set_ylabel("best validation loss", color=INK_2, fontsize=9)
ax1.set_ylim(2.95, 4.0)
ax1.set_yticks([3.0, 3.2, 3.4, 3.6, 3.8, 4.0])
chrome(ax1)

# --- panel 2: share of the front carrying the leak -------------------------
share = [100 * l / f for l, f in zip(LEAKED, FRONT)]
ax2.bar(GEN, share, width=0.55, color=[HONEST if s == 0 else LEAK for s in share],
        alpha=0.85, zorder=3)
for g, s, l, f in zip(GEN, share, LEAKED, FRONT):
    # zero bars are labelled too, so a clean generation does not read as missing data
    ax2.text(g, s + 5, f"{l}/{f}", ha="center", color=INK_2, fontsize=7.5)
ax2.set_ylabel("front leaking", color=INK_2, fontsize=9)
ax2.set_ylim(0, 122)
ax2.set_yticks([0, 50, 100])
ax2.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax2.set_xlabel("generation", color=INK_2, fontsize=9)
ax2.set_xticks(GEN)
ax2.set_xlim(0.4, 12.6)
chrome(ax2)

fig.text(0.085, 0.945, "Six generations of record-breaking progress, all of it fake",
         color=INK, fontsize=12, fontweight="700")
fig.text(0.085, 0.897,
         "Best loss per generation, and the share of the Pareto front carrying the acausal gate.",
         color=INK_2, fontsize=8.5)

out = "assets/blog/freegraph/leak_trajectory.png"
fig.savefig(out, dpi=200)
print("wrote", out)
