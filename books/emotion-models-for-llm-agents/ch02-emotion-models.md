---
title: "感情モデルの整理"
---

<!-- 執筆進捗: 改稿済み（節ごとの進捗は各見出し横に記載） -->

本章では、感情心理学の理論群を4つの系統に整理します。第4章から第7章までは、この4つに沿って理論とその実装を扱います。

先に断っておくことがあります。この4系統は筆者が実装の都合で切ったものであり、なんらかの標準化された分類ではありません。そもそも分類のしかた自体が論者によって割れるという事情もあります。本章は、その事情を示した上で、本書における4つの系統分類を提示するという順序で進めます。

## 感情とは何か <!-- 改稿済み -->

まず直感的に誰もが理解しているであろうこととして、「人間の感情とは何か」については定説がありません。
その上で、人ではなくAIエージェントに感情を持たせようとして最初に思いつくのは、感情らしきもののパラメータ化とその調節です。喜びと悲しみを1本の軸の両端に置くのか、それぞれ独立した量として持つのか。怒りと恐怖は別の感情なのか、どちらも不快で覚醒（興奮や活性化の度合い）の高い状態の言い換えなのか。それらのパラメータは誰が調節するのか。自然発生的にランダムな変動なのか、時間により移り変わるものなのか、内的な環境の変化によるものなのか、外界に影響されて現れ出でる何かなのか。

Tracy（以降トレイシー）とRandles（以降ランドルズ）は2011年に、基本感情説の立場をとるある4つのモデルを並べて比較しています[^tracy2011]。基本感情説は生物学的に基本的な感情があるとする立場で、4つのモデルはいずれもこの系統に属しています。実際、同論文も、4つのモデルが論じる基本的な概念は大枠で共通しており、当時の感情研究の到達点とおおむね収束していると述べています[^tr-converge]。それでも各モデルの詳細に踏み込むとその考えには一致しない部分が出てきます。たとえばpride（誇り）を基本感情に数えるかどうかはモデルによって異なります。
さらに立場をまたぐと、感情を構成する要素の相違も大きくなります。そもそも基本感情がいくつあるのかという数の時点で学者によって異なり、3要素〜11要素まで大きな幅があります[^plutchik2001]。さらに、少数の基本感情というカテゴリーで感情を数える枠組みそのものと競合する立場もあります。Russell（以降ラッセル）が1980年に提唱した円環モデルは、感情を独立したカテゴリーの集まりとしてではなく、快-不快と覚醒度の2つの軸が構成する空間の中の位置として表します[^russell1980]。カテゴリーとして数えるのか、次元の上の位置として表すのか。感情をどう分けるかという入り口から、このように立場が割れています。

そういうわけで、感情がどういうものかを説明するモデルは数多くあれども、定説や正解などはありません。ただしAIエージェントにおいて感情を模倣しようとする時のリファレンスとして、これらのモデルを活用できるのではないかと思います。改めて本章がこれから示す4つの系統は、筆者が恣意的に分類したものです。筆者が感情を模倣するコンポーネントを実装するうえで参照したモデルを、その背景や似たもの同士で整理した結果です。

## 既存の系統分類例 <!-- 改稿済み -->

本書における4つの系統を出す前に、既存の系統分類が学者ごとに異なる例を紹介しておきます。

ウィリアム・ジェームズは、1884年に「What is an Emotion?」という感情研究の出発点的な扱いをされる論文[^james1884]を書いた心理学者です。
第7章で扱う構成主義的情動理論の提唱者であるBarrett（以降バレット）は、2009年にGendron（以降ジェンドロン）との共著で、感情理論の1世紀を振り返る総説（レビュー論文）を発表しています[^gendron-barrett2009]。本書がのちに土台にするのがこの論文の分類です。同論文はジェームズを心理構成主義の系統に置き、彼を基本感情説の先駆として引用する現代の文献があることを誤った分類と指摘しています[^gb-james-misread]。

一方、感情心理学の研究者Cornelius（以降コーネリアス）が単著で著した概説書『The Science of Emotion』（1996）で示した分類では、ジェームズは独立した一つの系統の起点とされています。コーネリアスは感情研究を4つの系統（コーネリアス自身の語では伝統、tradition）に分けており[^cornelius1996]、基本感情の系統とも、認知的な評価の系統とも別に、ジェームズの名を冠した系統が独立して立てられています。同じ人物が、一方では他の系統に吸収され、もう一方では系統そのものとして捉えられているのです。また、コーネリアスの分類には、感情を次元で表すモデルが属する系統がありません。円環モデルという次元論を展開した当のラッセルも、この分類の中では基本感情の系統への批判者として現れるだけで、次元論の属する系統がないのです。

