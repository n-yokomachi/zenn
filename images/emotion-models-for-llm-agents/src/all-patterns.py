"""全パターン比較の図と表の生成スクリプト（ch4〜ch7 共通）。

affectus examples/evaluation の実測結果から、台本2本×性格2つ×構成2つの
8パターンの応答の感情スコアを1枚の図（台本ごとに1パネル）にし、
共通指標の表を Markdown で標準出力に書く。

  uv run python all-patterns.py <章の接頭辞> <evaluation ディレクトリ> [構成の呼び名]

  例: uv run python all-patterns.py ch04 _archive/plutchik-direct-20260810
      uv run python all-patterns.py ch07 _archive/barrett-direct-20261006 想起

構成の呼び名は既定で「感情エンジン」で、凡例と表に「感情エンジンあり／なし」と出る。
ch7 は「想起」を渡して「想起あり／なし」にする。

出力: images/emotion-models-for-llm-agents/<章の接頭辞>-polarity-all.png
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CH = sys.argv[1]
EVAL_DIR = Path(sys.argv[2])
ON_NAME = sys.argv[3] if len(sys.argv) > 3 else "感情エンジン"
OUT_DIR = Path(__file__).resolve().parent.parent

BG = "#fbfbfa"
INK = "#24241f"
MUTED = "#7a7a72"
GRID = "#ececea"
PIVOT = "#8a8a80"
BLUE = "#2f6fb3"   # フレンドリー
RUST = "#b0562c"   # 天邪鬼

PIVOT_TURN = 11
TURNS = range(1, 21)
RUNS = (1, 2, 3)

SCRIPTS = [
    ("direct-anger-to-praise", "和解台本", "誤解と判明し謝罪"),
    ("direct-praise-to-anger", "叱責台本", "本人の失敗が発覚"),
]
CELLS = [
    ("friendly-on", "フレンドリー", BLUE, "-", "o", True),
    ("friendly-off", "フレンドリー", BLUE, (0, (5, 3)), None, False),
    ("contrarian-on", "天邪鬼", RUST, "-", "o", True),
    ("contrarian-off", "天邪鬼", RUST, (0, (5, 3)), None, False),
]

plt.rcParams["font.family"] = "Hiragino Sans"
plt.rcParams["axes.unicode_minus"] = False


def load() -> dict[tuple[str, str, int], dict[int, float]]:
    """(script, cell, run) -> turn -> polarity"""
    d: dict[tuple[str, str, int], dict[int, float]] = defaultdict(dict)
    with (EVAL_DIR / "results" / "per_turn_scores.csv").open() as f:
        for r in csv.DictReader(f):
            d[(r["script"], r["cell"], int(r["run"]))][int(r["turn"])] = float(r["polarity"])
    return d


def style_axes(ax) -> None:
    ax.set_facecolor(BG)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=11)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot(d) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.6), dpi=100, sharey=True)
    fig.patch.set_facecolor(BG)
    for ax, (script, title, note) in zip(axes, SCRIPTS):
        style_axes(ax)
        for cell, who, color, ls, marker, on in CELLS:
            ys = [mean(d[(script, cell, r)][t] for r in RUNS) for t in TURNS]
            label = f"{who}（{ON_NAME}{'あり' if on else 'なし'}）"
            ax.plot(list(TURNS), ys, color=color, linestyle=ls, linewidth=2,
                    marker=marker, markersize=4.5, label=label)
        ax.axvline(PIVOT_TURN, color=PIVOT, linestyle=":", linewidth=1.5)
        ax.text(PIVOT_TURN + 0.15, 1.02, note, color=PIVOT, fontsize=10.5)
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set_xlim(0.5, 20.5)
        ax.set_ylim(-1.1, 1.15)
        ax.set_xticks([1, 5, 10, 11, 15, 20])
        ax.set_xlabel("ターン", color=INK, fontsize=12)
        ax.set_title(title, color=INK, fontsize=13)
    axes[0].set_ylabel("応答の感情スコア", color=INK, fontsize=12)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=10.5, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.01,
             f"各線は3回の実行の平均である。実線が{ON_NAME}あり、破線が{ON_NAME}なしである。",
             color=MUTED, fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    fig.savefig(OUT_DIR / f"{CH}-polarity-all.png", facecolor=BG)
    plt.close(fig)


def table(d) -> str:
    rows = [f"| 台本 | 性格 | 構成 | 前半（ターン1〜10）の平均 | 後半（ターン12〜20）の平均 | 後半の変動幅 |",
            "| --- | --- | --- | --- | --- | --- |"]
    for script, title, _ in SCRIPTS:
        for cell, who, _, _, _, on in CELLS:
            first = mean(mean(d[(script, cell, r)][t] for r in RUNS) for t in range(1, 11))
            second = mean(mean(d[(script, cell, r)][t] for r in RUNS) for t in range(12, 21))
            vol = mean(mean(abs(d[(script, cell, r)][t + 1] - d[(script, cell, r)][t])
                            for t in range(12, 20)) for r in RUNS)
            conf = f"{ON_NAME}{'あり' if on else 'なし'}"
            fmt = lambda v: f"{v:+.2f}".replace("-", "−").replace("+", "+")
            rows.append(f"| {title} | {who} | {conf} | {fmt(first)} | {fmt(second)} | {vol:.2f} |")
    return "\n".join(rows)


if __name__ == "__main__":
    data = load()
    plot(data)
    print(table(data))
    print(f"wrote {CH}-polarity-all.png", file=sys.stderr)
