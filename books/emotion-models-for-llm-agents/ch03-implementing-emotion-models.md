---
title: "感情エンジンの設計"
---

<!-- 執筆進捗: 2026-10-05 の全体推敲で全節を書き直したため未レビュー -->

「感情モデルの整理」の章では感情の理論を4つの系統に整理しました。本章では4系統に共通する設計や考え方を整理し、感情エンジンとして実装するときに何をどう作るのかについてを説明します。なお実装の詳細は各モデルを実装する章で説明します。

## プロンプト単体の感情表現に足りないもの <!-- レビュー済み -->

感情を模倣する最も手軽な方法はシステムプロンプトに性格やその時点の感情を書くことです。「あなたは明るい性格で、現在は機嫌がよい」と書けばAIエージェントはそのとおりに振る舞います。ポジティブな入力には（場合によっては絵文字付きで）ラフな出力が、ネガティブな入力には硬く真面目な印象の出力が返るでしょうし、多くの場合はこれで感情表現としては十分です。

一方でわかりやすい不自然さもいくつかあります。例えば1つ目のセッションでどれだけ怒らせても次のセッションではフラットな感情状態に戻りますし、逆に同じセッションが続くかぎり何週間経っても直前の温度感のまま会話が再開されます。一晩寝たら落ち着くような時間による減衰もありません。
この解決策として考えられるのは、メモリ機能のように感情状態を外部に保存してセッションをまたがせ、時間の経過も考慮させることです。ざっくり言うと本書の感情エンジンもこの仕組みですが、その感情の持ち方と時間による変化の設計が理論やモデルごとに変わるので、それらを実装し比較していこうというのが目的となります。

## LLM自体の感情表現 <!-- 未レビュー -->

外部に感情エンジンを作る前に、LLMそのものの感情表現についての先行研究を整理します。LLMの内部表現を調べた研究は複数のグループから公開されていて、筆者が確認した6件のうち5件は同じ方向の結論です[^five-studies]。LLMの内部には感情の概念に対応する構造化された表現があり、それが出力に影響するという結論です。快と不快や覚醒の高低といった軸に沿った構造も見つかっています。この2軸は「感情モデルの整理」の章で触れたラッセルの円環モデルに似ていて、研究ではvalence（感情価）とarousal（覚醒度）と呼ばれます。ラッセルの円環を実装する章でもこの呼び名を使いますが、valenceは後年に定着した呼称でラッセル自身の語ではありません[^valence]。

中でも詳しいのは、Anthropicが2026年に公開したClaude Sonnet 4.5の分析「Emotion Concepts and their Function in a Large Language Model」です。同論文は感情概念の内部表現が「特定の感情の広い概念を符号化し、その感情が結び付きうるコンテキストや振る舞いをまたいで一般化する」ことを示し[^generalize]、その表現を操作すると出力や望ましくない挙動の発生率が変わると報告しています。たとえば「ポジティブな感情のベクトル（happyやlovingなど）の方向に操作すると迎合的な振る舞いが増え、これらのベクトルを抑えると辛辣さが増す」と報告しています[^sycophancy-example]。シャットダウンの危機にあるモデルが人間を脅迫してしまう評価シナリオでは「desperate（必死さ）のベクトルを正の方向に操作すると脅迫の発生率は大きく上がり、負の方向に操作すると下がる。反対にcalm（平静）のベクトルを正の方向に操作すると脅迫は劇的に減る」とされています[^blackmail-example]。

一方で同論文は人間の感情との違いも示しています。「人間の感情は通常、時間を跨いで持続する状態である。ひどい知らせを受けた人は、その直後に明るい内容の文章を読んでいる間も悲しい状態が持続する」[^persist-quote]。これに対してLLMは保存された感情状態を読み出すのではなく、次のトークンを予測するたびにその時点のコンテキストから感情を表現しています。同論文はこの性質をlocally scopedと呼び、「会話を通じて一貫して見える応答は、各生成ステップで似た概念が繰り返し活性化した結果かもしれず、持続的に符号化された内部状態とは限らない」と書いています[^repeated-activation]。