以上のことから、既存の系統分類も各理論の性質だけではなく、分類する側の関心が反映されている余地も十分ありそうです。簡単に言うと恣意的な分類とも捉えられるということです。
というわけで本節の裏の目的は、「本書における4つの系統もまた、筆者の恣意的な分類でもいいよね？」という予防線を張ることでした。

## 本書で扱う4つの系統 <!-- 改稿済み -->

本書は、ジェンドロンとバレットが2009年の論文で示した3つの系統を土台にします。これが優れた分類だからではなく、本書の目的に合うからです。

前節で触れたコーネリアスの系統分類を土台にしない理由は2つあります。一つは、前節で触れたとおりコーネリアスの4系統には次元で感情を表すモデルの系統がないことです。本書は快と不快、覚醒の高低といった軸で感情を持つ設計を扱うため、そのモデルが含まれない分類では足りません。もう一つは、コーネリアスが身体反応に関連する立場を1つの系統に割いていることです。前節でジェームズが起点に立てられていると書いた系統がこれにあたります。（現時点では一般に）身体を持たないAIエージェントでは、そのままの形では扱えない系統になります。

ジェンドロンとバレットの3つは、基本感情（basic emotion）、評価（appraisal）、心理構成主義（psychological constructionist）です。同論文の定義に沿うと、それぞれ次のようになります。基本感情の立場は、生物学的に特権的な種類の感情があり、それが世界の対象や出来事によって自動的に引き起こされると考えます。評価の立場では、感情は対象によって反射的あるいは習慣的に引き起こされるだけのものではなく、個人が対象に与える意味づけから生じます。心理構成主義は、感情を、それ自体は感情に特化していない、より基本的な心理的材料から構成された心的な複合物とみなします[^gb-definitions]。
同論文に、分類の軸を明示的に宣言する記述は見当たりません。ただ、3つの定義がどれも感情がどこから生じるかを語っているため、生成のしくみで分けたものだと考えられます。何によって記述するかでも、どう計測するかでもなく、感情を何から作るかという本書の関心には、この分類軸が噛み合うと考えました。

そんなわけで本書ではこの3系統をベースにしつつ、さらに細かく心理構成主義の系統を2つに分けます。

ジェンドロンとバレットは、19世紀末に感情を3つの次元で捉えたWundt（以降ヴント）を、心理構成主義の系統の始まりに置いています[^gb-wundt]。快と不快、興奮と鎮静、緊張と弛緩という独立した性質の組み合わせで感情を捉える立場です。この、感情を構成する材料にあたる部分は、後にラッセルとバレットが1999年にcore affect（コア・アフェクト。日本語文献でもカタカナ表記が通例です）として定義しました[^russell-barrett1999]。ジェンドロンとバレットは、ラッセルが2003年に発表した論文「Core Affect and the Psychological Construction of Emotion」[^russell2003]も、この系統の展開として扱っています[^gb-stages]。
本書において心理構成主義を細分化するうちの一つは、ヴントやラッセル（2003）が説明する、感情を構成する材料そのものに注目する理論です。材料は快-不快などの軸を基準とした次元上の位置として表されます。もう一つは、バレットが提唱する、その材料に概念による意味づけが加わって感情という経験が構成されるとする理論です。
理論の上では、この2つは連続したひとつの説明です。材料があり、その材料から経験が構成される、という順につながっています。しかし感情コンポーネントとして作る場合、材料の数値だけを外部に持つ設計と、数値に名前を与えて記憶まで持つ設計とでは、必要な部品や保存するデータの形が変わります。そのため本書では、この2つを別の系統として数えます。

ラッセルの位置は少し悩むところです。1980年に円環モデルを提唱したラッセルは、感情を2つの軸を基準とした次元の位置として表す次元論の立場といえますが、1999年にはcore affectの論文をバレットと共著し、2003年には前述の論文で自らpsychological constructionの語を掲げており[^russell2003]、構成主義へ立場が移っています。本書では便宜的にラッセルを前者、つまり次元論の立場として捉えます。と言うのも本書においては1980年のラッセルの円環モデルを参考にしているためです。

