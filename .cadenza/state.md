# Cadenza Workflow State — affectus 技術記事

対象アウトプット: affectus（LLMエージェント向け感情ステートエンジン）の技術記事（Zenn）。将来的に LT 化も想定。
作業ディレクトリ: ~/work/workshop/zenn

---

## Phase 1: Issue Finding (✅ Done 2026-05-17)

### Confirmed issue
「AI キャラクターを自作するエンジニアは、プロンプトによる人格設定では会話が表面的に感じられるとき、『キャラクターの深み』をどう捉え、プロンプトに依らない感情制御をどう設計すべきか？」

### Target reader
すでに AI エージェントや自前の AI キャラクターを制作しようとしているエンジニア。affectus の導入を検討しそうな層。

### Reader's problem hypothesis
単純なプロンプトによるキャラクター設定では、会話の中で変化する感情の動きを補いきれず、キャラクター性が表面的になってしまう。キャラクターに深みを持たせたいが、その「深み」とは何なのかが言語化できていない。

### Post-read change
affectus の設計と仕組みを理解できる。さらに、単純なプロンプトに依らない感情制御のアイデア（持続・減衰する多軸の感情ステート）を得られる。

### Primary-source basis
著者自身が affectus を一から設計・実装し OSS として公開（github.com/n-yokomachi/affectus, v0.1.0）。さらに本記事の検証フェーズとして TONaRi（著者の個人 AI エージェント、Hermes Agent ベース）へ affectus を統合し、導入前後の一定ターン数の会話応答を実測・分析する。

### Differentiator
- 日本語の実務記事は「プロンプト／ファインチューニング／RAG（記憶）」が主流で、感情を「持続・減衰する多軸ベクトル」として扱う実務ガイドはほぼ無い
- クオリア構造学を着想元に「キャラクターの深み」を捉え直す視点（実務コンテンツに前例ほぼ無し）
- 自己申告＋cron の二層ループ（感情分類器を使わない決定論的エンジン）
- 実在の個人エージェント TONaRi での導入前後の実測データ

### 記事の骨子（暫定・Phase 2 で MECE 分解する）
クオリア構造学を着想元とした「深み」の捉え直し → affectus の設計 → TONaRi 導入前後の実測分析

### 参考資料
`./.cadenza/references.md` を参照。

---

## Phase 2: Issue Decomposition (✅ Done 2026-05-17)

### Main message
キャラクターの“深み”はプロンプトの作り込みではなく、持続し変化する感情の“構造”として設計できる ── ただしその構造を届けるチャネル（テキスト／音声）が、効果の見え方を決める。

### Adopted pattern
Before-After 基調（問題 → 深みの再定義 → 解決策 → 効果）。局所的に Sky-Rain-Umbrella を併用。

### Sub-issues and hypotheses
1. **SQ1：なぜプロンプト人格設定だけでは会話の中で動く感情を表現しきれないのか？**
   → プロンプトはキャラクターを「静的な設定」として固定するだけで、会話の経過に応じて変化・持続する感情の状態を保持できない。LLM 自身も感情をターン内ローカルにしか符号化せず人格はターンをまたいで揺らぐため、長い会話ほど設定が「演技」として表面化する。
2. **SQ2：「キャラクターの深み」とは何か？**
   → 「深み」とは単一の感情ラベルではなく、複数の感情軸が同時に異なる強度で存在し時間とともに連続的に変化する「構造」を持つこと。感情の意味は他の感情との関係の中で定まる（クオリア構造学）── 深みとは感情の関係的・多次元的な構造そのもの。
3. **SQ3：その深みをプロンプトに依らずどう設計・実装するか？**
   → 感情を「持続・減衰する多軸ベクトル」として LLM の外部に切り出し、会話ループ（LLM 自己申告でデルタ加算）と背景ループ（cron で時間減衰）の二層で更新する。プロンプトを膨らませずに連続性のある感情状態をエージェントに与えられる。
4. **SQ4：affectus を TONaRi に導入すると応答は実際にどう変わるのか？**
   → 【未検証・going-in 仮説】劇的な変化は予想しない。極度に愉快・不愉快な局面で口調・絵文字の有無として顕在化する程度。テキストは感情表現として本質的に低帯域なチャネルで、テキスト単独では効果を十分に引き出しにくい。TTS による抑揚など表現チャネルを広げて初めて真価が出る可能性が高い。

### Presentation order (storyline)
SQ1（問題）→ SQ2（深みの再定義）→ SQ3（解決策＝affectus）→ SQ4（効果＝TONaRi 実測）→ 結論（メインメッセージ）

### Unverified territory
- **SQ4 の実測結果**：TONaRi への affectus 統合後、導入前後で一定ターン数の会話応答を計測して確定する（検証フェーズ＝analysis-execution）。誠実な「modest な効果」の可能性を含めて記述する。
- **TTS の効果はスコープ外**：TONaRi は現状テキストのみ（音声合成は未実装）のため実測不可。記事では「考察・今後」として論じるに留める。「テキストという低帯域チャネルの限界」という気づき自体を記事の山場の一つとする。