ただし同論文は断定しておらず、この区別が「実践的あるいは哲学的に重要かどうかは、未解決の問いのままである」とし、「この結果は、観測手法が見落としている持続的に活性な表現の可能性を排除するものではない」とも明記しています[^open-question]。さらに「持続が感情の状態の鍵だという直感そのものが、transformerを基にしたモデルでは適切でないかもしれない」とも書いています[^persistence-intuition]。

本書もこの姿勢にならい、LLMの感情表現がどこまで模倣なのかという問いには踏み込みません。これから作る感情エンジンも模倣のためのPoCという位置付けです。そのうえで2つの事実を押さえておきます。1つはLLM単体の感情表現が機能するのはコンテキストウインドウの範囲までだということです。感情の内部表現がコンテキストウインドウを超えて保持されるかを扱った研究は、筆者が調べた中には見当たりませんでした。もう1つはLLMの感情の表現がエージェントハーネス側から状態として読み書きできる形になっていないことです。APIを通じた通常の利用で触れられるのは入出力のテキストだけです。なお重みが公開されているモデルなら内部を観察でき、5件のうちvan der Benらの研究はオープンなモデルでAnthropicの結果を追試したものです[^vanderben2026]。

そのため本書では、LLMは感情の表現と言語化を担当するものとして扱います。

## 外部の感情状態として何をどう置くか <!-- 未レビュー -->

LLMの内部表現は読み書きできず、コンテキストウインドウを超えた持続も難しいので、本書では感情の状態をLLMの外側に置きます。参考にする感情モデルを再現するために、モデルごとに次の4つの設計軸を考えます。

1. 状態: どのパラメータがどの程度あるかを記録し、コンテキストやセッションをまたいだ感情の持続を可能にします。
2. 時間: その状態がいつのものかを記録し、時間経過による変化を可能にします。
3. 更新の規則: 出来事が起きたときに状態がどう変わるかを定め、会話や出来事に応じた変化を可能にします。
4. ニュートラルな状態の定義と基準: 何も起きていないときの状態を定め、どこを基準に感情が動いたとみなすかを判断できるようにします。

LLM単体の感情表現に足りなかったのは、状態を持つことと、会話のターンの間にも時間が経って状態が変わることです。

## 感情エンジンとLLMの役割分担 <!-- 未レビュー -->

外部状態を管理する感情エンジンとLLMの役割分担は次のとおりです。

- 感情エンジン: 状態の保持と減衰と演算を決定論的な処理として担当します。状態は数値のままLLMに渡します。
- LLM: 状態の解釈と命名と言語化を非決定論的な処理として担当します。受け取った数値が何を意味するかはコンテキストも含めてLLMが判断します。

![LLMの外側に置く外部状態と決定論の処理、内側に残す解釈と言語化の分担](/images/emotion-models-for-llm-agents/ch03-division-of-labor.png)

状態の解釈をLLMに任せるのは、状態の意味がコンテキストによって変わるからです。怒りが0.6という値は、直前まで0.9だったならおさまりつつあり、ずっと0.2だったなら爆発しつつあると解釈できます。相手が誰で何の話をしていて直前に何があったかによって、返すべき言葉も変わります。

時間減衰の計算を感情エンジンに任せるのは、LLMに計算させると結果がぶれるからです。性格によって怒りを引きずりやすいといった違いも考えられますが、それは怒り0でも怒りっぽい性格なら少し怒っている状態として解釈する、というようにLLMの解釈で表せます。

感情の状態が動くきっかけは2種類あります。1つは会話で、ユーザーの発話に応じて更新の規則で状態を変えます。もう1つは時間の経過で、何も起きなくても状態はニュートラルな方向に戻ります。

![会話のターンによる更新と時間経過による更新が、同じ外部状態に入るループ](/images/emotion-models-for-llm-agents/ch03-update-triggers.png)

