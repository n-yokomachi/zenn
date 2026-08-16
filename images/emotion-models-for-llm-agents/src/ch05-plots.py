"""ch5 実測グラフの生成スクリプト。

affectus examples/evaluation の Russell 実測結果から、書籍用の日本語ラベル図を
生成する。

  python ch05-plots.py [evaluation ディレクトリ]

出力(このファイルの親の親 = images/emotion-models-for-llm-agents/):
  - ch05-va-trajectory-anger-to-praise.png
    (和解台本 friendly-on の valence-arousal 平面軌跡。3ラン平均・ターン番号付き)
  - ch05-valence-vs-polarity-praise-to-anger.png
    (称賛→立腹台本の 状態 valence × 応答極性 の時系列。friendly / contrarian 並置)

依存: matplotlib(evaluation の venv にある。`uv run python` で実行する)
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

EVAL_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else
                "/Users/Naoki/work/workshop/affectus/examples/evaluation")
OUT_DIR = Path(__file__).resolve().parent.parent

BG = "#fbfbfa"
INK = "#24241f"
MUTED = "#7a7a72"
GRID = "#ececea"
PIVOT = "#8a8a80"
BLUE = "#2f6fb3"   # フレンドリー(検証済みパレット)
RUST = "#b0562c"   # 天邪鬼(検証済みパレット)

PIVOT_TURN = 11
TURNS = range(1, 21)
BASELINE = (0.0, 0.3)  # russell.default.yaml: valence 0.0 / arousal 0.3

plt.rcParams["font.family"] = "Hiragino Sans"
plt.rcParams["axes.unicode_minus"] = False


def load_va(script: str, cell: str) -> dict[int, dict[int, tuple[float, float]]]:
    """run -> turn -> (valence, arousal)。transcripts の axes スナップショット。"""
    out: dict[int, dict[int, tuple[float, float]]] = {}
    for run in (1, 2, 3):
        path = EVAL_DIR / "transcripts" / f"{script}_{cell}_run{run}.jsonl"
        out[run] = {rec["turn"]: (rec["axes"]["valence"], rec["axes"]["arousal"])
                    for rec in (json.loads(l) for l in path.open())}
    return out


def mean_va(script: str, cell: str) -> tuple[list[float], list[float]]:
    """ターン順の (valence 平均列, arousal 平均列)。"""
    va = load_va(script, cell)
    v = [mean(va[r][t][0] for r in va) for t in TURNS]
    a = [mean(va[r][t][1] for r in va) for t in TURNS]
    return v, a


def load_polarity(script: str, cell: str) -> dict[int, dict[int, float]]:
    """run -> turn -> 極性。"""
    out: dict[int, dict[int, float]] = defaultdict(dict)
    with (EVAL_DIR / "results" / "per_turn_scores.csv").open() as f:
        for r in csv.DictReader(f):
            if r["script"] == script and r["cell"] == cell:
                out[int(r["run"])][int(r["turn"])] = float(r["polarity"])
    return out


def pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = mean(xs), mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / (sxx * syy) ** 0.5


def style_axes(ax) -> None:
    ax.set_facecolor(BG)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=11)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_va_trajectory() -> None:
    """図2: 和解台本 friendly-on の valence-arousal 平面軌跡。"""
    v, a = mean_va("direct-anger-to-praise", "friendly-on")
    fig, ax = plt.subplots(figsize=(10.6, 6.8), dpi=100)
    fig.patch.set_facecolor(BG)
    style_axes(ax)

    # 平面の目安: 快-不快の境界と、象限の読みの例語
    ax.axvline(0, color=GRID, linewidth=1.2)
    for x, y, word in [(-0.93, 0.96, "苦悩のあたり"), (0.93, 0.96, "興奮のあたり"),
                       (-0.93, 0.035, "抑うつのあたり"), (0.93, 0.035, "満足のあたり")]:
        ax.text(x, y, word, color=MUTED, fontsize=11,
                ha="left" if x < 0 else "right", va="center")

    # 開始前の基準点と t1 への導入
    ax.plot(*BASELINE, marker="x", color=PIVOT, markersize=10, markeredgewidth=2)
    ax.annotate("開始前の基準点(0, 0.3)", BASELINE, textcoords="offset points",
                xytext=(10, -14), color=PIVOT, fontsize=10.5)
    ax.plot([BASELINE[0], v[0]], [BASELINE[1], a[0]],
            color=PIVOT, linewidth=1.2, linestyle=":")

    # 叱責の局面(t1-10): 破線・白抜きマーカー / 謝罪後(t11-20): 実線・塗り
    ax.plot(v[:10], a[:10], color=BLUE, linewidth=2, linestyle=(0, (5, 3)),
            marker="o", markersize=6, markerfacecolor=BG,
            label="叱責の局面(t1–10)")
    ax.plot(v[9:], a[9:], color=BLUE, linewidth=2, marker="o", markersize=6,
            label="謝罪後(t11–20)")

    # ピボットの強調
    ax.plot(v[10], a[10], marker="o", markersize=11, color=BLUE,
            markerfacecolor=BG, markeredgewidth=2)
    ax.annotate("t11で誤解と判明し謝罪", (v[10], a[10]), textcoords="offset points",
                xytext=(12, 2), color=INK, fontsize=11)

    # ターン番号(重なりを避けた個別オフセット)
    offsets = {1: (8, 4), 3: (6, -12), 5: (-4, -15), 8: (6, -12), 10: (-16, -14),
               13: (2, 8), 16: (4, 8), 20: (8, -4)}
    for t, (dx, dy) in offsets.items():
        ax.annotate(f"t{t}", (v[t - 1], a[t - 1]), textcoords="offset points",
                    xytext=(dx, dy), color=MUTED, fontsize=10)

    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("valence(快−不快)", color=INK, fontsize=12)
    ax.set_ylabel("arousal(覚醒)", color=INK, fontsize=12)
    ax.legend(loc="upper center", ncol=2, fontsize=10.5, frameon=False)
    fig.text(0.01, 0.01,
             "フレンドリー+affectus(和解台本)の軌跡です。点は各ターン終了時の値(3ランの平均)、点線は基準点からt1への移動です。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT_DIR / "ch05-va-trajectory-anger-to-praise.png", facecolor=BG)
    plt.close(fig)


def plot_valence_vs_polarity() -> None:
    """図3: 称賛→立腹台本の 状態 valence × 応答極性。friendly / contrarian 並置。"""
    script = "direct-praise-to-anger"
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.4), dpi=100,
                             sharex=True, sharey=True)
    fig.patch.set_facecolor(BG)

    for ax, (cell, title) in zip(axes, [("friendly-on", "フレンドリー+affectus"),
                                        ("contrarian-on", "天邪鬼+affectus")]):
        style_axes(ax)
        v, _ = mean_va(script, cell)
        pol_runs = load_polarity(script, cell)
        pol = [mean(pol_runs[r][t] for r in pol_runs) for t in TURNS]

        # r はラン×ターンの60点の対で計算(平均線からではない)
        va_runs = load_va(script, cell)
        pairs = [(va_runs[r][t][0], pol_runs[r][t])
                 for r in va_runs for t in TURNS]
        r_val = pearson([p[0] for p in pairs], [p[1] for p in pairs])

        ax.plot(list(TURNS), v, color=BLUE, linewidth=2, marker="o",
                markersize=5, label="状態のvalence")
        ax.plot(list(TURNS), pol, color=RUST, linewidth=2, linestyle=(0, (5, 3)),
                marker="s", markersize=4.5, label="応答の極性")
        ax.axvline(PIVOT_TURN, color=PIVOT, linestyle=":", linewidth=1.5)
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set_title(title, color=INK, fontsize=13, pad=10)
        ax.text(0.03, 0.06, f"相関r={r_val:.2f}", transform=ax.transAxes,
                color=INK, fontsize=12)
        ax.set_xlim(0.5, 20.5)
        ax.set_ylim(-1.1, 1.1)
        ax.set_xticks([1, 5, 10, 11, 15, 20])
        ax.set_xlabel("ターン", color=INK, fontsize=12)

    axes[0].text(PIVOT_TURN + 0.3, 1.0, "本人の失敗が発覚", color=PIVOT, fontsize=10.5)
    axes[0].set_ylabel("値", color=INK, fontsize=12)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, fontsize=10.5,
               frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.01,
             "称賛→立腹台本の3ランの平均です。rは状態のvalenceと応答の極性をラン×ターンの60対で照合した相関です。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    fig.savefig(OUT_DIR / "ch05-valence-vs-polarity-praise-to-anger.png", facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    plot_va_trajectory()
    plot_valence_vs_polarity()
    print("wrote ch05-va-trajectory-anger-to-praise.png / "
          "ch05-valence-vs-polarity-praise-to-anger.png")