---

## Phase 3: Storyboarding (✅ Done 2026-05-17)

### Dominant output style
長文記事（Zenn）。**ただし「技術記事として冗長さを避け、簡潔に」が前提制約**。各セクションは要点に絞り、説明は図表で圧縮する。LT 版は publish フェーズで派生。

### Storyboard list

#### SQ1: プロンプト人格設定の限界
- **Form**: 概念図（軽量 Mermaid）＋ プロンプト抜粋（短）＋ 研究引用
- **Spec**: 「プロンプト＝静的スナップショット」vs「会話＝感情が時間で動く」の対比図。TONaRi 人格プロンプトを10行ほど抜粋。引用＝AAAI 2026（LLM は安定人格コアを持たない）/ Anthropic 2026（感情がターンをまたいで持続しない）。
- **Required verification**: 概念図の作成、引用箇所の確認
- **Skipped verification**: 計測なし、LLM 内部表現の独自調査なし

#### SQ2: 「深み」の再定義（クオリア構造学）
- **Form**: 概念図＋散文
- **Spec**: 「単一ラベル（点）」vs「多軸の構造（強度＋対極・隣接の関係）」の対比図。Plutchik の輪を構造の具体例に。散文は references.md A群（クオリア構造学）B群（Plutchik）を統合し「感情の意味は関係で定まる→深み＝関係的・多次元的構造」を導く。クオリア構造学は"概念的着想"と正直に線引き。
- **Required verification**: 概念図の作成、references.md 文献の読み込み・正確な要約
- **Skipped verification**: 圏論・米田の補題の数式展開なし、VAD 等の詳細比較なし

#### SQ3: affectus の設計（二層ループ）
- **Form**: アーキテクチャ図（Mermaid）＋ CLI 実行例コードブロック＋ ステート JSON 抜粋
- **Spec**: 二層ループ図（会話ループ show→応答→feel／背景ループ cron tick）。`affectus init/show/feel/show` の実入出力、日本語 config（plutchik8-ja.yaml）での show 出力例。
- **Required verification**: affectus を実行し CLI 入出力を採取、アーキ図の作成
- **Skipped verification**: 性能ベンチなし、全コード掲載なし、MCP は軽く触れる程度

#### SQ4: TONaRi 導入前後の実測（主題・クライマックス）
- **Form**: ① AWS Comprehend による感情スコア推移チャート（客観指標・**主役ビジュアル**）② Before/After 対トランスクリプト抜粋（最大2例）③ コンパクトな比較表
- **Spec**:
  - 実験：3シナリオ（強ポジティブ弧／強ネガティブ弧／中立＝対照）、各 固定発話列 約8〜12ターン。2条件（TONaRi 単体＝baseline／TONaRi＋affectus）に同一入力。
  - 客観指標：両条件の TONaRi 応答を AWS Comprehend `DetectSentiment`（言語 ja）で分析、ターンごとの感情スコアを採取しチャート化（baseline vs affectus）。
  - 比較表の軸：口調・語尾／絵文字の有無・量／トーン／応答長。
  - affectus 条件の内部感情ベクトル推移は補足的に小さく示す（または Comprehend チャートに併記）。
  - 「modest な差」も誠実に記述。
- **Required verification**:
  1. affectus を TONaRi へ統合（system prompt への感情プロトコル追記・日本語 config・呼び出し方式の決定・cron 登録）
  2. 実験シナリオ（固定発話列）の作成
  3. 両条件で各シナリオを実行、トランスクリプト＆affectus 感情ベクトルを採取
  4. 全応答を AWS Comprehend `DetectSentiment`（ja）で分析、ターン別スコアを採取
  5. Comprehend スコア推移チャート・比較表の作成、差分分析
- **Skipped verification**: TTS は実測せず（考察のみ）、統計的有意性検定や大規模 N なし、複数モデル比較なし

### Total verification work (handed off to next phase)
1. 概念図×2（SQ1, SQ2）、アーキ図×1（SQ3）の作成
2. references.md 文献の読み込み・クオリア構造学の正確な要約（SQ2）
3. affectus CLI 実入出力の採取（SQ3）
4. affectus の TONaRi 統合（SQ4-1）
5. 実験シナリオ作成（SQ4-2）
6. baseline/affectus 両条件での実験実行・トランスクリプト＆感情ベクトル採取（SQ4-3）
7. AWS Comprehend による感情スコア分析（SQ4-4）
8. Comprehend チャート・比較表作成・差分分析（SQ4-5）

### Cut verification
TTS 効果の実測、圏論の数式展開、affectus 性能ベンチ、統計的有意性検定、複数モデル比較。
