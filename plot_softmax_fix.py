"""Redraw the softmax-fix recreation figures in the site's dark theme.

Outputs: assets/blog/softmax/fig1_slingshot.png
         assets/blog/softmax/fig2_equilibrium.png
         assets/blog/softmax/fig3_distill.png
         assets/blog/softmax/fig4_paired_grok.png

This is a pure restyle of ``plots.py`` in the softmax-fix repo
(https://github.com/SteliosKyriacou/softmax-fix). It reads the same raw run
JSON and reproduces the same four panels with the same statistics, so the
numbers are untouched; only the surface, palette, type and reference-line
treatment change, so the figures sit on the site's #050505 background instead
of matplotlib's white.

Main grokking results come from results/grok_v2 (init="small", 20 seeds, 10k
steps). Point SRC at a checkout of that repo and run from the site repo root.

Palette: the two series are a categorical pair validated with the dataviz
skill's validate_palette.js against the #050505 surface (lightness band,
chroma floor, deutan/tritan separation, normal-vision floor and contrast all
pass). Cyan is the site accent family and carries the fixed loss; warm orange
carries the standard loss. In Fig 4 the "no difference" seeds are drawn as
hollow gray rings rather than a third hue, since a neutral gray fails the
categorical chroma floor and would sit too close to the cyan.
"""

import glob
import json
import math
import os
from math import comb

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SRC = os.path.expanduser("~/repos/recreading-papers/softmax-fix")
OUT = "assets/blog/softmax"
D = "results/grok_v2"

# --- site design tokens -----------------------------------------------------
SURFACE = "#050505"  # matches body background in style.css
INK = "#f2f2f2"  # primary
INK_2 = "#a0a0a0"  # --text-secondary
GRID = "#1e1e1e"
AXIS = "#3a3a3a"

C = {"standard": "#d4682a", "fixed": "#12a5bd"}
RULE = "#898781"  # reference lines, and the "no difference" seeds in Fig 4

CLIFF = {"bf16": 5.5, "fp32": 16.6, "fp64": 36.7}
EPS = ["1e-08", "1e-12", "1e-16"]
EPS_LABEL = {"1e-08": "1e-8", "1e-12": "1e-12", "1e-16": "1e-16"}
PRECS = ["bf16", "fp32", "fp64"]
SEEDS = range(20)

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.linewidth": 0.8,
        "text.color": INK,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "legend.frameon": False,
        "legend.labelcolor": INK_2,
        "legend.fontsize": 9,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
    }
)


def H(loss, prec, e, s):
    with open(os.path.join(SRC, D, f"{loss}_{prec}_eps{e}_small_s{s}.json")) as fh:
        return json.load(fh)["hist"]


def grok_step(h, th=0.95):
    return next((s for s, a in zip(h["step"], h["test_acc"]) if a > th), np.inf)


def tavg_margin(h, frac=0.1):
    """Time-average over the last 10% of training (standard CE oscillates)."""
    n = max(1, int(len(h["margin"]) * frac))
    return float(np.mean(h["margin"][-n:]))


def sign_p(w, l):
    n, k = w + l, min(w, l)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0


def recede(ax, axis="y"):
    """Recessive grid, no top/right spines."""
    ax.grid(axis=axis, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


os.makedirs(OUT, exist_ok=True)

# ---------- Fig 1: the slingshot -------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True)
for loss in ["standard", "fixed"]:
    for i, s in enumerate([0, 1, 2]):
        h = H(loss, "fp32", "1e-08", s)
        kw = dict(
            color=C[loss],
            alpha=0.85,
            lw=1.2,
            solid_capstyle="round",
            label=f"{loss} CE" if i == 0 else None,
            zorder=3,
        )
        ax[0].plot(h["step"], h["margin"], **kw)
        ax[1].plot(h["step"], h["test_acc"], **kw)

# The reference lines go in the legend rather than as floating text: the top
# panel has no empty interior left for a label that does not collide with the
# sawtooth.
eq = math.log(1e8)
ax[0].axhline(CLIFF["fp32"], ls="--", c=RULE, lw=0.9, zorder=2,
              label="fp32 precision cliff  16.6")
ax[0].axhline(eq, ls=":", c=RULE, lw=0.9, zorder=2,
              label="AdamW equilibrium  log(1/ε) = 18.4")

ax[0].set_ylabel("mean train margin  m")
ax[0].set_ylim(-6, 20.5)
ax[1].set_ylabel("test accuracy")
ax[1].set_ylim(-0.03, 1.08)
ax[1].set_xlabel("step")
ax[1].set_xlim(0, 10000)
for a in ax:
    recede(a)
ax[0].legend(loc="lower left", ncol=2, columnspacing=1.6, handlelength=2.4)
ax[0].set_title("a+b mod 31, fp32 logits, AdamW ε = 1e-8, seeds 0 to 2", pad=12)
plt.tight_layout()
plt.savefig(f"{OUT}/fig1_slingshot.png", dpi=170)
plt.close()

# ---------- Fig 2: equilibrium margins -------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(12, 3.9), sharey=True)
for j, prec in enumerate(PRECS):
    ax = axs[j]
    for k, loss in enumerate(["standard", "fixed"]):
        ms = [[tavg_margin(H(loss, prec, e, s)) for s in SEEDS] for e in EPS]
        pos = np.arange(3) + (k - 0.5) * 0.31
        ax.bar(
            pos,
            [np.mean(m) for m in ms],
            width=0.29,  # < 0.31 spacing, so a surface gap sits between the pair
            color=C[loss],
            yerr=[np.std(m) for m in ms],
            error_kw=dict(ecolor=INK_2, lw=0.9, capsize=2.5),
            label=f"{loss} CE",
            zorder=3,
        )
    for i, e in enumerate(EPS):
        ax.hlines(math.log(1 / float(e)), i - 0.38, i + 0.38,
                  colors=INK, lw=1.6, zorder=4)
    ax.axhline(CLIFF[prec], ls="--", c=RULE, lw=0.9, zorder=2)
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"ε = {EPS_LABEL[e]}" if i == 0 else EPS_LABEL[e]
                        for i, e in enumerate(EPS)])
    ax.set_title(f"{prec} logits", pad=10)
    recede(ax)
