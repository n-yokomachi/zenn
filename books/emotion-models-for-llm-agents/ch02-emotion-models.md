---
title: "感情モデルの整理"
---

<!-- 執筆進捗: レビュー済み（節ごとの進捗は各見出し横に記載） -->

本章では感情心理学の理論群を4つの系統（パラダイム）に整理する。後半の4つの章ではこの4系統に沿って理論と実装を扱う。なおこの4系統は筆者が実装の都合で分けたもので、標準化された分類ではない。分類のしかた自体が論者によって分かれるので、まずその事情を示してから本書の4系統を提示する。

## 感情とは何か <!-- レビュー済み -->

「人間の感情とは何か」については定説がない。それでもAIエージェントに感情を持たせようとすると、まず感情らしきもののパラメータ化と調節を考えることになる。喜びと悲しみを1本の軸の両端に置くのか、それぞれ独立した量として持つのか。怒りと恐怖は別の感情なのか、どちらも不快で覚醒（興奮や活性化の度合い）の高い状態の言い換えなのか。それらのパラメータは誰が調節するのか。自然発生的にランダムな変動なのか、時間により移り変わるものなのか、内的な環境の変化によるものなのか、外界に影響されて現れ出でる何かなのか。

Tracy（以降トレイシー）とRandles（以降ランドルズ）は2011年に、基本感情説（生物学的に基本的な感情があるとする立場）に属する4つのモデルを比較した[^tracy2011]。同論文は4つのモデルの考え方が「現在の感情科学の研究とおおむね収束している」としつつ[^tr-converge]、細部は一致しないとしている。たとえばpride（誇り）を基本感情に数えるかどうかはモデルによって異なる。基本感情の数も学者によって3から11まで幅がある[^plutchik2001]。さらに感情をカテゴリーとして数えること自体と競合する立場もある。Russell（以降ラッセル）が1980年に提唱した円環モデルは、感情を快-不快と覚醒度の2つの軸の上の位置として表す[^russell1980]。

このように感情を説明するモデルは数多くあっても定説はない。そこでAIエージェントで感情を模倣するときの参考として、大きくパラダイムを整理したうえでそれぞれの代表となるものをピックアップすることにした。本章で示す4つの系統は、筆者が実装で参照したモデルを、その背景や関連の度合いで整理した結果である。

## 既存の系統分類の例 <!-- レビュー済み -->

先行する系統分類の例をいくつか挙げる。

まず違いが分かりやすいのがウィリアム・ジェームズの位置づけである。ジェームズは1884年に感情研究の出発点とされる論文「What is an Emotion?」[^james1884]を書いた心理学者である。後述する総説によれば「現代の感情研究の文献では、ジェームズはしばしば基本感情説の論者として言及される」とされ、その例としてLevenson（1992）が挙げられている[^gb-james-misread]。
構成主義的情動理論の提唱者であるBarrett（以降バレット）は、2009年にGendron（以降ジェンドロン）との共著で感情理論の1世紀を振り返る総説を発表している[^gendron-barrett2009]。同論文はジェームズを心理構成主義に分類し「ジェームズは誤って基本感情説の論者と見なされている」と指摘している[^gb-james-misread]。
一方でCornelius（以降コーネリアス）は概説書『The Science of Emotion』（1996）で感情研究を4つの系統（コーネリアス自身の語では伝統、tradition）に分け[^cornelius1996]、ジェームズを独立した1つの系統に置いている。またこの分類には感情を次元で表すモデルの系統がなく、円環モデルのラッセルは基本感情への批判者として扱われるにとどまる。

既存の分類にも分類する側の関心が反映されていると言えそうである。
というわけで本節の裏の目的は、「本書における4つの系統もまた、筆者の恣意的な分類でもいいよね？」という予防線を張ることだった。

## 本書で扱う4つの系統 <!-- レビュー済み -->

本書はジェンドロンとバレットが示した3つの系統を土台にする。それが優れた分類だからではなく、本書の目的に合うからである。逆に上述のコーネリアスの分類を使わない理由は2つある。1つは次元で感情を表すモデルの系統がないことである。本書は快-不快や覚醒の軸で感情を持つ設計を扱う。もう1つは身体反応の立場を1つの系統に割いていることである。身体を持たないAIエージェントではそのままの形で扱えない。