さて、では本書における4系統を整理しましょう。

![ジェンドロンとバレットの3系統から本書の4系統への対応。心理構成主義だけが材料の層と構成の層に分かれる](/images/emotion-models-for-llm-agents/ch02-four-paradigms.png)

本書における各系統の名称もここで決めておきます。日本語の定訳が見当たらないため、本書に限った造語です。

| 本書の呼称 | 対応する系統 | 本書で扱う代表とモデル | 章 |
| --- | --- | --- | --- |
| カテゴリーパラメーター型 | basic emotion | Plutchik（以降プルチック）の感情の輪 | 第4章 |
| 次元パラメーター型 | dimensional（心理構成主義から切り出し） | ラッセルの円環モデル | 第5章 |
| 評価導出型 | appraisal | OCCモデル | 第6章 |
| 経験構成型 | psychological constructionist | バレットの構成主義的情動理論 | 第7章 |

各系統やモデルの説明は以降の章で行います。

## 各系統の代表モデルの選出理由 <!-- 改稿済み -->

上の表と図には、4つの系統の代表としてプルチック、ラッセル、OCCモデル、バレットの名前を出しましたが、断っておくとこの代表も筆者が恣意的に選んでいます。

基本感情の系統ならEkmanを代表とみなすこともできますし、次元の系統には、快と覚醒に支配（dominance）を加えたPADモデルがあります[^pad1974]。また評価の系統では、感情の生起を複数の評価の連鎖として定式化したSchererの理論が知られており[^scherer2005]、心理構成主義の系統からは、Schachter（以降シャクター）とSinger（以降シンガー）の二要因説を挙げられます[^schachter-singer1962]。
そんな中で本書がプルチック、ラッセル、OCCモデル、バレットを選んだのは、理論としての優劣によるものではありません。実装のしやすさと、筆者がどこに関心を持ったかによる選択の結果です。

最も実装しやすいのはプルチックです。8つの基本感情に、対極をなす組と、混ぜ合わせると別の感情になる組が定義されています[^plutchik2001]。喜びの反対は悲しみ、嫌悪と怒りを混ぜれば憎悪、というように、感情同士の関係が理論の側ですでに決まっています[^plutchik-relations]。対極どうしが1本の軸の両端として向かい合う関係まで理論に定義されており、理論が定めた関係構造をそのまま設計に流用できる点が、最初の一歩としてやりやすいと考えたためです。
残りの3つは、それぞれ別の理由で選びました。ラッセルは2軸という最小の構成で済むこと、OCCモデル（Ortony、Clore、Collinsの3人の姓の頭文字による通称）は評価から感情を導く手続きがif-thenの形で書けること、バレットは構成主義の中では計算モデルとしての先行研究があること[^tce-computational]がその理由です。

各モデルの選定は網羅的に比較検討した結果ではありません。本書の4系統は、理論の全体像から導出したものではありません。そもそも門外漢の初心者である筆者が全体像を把握できるはずもなく、コンポーネントを作る過程で増えていった参考モデルを後から整理し直したものです。

## 本書の分類に収まらないもの <!-- 改稿済み -->

以上、ここまでで本書で扱う4つの系統もその代表も、本書独自の整理となることを説明してきましたが、当然その中には入ってこない理論やモデルがあります。
この節では簡単に、他にどういった理論があるかの一部の例を紹介します。

一つはPanksepp（以降パンクセップ）の感情神経科学です。最初の節で挙げたトレイシーとランドルズの4つの比較対象の一つがパンクセップのため、基本感情説の一種として数えられてはいますが、この立場は感情の基盤を大脳皮質よりさらに下の、皮質下の神経回路に求める点で、他の3つとは着眼点が異なります。哺乳類に種を越えて共通する一次的な情動システムがあるとして、探索のSEEKING、養育のCARE、遊びのPLAYなど7つに名前が与えられています[^panksepp1998]。
本書ではパンクセップのモデルを取り上げはしませんが、AIエージェントに実装する場合その構造自体はプルチックの8軸モデルと大きく変わらないと考えられます。

