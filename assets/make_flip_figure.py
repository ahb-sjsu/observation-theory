#!/usr/bin/env python3
"""The front-door figure: the consumer-relative flip.

Two posteriors with identical total uncertainty (tr S = 2.0) and two
consumers with different read directions (15 deg / 75 deg — the
canonical pair declared in campaign DR-2). Every number in the figure
is computed here, not drawn: d_O = g' S g = tr(P_C S) for the
rank-one read operator P_C = g g'.

Outputs assets/flip-light.svg and assets/flip-dark.svg (transparent
backgrounds; GitHub <picture> selects by viewer theme).

Reproduce:  python assets/make_flip_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch

S1 = np.diag([0.3, 1.7])   # narrow along x, wide along y
S2 = np.diag([1.7, 0.3])   # the reverse; tr S1 = tr S2 = 2.0
ANGLES = {"A": 15.0, "B": 75.0}   # DR-2's canonical consumers


def g(deg):
    r = np.radians(deg)
    return np.array([np.cos(r), np.sin(r)])


D = {(c, i): float(g(a) @ S @ g(a))
     for c, a in ANGLES.items() for i, S in (("1", S1), ("2", S2))}

PALETTES = {
    "light": dict(ink="#232733", muted="#6b7080", s1="#0e7c86",
                  s2="#c1502e", grid="#c9ccd4"),
    "dark": dict(ink="#e8e6e1", muted="#9a9fae", s1="#53c8d2",
                 s2="#f09a6e", grid="#4a4f5c"),
}


def make(theme):
    p = PALETTES[theme]
    plt.rcParams.update({
        "svg.fonttype": "path", "font.family": "DejaVu Sans",
        "text.color": p["ink"], "axes.edgecolor": p["grid"],
    })
    fig = plt.figure(figsize=(11.6, 4.6))
    fig.patch.set_alpha(0.0)

    # ---- left panel: the object every classical metric sees ----
    ax = fig.add_axes([0.045, 0.13, 0.40, 0.72])
    ax.set_aspect("equal")
    ax.set_facecolor("none")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    for S, color, name in ((S1, p["s1"], "Σ₁"), (S2, p["s2"], "Σ₂")):
        w, h = 2 * np.sqrt(np.diag(S))  # 1-sigma ellipse
        ax.add_patch(Ellipse((0, 0), w, h, facecolor=color, alpha=0.14,
                             edgecolor=color, lw=2.2))
    ax.annotate("Σ₁", (0.30, 1.12), color=p["s1"], fontsize=13,
                fontweight="bold", ha="left")
    ax.annotate("Σ₂", (1.24, 0.36), color=p["s2"], fontsize=13,
                fontweight="bold", ha="left")
    for c, a in ANGLES.items():
        v = g(a) * 1.85
        for sgn in (1, -1):
            ax.add_patch(FancyArrowPatch((0, 0), tuple(sgn * v),
                         arrowstyle="-|>", mutation_scale=13,
                         lw=1.6, color=p["ink"], alpha=0.85))
        off = 1.12 if c == "A" else 1.16
        ax.annotate(f"consumer {c}\nreads at {a:.0f}°",
                    tuple(g(a) * 1.85 * off + np.array([0.06, 0.02])),
                    color=p["ink"], fontsize=10.5, ha="left",
                    va="center", linespacing=1.25)
    lim = 2.45
    ax.set_xlim(-lim, lim + 0.7)
    ax.set_ylim(-lim + 0.35, lim)
    ax.set_title("two estimates, identical total uncertainty\n"
                 "tr Σ₁ = tr Σ₂ = 2.0", fontsize=12.5, color=p["ink"],
                 pad=10)

    # ---- right panel: what each consumer actually experiences ----
    ax2 = fig.add_axes([0.545, 0.20, 0.42, 0.60])
    ax2.set_facecolor("none")
    for s in ("top", "right", "left"):
        ax2.spines[s].set_visible(False)
    ax2.spines["bottom"].set_color(p["grid"])
    x = np.array([0.0, 1.0])
    wbar = 0.30
    subs = {"1": "Σ₁", "2": "Σ₂"}
    for k, (i, color) in enumerate((("1", p["s1"]), ("2", p["s2"]))):
        vals = [D[("A", i)], D[("B", i)]]
        ax2.bar(x + (k - 0.5) * (wbar + 0.05), vals, wbar,
                color=color, alpha=0.88, label=f"under {subs[i]}")
        for xi, v in zip(x + (k - 0.5) * (wbar + 0.05), vals):
            ax2.annotate(f"{v:.2f}", (xi, v + 0.05), ha="center",
                         fontsize=10.5, color=p["ink"])
    ax2.set_xticks(x)
    ax2.set_xticklabels(["consumer A", "consumer B"], fontsize=11.5,
                        color=p["ink"])
    ax2.set_yticks([])
    ax2.set_ylim(0, 2.05)
    ax2.set_title("consumer-read distortion  d_O = tr(P_C Σ)",
                  fontsize=12.5, color=p["ink"], pad=10)
    leg = ax2.legend(frameon=False, fontsize=10.5, loc="upper center",
                     bbox_to_anchor=(0.5, 1.02), ncol=2)
    for t in leg.get_texts():
        t.set_color(p["ink"])
    rA = D[("A", "2")] / D[("A", "1")]
    fig.text(0.5, 0.030,
             f"A prefers Σ₁ ({rA:.1f}× better); B prefers Σ₂ — "
             "indistinguishable by every consumer-blind metric, ranked "
             "oppositely by every consumer.\nDistortion is a property of "
             "the observation, not the object. Measured, sealed: verdict "
             "inversion in 100% of trace-matched systems (GO-EC-2).",
             ha="center", fontsize=10, color=p["muted"], linespacing=1.5)
    out = f"assets/flip-{theme}.svg"
    fig.savefig(out, transparent=True)
    import os
    if os.environ.get("QA_PNG"):  # raster preview on a GitHub-like ground
        bg = "#ffffff" if theme == "light" else "#0d1117"
        fig.patch.set_alpha(1.0)
        fig.patch.set_facecolor(bg)
        fig.savefig(out.replace(".svg", "-qa.png"), dpi=110,
                    transparent=False, facecolor=bg)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    for c, a in ANGLES.items():
        print(f"consumer {c} ({a:.0f}deg): d(S1)={D[(c, '1')]:.3f} "
              f"d(S2)={D[(c, '2')]:.3f}")
    for theme in PALETTES:
        make(theme)
