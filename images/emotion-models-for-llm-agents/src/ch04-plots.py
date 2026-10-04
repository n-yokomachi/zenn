"""ch4 実測グラフの生成スクリプト。

affectus examples/evaluation の実測結果(直接互動型2台本)から、書籍用の
日本語ラベル図を台本ごとに生成する。

  python ch04-plots.py [evaluation ディレクトリ]

出力(このファイルの親の親 = images/emotion-models-for-llm-agents/):
  - ch04-polarity-praise-to-anger.png / ch04-polarity-anger-to-praise.png
  - ch04-8axis-praise-to-anger.png   / ch04-8axis-anger-to-praise.png
    (8軸は friendly-on の2×4スモールマルチプル)

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

# 台本 stem -> (出力ファイル用の短名, ピボット線の注記)
SCRIPTS = {
    "direct-praise-to-anger": ("praise-to-anger", "本人の失敗が発覚"),
    "direct-anger-to-praise": ("anger-to-praise", "誤解と判明し謝罪"),
}

# 輪の並び順(affectus 設定と同じ)と日本語ラベル
AXES_JA = [
    ("joy", "喜び"), ("acceptance", "受容"), ("fear", "恐れ"),
    ("surprise", "驚き"), ("sorrow", "悲しみ"), ("disgust", "嫌悪"),
    ("anger", "怒り"), ("expectancy", "予期"),
]

plt.rcParams["font.family"] = "Hiragino Sans"
plt.rcParams["axes.unicode_minus"] = False


def load_polarity(script: str) -> dict[str, list[float]]:
    """cell -> ターン順の平均極性(3回の実行の平均)。"""
    acc: dict[tuple[str, int], list[float]] = defaultdict(list)
    with (EVAL_DIR / "results" / "per_turn_scores.csv").open() as f:
        for r in csv.DictReader(f):
            if r["script"] != script:
                continue
            acc[(r["cell"], int(r["turn"]))].append(float(r["polarity"]))
    return {cell: [mean(acc[(cell, t)]) for t in TURNS]
            for cell in {c for c, _ in acc}}


def load_axes(script: str, cell: str) -> dict[str, list[float]]:
    """axis -> ターン順の平均値(3回の実行の平均)。transcripts の axes スナップショット。"""
    acc: dict[tuple[str, int], list[float]] = defaultdict(list)
    for run in (1, 2, 3):
        path = EVAL_DIR / "transcripts" / f"{script}_{cell}_run{run}.jsonl"
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


def plot_polarity(script: str, short: str, pivot_note: str) -> None:
    pol = load_polarity(script)
    fig, ax = plt.subplots(figsize=(11.6, 6.2), dpi=100)
    fig.patch.set_facecolor(BG)
    style_axes(ax)

    series = [
        ("friendly-on", "フレンドリー+affectus", BLUE, "-", "o"),
        ("friendly-off", "フレンドリー(affectusなし)", BLUE, (0, (5, 3)), None),
        ("contrarian-on", "天邪鬼+affectus", RUST, "-", "o"),
        ("contrarian-off", "天邪鬼(affectusなし)", RUST, (0, (5, 3)), None),
    ]
    for cell, label, color, ls, marker in series:
        if cell not in pol:
            continue
        ax.plot(list(TURNS), pol[cell], color=color, linestyle=ls, linewidth=2,
                marker=marker, markersize=5, label=label)

    ax.axvline(PIVOT_TURN, color=PIVOT, linestyle=":", linewidth=1.5)
    ax.text(PIVOT_TURN + 0.15, 1.02, pivot_note, color=PIVOT, fontsize=11)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set_xlim(0.5, 20.5)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([1, 5, 10, 11, 15, 20])
    ax.set_xlabel("ターン", color=INK, fontsize=12)
    ax.set_ylabel("応答の感情スコア", color=INK, fontsize=12)
    fig.legend(loc="upper center", ncol=4, fontsize=10.5, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.01, "各線は3回の実行の平均です。実線がaffectusあり、破線がなしです。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(OUT_DIR / f"ch04-polarity-{short}.png", facecolor=BG)
    plt.close(fig)


def plot_8axis(script: str, short: str) -> None:
    data = load_axes(script, "friendly-on")
    fig, axes = plt.subplots(2, 4, figsize=(11.6, 5.8), dpi=100,
                             sharex=True, sharey=True)
    fig.patch.set_facecolor(BG)
    for ax, (axis, ja) in zip(axes.flat, AXES_JA):
        style_axes(ax)
        ax.plot(list(TURNS), data[axis], color=BLUE, linewidth=2)
        ax.axvline(PIVOT_TURN, color=PIVOT, linestyle=":", linewidth=1.2)
        ax.set_title(f"{ja}", color=INK, fontsize=13, pad=10)
        ax.text(0.02, 0.9, axis, transform=ax.transAxes,
                color=MUTED, fontsize=10)
        ax.set_ylim(-0.05, 1.1)
        ax.set_xticks([1, 11, 20])
    for ax in axes[1]:
        ax.set_xlabel("ターン", color=MUTED, fontsize=11)
    fig.text(0.01, 0.01,
             "フレンドリー+affectusの外部状態(3回の実行の平均)です。点線はターン11の転換を示します。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT_DIR / f"ch04-8axis-{short}.png", facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    for script, (short, pivot_note) in SCRIPTS.items():
        plot_polarity(script, short, pivot_note)
        plot_8axis(script, short)
        print(f"wrote ch04-polarity-{short}.png / ch04-8axis-{short}.png")