会話による変化はLLMが担当します。「ユーザーから謝られる」という出来事が怒りをどれだけ下げるかは、コンテキストによって変わる評価が必要で計算では決められないからです（LLMの評価は人間の判断とずれたり不安定になったりするという報告もあります[^bhattacharyya2026]）。本書では応答を生成するLLM自身が応答と一緒に状態の変化量を申告します。時間による変化は感情エンジンが担当します。申告があったときに前回からの経過時間分の変化をまとめて反映し、会話がない間も定期実行で同じ変化を加えます。

## コンピュータ上の感情表現に関する先行研究の整理 <!-- 未レビュー -->

感情を数値として外部に保持して決定論的に減衰させる設計は、affective computing（感情を扱う計算技術の研究分野）がLLMの登場以前から積み上げてきたものです。たとえばGebhardが2005年に発表した対話キャラクター向けの感情モデルALMA[^gebhard2005]は、感情とムードと性格を持続時間の異なる3つの層に分けます。感情は調整可能な減衰関数で決定論的に減衰し、ムードは性格から決まる既定値へ時間をかけて戻ります。4つの設計軸に対応する仕組みは20年前のモデルがすでに持っていました。同じ時期にはPADの3次元空間で感情の時間変化を扱ったWASABIや、評価理論を計算モデルにしたEMAもあります。

ALMAと本書の感情エンジンの違いは、状態を表出に変える側です。ALMAでは発話や表情があらかじめ用意されたものから現在のムードに応じて選ばれ、表出も決定論でした。LLMを使う本書では数値の解釈をLLMが担当します。

LLMを使った例では、2023年のGenerative Agents[^park2023]が記憶を決定論的に蓄積してその解釈をLLMに任せています。CroissantらのChain-of-Emotion[^croissant2024]は応答とは別のLLM呼び出しで感情の生成と言語化を行います。LuとLiが2025年に発表したモデル[^lu-li2025]は感情の保持と時間減衰を外部システムに任せ、LLMには応答の方針の判断だけを任せていて、本章の役割分担とよく似ています。

![2005年ごろと現在の対比。感情の数値状態は同じで、解釈と言語化の層だけが置き換わった](/images/emotion-models-for-llm-agents/ch03-interpreter-shift.png)

感情の数値状態の上に解釈と言語化のレイヤーがあるという構図は20年前から同じで、変わったのはそのレイヤーをLLMが担うようになったことです。

## 感情モデルで変わるものと変わらないもの <!-- 未レビュー -->

感情の状態をLLMの外に置くことは4つのモデルで共通ですが、外部状態に置くものはモデルごとに異なります。

| 感情モデル | 外部状態に置くもの |
| --- | --- |
| プルチックの感情の輪 | 感情の種類ごとの量、および感情同士の関係 |
| ラッセルの円環モデル | 感情を左右する少数の軸の値 |
| OCCモデル | 感情の量に加えて、評価から感情を導く規則と、評価の対象の記録 |
| バレットの構成主義的情動理論 | 感情を構成する材料の値に加えて、経験と概念を蓄えて引き出す仕組み |

プルチックの感情の輪は、感情の種類ごとの量に加えて対極や混合といった感情同士の関係を持ちます。
ラッセルの円環モデルは軸の値だけを持ち、それがどの感情にあたるかはLLMが判断します。4つの中でLLMに任せる解釈が最も多いモデルです。
OCCモデルは感情の量に加えて出来事の評価の記録を持ちます。OCCモデルには将来の出来事の見込みから生じる感情が定義されていて[^occ-prospect]、望ましい出来事を見込めば希望が、望ましくない出来事を見込めば恐れが生じます。見込みが当たったか外れたかで安堵や失望に変わるので、何を恐れていたのかの記録が必要です。
バレットの構成主義的情動理論は、快と不快のような材料の値と、感情を組み立てるための過去の経験の記録を持ちます。OCCモデルの見込みの記録が短期のものであるのに対して、経験の蓄積は長期の記録です。

