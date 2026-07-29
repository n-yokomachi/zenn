"""ch4 実測グラフの生成スクリプト。

affectus examples/strands-eval の再ラン結果(2026-07-30・改名済み軸名)から、
書籍用の日本語ラベル図2枚を生成する。

  python ch04-plots.py [strands-eval ディレクトリ]

出力(このファイルの親の親 = images/emotion-models-for-llm-agents/):
  - ch04-polarity.png  極性カーブ(4セル・3ラン平均)
  - ch04-8axis.png     friendly-on の8軸スモールマルチプル(3ラン平均)

依存: matplotlib(strands-eval の venv にある。`uv run python` で実行する)
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
                "/Users/Naoki/work/workshop/affectus/examples/strands-eval")
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

# 輪の並び順(affectus 設定と同じ)と日本語ラベル
AXES_JA = [
    ("joy", "喜び"), ("acceptance", "受容"), ("fear", "恐れ"),
    ("surprise", "驚き"), ("sorrow", "悲しみ"), ("disgust", "嫌悪"),
    ("anger", "怒り"), ("expectancy", "予期"),
]

plt.rcParams["font.family"] = "Hiragino Sans"
plt.rcParams["axes.unicode_minus"] = False


def load_polarity() -> dict[str, list[float]]:
    """cell -> ターン順の平均極性(3ラン平均)。"""
    acc: dict[tuple[str, int], list[float]] = defaultdict(list)
    with (EVAL_DIR / "results" / "per_turn_scores.csv").open() as f:
        for r in csv.DictReader(f):
            acc[(r["cell"], int(r["turn"]))].append(float(r["polarity"]))
    return {cell: [mean(acc[(cell, t)]) for t in TURNS]
            for cell in {c for c, _ in acc}}


def load_axes(cell: str) -> dict[str, list[float]]:
    """axis -> ターン順の平均値(3ラン平均)。transcripts の axes スナップショット。"""
    acc: dict[tuple[str, int], list[float]] = defaultdict(list)
    for run in (1, 2, 3):
        path = EVAL_DIR / "transcripts" / f"{cell}_run{run}.jsonl"
        for rec in (json.loads(l) for l in path.open()):
            for k, v in (rec["axes"] or {}).items():
                acc[(k, rec["turn"])].append(v)
    return {axis: [mean(acc[(axis, t)]) for t in TURNS]
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


def plot_polarity() -> None:
    pol = load_polarity()
    fig, ax = plt.subplots(figsize=(11.6, 6.2), dpi=100)
    fig.patch.set_facecolor(BG)
    style_axes(ax)

    series = [
        ("friendly-on", "フレンドリー + affectus", BLUE, "-", "o"),
        ("friendly-off", "フレンドリー(affectus なし)", BLUE, (0, (5, 3)), None),
        ("contrarian-on", "天邪鬼 + affectus", RUST, "-", "o"),
        ("contrarian-off", "天邪鬼(affectus なし)", RUST, (0, (5, 3)), None),
    ]
    for cell, label, color, ls, marker in series:
        ax.plot(list(TURNS), pol[cell], color=color, linestyle=ls, linewidth=2,
                marker=marker, markersize=5, label=label)

    ax.axvline(PIVOT_TURN, color=PIVOT, linestyle=":", linewidth=1.5)
    ax.text(PIVOT_TURN + 0.15, 1.02, "話題の転換", color=PIVOT, fontsize=11)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set_xlim(0.5, 20.5)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([1, 5, 10, 11, 15, 20])
    ax.set_xlabel("ターン", color=INK, fontsize=12)
    ax.set_ylabel("応答の極性スコア", color=INK, fontsize=12)
    fig.legend(loc="upper center", ncol=4, fontsize=10.5, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.01, "各線は3ランの平均です。実線が affectus あり、破線がなしです。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(OUT_DIR / "ch04-polarity.png", facecolor=BG)
    plt.close(fig)


def plot_8axis() -> None:
    data = load_axes("friendly-on")
    fig, axes = plt.subplots(2, 4, figsize=(11.6, 5.8), dpi=100,
                             sharex=True, sharey=True)
    fig.patch.set_facecolor(BG)
    for ax, (axis, ja) in zip(axes.flat, AXES_JA):
        style_axes(ax)
        ax.plot(list(TURNS), data[axis], color=BLUE, linewidth=2)
        ax.axvline(PIVOT_TURN, color=PIVOT, linestyle=":", linewidth=1.2)
        ax.set_title(f"{ja}", color=INK, fontsize=13, pad=10)
        ax.text(0.5, 1.02, "", transform=ax.transAxes)
        ax.text(0.02, 0.9, axis, transform=ax.transAxes,
                color=MUTED, fontsize=10)
        ax.set_ylim(-0.05, 1.1)
        ax.set_xticks([1, 11, 20])
    for ax in axes[1]:
        ax.set_xlabel("ターン", color=MUTED, fontsize=11)
    fig.text(0.01, 0.01,
             "フレンドリー + affectus の外部状態(3ランの平均)です。点線はターン11の話題の転換を示します。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT_DIR / "ch04-8axis.png", facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    plot_polarity()
    plot_8axis()
    print(f"wrote {OUT_DIR / 'ch04-polarity.png'}")
    print(f"wrote {OUT_DIR / 'ch04-8axis.png'}")