ジェンドロンとバレットが示した3つの系統は基本感情（basic emotion）、評価（appraisal）、心理構成主義（psychological constructionist）である。同論文の定義では、基本感情の立場は「生物学的に特権的な種類の感情が、世界の対象や出来事によって自動的に引き起こされる」と考える。評価の立場では「感情は対象によって反射的あるいは習慣的に引き起こされるだけではなく、個人が対象に与える意味づけから生じる」とされる。心理構成主義は「感情は、それ自体は感情に特化していない、より基本的な心理的材料から構成された心的な複合物である」とみなす[^gb-definitions]。同論文は分類の基準を明示してはいないが、3つの定義がどれも感情がどこから生じるかを述べているため、その生成のしくみで分けたものと考えられる。

本書ではこの3系統をもとに心理構成主義をさらに分割し、次元論と構成主義的情動理論の2つに分ける。
次元論は感情を快-不快や覚醒の高低といった少数の次元の上の位置として表す理論である。ジェンドロンとバレットは、19世紀末に感情を快と不快、興奮と鎮静、緊張と弛緩の3つの次元（感情の材料）で捉えたWundt（以降ヴント）を心理構成主義の始まりに置いている[^gb-wundt]。この感情の材料は後にラッセルとバレットが1999年にcore affect（コア・アフェクト）として定義した[^russell-barrett1999]。ラッセルの2003年の論文「Core Affect and the Psychological Construction of Emotion」[^russell2003]も心理構成主義の展開として扱われている[^gb-stages]。
構成主義的情動理論はバレットの理論で、上述した感情の材料に概念による意味づけが加わって感情という経験が構成されるとする。なおラッセル自身は1999年と2003年の論文で構成主義へ立場を移しているが[^russell2003]、本書は1980年の円環モデルを使うのでラッセルを次元論の側として扱う。

以上を整理すると次のようになる。

![ジェンドロンとバレットの3系統から本書の4系統への対応。心理構成主義だけが材料と構成の2つに分かれる](/images/emotion-models-for-llm-agents/ch02-four-paradigms.png)

4つの呼称は日本語の定訳が見当たらないため、本書に限った造語である。

| 本書の呼称 | 対応する系統 | 本書で扱う代表とモデル | 章 |
| --- | --- | --- | --- |
| カテゴリーパラメーター型 | 基本感情（basic emotion） | Plutchik（以降プルチック）の感情の輪 | 第4章 |
| 次元パラメーター型 | 心理構成主義（psychological constructionist）のうち次元論 | ラッセルの円環モデル | 第5章 |
| 評価導出型 | 評価（appraisal） | OCCモデル | 第6章 |
| 経験構成型 | 心理構成主義（psychological constructionist）のうち構成主義的情動理論 | バレットの構成主義的情動理論 | 第7章 |

代表のモデルも筆者が選んだものである。カテゴリーパラメーター型ならEkman、次元パラメーター型なら快と覚醒に支配（dominance）を加えたPADモデル[^pad1974]、評価導出型なら評価の連鎖として定式化したSchererの理論[^scherer2005]、経験構成型ならSchachter（以降シャクター）とSinger（以降シンガー）の二要因説[^schachter-singer1962]を代表とすることもできる。本書が選んだモデルはその優劣ではなく、実装のしやすさと筆者の関心によるものである。

最も実装しやすいのはプルチックの感情の輪である。8つの基本感情に加えて対極の組や混ぜると別の感情になる組まで定義されているなど[^plutchik2001][^plutchik-relations]、理論が定めた関係をそのまま設計に使える点が最初の一歩としてやりやすいと考えた。
ラッセルの円環モデルは2軸という最小の構成で済むこと、OCCモデル（Ortony、Clore、Collinsの3人の姓の頭文字）[^occ1988]は評価から感情を導く手続きがif-thenの形で書けること、バレットは構成主義の中で計算モデルとしての先行研究があること[^tce-computational]も、設計上のしがらみが少ないと考えて代表に選んだ理由である。
いずれも感情理論を網羅的に比較した結果ではない。門外漢の筆者が無軌道に感情エンジンを作る過程で増えていった参考モデルを、後から整理し直したものである。

## 本書の分類に収まらないもの <!-- レビュー済み -->

本章の最後に、本書で扱う4つの系統に入らない理論の例も2つ紹介する。

1つはPanksepp（以降パンクセップ）の感情神経科学である。トレイシーとランドルズの比較対象の1つで基本感情説に数えられるが、感情の基盤を皮質下の神経回路に求める点が他と異なる。哺乳類に共通する一次的な情動システムとして、探索のSEEKING、養育のCARE、遊びのPLAYなど7つが挙げられている[^panksepp1998]。AIエージェントに実装する場合、構造はプルチックの8軸と大きく変わらないと考えられる。
もう1つは身体そのものが感情の原因になるという理論である。悲しいから泣くのではなく泣くから悲しいという順序で知られるジェームズの理論がこれにあたり、20世紀の終わりにはDamasioが、身体の状態が意思決定に先立って選択肢を絞り込むというソマティック・マーカー仮説を示している[^damasio1996]。身体があることを前提にする理論なので、身体を持たないAIエージェントには向かないと考えて本書では扱わない。

