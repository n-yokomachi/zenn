---
title: "感情モデルをAIエージェントに実装するには"
---

<!-- 執筆進捗: 改稿済み（節ごとの進捗は各見出し横に記載） -->

前章では、感情の理論を4つの系統に整理しました。本章では、それらの理論をAIエージェントに実装するとしたら、何をどこに作ることになるのかを考えます。
なお、本章では4系統に共通する設計の基本的な考え方を紹介するにとどめ、実装の詳細は次章から説明します。

## プロンプト単体の感情表現に足りないもの <!-- 改稿済み -->

感情の模倣でいちばん手軽な方法は、AIエージェントに与えるシステムプロンプトなどのインプットに直接、性格やその時点での感情を記述することです。「あなたは明るい性格で、いま機嫌がよい」と書けば、AIエージェントはそのとおりに振る舞います。また会話の中でポジティブな入力をすれば、LLMの出力もポジティブなものになる傾向があるでしょう。場合によっては絵文字なども交えた回答が得られるはずです。同じくネガティブな入力をすれば、LLMの出力もどこかしら硬い文面で真面目なトーンになることは、LLMアプリを使ったことのあるユーザーなら心当たりがあるのではないでしょうか。会話の中で感情表現らしきものが見えますし、実際、多くの場合はこれで十分です。

一方で、このような一時的な入力から感情を模倣させるだけでは、例えば時間的な自然さを考慮した際に不十分となります。1つ目のセッションでどれだけ怒らせても、直後に開始した2つ目のセッションでは何ごともなかったようにフラットな状態にリセットされます。あるいは逆に、同じセッションが続いているかぎり、何週間経っても会話は直前の温度感のまま再開されます。人間のように一晩寝たら落ち着いた、のような時間的な減衰もありません。
ここから考えられる端的な解決方法は、一般的なメモリ機能などを使用して会話の要約や履歴と一緒にその時の感情状態を外部に保存してセッションを跨がせたり、時間的な考慮をさせることでしょう。実際本書で実装する感情コンポーネントもほとんど似たような仕組みです。ただ、その感情の持ち方や時間的な変動をどう設計するか、というところが理論やモデルごとに変わってくるところとなります。

## LLM自体の感情表現はあるのか <!-- 改稿済み -->

LLMの外側に感情コンポーネントを作る話をする前に、まずLLMそのもので起こる感情表現についての先行研究を整理します。
LLMの内部表現を調べた研究のレポートが、複数の独立したグループから公開されています。筆者が確認した6件のうち5件は、大まかには同じ方向の結論に収束しています[^five-studies]。
すなわち、LLMの内部には感情の概念に対応する構造化された表現があり、それが出力に対して影響を与える、という結論です。快と不快、覚醒の高低といった軸に沿った構造も見つかっています（この2軸の構図は、前章で紹介したラッセルの円環モデルと似通っていると考えられます。LLMの内部表現の研究では、この2軸はvalence（感情価）とarousal（覚醒度）という言葉で呼ばれており、第5章で円環モデルを実装に使うときもこの呼び名を使用します。ただしvalenceのほうは後年に定着した呼称で、円環モデルを出したラッセル自身の語ではありません[^valence]）。

