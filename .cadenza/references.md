# affectus 関連 参考資料リスト

affectus の設計を支える研究・書籍。記事の各フェーズ（特に analysis-execution / output-crafting）での
引用元としても使用する。★ = 著者がまず読むべき優先度。

## A. クオリア構造学（affectus の着想元 — 最優先）

- ★ 土谷尚嗣『クオリアと人工意識』講談社現代新書, 2021
  - 一般向け。クオリアと人工意識を扱う。affectus の「感情を構造で捉える」視点の入口。
- ★ 土谷尚嗣・西郷甲矢人「圏論による意識の理解」認知科学 26(4), 462-477, 2019（J-STAGE で無料公開）
  - 日本語で読める原著系論文。米田の補題を意識研究に持ち込む発想の核。
- Tsuchiya, N., Phillips, S., & Saigo, H. (2022). "Enriched category as a model of qualia structure based on similarity judgements." Consciousness and Cognition, 101, 103319.
  - クオリアを「他のクオリアとの類似関係の集合」として豊穣圏でモデル化。affectus の「軸を関係性で定義する」着想の直接の根拠。
- Tsuchiya, N. & Saigo, H. (2021). "A relational approach to consciousness: categories of level and contents of consciousness." (PMC8517618)
  - 米田の補題による「経験の同一性＝関係性の集合で決まる」の定式化。
- クオリア構造（学術変革領域研究 A, 2023-2028）プロジェクト公式サイトの References ページ
  - https://en.qualia-structure.jp/ — 最新の論文一覧。

## B. 感情モデルの古典（affectus の軸設計の土台）

- ★ Plutchik, R. (1980). Emotion: A Psychoevolutionary Synthesis. Harper & Row.
  - 感情の輪（8基本感情・強度・混合）。affectus のデフォルト 8 軸の出典。
- Plutchik, R. (2001). "The Nature of Emotions." American Scientist, 89(4).
  - 上記の簡潔な論文版。まずこちらで概観できる。
- Russell, J. A. (1980). "A Circumplex Model of Affect." Journal of Personality and Social Psychology, 39(6).
  - Valence-Arousal の円環モデル。将来拡張（VAD）の理論的背景。
- Mehrabian, A. & Russell, J. A. (1974). An Approach to Environmental Psychology. MIT Press.
  - PAD（快・覚醒・支配）次元モデルの原典。
- Ortony, A., Clore, G. L., & Collins, A. (1988). The Cognitive Structure of Emotions. Cambridge University Press.
  - OCC モデル。「なぜその感情が起きたか」を評価から導く appraisal 理論の代表。

## C. 感情理論の対立軸（「深みとは何か」を論じるための視点）

- ★ Lisa Feldman Barrett『情動はこうしてつくられる』(How Emotions Are Made, 2017／邦訳 紀伊國屋書店)
  - 「基本感情は実在せず、感情は脳が構成する」とする構成主義。Plutchik 的な固定軸への強力な反論。affectus が「軸を設定で差し替え可能」にした設計判断と直接対話する一冊。

## D. アフェクティブ・コンピューティング / LLM × 感情

- ★ Picard, R. W. (1997). Affective Computing. MIT Press.
  - 「感情を扱う計算機」という分野そのものの基礎文献。
- Anthropic (2026). "Emotion Concepts and their Function in a Large Language Model." transformer-circuits.pub
  - LLM 内部の感情表現は局所的でターンをまたいで持続しない、という知見。affectus が外部ステートで感情を持続させる意義の根拠。
- "Affective Computing in the Era of Large Language Models: A Survey" (arXiv:2408.04638)
  - LLM 時代の感情計算の俯瞰。関連手法の地図として。
- "Persistent Instability in LLM's Personality Measurements" (AAAI 2026, arXiv:2508.04826)
  - LLM は安定した人格コアを持たない、という実証。プロンプト人格の限界＝記事の問題意識を裏づける。

## メモ
- affectus はクオリア構造学を「概念的着想」として取り込む（圏論の数値実装はしない）。
  記事でもこの線引きを正直に書くこと — 過度に「クオリア構造を実装した」と主張しない。
