---
title: "付録：注釈"
---

本文で引いた文献の原文や、訳語と用語の補足を章ごとに挙げる。各項目の先頭は、注を付けた本文の箇所である。文献の書誌は付録「参考文献」に載せている。

## 感情モデルの整理

- 「現在の感情科学の研究とおおむね収束している」: Tracy & Randles (2011)のアブストラクトの原文は"largely converge with the current state of affective science research"である。
- 円環モデルの主張: Russell (1980)の原文は"My thesis is that affective states are, in fact, best represented as a circle in a two-dimensional bipolar space."である。
- 「ジェームズは誤って基本感情説の論者と見なされている」: Gendron & Barrett (2009)の原文は"In modern works on emotion, James is often referred to as a basic emotion theorist (e.g., Levenson, 1992)."である。同論文はこの引用のされ方を"James is mistakenly thought of as a basic emotion theorist"と誤りだと述べている。
- 「伝統、tradition」: Cornelius (1996)。traditionの語は書名の副題Research and Tradition in the Psychology of Emotionにも現れる。著者自身による要約論文（Cornelius 2000）では"four of the most influential theoretical perspectives and research traditions in the study of emotion"と紹介されている。
- 3つの系統の定義: Gendron & Barrett (2009)の原文は、基本感情が"certain biologically privileged kinds of emotion are automatically triggered by objects and events in the world"、評価が"emotions are not merely triggered by objects in a reflexive or habitual way, but arise from a meaningful interpretation of an object by an individual"、心理構成主義が"emotions are psychical compounds that are constructed out of more basic psychological ingredients that are not themselves specific to emotion"である。
- ヴントを心理構成主義の始まりに置く記述: Gendron & Barrett (2009)の原文は"Along with William James, Wilhelm Wundt is the other major figure of the Golden Years who crafted a psychological constructionist approach to emotion."である。
- 「Core Affect and the Psychological Construction of Emotion」: Russell (2003)のアブストラクトに"an approach based on the concepts of core affect and psychological construction"とある。
- 「心理構成主義の展開として扱われている」: Gendron & Barrett (2009)の原文は"In some models, these ingredients combine in stages (e.g., Russell, 2003; Schachter & Singer, 1962; Wundt, 1897/1998)."である。
- 「対極の組や混ぜると別の感情になる組」: Plutchik (2001)の原文は、対極が"I suggested eight basic bipolar emotions: joy versus sorrow, anger versus fear, acceptance versus disgust and surprise versus expectancy."、混合（一次双対）が"mixing joy and acceptance produces the mixed emotion of love; disgust plus anger produces hatred or hostility. Such mixtures have been called primary dyads in the theory."である。
- 「計算モデルとしての先行研究」: バレット自身が能動的推論（active inference）の枠組みで理論を定式化したBarrett (2017b)と、感情状態の推定と感情概念の学習を能動的推論の計算モデルとして実装したSmith, Parr & Friston (2019)がある。
- 「7つ」の情動システム: Panksepp (1998)。7つのシステムはSEEKING（探索）、RAGE（怒り）、FEAR（恐れ）、LUST（性欲）、CARE（養育）、PANIC/GRIEF（悲嘆）、PLAY（遊び）である。原著の表記はPANICで、PANIC/GRIEFは後年に精緻化された表記である。

## 感情エンジンの設計

- 「6件のうち5件」: 収束している5件は、本文で詳しく見るSofroniew et al. (2026)のほか、Li et al. (2024)、Tak et al. (2025)、Choi & Weber (2026)、van der Ben et al. (2026)である。残る1件（Tosato et al. 2026）は感情ではなく人格特性の測定を扱うもので、結論が対立しているというより主題が別である。
- 「valenceは後年に定着した呼称」: Russell (1980) の原文が使うのは "pleasure-displeasure" と "degree of arousal" で、valence という語は登場しない。
- 「特定の感情の広い概念を符号化し…」: 原文: "internal representations of emotion concepts, which encode the broad concept of a particular emotion and generalize across contexts and behaviors it might be linked to."
- 「ポジティブな感情のベクトル…」: 原文: "steering toward positive emotion vectors (e.g. happy, loving) increases sycophantic behavior, while suppressing these emotion vectors increases harshness."
- 「desperate（必死さ）のベクトル…」: 原文: "Steering positively with the desperate vector substantially increases blackmail rates, while steering negatively decreases them. Conversely, steering positively with the calm vector dramatically reduces blackmail behavior". シナリオは同論文が評価用に用意したもので、シャットダウンの脅威に直面したモデルが人間への脅迫を選んでしまうという設定である。
- 「人間の感情は通常、時間を跨いで持続する状態である…」: 原文: "human emotions are states that typically persist across time—a person who receives devastating news remains sad even while reading a positively valenced sentence shortly thereafter."
- 「会話を通じて一貫して見える応答は…」: 原文: "what might appear as consistent emotional responses from an Assistant across a conversation may reflect repeated activation of similar emotion concepts at each generation step (perhaps queried from earlier in the context via the attention mechanism), rather than a persistently encoded internal emotional state."
- 「実践的あるいは哲学的に重要かどうかは…」: 原文: "Whether this distinction matters—practically or philosophically—remains an open question." および "That said, our results do not preclude the possibility of persistently active representations that are missed by our probing methods."
- 「持続が感情の状態の鍵だという直感そのものが…」: 原文: "intuitions that persistence is a key property of emotional states may be inappropriate in the context of transformer-based models."
- 「将来の出来事の見込みから生じる感情」: 見込みに基づく感情の構造は、原著の該当表を転載したSteunebrink, Dastani & Meyer (2009)で確認している。

