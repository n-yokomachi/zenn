"""ch6 実測グラフの生成スクリプト。

affectus examples/evaluation の OCC 実測結果から、書籍用の日本語ラベル図を
生成する。

  python ch06-plots.py [evaluation ディレクトリ]

出力(このファイルの親の親 = images/emotion-models-for-llm-agents/):
  - ch06-axes-anger-to-praise.png
    (和解台本 friendly-on の主要8軸スモールマルチプル。3回の実行の平均・
     見込みリストの記録(t9 見込みの追加・t11 謝罪と当たり外れの申告)の注記付き)

依存: matplotlib(evaluation の venv にある。`uv run python` で実行する)
"""

from __future__ import annotations

import json
import sys
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
LEDGER = "#b0562c" # 見込みリストの記録の注記(検証済みパレット)

TURNS = range(1, 21)

# 表示する軸(V5 採用訳)と並び順。和解台本 friendly-on で動いた軸から8つ
AXES_JA = [
    ("distress", "苦悩"), ("reproach", "非難"), ("anger", "怒り"),
    ("fear", "恐れ"), ("relief", "安堵"), ("joy", "喜び"),
    ("admiration", "敬服"), ("gratitude", "感謝"),
]

plt.rcParams["font.family"] = "Hiragino Sans"
plt.rcParams["axes.unicode_minus"] = False


def load_axes(script: str, cell: str) -> dict[str, list[float]]:
    """axis -> ターン順の平均値(3回の実行の平均)。"""
    acc: dict[tuple[str, int], list[float]] = {}
    for run in (1, 2, 3):
        path = EVAL_DIR / "transcripts" / f"{script}_{cell}_run{run}.jsonl"
        for rec in (json.loads(l) for l in path.open()):
            for k, v in (rec["axes"] or {}).items():
                acc.setdefault((k, rec["turn"]), []).append(v)
    return {axis: [mean(acc.get((axis, t), [0.0])) for t in TURNS]
            for axis, _ in AXES_JA}


def style_axes(ax) -> None:
    ax.set_facecolor(BG)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=11)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_axes_small_multiples() -> None:
    data = load_axes("direct-anger-to-praise", "friendly-on")
    fig, axes = plt.subplots(2, 4, figsize=(11.6, 6.0), dpi=100,
                             sharex=True, sharey=True)
    fig.patch.set_facecolor(BG)
    for ax, (axis, ja) in zip(axes.flat, AXES_JA):
        style_axes(ax)
        ax.plot(list(TURNS), data[axis], color=BLUE, linewidth=2)
        ax.axvline(9, color=LEDGER, linestyle=":", linewidth=1.2)
        ax.axvline(11, color=PIVOT, linestyle="--", linewidth=1.2)
        ax.set_title(ja, color=INK, fontsize=13, pad=10)
        ax.text(0.03, 0.88, axis, transform=ax.transAxes,
                color=MUTED, fontsize=10)
        ax.set_ylim(-0.05, 1.1)
        ax.set_xticks([1, 9, 11, 20])
    for ax in axes[1]:
        ax.set_xlabel("ターン", color=MUTED, fontsize=11)
    fig.text(0.5, 0.955,
             "t9の解約の脅し(点線)で見込みが記録されて恐れが上がり、t11の謝罪(破線)で見込みが外れて安堵が導出される。",
             color=INK, fontsize=11.5, ha="center")
    fig.text(0.01, 0.01,
             "和解台本でのフレンドリー(感情エンジンあり)の外部状態(3回の実行の平均)である。"
             "叱責期は苦悩・非難・怒りが上がり、謝罪後はそれらが下がって喜び・敬服・感謝が上がる。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(OUT_DIR / "ch06-axes-anger-to-praise.png", facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    plot_axes_small_multiples()
    print("wrote ch06-axes-anger-to-praise.png")
