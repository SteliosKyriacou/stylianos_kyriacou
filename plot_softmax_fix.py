"""Redraw the softmax-fix recreation figures in the site's dark theme.

Outputs: assets/blog/softmax/fig1_slingshot.png
         assets/blog/softmax/fig2_equilibrium.png
         assets/blog/softmax/fig3_distill.png

This is a pure restyle of ``plots.py`` in the softmax-fix repo
(https://github.com/SteliosKyriacou/softmax-fix). It reads the same raw run
JSON and reproduces the same three panels, so the numbers are untouched; only
the surface, palette, type and reference-line treatment change, so the figures
sit on the site's #050505 background instead of matplotlib's white.

Point SRC at a checkout of that repo and run from the site repo root.

Palette: the two series are a categorical pair validated with the dataviz
skill's validate_palette.js against the #050505 surface (lightness band,
chroma floor, deutan/tritan separation, normal-vision floor, contrast all
pass). Cyan is the site accent family and carries the fixed loss; warm orange
carries the standard loss.
"""

import glob
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SRC = os.path.expanduser("~/repos/recreading-papers/softmax-fix")
OUT = "assets/blog/softmax"

# --- site design tokens -----------------------------------------------------
SURFACE = "#050505"  # matches body background in style.css
INK = "#f2f2f2"  # primary
INK_2 = "#a0a0a0"  # --text-secondary
GRID = "#1e1e1e"
AXIS = "#3a3a3a"

C = {"standard": "#d4682a", "fixed": "#12a5bd"}
RULE = "#898781"  # reference lines: precision cliff, predicted equilibrium

CLIFF = {"bf16": 5.5, "fp32": 16.6, "fp64": 36.7}

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


def load(pattern):
    return [json.load(open(f)) for f in sorted(glob.glob(os.path.join(SRC, pattern)))]


def recede(ax, axis="y"):
    """Recessive grid, no top/right spines."""
    ax.grid(axis=axis, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


os.makedirs(OUT, exist_ok=True)

# ---------- Fig 1: the slingshot, fp32 eps=1e-8, margin + test acc ----------
fig, ax = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True)
for loss in ["standard", "fixed"]:
    for i, r in enumerate(load(f"results/grok/{loss}_fp32_eps1e-08_s*.json")[:3]):
        h = r["hist"]
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
ax[0].set_ylim(-6, 21)
ax[1].set_ylabel("test accuracy")
ax[1].set_ylim(-0.03, 1.08)
ax[1].set_xlabel("step")
ax[1].set_xlim(0, 40000)
for a in ax:
    recede(a)
ax[0].legend(loc="lower left", ncol=2, columnspacing=1.6, handlelength=2.4)
ax[0].set_title("a+b mod 31, fp32 logits, AdamW ε = 1e-8, three seeds", pad=12)
plt.tight_layout()
plt.savefig(f"{OUT}/fig1_slingshot.png", dpi=170)
plt.close()

# ---------- Fig 2: final margin vs predicted equilibrium --------------------
fig, axs = plt.subplots(1, 3, figsize=(12, 3.9), sharey=True)
for j, prec in enumerate(["bf16", "fp32", "fp64"]):
    ax = axs[j]
    for k, loss in enumerate(["standard", "fixed"]):
        xs, ms = [], []
        for e in ["1e-08", "1e-12", "1e-16"]:
            rs = load(f"results/grok/{loss}_{prec}_eps{e}_s*.json")
            if not rs:
                continue
            # average margin over last 10% of training (standard CE oscillates)
            ms.append([np.mean(r["hist"]["margin"][-160:]) for r in rs])
            xs.append(e)
        pos = np.arange(len(xs)) + (k - 0.5) * 0.31
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
    for i, e in enumerate(["1e-08", "1e-12", "1e-16"]):
        ax.hlines(math.log(1 / float(e)), i - 0.38, i + 0.38,
                  colors=INK, lw=1.6, zorder=4)
    ax.axhline(CLIFF[prec], ls="--", c=RULE, lw=0.9, zorder=2)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["ε = 1e-8", "1e-12", "1e-16"])
    ax.set_title(f"{prec} logits", pad=10)
    recede(ax)
axs[0].set_ylabel("final mean margin")
axs[0].legend(loc="upper left")
plt.suptitle(
    "White ticks: predicted AdamW equilibrium  m* = log(1/ε).   "
    "Dashed: the precision cliff.",
    fontsize=9.5,
    color=INK_2,
    y=1.0,
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig2_equilibrium.png", dpi=170)
plt.close()

# ---------- Fig 3: distillation drift --------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
for j, prec in enumerate(["bf16", "fp32", "fp64"]):
    for loss in ["standard", "fixed"]:
        for i, r in enumerate(load(f"results/distill/{loss}_{prec}_s*.json")):
            h = r["hist"]
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
    "Student initialised bit-identical to its teacher. The correct answer is "
    "that nothing happens.",
    fontsize=9.5,
    color=INK_2,
    y=1.0,
)
plt.tight_layout()
plt.savefig(f"{OUT}/fig3_distill.png", dpi=170)
plt.close()

print("wrote", OUT)