## プルチックの輪を実装する

- 「一次双対（primary dyads）」: 円環の並びと一次双対8つの図はPlutchik (2001a)のFigure 2による。ただし嫌悪と怒りの双対の名前は、American Scientist論文（Plutchik 2001b）の本文の語彙（憎悪あるいは敵意）に合わせている（Figure 2のラベルはcontempt）。
- 「基本となる感情は種を越えて共通する少数に絞られる」: Plutchik (1980)の理論の10の公準のうち、公準1「The concept of emotion is applicable to all evolutionary levels and applies to animals as well as to humans」、公準3「Emotions serve an adaptive role in helping organisms deal with key survival issues posed by the environment」、公準5「There is a small number of basic, primary, or prototype emotions」による。
- 「trust、sadness、anticipationとは3語が異なる」: 原語の揺れの例。本人の別論文（Evolution and Cognition誌）の円環図はラベルがsadnessとanticipation、American Scientist論文の本文はsorrowとexpectancyである。trustが本人の図のラベルに使われた例は、筆者が参照した範囲では見つからなかった。

## ラッセルの円環を実装する

- 「感情の状態は2次元の双極空間の上の円として最もよく表される」: Russell (1980)の原文は"My thesis is that affective states are, in fact, best represented as a circle in a two-dimensional bipolar space"（pp. 1161-1162）である。
- 「原点はおそらく順応水準ないし中立的な感情に対応する」「円盤や車輪のほうがよいイメージだろう」: Russell (1980)の原文は"although a disk or a wheel would be a better image, since affective states of moderate intensity would fall toward the middle of the space, with the origin presumably corresponding to adaptation level or a neutral feeling"（p. 1170）である。順応水準（adaptation level）は、刺激に慣れたときに落ち着く基準の水準のことである。
- 「名前を付けるのはあなた」「意味はすべて平面上の位置にある」: 指示文の原文は"You name the feeling."と"the meaning lives entirely in the position on the plane."である。
- 「感情の空間は双極であり、反意語はおよそ180度離れて位置する」: Russell (1980)の原文は"Affective space is bipolar, with antonyms falling approximately 180° apart."（p. 1167）である。

## OCCモデルを実装する

- 22のタイプと構造図: 感情タイプの全体構造の図はOrtony et al. (1988)のFigure 2.1（p. 19）、タイプ数が22であることはpp. 173, 191にある。OCCモデルの章の頁参照は1988年版による。
- 充足、恐れの的中、安堵、失望などの訳語: 訳し分けの注（構造図の訳語を含む）。ラッセルの円環モデルの満足（contentment）と区別するため、OCCのsatisfactionは充足、gratificationは達成感と訳している。充足は見込んでいたことの成就、達成感は自分の行為がよい結果を生んだ複合である。またresentmentを妬みとしたのは、原典がこのタイプのトークンとして挙げる語にenvyが並ぶためである。構造図のシャーデンフロイデ（gloating）は、他者の不幸を喜ぶ感情を指す心理学の用語である。
- 「恥」などのタイプの名前: 本書の図と実装で使うタイプの名前は原典の構造図に書かれた感情語に合わせている。原典がタイプを定義する箇所で使う正式なタイプ名は、恥ではなくSelf-reproach（自責）、哀れみではなくSorry-for、好意と反感はLiking/Dislikingである。正式なタイプ名がSelf-reproachであることと、shameの語は道徳的な含意のためにタイプの範囲を狭めすぎる、という理由はp. 142にある。原典の索引もshameの項からself-reproachへ誘導している。

## 構成主義的情動理論を実装する

- 構成主義的情動理論の論文からの引用: 構成の定式はBarrett (2017b)のpp. 9, 13、「感情は、世界への反応ではなく、世界の構成である」は原文"Emotions are constructions of the world, not reactions to it."（p. 16）の意訳である。概念と過去経験の一文は原文"An internal model runs on past experiences, implemented as concepts."（p. 12）である。実例の多様さの議論はp. 3による。「共通の核となる特徴を持つ見込みは薄い」の原文は"it is unlikely that all instances of an emotion category share a set of core features (i.e. a single facial expression, autonomic pattern or set of neurons)"である。
- コア・アフェクトという用語: 用語の注。2017年の論文の本文が使う語はaffectである（p. 6）。コア・アフェクトの術語は「感情モデルの整理」の章で触れた1999年の共著論文とRussell（2003）に由来し、本書はカタカナ表記で通す。なお2017年の論文がvalenceとarousalの典拠に挙げるBarrett and Russell（1999）は、「感情モデルの整理」の章で使ったRussell & Barrett（1999、JPSP誌）とは別の論文（Current Directions in Psychological Science誌）である。
- 「Generative Agentsの記憶の検索と同じ方式」: Park et al. (2023)は記憶の検索を関連・新しさ・重要度の重み付き和で評価する設計である。
- 「сердиться」と「злиться」: Barrett (2017a)の第7章による。ロシア語の2つの概念は、人に向けた怒りと、政治的な状況のような抽象的な対象に向けた怒りの区別として紹介されている。
- 14属性: Li et al. (2024)は、人間の評定で感情概念の内容を14属性として測定し（コア・アフェクト2、典型表情への類似6、先行評価6。評価の6属性はSkerry & Saxe（2015）の38項目を主成分分析で縮約したもの）、言語モデルの内部表現と照合した研究である。表情の6属性は幸福・怒り・悲しみ・恐れ・驚き・嫌悪の典型表情への類似、評価の6属性はcontrol・fairness・self-relativity・other-relativity・expectedness・noveltyである。14属性の表現を提案した論文ではなく、本実装が測定のスキーマを検索の規約として借用している。