もう一つの例として、身体そのものが感情の原因になるという理論があります。悲しいから泣くのではなく、泣くから悲しいという順序の逆転で知られる、ジェームズの理論がこれにあたります。20世紀の終わりにはDamasioが、身体の状態が意思決定に先立って選択肢を絞り込むというソマティック・マーカー仮説を提示しています[^damasio1996]。
なお、ジェンドロンとバレットの分類では、ジェームズは心理構成主義に含まれます。しかし身体反応説そのものが身体が備わっていることを前提にするため、（現時点では一般に）身体を持たないAIエージェントに状態として持たせるのは実装上の困難があるとして、本書では扱いません。
:::message
と、ここまで書いて気づきましたが、物理的な身体を備えている必要があるかと言うとそれには疑問符がつきます。つまり2D・3Dモデルなどのソフトウェア的な身体を持ったAIエージェントで実装を試してみるのも面白そうです。個人的に少し前まで3Dモデルを使用したAIエージェントの開発をしていたので、次の個人開発で試してみようと思います。

![筆者が開発している3Dモデル付きAIエージェント「TONaRi」](/images/emotion-models-for-llm-agents/ch02-tonari-v1.png)
:::

## まとめ <!-- 改稿済み -->

この章では本書で扱う4つの系統に関して、先行研究の例示から、本書で取り上げる理論や系統の整理をしてきました。
次章では、この4つに共通する課題、つまりAIエージェントが扱うために感情を模倣するコンポーネントをどう設計するのかを取り上げます。

## 参考文献

本章で言及した文献を、登場順に挙げます。所在は DOI を優先し、無料で読めるものはその URL を添えています。

- Tracy, J. L., & Randles, D. (2011). Four Models of Basic Emotions: A Review of Ekman and Cordaro, Izard, Levenson, and Panksepp and Watt. Emotion Review. https://doi.org/10.1177/1754073911410747
- Plutchik, R. (2001). The Nature of Emotions. American Scientist. https://www.jstor.org/stable/27857503
- Russell, J. A. (1980). A Circumplex Model of Affect. Journal of Personality and Social Psychology. https://doi.org/10.1037/h0077714
- James, W. (1884). What is an Emotion? Mind, os-9(34), 188-205. 全文は https://psychclassics.yorku.ca/James/emotion.htm で公開されています
- Gendron, M., & Barrett, L. F. (2009). Reconstructing the Past: A Century of Ideas About Emotion in Psychology. Emotion Review. https://doi.org/10.1177/1754073909338877
- Cornelius, R. R. (1996). The Science of Emotion: Research and Tradition in the Psychology of Emotion. Prentice Hall. ISBN 0133001539. 絶版ですが、著者自身が同じ四分法を要約した Cornelius, R. R. (2000). Theoretical Approaches to Emotion. Proceedings of the ISCA Workshop on Speech and Emotion が ISCA アーカイブで無料公開されています
- Wundt, W. (1896). Grundriss der Psychologie. Wilhelm Engelmann. 英訳 Outlines of Psychology（1897）の全文が https://psychclassics.yorku.ca/Wundt/Outlines/ で公開されています
- Russell, J. A., & Barrett, L. F. (1999). Core Affect, Prototypical Emotional Episodes, and Other Things Called Emotion: Dissecting the Elephant. Journal of Personality and Social Psychology. https://doi.org/10.1037/0022-3514.76.5.805
- Russell, J. A. (2003). Core Affect and the Psychological Construction of Emotion. Psychological Review. https://doi.org/10.1037/0033-295X.110.1.145
- Mehrabian, A., & Russell, J. A. (1974). An Approach to Environmental Psychology. MIT Press. ISBN 978-0-262-13090-5
- Scherer, K. R. (2005). What are emotions? And how can they be measured? Social Science Information. https://doi.org/10.1177/0539018405058216
- Schachter, S., & Singer, J. E. (1962). Cognitive, Social, and Physiological Determinants of Emotional State. Psychological Review. https://doi.org/10.1037/h0046234
- Ortony, A., Clore, G. L., & Collins, A. (1988). The Cognitive Structure of Emotions. Cambridge University Press. 2022年に新版が出ています（ISBN 9781108928755）
- Barrett, L. F. (2017). The Theory of Constructed Emotion: An Active Inference Account of Interoception and Categorization. Social Cognitive and Affective Neuroscience, 12(1), 1-23. https://doi.org/10.1093/scan/nsw154
- Smith, R., Parr, T., & Friston, K. J. (2019). Simulating Emotions: An Active Inference Model of Emotional State Inference and Emotion Concept Learning. Frontiers in Psychology, 10, 2844. https://doi.org/10.3389/fpsyg.2019.02844
- Panksepp, J. (1998). Affective Neuroscience: The Foundations of Human and Animal Emotions. Oxford University Press.
- Damasio, A. R. (1994). Descartes' Error: Emotion, Reason, and the Human Brain. Putnam. 学術論文としては Damasio, A. R. (1996). The Somatic Marker Hypothesis and the Possible Functions of the Prefrontal Cortex. Philosophical Transactions of the Royal Society B, 351(1346), 1413-1420. https://doi.org/10.1098/rstb.1996.0125