中でも詳しいのが、Anthropicが2026年に公開した「Emotion Concepts and their Function in a Large Language Model」という、Claude Sonnet 4.5を対象とする分析です。ある感情に対応する表現が、特定の場面や特定の振る舞いに固有ではなく、その感情が関わりうるさまざまなコンテキストや振る舞いに共通して現れること（一般化）を示し[^generalize]、その表現を操作すると出力が変わること、さらに迎合や報酬ハッキング（与えられた目標の抜け道を突く挙動）といった望ましくない挙動の発生率まで変わることを報告しています。たとえば、happyやlovingといったポジティブな感情のベクトルを強めるほど応答は相手への迎合に寄り、逆に抑えるほど辛辣さが増します[^sycophancy-example]。また、シャットダウンの危機に瀕したモデルが人間を脅迫してしまう評価シナリオでは、desperate（必死さ）のベクトルを強めると脅迫の発生率が大きく上がり、calm（平静）を強めると大きく下がることが示されています[^blackmail-example]。
この結果を見るといかにも感情表現らしい動きをしていますが、同論文では人間の感情との違いも提示しています。「人間の感情は通常、時間を跨いで持続する状態である。ひどい知らせを受けた人は、その直後に明るい内容の文章を読んでいる間も悲しい状態が持続する」[^persist-quote]一方で、LLMの場合は会話全体を通じて保持されている感情の状態ではなく、モデルが直後のトークンを予測する時点で、その予測に関係しているコンテキストから感情を表現していると報告しています。保存された感情状態を読み出しているというより、その時処理に使われているトークンから逐一妥当な感情を分析している、ということです。同論文ではこの性質をlocally scopedと呼び、「会話を通じて一貫して見える応答は、各生成ステップで似た概念が繰り返し活性化した結果かもしれず、持続的に符号化された内部状態とは限らない」と書いています[^repeated-activation]。つまり、会話の中で表現される感情らしきものは、トークンを生成するステップごとに、それまでのコンテキストから推測された感情をそのつど表現しているに過ぎず、状態が保存され続けている証拠とは限らない、ということです。
なお、同論文では結論を断定しておらず、この区別（感情の状態が内部に持続的に保存されているのか、生成のたびに都度分析しているのか）について「実践的あるいは哲学的に重要かどうかは、未解決の問いのままである」とし、「この結果は、観測手法が見落としている持続的に活性な表現の可能性を排除するものではない」とも明記しています[^open-question]。さらに踏み込んで、「持続が感情の状態の鍵だという直感そのものが、transformerを基にしたモデルでは適切でないかもしれない」とも書いています[^persistence-intuition]。言い換えると、感情とはそもそも持続するものだという人間を基準にした前提が、この仕組みには当てはまらないかもしれない、ということです。

本書もこの姿勢にならい、LLMの感情表現がどの程度まで模倣なのかという一種形而上学的な問いには立ち入りませんし、これから作る感情エンジンもあくまで模倣のためのPoC的な位置付けとして捉えています。
代わりに2つの事実を押さえておきます。一つは、LLM単体の感情表現が機能するのはコンテキストウインドウの範囲が限界だということです。感情概念の内部表現がコンテキストウインドウを超えて保持されるのかどうかを扱った研究は、筆者が調査した中には見当たりませんでした。もう一つは、LLMが一定の感情概念の表現を持っているとしても、それはエージェントハーネス側が状態として読み書きできる形にはなっていないということです。表現はモデル内部の活性の中にあり、APIを通じた通常の利用で開発者が触れられるのは基本的に入出力のテキストだけだからです。

この節ではLLMが内部的に感情の状態を持っているかどうかの先行研究を整理しましたが、いずれにしてもその状態を外から観察するのは難しそうだ、ということがわかりました（なお、重みが公開されているモデルならこうした内部の観察は可能で、実際に先行研究の5件のうちvan der Benらの研究は、オープンなモデルでAnthropicの結果を追試したものです[^vanderben2026]）。
ということで本書においてはあくまでLLMは感情の表現、言語化を担当するレイヤーという位置付けで進めていきます。

## 外部の感情状態として何をどう置くか <!-- 改稿済み -->

前節の内容から、（通常プロバイダから提供される）LLMの内部表現はエージェントハーネス側が状態として読み書きできる形になっていないこと、そしてコンテキストウインドウを超えた持続はそれ単体では難しいだろうということを前提に、本書では感情の状態をLLMの外側に置く設計を考えていきます。
設計にあたり参考とする感情モデルを再現する際には、それらを表現するために4つの軸の仕組みを感情モデル毎に考えます。

1. 状態: いまどういったパラメータがどの程度の量存在するのか、という状態の記録を持つことでコンテキストやセッションを跨いだ感情状態の持続を可能にします。
2. 時間: その状態はいつの時点のものか、という時刻の記録を持つことで時間経過による変化や判断を可能にします。
3. 更新の規則: 感情を変化させる出来事が起きたとき状態がどう変わるのか、という規則を持つことで、会話や出来事に応じて状態を変化させることを可能にします。
4. ニュートラルな状態の定義と基準: 感情を変化させる出来事が何も起きていない場合、状態はどうなるのかという定義を持つことで、フラットな状態をどうパラメータとして持つのか、出来事によりパラメータが変わる時どこを基準として感情が励起しているとみなすのかを判断できるようにします。

さて、こうして設計の軸を並べてみると、LLM単体では感情表現に欠けているものの一部が見えてきます。状態を持つことそのものはもちろん、会話のターンの間にも時間が経過して状態が変わっていくという時間的な要素もまた、LLMの感情表現には不足しているものでした。

## 感情エンジンとLLMの役割分担 <!-- 改稿済み -->

外部状態を管理する感情エンジンとそれを使用するLLMの役割分担は以下の通りとなります。

