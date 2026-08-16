# ch6 文献拡張収集（2026-08-16・Fable 調査）

第6章（評価導出型・OCC）のための候補リスト。全13件、書誌はすべて一次資料（出版社・ジャーナル・arXiv・機関リポジトリ・Crossref）で検証済み。ch2 収集分（Moors 2009・Scherer 2005・EMA・CoRE・Yeo & Jaidka・OCC 原典と2022新版など）との重複なし。**採否はオーナー判断待ち**。

## 収集全体からの重要な所見

「OCC のルールを明示的に LLM に接続した 2024〜2026 の実装研究」は探索範囲では見つからなかった。最接近は Croissant 2024（評価ベースだが OCC 非依存・感情は LLM 自身が生成）と GAMYGDALA 2014（OCC 決定論ルールエンジンだが pre-LLM）。第6章の構成（LLM は評価だけを申告し、OCC ルールが感情を導出）はこの2系統の合流点に位置する。⚠ ただし全章方針「初めての試み・新しいアプローチと書かない」に従い、新規性の主張はせず先行2系統との位置関係の記述にとどめる。

## 系統1: OCC の位置づけ・評価理論のレビュー/ハンドブック級・形式化（4件）

1. Scherer, K. R., Schorr, A., & Johnstone, T. (Eds.) (2001). Appraisal Processes in Emotion: Theory, Methods, Research. Oxford University Press. ISBN 9780195130072. DOI 10.1093/oso/9780195130072.001.0001
   - 評価理論の標準ハンドブック。OCC を「評価理論ファミリー」の一員として位置づける背景文献
   - 検証: Crossref・https://academic.oup.com/book/53557
2. Moors, A., Ellsworth, P. C., Scherer, K. R., & Frijda, N. H. (2013). Appraisal theories of emotion: State of the art and future development. Emotion Review, 5(2), 119-124. doi:10.1177/1754073912468165
   - 評価理論の代表的レビュー（6頁）。「評価→感情」の理論前提を1本で支える。ch2 の Moors 2009 とは別論文
   - 検証: https://journals.sagepub.com/doi/abs/10.1177/1754073912468165
3. Marsella, S., Gratch, J., & Petta, P. (2010). Computational models of emotion. In A Blueprint for Affective Computing (pp. 21-46). Oxford University Press. ISBN 9780199566709
   - 計算感情モデル研究の標準レビュー章。EMA と OCC 系実装の関係の参照点
   - 検証: 著者機関ページ＋OUP 書籍ページ。⚠ 頁 21-46 は二次情報由来。本文で頁を書く場合は再確認
4. Steunebrink, B. R., Dastani, M., & Meyer, J.-J. Ch. (2009). The OCC model revisited. Proc. 4th Workshop on Emotion and Computing (KI 2009).
   - OCC の論理構造の曖昧さ・不整合を特定し再構成を提案した形式化研究。「原典のままではルールに落とせない箇所がある」の一次資料
   - 検証: 著者 PDF https://people.idsia.ch/~steunebrink/Publications/KI09_OCC_revisited.pdf（1頁目実見）。⚠ ワークショップ名は二次情報由来。本文で venue 名を使う場合は再確認

## 系統2: OCC・評価理論への批判・修正の一次資料（4件）

5. Zajonc, R. B. (1980). Feeling and thinking: Preferences need no inferences. American Psychologist, 35(2), 151-175. doi:10.1037/0003-066X.35.2.151
6. Lazarus, R. S. (1982). Thoughts on the relations between emotion and cognition. American Psychologist, 37(9), 1019-1024. doi:10.1037/0003-066X.37.9.1019
   - 感情-認知プライマシー論争の直接応酬ペア。「評価→感情」という前提自体が争われてきた事実の土台。ch2 の Ekman-Russell 応酬と同型の同誌上論争
   - 検証: Crossref（両 DOI）
7. Clore, G. L., & Ortony, A. (2013). Psychological construction in the OCC model of emotion. Emotion Review, 5(4), 335-343. doi:10.1177/1754073913489751
   - OCC 著者2名による四半世紀後の再解釈（評価はトリガーではなく感情を区別する状況の心理的側面）。構成主義との接続。本章の設計との整合・緊張を論じる最重要候補。ch7 への橋の材料にもなりうる
   - 検証: Crossref