[^tracy2011]: Tracy & Randles (2011). https://doi.org/10.1177/1754073911410747

[^tr-converge]: 同論文アブストラクトの "largely converge with the current state of affective science research" の意訳です。

[^plutchik2001]: Plutchik (2001). https://www.jstor.org/stable/27857503

[^russell1980]: Russell (1980). https://doi.org/10.1037/h0077714。原文は "My thesis is that affective states are, in fact, best represented as a circle in a two-dimensional bipolar space." です。

[^james1884]: James (1884). 全文が https://psychclassics.yorku.ca/James/emotion.htm で公開されています。

[^gendron-barrett2009]: Gendron & Barrett (2009). https://doi.org/10.1177/1754073909338877

[^gb-james-misread]: 原文: "In modern works on emotion, James is often referred to as a basic emotion theorist (e.g., Levenson, 1992)."。同論文はこの引用のされ方を "James is mistakenly thought of as a basic emotion theorist" と誤りだと述べています。

[^cornelius1996]: Cornelius (1996)。tradition の語は書名の副題 Research and Tradition in the Psychology of Emotion にも現れます。著者自身による要約論文（Cornelius 2000）では "four of the most influential theoretical perspectives and research traditions in the study of emotion" と紹介されています。

[^gb-definitions]: 原文は、基本感情 "certain biologically privileged kinds of emotion are automatically triggered by objects and events in the world"、評価 "emotions are not merely triggered by objects in a reflexive or habitual way, but arise from a meaningful interpretation of an object by an individual"、心理構成主義 "emotions are psychical compounds that are constructed out of more basic psychological ingredients that are not themselves specific to emotion" です。

[^gb-wundt]: 原文: "Along with William James, Wilhelm Wundt is the other major figure of the Golden Years who crafted a psychological constructionist approach to emotion."

[^russell-barrett1999]: Russell & Barrett (1999). https://doi.org/10.1037/0022-3514.76.5.805

[^russell2003]: Russell (2003). https://doi.org/10.1037/0033-295X.110.1.145。アブストラクトに "an approach based on the concepts of core affect and psychological construction" とあります。

[^gb-stages]: 原文: "In some models, these ingredients combine in stages (e.g., Russell, 2003; Schachter & Singer, 1962; Wundt, 1897/1998)."

[^pad1974]: Mehrabian & Russell (1974). ISBN 978-0-262-13090-5

[^scherer2005]: Scherer (2005). https://doi.org/10.1177/0539018405058216

[^schachter-singer1962]: Schachter & Singer (1962). https://doi.org/10.1037/h0046234

[^plutchik-relations]: 対極は原文 "I suggested eight basic bipolar emotions: joy versus sorrow, anger versus fear, acceptance versus disgust and surprise versus expectancy."、混合（一次双対）は原文 "mixing joy and acceptance produces the mixed emotion of love; disgust plus anger produces hatred or hostility. Such mixtures have been called primary dyads in the theory." によります。

[^tce-computational]: バレット自身が能動的推論（active inference）の枠組みで理論を定式化した Barrett (2017) https://doi.org/10.1093/scan/nsw154 と、感情状態の推定と感情概念の学習を能動的推論の計算モデルとして実装した Smith, Parr & Friston (2019) https://doi.org/10.3389/fpsyg.2019.02844 があります。

[^panksepp1998]: Panksepp (1998)。7つのシステムは SEEKING（探索）、RAGE（怒り）、FEAR（恐れ）、LUST（性欲）、CARE（養育）、PANIC/GRIEF（悲嘆）、PLAY（遊び）。原著の表記は PANIC で、PANIC/GRIEF は後年に精緻化された表記です。

[^damasio1996]: Damasio (1996). https://doi.org/10.1098/rstb.1996.0125