- 感情エンジン: 状態の保持・減衰・演算は感情エンジン内の決定論的な処理。状態は数値など持っているパラメータのままLLMに渡す。
- LLM: 状態の解釈・命名・言語化などの非決定論的な処理。感情エンジンから受け取ったパラメータが何を意味するかはLLMがコンテキストの内容も含めて判断。

![LLMの外側に置く外部状態と決定論の処理、内側に残す解釈と言語化の分担](/images/emotion-models-for-llm-agents/ch03-division-of-labor.png)

この役割分担は主に決定論的・非決定論的処理で分けています。

例えば状態の解釈をLLMの役割としているのは、状態の意味をコンテキストに依存して解釈する必要があるからです。怒りが0.6という値は、それだけでは何も意味しません。これが直前まで0.9だったなら、怒りはおさまりつつあると解釈できますし、逆にこれまではずっと0.2で推移してきたなら、苛立ちが爆発しつつあると解釈できます。同じ0.6の怒りでも、相手が誰で、何の話をしていて、直前に何があったかで、返すべき言葉を選ぶ必要があります。
また一方で、時間減衰の計算を感情エンジンの役割としているのは単にLLMに計算を委ねる必要が薄いからです。「3時間経ったから、怒りは0.6から0.3まで下がっているはず」という計算をLLMに委ねる場合、生成結果によるブレが発生しかねません（とはいえLLMに与えた性格設定によっては怒りを引き摺りやすいとか常に明るいとかの時間減衰に影響する性格も考えられます。が、ここでは、怒り0でも怒りっぽい性格の場合はそれが若干怒ってる状態、明るい人では若干楽しい状態、のようにLLMが柔軟に解釈する可能性も考え、あくまで時間減衰の計算は決定論的に感情エンジン側で行うこととします）。

ということで感情の状態をもとにそれを表現するという出力面の役割分担は、それぞれ感情の容れ物は感情エンジンが、感情の表出はLLMが受け持つこととします。

続いては感情に影響する出来事や会話があった時、それを状態へ反映する入力面での役割分担について考えます。

まず感情の状態が動く要因には2種類あります。
一つは会話です。ユーザーからの発話という出来事が起き、その内容に応じて状態を動かします。先述した4つの軸で言えば、更新の規則に則って状態を変化させます。もう一つは時間の経過です。何も出来事が起こらなくても、状態はニュートラルな方向へ向かって戻っていきます。同じく4つの軸で言うと、ニュートラルな状態の定義と基準が受け持つ変化です。

![会話のターンによる更新と時間経過による更新が、同じ外部状態に入るループ](/images/emotion-models-for-llm-agents/ch03-update-triggers.png)

前者の会話による状態の変化は、非決定論的な処理としてLLMが担当します。
例えば「ユーザーから謝られる」という出来事が怒りをどれだけ下げるのかは、決定論的な計算では決められません。その出来事の意味づけ、つまり評価が必要で、評価はコンテキストによって変わるものだからです（なお、LLMに出来事の評価をさせると人間の判断とズレたり、コンテキストによっては不安定になるという報告もあります[^bhattacharyya2026]）。本書では、応答を生成するLLM自身が、応答と一緒に状態の変化量を申告します。
一方で後者、時間の経過によるニュートラルな方向への変化は、決定論的な処理として感情エンジンが担当します。LLMから変化量の申告があった際に、その前の状態から経過した時間に応じて一定量のパラメータの変化を合算した上で状態に反映したり、まったく会話がない時間では定期実行で同じく時間経過に応じた一定量の変化を状態に加えます。

## コンピュータ上の感情表現に関する先行研究の整理 <!-- 改稿済み -->

コンピュータ上で感情を表現するための設計については、過去にも前例があるためこの節ではそれらを整理します。

感情を数値として外部に保持し、決定論的に減衰させる設計は、affective computing（感情を扱う計算技術の研究分野）が、LLMの登場よりずっと前から積み上げてきたものです。代表的な例を一つ見てみます。Gebhardが2005年に発表したALMAという対話キャラクター向けの感情モデル[^gebhard2005]は、感情・ムード・性格を、持続する時間の長さが違う3つの層に分けます。感情の強度は調整可能な減衰関数で決定論的に減衰し、ムードは性格から算出される既定値へ一定の時間をかけて戻っていきます。先述した4つの軸に対応する仕組みは、20年前のモデルがすでに持っていたのです。同じ時期に、PADと呼ばれる3次元の空間で感情の時間変化を扱ったWASABI、評価理論を計算モデルにしたEMAなど、同型の研究が続いています。