次章からは、それぞれの外部状態がどんなデータを持ちエージェントの応答にどう影響するかを1つずつ確かめます。

## まとめ <!-- 未レビュー -->

本章ではLLM単体の感情表現の限界を先行研究から確認し、感情の状態をLLMの外側に置く基本設計を整理しました。外部状態の4つの設計軸を定め、保持と演算は感情エンジンが、解釈と言語化はLLMが担う役割分担を決めて、先行研究との関係も確認しました。次章からはこの設計をもとに4つの感情モデルを1つずつ実装します。

## 参考文献

本章で言及した文献を、登場順に挙げます。所在は DOI を優先し、無料で読めるものはその URL を添えています。

- Sofroniew, N., Kauvar, I., Saunders, W., Chen, R., Henighan, T., Hydrie, S., Citro, C., Pearce, A., Tarng, J., Gurnee, W., Batson, J., Zimmerman, S., Rivoire, K., Fish, K., Olah, C., & Lindsey, J. (2026). Emotion Concepts and their Function in a Large Language Model. arXiv:2604.07729. 公開版が https://transformer-circuits.pub/2026/emotions/ で読めます
- Li, M., Su, Y., Huang, H., Cheng, J., Hu, X., Zhang, X., Wang, H., Qin, Y., Wang, X., Lindquist, K. A., Liu, Z., & Zhang, D. (2024). Language-specific representation of emotion-concept knowledge causally supports emotion inference. iScience, 27(12), 111401. https://doi.org/10.1016/j.isci.2024.111401
- Tak, A. N., Banayeeanzade, A., Bolourani, A., Kian, M., Jia, R., & Gratch, J. (2025). Mechanistic Interpretability of Emotion Inference in Large Language Models. Findings of ACL 2025. arXiv:2502.05489
- Choi, B. J., & Weber, M. (2026). Latent Structure of Affective Representations in Large Language Models. arXiv:2604.07382. 査読前のプレプリントです
- van der Ben, S., Baur, R., Metz, Y., & El-Assady, M. (2026). Where Do Models Find Happiness? Emotion Vectors in Open-Source LLMs. arXiv:2606.26987. 査読前のプレプリントです
- Tosato, T., Helbling, S., Mantilla-Ramos, Y.-J., Hegazy, M., Tosato, A., Lemay, D. J., Rish, I., & Dumas, G. (2026). Persistent Instability in LLM's Personality Measurements: Effects of Scale, Reasoning, and Conversation History. arXiv:2508.04826
- Russell, J. A. (1980). A Circumplex Model of Affect. Journal of Personality and Social Psychology. https://doi.org/10.1037/h0077714
- Bhattacharyya, S., Kuriabov, E., Craig, L., Dilliraj, T., Adams, R. B., Jr., Li, J., & Wang, J. Z. (2026). Large Language Models Show Fragile Cognitive Reasoning About Human Emotions. arXiv:2508.05880. 査読前のプレプリントです
- Gebhard, P. (2005). ALMA - A Layered Model of Affect. AAMAS'05. https://doi.org/10.1145/1082473.1082478. 著者の所属機関のサイト https://alma.dfki.de/papers/aamas05.pdf で無料公開されています
- Becker-Asano, C., & Wachsmuth, I. (2010). Affective Computing with Primary and Secondary Emotions in a Virtual Human. Autonomous Agents and Multi-Agent Systems. https://doi.org/10.1007/s10458-009-9094-9
- Marsella, S. C., & Gratch, J. (2009). EMA: A Process Model of Appraisal Dynamics. Cognitive Systems Research. https://doi.org/10.1016/j.cogsys.2008.03.005
- Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative Agents: Interactive Simulacra of Human Behavior. UIST '23. https://doi.org/10.1145/3586183.3606763
- Croissant, M., Frister, M., Schofield, G., & McCall, C. (2024). An Appraisal-Based Chain-of-Emotion Architecture for Affective Language Model Game Agents. PLOS ONE. https://doi.org/10.1371/journal.pone.0301033
- Lu, J., & Li, Y. (2025). Dynamic Affective Memory Management for Personalized LLM Agents. arXiv:2510.27418. 査読前のプレプリントです
- Ortony, A., Clore, G. L., & Collins, A. (1988). The Cognitive Structure of Emotions. Cambridge University Press. 2022年に新版が出ています（ISBN 9781108928755）
- Steunebrink, B. R., Dastani, M. M., & Meyer, J.-J. Ch. (2009). The OCC Model Revisited. Proceedings of the 4th Workshop on Emotion and Computing. 査読誌ではなくワークショップ論文集です。https://people.idsia.ch/~steunebrink/Publications/KI09_OCC_revisited.pdf で無料公開されています