8. Ortony, A. (2003). On making believable emotional agents believable. In Emotions in Humans and Artifacts (pp. 189-211). MIT Press.
   - 筆頭著者自身が「エージェント実装には22カテゴリは複雑すぎる」として簡素化を提案。実装上の限界を著者本人の言として書ける
   - 検証: MIT Press Direct 章ページ

## 系統3: 2024〜2026 の LLM × 評価ベース感情研究（4件＋関連1件）

9. Croissant, M., Frister, M., Schofield, G., & McCall, C. (2024). An appraisal-based chain-of-emotion architecture for affective language model game agents. PLOS ONE, 19(5), e0301033. doi:10.1371/journal.pone.0301033
   - 評価ステップを挟んでから感情を生成する構造が対照条件より優ることを3実験で示した査読済み実証。本章の対照実験設計の直接の先行例。最優先候補
   - 検証: PLOS ONE 誌面ページ（arXiv 版 2309.05076）
10. Tak, A. N., & Gratch, J. (2023). Is GPT a computational model of emotion? Detailed analysis. arXiv:2307.13779
    - GPT の感情推論を評価理論の成分ごとに検証。評価と感情ラベルは人間と一致するが強度・対処は苦手。「LLM に評価だけを申告させる」役割分担の実証的裏付け
    - 検証: arXiv。⚠ ACII 2023 発表の旨は二次情報由来。引用は arXiv 版が安全
11. Tak, A. N., & Gratch, J. (2024). GPT-4 emulates average-human emotional cognition from a third-person perspective. arXiv:2408.13718
    - GPT-4 は第三者視点の感情推定で人間と顕著に一致する続編。外部状態を第三者的ルールで導出する設計の傍証
    - 検証: arXiv
12. Sun, Z., Xu, H., Uusberg, A., Gross, J. J., Slovak, P., & He, Y. (2026). CAREBench: Evaluating LLMs' emotion understanding by assessing cognitive appraisal reasoning. arXiv:2605.17176
    - 認知的評価推論のプロセスレベル評価ベンチマーク（共著に Gross）。2026 年の評価系ベンチマークの最新点
    - 検証: arXiv
13. Cai, J., et al. (2026). From triggers to emotions: A CPM-grounded appraisal multi-agent for dynamic emotional evolution in persona-based dialogue. arXiv:2607.07824
    - Scherer の CPM 基盤でイベント評価→感情状態を動的更新するマルチエージェント。本章と同型アーキテクチャの最新例・OCC でなく CPM を選んだ対比
    - 検証: arXiv（査読先未記載）

関連（pre-LLM・本章設計の直系先行）: Popescu, A., Broekens, J., & van Someren, M. (2014). GAMYGDALA: An emotion engine for games. IEEE Transactions on Affective Computing, 5(1), 32-44. doi:10.1109/T-AFFC.2013.24
- OCC を決定論的ルールエンジンとして実装した感情エンジン。Croissant 2024 と組み合わせて本章の位置（2系統の合流点）を書ける
- 検証: Crossref・著者機関 PDF

## 系統4: 「OCC は感情合成の標準モデル」という通説の帰属先（検証済み・即引用可）

Bartneck, C. (2002). Integrating the OCC model of emotions in embodied characters. Proc. Workshop on Virtual Conversational Characters, Melbourne.
- 正確な引用（PDF 実見）: "The OCC (Ortony, Clore, & Collins, 1988) model has established itself as the standard model for emotion synthesis."
- 「OCC は感情合成の標準モデルとしての地位を確立した（Bartneck 2002）」と帰属付きで書ける。22カテゴリ・履歴機能欠如など実装上の欠落の列挙もあり系統2の補助にも
- 補助帰属: Steunebrink et al. (2009) abstract 冒頭 "Although popular among computer scientists, the OCC model of emotions..."（PDF 実見）
- 検証: 著者本人サイト PDF https://www.bartneck.de/publications/2002/integratingTheOCCModel/bartneckHF2002.pdf

## 調査エージェントの絞り込み推奨（10件前後に絞る場合）

系統1は 2（Moors 2013）と 4（Steunebrink）を優先。系統2は 7（Clore & Ortony 2013）と 8（Ortony 2003）を優先（Zajonc/Lazarus は章の射程が論争史まで広がる場合のみ）。系統3は 9（Croissant）が最優先。系統4（Bartneck）と GAMYGDALA は本章の位置づけに直結するため採用推奨。