axs[0].set_ylabel("margin, mean of last 10%\nof training")
axs[0].legend(loc="upper left")
plt.suptitle(
    "White ticks: predicted AdamW equilibrium  m* = log(1/ε).   "
    "Dashed: the precision cliff.   20 seeds per bar.",
    fontsize=9.5,
    color=INK_2,
    y=1.0,
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig2_equilibrium.png", dpi=170)
plt.close()

# ---------- Fig 4: paired grokking -----------------------------------------
CAP = 11000
fig, axs = plt.subplots(3, 3, figsize=(11, 10.2), sharex=True, sharey=True)
for i, prec in enumerate(PRECS):
    for j, e in enumerate(EPS):
        gs = np.array([grok_step(H("standard", prec, e, s)) for s in SEEDS])
        gf = np.array([grok_step(H("fixed", prec, e, s)) for s in SEEDS])
        sooner, later = int((gf < gs).sum()), int((gf > gs).sum())
        x, y = np.minimum(gs, CAP), np.minimum(gf, CAP)

        ax = axs[i, j]
        ax.plot([0, CAP], [0, CAP], c=AXIS, lw=0.8, zorder=1)
        ax.axhline(10500, c=RULE, lw=0.5, ls=":", zorder=1)
        ax.axvline(10500, c=RULE, lw=0.5, ls=":", zorder=1)
        tie = gf == gs
        # ties are drawn as hollow rings, so the three outcomes are not
        # separated by hue alone
        ax.scatter(x[tie], y[tie], s=34, facecolors="none", edgecolors=RULE,
                   linewidths=1.1, zorder=3, label="no difference")
        ax.scatter(x[gf < gs], y[gf < gs], s=30, c=C["fixed"],
                   edgecolors=SURFACE, linewidths=0.8, zorder=4,
                   label="fix groks sooner")
        ax.scatter(x[gf > gs], y[gf > gs], s=30, c=C["standard"],
                   edgecolors=SURFACE, linewidths=0.8, zorder=4,
                   label="fix groks later")

        ax.set_xlim(0, CAP + 600)
        ax.set_ylim(0, CAP + 600)
        ax.set_title(
            f"{prec}, ε = {EPS_LABEL[e]}:  sooner {sooner}, later {later}",
            fontsize=9.5,
            pad=8,
        )
        recede(ax, axis="both")
        if i == 2:
            ax.set_xlabel("standard CE: step to 95%")
        if j == 0:
            ax.set_ylabel("fixed CE: step to 95%")
axs[0, 0].legend(loc="upper left", fontsize=8.5, handletextpad=0.4)
plt.suptitle(
    "Paired by seed (same initialization and split). Below the diagonal, the "
    "fix groks sooner.\nPoints at 11,000 did not grok within 10k steps.",
    fontsize=9.5,
    color=INK_2,
    y=0.995,
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig4_paired_grok.png", dpi=150)
plt.close()

# ---------- Fig 3: distillation drift --------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
for j, prec in enumerate(PRECS):
    for loss in ["standard", "fixed"]:
        files = sorted(glob.glob(os.path.join(SRC, f"results/distill/{loss}_{prec}_s*.json")))
        for i, path in enumerate(files):
            with open(path) as fh:
                h = json.load(fh)["hist"]
            axs[j].semilogy(
                h["step"],
                np.maximum(h["kl"], 1e-20),
                color=C[loss],
                alpha=0.85,
                lw=1.3,
                solid_capstyle="round",
                label=f"{loss} CE" if i == 0 else None,
                zorder=3,
            )
    axs[j].set_title(f"{prec} forward + loss", pad=10)
    axs[j].set_xlabel("step")
    recede(axs[j])
axs[0].set_ylabel("held-out KL(teacher ‖ student)")
axs[0].legend(loc="center right")
plt.suptitle(
    "Student initialized bit-identical to its teacher. The correct answer is "
    "that nothing happens.",
    fontsize=9.5,
    color=INK_2,
    y=1.0,
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig3_distill.png", dpi=170)
plt.close()

print("wrote", OUT)