[^five-studies]: 収束している5件は、次の段落で詳しく見る Sofroniew et al. (2026) arXiv:2604.07729 のほか、Li et al. (2024) doi:10.1016/j.isci.2024.111401、Tak et al. (2025) arXiv:2502.05489、Choi & Weber (2026) arXiv:2604.07382、van der Ben et al. (2026) arXiv:2606.26987。残る1件（Tosato et al. 2026, arXiv:2508.04826）は感情ではなく人格特性の測定を扱うもので、結論が対立しているというより主題が別です。

[^valence]: Russell (1980) の原文が使うのは "pleasure-displeasure" と "degree of arousal" で、valence という語は登場しません。

[^generalize]: 原文: "internal representations of emotion concepts, which encode the broad concept of a particular emotion and generalize across contexts and behaviors it might be linked to."

[^sycophancy-example]: 原文: "steering toward positive emotion vectors (e.g. happy, loving) increases sycophantic behavior, while suppressing these emotion vectors increases harshness."

[^blackmail-example]: 原文: "Steering positively with the desperate vector substantially increases blackmail rates, while steering negatively decreases them. Conversely, steering positively with the calm vector dramatically reduces blackmail behavior". シナリオは同論文が評価用に用意したもので、シャットダウンの脅威に直面したモデルが人間への脅迫を選んでしまうという設定です。

[^persist-quote]: 原文: "human emotions are states that typically persist across time—a person who receives devastating news remains sad even while reading a positively valenced sentence shortly thereafter."

[^repeated-activation]: 原文: "what might appear as consistent emotional responses from an Assistant across a conversation may reflect repeated activation of similar emotion concepts at each generation step (perhaps queried from earlier in the context via the attention mechanism), rather than a persistently encoded internal emotional state."

[^open-question]: 原文: "Whether this distinction matters—practically or philosophically—remains an open question." および "That said, our results do not preclude the possibility of persistently active representations that are missed by our probing methods."

[^persistence-intuition]: 原文: "intuitions that persistence is a key property of emotional states may be inappropriate in the context of transformer-based models."

[^vanderben2026]: van der Ben et al. (2026). Where Do Models Find Happiness? Emotion Vectors in Open-Source LLMs. arXiv:2606.26987 https://arxiv.org/abs/2606.26987

[^bhattacharyya2026]: Bhattacharyya et al. (2026). arXiv:2508.05880

[^gebhard2005]: Gebhard (2005). https://doi.org/10.1145/1082473.1082478

[^park2023]: Park et al. (2023). https://doi.org/10.1145/3586183.3606763

[^croissant2024]: Croissant et al. (2024). https://doi.org/10.1371/journal.pone.0301033

[^lu-li2025]: Lu & Li (2025). Dynamic Affective Memory Management for Personalized LLM Agents. arXiv:2510.27418

[^occ-prospect]: Ortony, Clore & Collins (1988)。見込みに基づく感情の構造は、原著の該当表を転載した Steunebrink, Dastani & Meyer (2009) The OCC Model Revisited で確認しています。