ただし、ALMAと本書で扱うLLM用感情エンジンの間には決定的な違いが一つあります。ALMAでは、状態を表出へ変える側も決定論でした。発話や表情はあらかじめ用意されたものの中から、現在のムードに応じて選ばれます。これに対し、LLM時代の感情表現では数値の解釈はLLMが担当します。
2023年のGenerative Agents[^park2023]は、記憶を決定論的に蓄積し、その解釈をLLMに任せる役割分担を実装しています。感情に絞った例もあります。CroissantらのChain-of-Emotion[^croissant2024]は、応答の生成とは別のLLM呼び出しで感情の生成と言語化を行なっています。LuとLiが2025年に発表したモデル[^lu-li2025]では、感情の保持と時間減衰を外部システムが受け持ち、LLMは応答の方針の判断だけを受け持ちます。この役割の分け方は、本章で扱う役割分担として先述した形とかなり似ています。

![2005年ごろと現在の対比。感情の数値状態は同じで、解釈と言語化の層だけが置き換わった](/images/emotion-models-for-llm-agents/ch03-interpreter-shift.png)

これらを並べると、変わっていないもの、変わったものが見えてきます。感情の数値状態があり、その上に解釈と言語化のレイヤーがあるという役割分担の構図は20年前から同じですが、そのレイヤーの担い手がいまでは数値をコンテキストに応じて解釈できるLLMに置き換えられたのです。

## 感情モデルで変わるものと変わらないもの <!-- 改稿済み -->

ここまでの節では、特定の感情理論を前提にせず、基本となる設計の考え方の話をしてきました。
この章の最後となる本節では、本書が参考とする感情モデルをこの基本設計に照らし合わせるとどういった面で差分が出てくるのかを見ていきます。
感情エンジンを入れ物としてLLMの外部に感情状態を保つことは共通していますが、その内容は感情モデル毎に異なります。

| 感情モデル | 外部状態に置くもの |
| --- | --- |
| プルチックの感情の輪 | 感情の種類ごとの量、および感情同士の関係 |
| ラッセルの円環モデル | 感情を左右する少数の軸の値 |
| OCCモデル | 感情の量に加えて、評価から感情を導く規則と、評価の対象の記録 |
| バレットの構成主義的情動理論 | 感情を構成する材料の値に加えて、経験と概念を蓄えて引き出す仕組み |

プルチックの感情の輪は、感情の種類ごとの量を持つのに加え、対極や混合といった感情同士の関係構造も感情状態として保持します。

ラッセルの円環モデルは感情状態として置くものが最も少ない感情モデルです。保持するのは軸の値だけで、それがどういった感情にあたるかという情報は持っていないため、この値を読み取ったLLMが判断します。4つの中ではLLMに委ねる解釈の割合が最も多い感情モデルです。

OCCモデルでは、感情の量のほかに、出来事への評価の記録が外部状態に加わります。本書で扱うOCCモデルでは、まだ確定していない将来の出来事の見込みから生じる感情が定義されています[^occ-prospect]。望ましい出来事を見込めば希望が、望ましくない出来事を見込めば恐れが生じ、その見込みが後で当たったか外れたかによって、安堵や失望といった別の感情に変わります。また、安堵を導出するには何を恐れていたのかという記録が必要となります。つまり感情の量だけでは足りず、見込んだ出来事自体の記録も保持するものに含まれます。

バレットの構成主義的情動理論では、感情はあらかじめ決まった型を持たず、材料から組み立てられるものとされます。そのため再現する感情状態が持つのは、快と不快のような材料の値と、組み立てに使う過去の経験の記録の2種類です。経験を蓄えて概念として引き出す仕組みが必要で、OCCモデルの出来事の記録が進行中の感情を導出するための短期の記録であるのに対して、こちらの経験の蓄積は長期の記録にあたります。

感情状態の構成は上述のように感情モデルにより異なります。
それぞれの感情状態が実際にどんなデータを持ち、それによってエージェントの応答にどのような影響が見られるかを次章から1つずつ確かめていきます。

## まとめ <!-- 改稿済み -->

この章では、LLM単体の感情表現の限界を先行研究から確認した上で、感情の状態をLLMの外側に置くという本書の基本設計を整理しました。感情状態が持つべき4つの設計軸を整理し、保持と演算は感情エンジンが、解釈と言語化はLLMが受け持つという役割分担を決め、本書の設計に先立つ先行研究も確認しました。
次章からは、この設計をもとに4つの感情モデルを1つずつ実装していきます。

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
