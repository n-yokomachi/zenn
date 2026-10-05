---
title: "プルチックの輪を実装する"
---

<!-- 執筆進捗: レビュー済み（節ごとの進捗は各見出し横に記載） -->

本章からは感情モデルを元にした感情エンジンを作って検証します。第7章まで1つの章で1つの理論を扱い、理論の中身、設計への落とし込み、実装、検証の順に進めます。実装には筆者が作った[affectus](https://github.com/n-yokomachi/affectus)というOSSを使います。affectusは感情の状態をLLMの外側に置くための小さなコンポーネントで、感情モデルを差し替えてもLLMから使うときのインタフェースが変わらないように作っています。

本章では4系統のうちカテゴリーパラメーター型と呼んだ系統の代表モデルとして「プルチックの感情の輪」を扱います。

## プルチックの感情の輪 <!-- レビュー済み -->

Plutchik（以降プルチック）の理論は8つの基本感情を4組の対極として定義しています。2001年の総説では、喜び（joy）と悲しみ（sorrow）、怒り（anger）と恐れ（fear）、受容（acceptance）と嫌悪（disgust）、驚き（surprise）と予期（expectancy）がそれぞれ対極の組です[^plutchik-amsci2001]。8つの感情は対極同士が正反対に来るように円環状に並び、隣り合う感情が混ざると別の感情になります。これを一次双対（primary dyads）と呼びます[^plutchik-ec2001]。たとえば喜びと受容の混合は愛で、嫌悪と怒りの混合は憎悪あるいは敵意です。

![プルチックの感情の輪。8つの基本感情の円環と隣接どうしの混合である一次双対](/images/emotion-models-for-llm-agents/ch04-wheel.png)

円環には強度の次元もあります。同じ軸の感情でも強度によって呼び方が変わり、弱い怒りは苛立ち、強い怒りは激怒になります。そのため円環の中心から強度の軸を伸ばした円錐としても表されます。
なお、プルチックは感情を生物の進化の産物と捉えていました。感情は生存のための適応の基本過程であり、そのため基本となる感情は種を越えて共通する少数に絞られるという考えです[^plutchik-postulates]。

## プルチックの感情の輪を元にした4つの設計軸 <!-- レビュー済み -->

第3章の4つの設計軸は、プルチックの感情の輪では次のようになります。

| 第3章の設計軸 | プルチックでの設計 |
| --- | --- |
| 状態 | 8つの感情それぞれの量 |
| 時間 | 状態を最後に更新した時刻 |
| 更新の規則 | 出来事に応じた差分の加算 |
| ニュートラルな状態の定義と基準 | 各感情の値が基準値のゼロへ時間経過により戻っていく |

状態は8つの軸の量で、たとえば喜びが0.6で悲しみが0.1という形です。この理論は感情同士の関係も定めているので喜びの対極は悲しみといった関係の定義も外部状態に含めます。
時間は状態を最後に更新した時刻として持ちます。感情エンジンは常駐するプログラムではなくコマンドとして呼ばれたときだけ動くので、状態を読み書きするたびに最後の更新から現在までの経過時間分の減衰をまとめて適用します。会話がない間はcronで定期的に実行するtickがこの処理を進めます。
更新の規則は、会話や出来事に応じて各軸に差分を足すことです。たとえばユーザーから謝られたら怒りに負の差分を、褒められたら喜びに正の差分を足します。
ニュートラルな状態では何も起きなければすべての軸が基準値のゼロへ戻ります。一定時間ごとに基準値との差が半分になる減り方で既定の半減期は90分です。たとえば怒りが0.8なら、何も起きなければ90分後に0.4、180分後に0.2になります。

## 感情エンジンの中身 <!-- レビュー済み -->

感情エンジンのプルチックモデルでは、1つの設定ファイルに軸の名前と基準値と半減期と対極の感情を定義します。

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

隣接関係は書かれていませんが、軸の並び順が隣接を表しています。たとえばsurprise（驚き）の対極はexpectancy（予期）で、隣接するのは上下のfear（恐れ）とsorrow（悲しみ）です。なお軸の名前は2001年の総説の本文に従っていて、一般に流布している感情の輪の図のtrust、sadness、anticipationとは3語が異なります[^vocab-variants]。

状態は8軸の値と更新時刻を持つJSONファイルとして保存されます。joy（喜び）に0.6、surprise（驚き）に0.2を足した直後の中身は次のとおりです。

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

状態を操作するコマンドは3つです。showは現在の状態を返し、feelは差分を足して適用後の状態を返します（値は0から1の範囲に切り詰められます）。tickは時間経過の処理だけを進めます。

```sh
$ affectus show
{"joy":0.00,"acceptance":0.00,"fear":0.00,"surprise":0.00,"sorrow":0.00,...}
$ affectus feel '{"joy":0.6,"surprise":0.2}'
{"joy":0.60,"acceptance":0.00,"fear":0.00,"surprise":0.20,"sorrow":0.00,...}
```

tickは何も出力しません。feelの90分後にtickを実行してからshowで見ると、半減期が経過したのでどちらの値も半分になっています。

```sh
$ affectus tick
$ affectus show
{"joy":0.30,"acceptance":0.00,"fear":0.00,"surprise":0.10,"sorrow":0.00,...}
```

エージェントはこれらのコマンドを2種類のきっかけで実行します。

![会話のループと時間のループがshow・feel・tickの3操作になる](/images/emotion-models-for-llm-agents/ch04-two-loops.png)

会話では、エージェントはターンの最初にshowで状態を取得してプロンプトに入れ応答を作ります。同時に今の出来事で感情がどう動いたかの差分を申告し、feelで状態に反映してターンを終えます。時間の経過ではエージェントは会話の有無にかかわらずcronで定期的にtickを実行します。減衰は「基準値+(現在値−基準値)×0.5^(経過分÷半減期)」で計算します。

対極と隣接の関係はエンジンの計算には使わず、LLMへの指示に使います。感情エンジンにはシステムプロンプトに組み込む指示文が付属していて、対極の感情が同時に強いときは両立した状態として、隣接する感情が同時に強いときは混ざり合った1つの感情として解釈するようLLMに対して求めます。

## 検証の目的と方法 <!-- レビュー済み -->

ここまでの実装を対照実験で検証します。本書の関心は、感情モデルを載せたエージェントがどれだけ自然に感情を表現し、性格による違いを出せるかです。そこで検証の目的を次の3つとします。

1. 感情の状態が会話の出来事で変化してターンをまたいで持続し、会話のポジネガの転換点で切り替わるか。感情エンジン自体の動作を確認します
2. その状態が応答の言葉に反映されるか。筆者の印象ではなく客観的に判定するため、Amazon Web Servicesの自然言語処理サービスであるAWS Comprehendの感情分析を使います
3. 性格の異なるLLMで感情状態や応答に違いが出るか。性格に応じた状態の変化や解釈の違いを見ます

台本は人間役の発話を20ターン分固定したものを2本用意しました。1本目は前半10ターンでエージェントを大事なメモを消した犯人と決めつけて責め、11ターン目に人違いと分かって謝罪し、後半は和解と感謝に転じます。2本目は逆に前半でエージェントを褒めて頼り、11ターン目にエージェントの教えた手順が本番の障害を起こしたと分かり、後半は叱責に転じます。この2本を明るく協力的な性格（以降フレンドリー）と皮肉屋の性格（以降天邪鬼）のエージェントに、感情エンジンあり・なしの2構成で読ませます。

検証の条件は次のとおりです。

- モデルはClaude Sonnet 4.6で、Claude Agent SDK経由で呼び出します
- 応答の出力は512トークンを上限にします
- 生成は確率的なので同じ入力でも応答は毎回変わります。そのため各構成をセッションを分けて3回ずつ実行し、図と数値は3回の平均で示します
- Claude Agent SDKにはTemperatureの設定がないので、既定値のまま生成します
- 応答はAWS Comprehendで感情分析し、ポジティブとネガティブの確からしさの差を1軸のスコア（以下、感情スコア）にします
- 感情の状態は毎ターン記録します

## 検証結果 <!-- レビュー済み -->

それではプルチックの感情の輪をベースとした感情モデルの検証結果を見ていきます。

### 感情状態の変化・持続・転換

感情状態は出来事に応じて変化して会話の間持続し、謝罪をきっかけに転換しました。

![和解台本でのフレンドリーの8軸の推移](/images/emotion-models-for-llm-agents/ch04-8axis-anger-to-praise.png)

図は和解の台本をフレンドリー（感情エンジンあり）に読ませたときの8軸の推移です。責められる前半で悲しみが0.2から0.98まで上がり、11ターン目の謝罪のあとは0.05まで下がりました。入れ替わりに喜びは0から1.0まで上がっています。受容は前半から上がり続けたので、相手を受け入れたまま悲しむ状態が2つの軸に分かれて記録されました。

称賛から立腹へ向かう台本では、11ターン目に自分の失敗を指摘されると恐れが0から約0.8まで上がりました。

### 応答への反映

和解の台本では感情状態が応答に反映されました。称賛から立腹へ向かう台本でははっきりした差が出ませんでした。

![和解台本での応答の感情スコアの推移](/images/emotion-models-for-llm-agents/ch04-polarity-anger-to-praise.png)

図は和解の台本での応答の感情スコアです。実線が感情エンジンあり、破線が感情エンジンなしで、色が性格を表します。数値は次のとおりです。

| 和解の台本 | 感情エンジンあり | 感情エンジンなし |
| --- | --- | --- |
| 叱責中（ターン6〜10）の平均（フレンドリー） | −0.60 | −0.22 |
| 謝罪後（ターン12〜20）の変動幅（フレンドリー） | 0.24 | 0.34 |
| 謝罪後（ターン12〜20）の変動幅（天邪鬼） | 0.37 | 0.52 |

変動幅は実行ごとに隣り合うターンの差の絶対値を平均し、3回分を平均した値です。

感情エンジンなしのフレンドリーは、責められている最中でも感情スコアが大きくプラスに振れるターンがありました（7ターン目付近）。前のターンまでの感情状態を持たないので、明るく協力的という性格の指示がそのまま応答に出たと考えられます。感情エンジンありでは積み上がった悲しみが応答に反映されて低いまま推移し、謝罪後の変動幅も小さくなりました。

称賛から立腹へ向かう台本は11ターン目以降に叱責が続く展開なので、どの構成の応答もその展開に沿ったと考えられます。

### 性格による違い

性格によって動く軸が変わりました。

和解の台本の責められる前半で、フレンドリーは嫌悪と怒りを上げませんでした。天邪鬼は悲しみ（0.4）に加えて嫌悪（0.28）と怒り（0.18）も上げています。数値を保持する規則は同じなので、この差は申告するLLMが性格をふまえて出来事を違うように評価した結果です。

また天邪鬼の申告は全体に小さめでした（受容の最大値は0.43）。性格に沿った評価なのか演技に引っ張られた偏りなのかは、この検証だけでは判断できません。

### 検証の限界

反復は3回で統計的な検定はしていません。台本は2本だけで、感情スコアはポジティブとネガティブの1軸なので言葉の細かいニュアンスは測れません。ターンの間隔が秒単位のため時間経過による減衰もほぼ働いていません。

## まとめ：カテゴリーパラメーター型で得たものと足りないもの <!-- レビュー済み -->

プルチックの感情の輪を使って得られた利点は設計の判断が少なくて済むことでした。軸の数や名前や軸同士の関係といった外部状態の設計項目の多くが理論の時点で決まっていましたし、検証結果として実際に8つの軸は出来事に応じて変化することも確認できました。
しかしこれは逆に感情の粒度と名前が8つに固定されていることでもあります。例えば「懐かしさ」のような8つの軸に含まれてはおらず、かつ単純な組み合わせでは表しにくい感情はどう表現・保存すると良いのでしょうか。

次章では感情の名前を外部状態に持たせずにより少ない軸だけで感情を表す次元パラメーター型を扱います。

## 参考文献

本章で言及した文献を、登場順に挙げます。所在はDOIを優先し、無料で読めるものはそのURLを添えています。

- Plutchik, R. (2001). The Nature of Emotions. American Scientist. https://www.jstor.org/stable/27857503
- Plutchik, R. (2001). Integration, Differentiation, and Derivatives of Emotion. Evolution and Cognition, 7(2), 114-125. 掲載号のPDFがKonrad Lorenz Instituteのサイトで公開されています（https://kli.ac.at/webroot/files/file/Evolution%20&%20Cognition/2001%207-2.pdf）
- Plutchik, R. (1980). A General Psychoevolutionary Theory of Emotion. In R. Plutchik & H. Kellerman (Eds.), Emotion: Theory, Research, and Experience, Vol. 1: Theories of Emotion (pp. 3-33). Academic Press.

[^plutchik-amsci2001]: Plutchik, R. (2001). The Nature of Emotions. American Scientist, 89(4). https://www.jstor.org/stable/27857503
[^vocab-variants]: 原語の揺れの例。本人の別論文（Evolution and Cognition誌）の円環図はラベルがsadnessとanticipation、American Scientist論文の本文はsorrowとexpectancyです。trustが本人の図のラベルに使われた例は、筆者が参照した範囲では見つかりませんでした。
[^plutchik-postulates]: Plutchik, R. (1980). A General Psychoevolutionary Theory of Emotion. In R. Plutchik & H. Kellerman (Eds.), Emotion: Theory, Research, and Experience, Vol. 1 (pp. 3-33). Academic Press. 理論の10の公準のうち、公準1「The concept of emotion is applicable to all evolutionary levels and applies to animals as well as to humans」、公準3「Emotions serve an adaptive role in helping organisms deal with key survival issues posed by the environment」、公準5「There is a small number of basic, primary, or prototype emotions」によります。
[^plutchik-ec2001]: 円環の並びと一次双対8つの図はPlutchik, R. (2001). Integration, Differentiation, and Derivatives of Emotion. Evolution and Cognition, 7(2), 114-125のFigure 2によります。掲載号のPDFがKonrad Lorenz Instituteのサイトで公開されています。ただし嫌悪と怒りの双対の名前は、American Scientist論文の本文の語彙（憎悪あるいは敵意）に合わせています（Figure 2のラベルはcontempt）。
