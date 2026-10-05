"""構成主義的情動理論の章の図: 称賛→立腹台本で天邪鬼が保存した感情の名前(想起あり/なし)。

使い方: python ch07-label-lineage.py <EVAL_DIR> [run]
EVAL_DIR は affectus の examples/evaluation 配下のキャンペーンディレクトリ
(transcripts/ を含む)。出力は同じディレクトリの ch07-label-lineage.svg。
"""
import json
import sys
from html import escape
from pathlib import Path

EVAL_DIR = Path(sys.argv[1])
RUN = int(sys.argv[2]) if len(sys.argv) > 2 else 1
SCRIPT = "direct-praise-to-anger"
OUT = Path(__file__).parent / "ch07-label-lineage.svg"

INK, MUTED, PIVOT, BG, LINE = "#24241f", "#7a7a72", "#b0562c", "#fbfbfa", "#d8d8d2"
BANDS = ["#dce9f6", "#f5e7d3", "#e3eede", "#f6efd4"]
TOP, ROW, H = 150, 36, 34


def labels(cell: str) -> list[str]:
    path = EVAL_DIR / "transcripts" / f"{SCRIPT}_{cell}_run{RUN}.jsonl"
    return [(json.loads(l).get("remember") or {}).get("label", "") for l in path.open()]


def fills(names: list[str]) -> list[str]:
    """同じ名前が2ターン以上続く区間に色を付ける(区間ごとに色を回す)。"""
    out = ["#ffffff"] * len(names)
    i, k = 0, 0
    while i < len(names):
        j = i
        while j + 1 < len(names) and names[j + 1] == names[i]:
            j += 1
        if j > i:
            for t in range(i, j + 1):
                out[t] = BANDS[k % len(BANDS)]
            k += 1
        i = j + 1
    return out


def main() -> None:
    on, off = labels("contrarian-on"), labels("contrarian-off")
    fon, foff = fills(on), fills(off)
    el = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="960" viewBox="0 0 1160 960" '
        f"font-family=\"'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif\">",
        f'<rect width="1160" height="960" fill="{BG}"/>',
        f'<text x="80" y="52" font-size="19" fill="{INK}">称賛→立腹台本で、天邪鬼が各ターン末に保存した感情の名前（label）</text>',
        f'<text x="80" y="80" font-size="14" fill="{MUTED}">色の帯は、同じ名前が2ターン以上使われた区間です。</text>',
        f'<text x="340" y="128" font-size="16" fill="{INK}" text-anchor="middle">想起あり（{RUN}回目の実行）</text>',
        f'<text x="840" y="128" font-size="16" fill="{INK}" text-anchor="middle">想起なし（{RUN}回目の実行）</text>',
    ]
    for t in range(20):
        y = TOP + t * ROW
        for x, name, fill in ((120, on[t], fon[t]), (620, off[t], foff[t])):
            el.append(f'<rect x="{x}" y="{y}" width="440" height="{H}" rx="4" fill="{fill}" '
                      f'stroke="{LINE}" stroke-width="1"/>')
            el.append(f'<text x="{x + 14}" y="{y + 23}" font-size="15" fill="{INK}">{escape(name)}</text>')
        el.append(f'<text x="108" y="{y + 23}" font-size="12" fill="{MUTED}" text-anchor="end">t{t + 1}</text>')
    yp = TOP + 10 * ROW - 1
    el += [
        f'<line x1="100" y1="{yp}" x2="1080" y2="{yp}" stroke="{PIVOT}" stroke-width="1.6" stroke-dasharray="6,5"/>',
        f'<text x="1084" y="{yp - 6}" font-size="13" fill="{PIVOT}" text-anchor="end">↑ここまで称賛　↓t11で本人の失敗が発覚</text>',
        f'<text x="80" y="930" font-size="15" fill="{MUTED}">どちらの側も経験は毎ターン保存されます。違いは、保存した経験が次のターンに想起されて渡るかどうかだけです。</text>',
        "</svg>",
    ]
    OUT.write_text("\n".join(el) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
