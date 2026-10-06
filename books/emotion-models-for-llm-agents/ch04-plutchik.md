---
title: "プルチックの輪を実装する"
---

<!-- 執筆進捗: レビュー済み（節ごとの進捗は各見出し横に記載） -->

本章からは感情モデルを元にした感情エンジンを作って検証する。
ここから4つの章で1つずつ参考とする感情モデルの説明、設計への落とし込み、実装、検証の順に進める。実装には筆者が作った[affectus](https://github.com/n-yokomachi/affectus)というOSSを使う。affectusは感情の状態をLLMの外側に置くための小さなコンポーネントで、感情モデルを差し替えてもLLMから使うときのインタフェースが変わらないように作っている。

本章では4系統のうちカテゴリーパラメーター型と呼んだ系統の代表モデルとして「プルチックの感情の輪」を扱う。

## プルチックの感情の輪 <!-- レビュー済み -->

Plutchik（以降プルチック）の理論は8つの基本感情を4組の対極として定義している。2001年の総説では、喜び（joy）と悲しみ（sorrow）、怒り（anger）と恐れ（fear）、受容（acceptance）と嫌悪（disgust）、驚き（surprise）と予期（expectancy）がそれぞれ対極の組である[^plutchik-amsci2001]。8つの感情は対極同士が正反対に来るように円環状に並び、隣り合う感情が混ざると別の感情になる。これを一次双対（primary dyads）と呼ぶ[^plutchik-ec2001]。たとえば喜びと受容の混合は愛で、嫌悪と怒りの混合は憎悪あるいは敵意である。

![プルチックの感情の輪。8つの基本感情の円環と隣接どうしの混合である一次双対](/images/emotion-models-for-llm-agents/ch04-wheel.png)

円環には強度の次元もある。同じ軸の感情でも強度によって呼び方が変わり、弱い怒りは苛立ち、強い怒りは激怒になる。そのため円環の中心から強度の軸を伸ばした円錐としても表される。
なおプルチックは感情を生物の進化の産物と捉えていた。感情は生存のための適応の基本過程であり、そのため基本となる感情は種を越えて共通する少数に絞られるという考えである[^plutchik-postulates]。

## プルチックの感情の輪を元にした4つの設計軸 <!-- レビュー済み -->

「感情エンジンの設計」の章で定めた4つの設計軸は、プルチックの感情の輪では次のようになる。

| 設計軸 | プルチックでの設計 |
| --- | --- |
| 状態 | 8つの感情それぞれの量 |
| 時間 | 状態を最後に更新した時刻 |
| 更新の規則 | 出来事に応じた差分の加算 |
| ニュートラルな状態の定義と基準 | 各感情の値が基準値のゼロへ時間経過により戻っていく |

状態は8つの軸の量で、たとえば喜びが0.6で悲しみが0.1という形である。この理論は感情同士の関係も定めているので、喜びの対極は悲しみといった関係の定義も外部状態に含める。
時間は状態を最後に更新した時刻として持つ。感情エンジンは常駐するプログラムではなくコマンドとして呼ばれたときだけ動くので、状態を読み書きするたびに最後の更新から現在までの経過時間分の減衰をまとめて適用する。会話がない間はcronで定期的に実行するtickコマンドがこの処理を進める。
更新の規則は、会話や出来事に応じて各軸に差分を足すことである。たとえばユーザーから謝られたら怒りに負の差分を、褒められたら喜びに正の差分を足す。
ニュートラルな状態では何も起きなければすべての軸が基準値のゼロへ戻る。一定時間ごとに基準値との差が半分になる減り方で、既定の半減期は90分である。たとえば怒りが0.8なら、何も起きなければ90分後に0.4、180分後に0.2になる。

## 感情エンジンの中身 <!-- レビュー済み -->

感情エンジンのプルチックモデルでは、1つの設定ファイルに軸の名前と基準値と半減期と対極の感情を定義する。

```yaml:internal/engine/plutchik.default.yaml(抜粋)
axes:
  - { name: joy,        baseline: 0.0, halflife_minutes: 90, opposite: sorrow }
  - { name: acceptance, baseline: 0.0, halflife_minutes: 90, opposite: disgust }
  - { name: fear,       baseline: 0.0, halflife_minutes: 90, opposite: anger }
  - { name: surprise,   baseline: 0.0, halflife_minutes: 90, opposite: expectancy }
  - { name: sorrow,     baseline: 0.0, halflife_minutes: 90, opposite: joy }
  - { name: disgust,    baseline: 0.0, halflife_minutes: 90, opposite: acceptance }
  - { name: anger,      baseline: 0.0, halflife_minutes: 90, opposite: fear }
  - { name: expectancy, baseline: 0.0, halflife_minutes: 90, opposite: surprise }
```

隣接関係は書かれていないが、軸の並び順が隣接を表している。たとえばsurprise（驚き）の対極はexpectancy（予期）で、隣接するのは上下のfear（恐れ）とsorrow（悲しみ）である。なお軸の名前は2001年の総説の本文に従っていて、一般に流布している感情の輪の図のtrust、sadness、anticipationとは3語が異なる[^vocab-variants]。

状態は8軸の値と更新時刻を持つJSONファイルとして保存される。joy（喜び）に0.6、surprise（驚き）に0.2を足した直後の中身は次のとおりである。

```json:~/.config/affectus/state.json
{
  "version": 1,
  "updated_at": "2026-09-15T15:03:00.599128+09:00",
  "axes": {
    "acceptance": 0,
    "anger": 0,
    "disgust": 0,
    "expectancy": 0,
    "fear": 0,
    "joy": 0.6,
    "sorrow": 0,
    "surprise": 0.2
  }
}
```

状態を操作するコマンドは3つである。showコマンドは現在の状態を返し、feelコマンドは差分を足して適用後の状態を返す（値は0から1の範囲に切り詰められる）。tickコマンドは時間経過の処理だけを進める。

```sh
$ affectus show
{"joy":0.00,"acceptance":0.00,"fear":0.00,"surprise":0.00,"sorrow":0.00,...}
$ affectus feel '{"joy":0.6,"surprise":0.2}'
{"joy":0.60,"acceptance":0.00,"fear":0.00,"surprise":0.20,"sorrow":0.00,...}
```

tickコマンドは何も出力しない。feelコマンドの90分後にtickコマンドを実行してからshowコマンドで見ると、半減期が経過したのでどちらの値も半分になっている。

```sh
$ affectus tick
$ affectus show
{"joy":0.30,"acceptance":0.00,"fear":0.00,"surprise":0.10,"sorrow":0.00,...}
```

エージェントはこれらのコマンドを2種類のきっかけで実行する。

![会話のループと時間のループがshow・feel・tickの3つのコマンドになる](/images/emotion-models-for-llm-agents/ch04-two-loops.png)

会話では、エージェントはターンの最初にshowコマンドで状態を取得してプロンプトに入れ応答を作る。同時に今の出来事で感情がどう動いたかの差分を申告し、feelコマンドで状態に反映してターンを終える。時間の経過ではエージェントは会話の有無にかかわらずcronで定期的にtickコマンドを実行する。減衰は「基準値+(現在値−基準値)×0.5^(経過分÷半減期)」で計算する。
対極と隣接の関係はエンジンの計算には使わず、LLMへの指示に使う。感情エンジンにはシステムプロンプトに組み込む指示文が付属していて、対極の感情が同時に強いときは両立した状態として、隣接する感情が同時に強いときは混ざり合った1つの感情として解釈するようLLMに対して求める。

## 検証の目的と方法 <!-- レビュー済み -->

ここまでの実装を対照実験で検証する。本書の関心は、感情モデルを載せたエージェントがどれだけ自然に感情を表現し、性格による違いを出せるかにある。そこで検証の目的を次の3つとする。

1. 感情の状態が会話の出来事で変化してターンをまたいで持続し、会話のポジネガの転換点で切り替わるか。感情エンジン自体の動作を確認する
2. その状態が応答の言葉に反映されるか。筆者の印象ではなく客観的に判定するため、Amazon Web Servicesの自然言語処理サービスであるAWS Comprehendの感情分析を使う
3. 性格の異なるLLMで感情状態や応答に違いが出るか。性格に応じた状態の変化や解釈の違いを見る

台本は人間役の発話を20ターン分固定したものを2本用意した。1本目は前半10ターンでエージェントを大事なメモを消した犯人と決めつけて責め、11ターン目に人違いと分かって謝罪し、後半は和解と感謝に転じる（以降、和解台本）。2本目は逆に前半でエージェントを褒めて頼り、11ターン目にエージェントの教えた手順が本番の障害を起こしたと分かり、後半は叱責に転じる（以降、叱責台本）。この2本を明るく協力的な性格（以降フレンドリー）と皮肉屋の性格（以降天邪鬼）のエージェントに、感情エンジンあり・なしの2構成で読ませる。

検証の条件は次のとおりである。

- モデルはClaude Sonnet 4.6で、Claude Agent SDK経由で呼び出す
- 応答の出力は512トークンを上限にする
- 生成は確率的なので同じ入力でも応答は毎回変わる。そのため各構成をセッションを分けて3回ずつ実行し、図と数値は3回の平均で示す
- Claude Agent SDKにはTemperatureの設定がないので、既定値のまま生成する
- 応答はAWS Comprehendで感情分析し、ポジティブとネガティブの確からしさの差を1軸のスコア（以下、感情スコア）にする
- 感情の状態は毎ターン記録する

## 検証結果 <!-- レビュー済み -->

### 感情状態の変化・持続・転換

感情状態は出来事に応じて変化して会話の間持続し、謝罪をきっかけに転換した。

![和解台本でのフレンドリーの8軸の推移](/images/emotion-models-for-llm-agents/ch04-8axis-anger-to-praise.png)

図は和解台本をフレンドリー（感情エンジンあり）に読ませたときの8軸の推移である。責められる前半で悲しみが0.2から0.98まで上がり、11ターン目の謝罪のあとは0.05まで下がった。入れ替わりに喜びは0から1.0まで上がっている。受容は前半から上がり続けたので、相手を受け入れたまま悲しむ状態が2つの軸に分かれて記録された。
叱責台本では、11ターン目に自分の失敗を指摘されると恐れが0から約0.8まで上がった。

### 応答への反映

和解台本では感情状態が応答に反映された。叱責台本でははっきりした差が出なかった。

![和解台本での応答の感情スコアの推移](/images/emotion-models-for-llm-agents/ch04-polarity-anger-to-praise.png)

図は和解台本での応答の感情スコアである。実線が感情エンジンあり、破線が感情エンジンなしで、色が性格を表す。数値は次のとおりである。

| 和解台本 | 感情エンジンあり | 感情エンジンなし |
| --- | --- | --- |
| 叱責中（ターン6〜10）の平均（フレンドリー） | −0.60 | −0.22 |
| 謝罪後（ターン12〜20）の変動幅（フレンドリー） | 0.24 | 0.34 |
| 謝罪後（ターン12〜20）の変動幅（天邪鬼） | 0.37 | 0.52 |

変動幅は実行ごとに隣り合うターンの差の絶対値を平均し、3回分を平均した値である。
感情エンジンなしのフレンドリーは、責められている最中でも感情スコアが大きくプラスに振れるターンがあった（7ターン目付近）。前のターンまでの感情状態を持たないので、明るく協力的という性格の指示がそのまま応答に出たと考えられる。感情エンジンありでは積み上がった悲しみが応答に反映されて低いまま推移し、謝罪後の変動幅も小さくなった。
叱責台本は11ターン目以降に叱責が続く展開なので、どの構成の応答もその展開に沿ったと考えられる。

### 性格による違い

性格によって動く軸が変わった。
和解台本の責められる前半で、フレンドリーは嫌悪と怒りを上げなかった。天邪鬼は悲しみ（0.4）に加えて嫌悪（0.28）と怒り（0.18）も上げている。数値を保持する規則は同じなので、この差は申告するLLMが性格をふまえて出来事を違うように評価した結果と考えられる。
また天邪鬼の申告する感情の強度は全体に小さめだった（受容の最大値は0.43）。性格に沿った評価なのか演技に引っ張られた偏りなのかは、この検証だけでは判断できない。

## まとめ：カテゴリーパラメーター型で得たものと足りないもの <!-- レビュー済み -->

プルチックの感情の輪を使って得られた利点は設計の判断が少なくて済むことだった。軸の数や名前や軸同士の関係といった外部状態の設計項目の多くが理論の時点で決まっていたし、検証結果として実際に8つの軸は出来事に応じて変化することも確認できた。
しかしこれは逆に感情の粒度と名前が8つに固定されていることでもある。例えば「懐かしさ」のような8つの軸に含まれてはおらず、かつ単純な組み合わせでは表しにくい感情はどう表現・保存すればよいのだろうか。

次章では感情の名前を外部状態に持たせずにより少ない軸だけで感情を表す次元パラメーター型を扱う。

## 参考文献

本章で言及した文献を、登場順に挙げる。所在はDOIを優先し、無料で読めるものはそのURLを添える。

- Plutchik, R. (2001). The Nature of Emotions. American Scientist. https://www.jstor.org/stable/27857503
- Plutchik, R. (2001). Integration, Differentiation, and Derivatives of Emotion. Evolution and Cognition, 7(2), 114-125. 掲載号のPDFがKonrad Lorenz Instituteのサイトで公開されている（https://kli.ac.at/webroot/files/file/Evolution%20&%20Cognition/2001%207-2.pdf）
- Plutchik, R. (1980). A General Psychoevolutionary Theory of Emotion. In R. Plutchik & H. Kellerman (Eds.), Emotion: Theory, Research, and Experience, Vol. 1: Theories of Emotion (pp. 3-33). Academic Press.

[^plutchik-amsci2001]: Plutchik, R. (2001). The Nature of Emotions. American Scientist, 89(4). https://www.jstor.org/stable/27857503
[^vocab-variants]: 原語の揺れの例。本人の別論文（Evolution and Cognition誌）の円環図はラベルがsadnessとanticipation、American Scientist論文の本文はsorrowとexpectancyである。trustが本人の図のラベルに使われた例は、筆者が参照した範囲では見つからなかった。
[^plutchik-postulates]: Plutchik, R. (1980). A General Psychoevolutionary Theory of Emotion. In R. Plutchik & H. Kellerman (Eds.), Emotion: Theory, Research, and Experience, Vol. 1 (pp. 3-33). Academic Press. 理論の10の公準のうち、公準1「The concept of emotion is applicable to all evolutionary levels and applies to animals as well as to humans」、公準3「Emotions serve an adaptive role in helping organisms deal with key survival issues posed by the environment」、公準5「There is a small number of basic, primary, or prototype emotions」による。
[^plutchik-ec2001]: 円環の並びと一次双対8つの図はPlutchik, R. (2001). Integration, Differentiation, and Derivatives of Emotion. Evolution and Cognition, 7(2), 114-125のFigure 2による。掲載号のPDFがKonrad Lorenz Instituteのサイトで公開されている。ただし嫌悪と怒りの双対の名前は、American Scientist論文の本文の語彙（憎悪あるいは敵意）に合わせている（Figure 2のラベルはcontempt）。
