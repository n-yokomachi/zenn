"""付録「各モデルの状態の推移」の表を生成するスクリプト。

  uv run python appendix-states.py <evaluation の退避ディレクトリ>×4（plutchik russell occ barrett の順）

感情エンジンあり（バレットは想起あり）の4パターンについて、20ターンの状態の
3回の平均と応答の感情スコアを Markdown の表で標準出力に書く。
"""
from __future__ import annotations
import csv, json, sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

RUNS=(1,2,3); TURNS=range(1,21)
SCRIPTS=[("direct-anger-to-praise","和解台本"),("direct-praise-to-anger","叱責台本")]
CELLS=[("friendly-on","フレンドリー"),("contrarian-on","天邪鬼")]
JA={"joy":"喜び","acceptance":"受容","fear":"恐れ","surprise":"驚き","sorrow":"悲しみ","disgust":"嫌悪","anger":"怒り","expectancy":"予期",
 "valence":"valence","arousal":"arousal",
 "distress":"苦悩","hope":"希望","satisfaction":"充足","disappointment":"失望","relief":"安堵","fears-confirmed":"恐れの的中",
 "happy-for":"共感的喜び","pity":"哀れみ","resentment":"妬み","gloating":"シャーデンフロイデ","pride":"誇り","shame":"恥",
 "admiration":"敬服","reproach":"非難","love":"好意","hate":"反感","gratification":"達成感","gratitude":"感謝","remorse":"悔恨"}
OCC_ORDER=["joy","distress","hope","fear","satisfaction","disappointment","relief","fears-confirmed","happy-for","pity","resentment","gloating","pride","shame","admiration","reproach","love","hate","gratification","gratitude","remorse","anger"]

def load(d: Path):
    pol=defaultdict(dict)
    for r in csv.DictReader(open(d/"results/per_turn_scores.csv")):
        pol[(r["script"],r["cell"],int(r["run"]))][int(r["turn"])]=float(r["polarity"])
    tr={}
    for s,_ in SCRIPTS:
        for c,_ in CELLS:
            for run in RUNS:
                tr[(s,c,run)]=[json.loads(l) for l in open(d/f"transcripts/{s}_{c}_run{run}.jsonl")]
    return pol,tr

def fmt(v): return f"{v:+.2f}".replace("-","−") if v<0 else f"{v:.2f}"

def tables(model, d, order=None, labels=False):
    pol,tr=load(d); out=[]
    for s,sn in SCRIPTS:
        for c,cn in CELLS:
            recs={r:tr[(s,c,r)] for r in RUNS}
            axes=order or list(recs[1][0]["axes"].keys())
            m={ax:[mean(recs[r][t-1]["axes"][ax] for r in RUNS) for t in TURNS] for ax in axes}
            if order: axes=[ax for ax in axes if max(abs(v) for v in m[ax])>=0.005]
            head=["ターン"]+[JA.get(a,a) for a in axes]+(["名前（1回目／2回目／3回目）"] if labels else [])+["感情スコア"]
            out.append(f"### {sn}の{cn}（{'想起' if labels else '感情エンジン'}あり）\n")
            out.append("| "+" | ".join(head)+" |"); out.append("|"+" --- |"*len(head))
            for t in TURNS:
                row=[str(t)]+[fmt(m[a][t-1]) for a in axes]
                if labels:
                    row.append("／".join(((recs[r][t-1].get("remember") or {}).get("label") or "—") for r in RUNS))
                row.append(fmt(mean(pol[(s,c,r)][t] for r in RUNS)))
                out.append("| "+" | ".join(row)+" |")
            out.append("")
    return "\n".join(out)

if __name__=="__main__":
    pl,ru,oc,ba=[Path(a) for a in sys.argv[1:5]]
    print("## プルチックの感情の輪\n"); print(tables("plutchik",pl,order=["joy","acceptance","fear","surprise","sorrow","disgust","anger","expectancy"]))
    print("## ラッセルの円環モデル\n"); print(tables("russell",ru))
    print("## OCCモデル\n"); print(tables("occ",oc,order=OCC_ORDER))
    print("## バレットの構成主義的情動理論\n"); print(tables("barrett",ba,labels=True))