:::message
と、ここまで書いて気づいたが、身体が必ずしも物理的なものである必要があるかというと疑問が残る。2D・3Dモデルなどのソフトウェア的な身体を持ったAIエージェントで試してみるのも面白そうである。少し前まで3Dモデルを使ったAIエージェントを開発していたので、次の個人開発で試してみようと思う。

![筆者が開発している3Dモデル付きAIエージェント「TONaRi」](/images/emotion-models-for-llm-agents/ch02-tonari-v1.png)
:::

## まとめ <!-- レビュー済み -->

本章では既存の分類を紹介したうえで、本書で扱う4つの系統と代表モデルを整理した。
次章では4つに共通する課題として、感情を模倣するコンポーネントをどう設計するかを扱う。

## 参考文献

本章で言及した文献を登場順に挙げる。所在はDOIを優先し、無料で読めるものはそのURLを添える。

- Tracy, J. L., & Randles, D. (2011). Four Models of Basic Emotions: A Review of Ekman and Cordaro, Izard, Levenson, and Panksepp and Watt. Emotion Review, 3(4), 397-405. https://doi.org/10.1177/1754073911410747
- Plutchik, R. (2001). The Nature of Emotions. American Scientist, 89(4), 344-350. https://www.jstor.org/stable/27857503
- Russell, J. A. (1980). A Circumplex Model of Affect. Journal of Personality and Social Psychology, 39(6), 1161-1178. https://doi.org/10.1037/h0077714
- James, W. (1884). What is an Emotion? Mind, os-9(34), 188-205. 全文がhttps://psychclassics.yorku.ca/James/emotion.htm で公開されている
- Levenson, R. W. (1992). Autonomic Nervous System Differences among Emotions. Psychological Science, 3(1), 23-27. https://doi.org/10.1111/j.1467-9280.1992.tb00251.x
- Gendron, M., & Barrett, L. F. (2009). Reconstructing the Past: A Century of Ideas About Emotion in Psychology. Emotion Review, 1(4), 316-339. https://doi.org/10.1177/1754073909338877
- Cornelius, R. R. (1996). The Science of Emotion: Research and Tradition in the Psychology of Emotion. Prentice Hall. ISBN 0133001539. 絶版である。著者自身が同じ四分法を要約したCornelius, R. R. (2000). Theoretical Approaches to Emotion. Proceedings of the ISCA Workshop on Speech and EmotionがISCAアーカイブで無料公開されている
- Wundt, W. (1896). Grundriss der Psychologie. Wilhelm Engelmann. 英訳Outlines of Psychology（1897）の全文がhttps://psychclassics.yorku.ca/Wundt/Outlines/ で公開されている
- Russell, J. A., & Barrett, L. F. (1999). Core Affect, Prototypical Emotional Episodes, and Other Things Called Emotion: Dissecting the Elephant. Journal of Personality and Social Psychology, 76(5), 805-819. https://doi.org/10.1037/0022-3514.76.5.805
- Russell, J. A. (2003). Core Affect and the Psychological Construction of Emotion. Psychological Review, 110(1), 145-172. https://doi.org/10.1037/0033-295X.110.1.145
- Mehrabian, A., & Russell, J. A. (1974). An Approach to Environmental Psychology. MIT Press. ISBN 978-0-262-13090-5
- Scherer, K. R. (2005). What are emotions? And how can they be measured? Social Science Information, 44(4), 695-729. https://doi.org/10.1177/0539018405058216
- Schachter, S., & Singer, J. E. (1962). Cognitive, Social, and Physiological Determinants of Emotional State. Psychological Review, 69(5), 379-399. https://doi.org/10.1037/h0046234
- Ortony, A., Clore, G. L., & Collins, A. (1988). The Cognitive Structure of Emotions. Cambridge University Press. https://doi.org/10.1017/CBO9780511571299 （2022年に第2版が出ている。ISBN 9781108928755）
- Barrett, L. F. (2017). The Theory of Constructed Emotion: An Active Inference Account of Interoception and Categorization. Social Cognitive and Affective Neuroscience, 12(1), 1-23. https://doi.org/10.1093/scan/nsw154
- Smith, R., Parr, T., & Friston, K. J. (2019). Simulating Emotions: An Active Inference Model of Emotional State Inference and Emotion Concept Learning. Frontiers in Psychology, 10, 2844. https://doi.org/10.3389/fpsyg.2019.02844
- Panksepp, J. (1998). Affective Neuroscience: The Foundations of Human and Animal Emotions. Oxford University Press.
- Damasio, A. R. (1996). The Somatic Marker Hypothesis and the Possible Functions of the Prefrontal Cortex. Philosophical Transactions of the Royal Society B, 351(1346), 1413-1420. https://doi.org/10.1098/rstb.1996.0125 （一般書としてはDamasio, A. R. (1994). Descartes' Error: Emotion, Reason, and the Human Brain. Putnam.）

[^tracy2011]: Tracy & Randles (2011). https://doi.org/10.1177/1754073911410747

[^tr-converge]: Tracy & Randles (2011)のアブストラクトの原文は"largely converge with the current state of affective science research"である。

[^plutchik2001]: Plutchik (2001). https://www.jstor.org/stable/27857503

[^russell1980]: Russell (1980). https://doi.org/10.1037/h0077714 。原文は"My thesis is that affective states are, in fact, best represented as a circle in a two-dimensional bipolar space."である。

[^james1884]: James (1884). 全文がhttps://psychclassics.yorku.ca/James/emotion.htm で公開されている。

[^gb-james-misread]: Gendron & Barrett (2009)の原文は"In modern works on emotion, James is often referred to as a basic emotion theorist (e.g., Levenson, 1992)."である。同論文はこの引用のされ方を"James is mistakenly thought of as a basic emotion theorist"と誤りだと述べている。Levenson (1992)の書誌は参考文献を参照。

[^gendron-barrett2009]: Gendron & Barrett (2009). https://doi.org/10.1177/1754073909338877

[^cornelius1996]: Cornelius (1996)。traditionの語は書名の副題Research and Tradition in the Psychology of Emotionにも現れる。著者自身による要約論文（Cornelius 2000）では"four of the most influential theoretical perspectives and research traditions in the study of emotion"と紹介されている。

[^gb-definitions]: Gendron & Barrett (2009)の原文は、基本感情が"certain biologically privileged kinds of emotion are automatically triggered by objects and events in the world"、評価が"emotions are not merely triggered by objects in a reflexive or habitual way, but arise from a meaningful interpretation of an object by an individual"、心理構成主義が"emotions are psychical compounds that are constructed out of more basic psychological ingredients that are not themselves specific to emotion"である。

[^gb-wundt]: Gendron & Barrett (2009)の原文は"Along with William James, Wilhelm Wundt is the other major figure of the Golden Years who crafted a psychological constructionist approach to emotion."である。

[^russell-barrett1999]: Russell & Barrett (1999). https://doi.org/10.1037/0022-3514.76.5.805

[^russell2003]: Russell (2003). https://doi.org/10.1037/0033-295X.110.1.145 。アブストラクトに"an approach based on the concepts of core affect and psychological construction"とある。

[^gb-stages]: Gendron & Barrett (2009)の原文は"In some models, these ingredients combine in stages (e.g., Russell, 2003; Schachter & Singer, 1962; Wundt, 1897/1998)."である。

[^pad1974]: Mehrabian & Russell (1974). ISBN 978-0-262-13090-5

[^scherer2005]: Scherer (2005). https://doi.org/10.1177/0539018405058216

[^schachter-singer1962]: Schachter & Singer (1962). https://doi.org/10.1037/h0046234

[^plutchik-relations]: Plutchik (2001)の原文は、対極が"I suggested eight basic bipolar emotions: joy versus sorrow, anger versus fear, acceptance versus disgust and surprise versus expectancy."、混合（一次双対）が"mixing joy and acceptance produces the mixed emotion of love; disgust plus anger produces hatred or hostility. Such mixtures have been called primary dyads in the theory."である。

[^occ1988]: Ortony, Clore & Collins (1988). https://doi.org/10.1017/CBO9780511571299

[^tce-computational]: バレット自身が能動的推論（active inference）の枠組みで理論を定式化したBarrett (2017) https://doi.org/10.1093/scan/nsw154 と、感情状態の推定と感情概念の学習を能動的推論の計算モデルとして実装したSmith, Parr & Friston (2019) https://doi.org/10.3389/fpsyg.2019.02844 がある。

[^panksepp1998]: Panksepp (1998)。7つのシステムはSEEKING（探索）、RAGE（怒り）、FEAR（恐れ）、LUST（性欲）、CARE（養育）、PANIC/GRIEF（悲嘆）、PLAY（遊び）である。原著の表記はPANICで、PANIC/GRIEFは後年に精緻化された表記である。

[^damasio1996]: Damasio (1996). https://doi.org/10.1098/rstb.1996.0125
