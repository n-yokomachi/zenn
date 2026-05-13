---
title: "イシューベースでアウトプット制作をサポートするClaude Codeプラグイン「cadenza（カデンツァ）」を作った"
emoji: "🎼"
type: "idea"
topics: [claudecode, claude, ai, aiagent, productivity]
published: true
---

# はじめに

普段ブログやLTをしていると、なんか自分のアウトプットの内容が面白くないなあと感じることが多々あります。
簡単に振り返ってみると、①色々詰め込もうとして広く浅くなっている、②紹介にとどまって自分なりの検証や考察ができていない、③構成に緩急がなくてのっぺりしている、あたりがその原因かなと思っています。

というわけでこれらを解消しつつ、効果的なアウトプットを効率的・持続可能的にしていくため、Claude Codeのプラグインを作成しました。
（中身は単純なSkillsのかたまりなので別のエージェントでも使用可能です）

リポジトリは以下です。README.mdに沿ってインストールすることで誰でも使用可能です。
https://github.com/n-yokomachi/cadenza

# プラグインの紹介

プラグインの名前は`cadenza`です。
音楽用語の「カデンツァ」（協奏曲の中で独奏者が技巧を披露する自由楽章）に由来します。構造化されたワークフローを徹底しつつその課題設定や検証にはユーザーの自由意志を活かす、というニュアンスです。

cadenzaは、技術アウトプット制作を5フェーズに区切ったClaude Codeプラグインです。
各フェーズが「ゲート」として機能し、書き急ぎを防ぎながら、ユーザーが問いを明確にすることを促します。

根本的な設計思想は、安宅和人著『イシューからはじめよ』(英治出版, 2010)などのイシューファースト系の知的生産論をベースにしています。

## 5フェーズの構造

|フェーズ|スキル|役割|
|---|---|---|
| 1.計画| `/cadenza:issue-finding` | 「答える価値のある問いは何か」を特定する|
| 2.設計| `/cadenza:issue-decomposition` |サブイシューに分解しストーリーラインを設計する|
| 3.絵コンテ| `/cadenza:storyboarding` |各サブイシューの「見せ方」（コード片・図・表など）を決める|
| 4.検証| `/cadenza:analysis-execution` |絵コンテに従って実装・計測・作図する|
| 5.仕上げ| `/cadenza:output-crafting` | Markdown成果物を生成する|

加えて、レビュー用に2つのスキルがあります。

- `/cadenza:output-proofread` — AI主導の徹底校正（事実検証+言語校正）
- `/cadenza:output-review` — 著者主導のレビューサイクル支援

各スキルは完了時に「次のフェーズに進みますか？」と確認し、承認されれば次のスキルを呼び出してチェーンします。
またcadenzaの最終成果物は、`./.cadenza/output.md` という単一の汎用Markdownファイルです。
このMarkdownをベースにブログ記事を書いたりスライドにしたり、といった利用を想定しています。

## 各フェーズが「ゲート」として機能する

このプラグインの特徴は、各フェーズが下流フェーズの開始条件をチェックする点です。
例えば `storyboarding` は `./.cadenza/state.md` にPhase 2 (Issue Decomposition)のセクションが書かれているかを起動時に確認し、無ければ `issue-decomposition` を先に実行するよう案内します。

これによって構造的にフェーズスキップができないようにしています。

また各フェーズには「上流回帰シグナル」も定義されています。
例えば設計フェーズでストーリーラインが迷走してきた場合、計画フェーズに戻りイシューの再検討に戻る案内が出たりします。

## ユーザーの説明責任を強制するために

ところで普通にアウトプットのためのAIツールを紹介していますが、私はいまだAIにただ書かせただけのアウトプットには否定的な立場をとっています。

そのためcadenzaによるアウトプットも単にエージェントに任せただけではできないようにしています。
書いたものが全てユーザーの責任となるよう、フェーズごとにユーザーの確認を取るなどの必須ステップを設けており、全部エージェントに委ねることができないようにしています。

ざっくりユーザーとエージェントの主導ステップは以下のようになっています。

| Phase / Skill |ユーザー主導ステップ|エージェント主導ステップ|
|--------------|-------------------|---------------|
| Phase 1: issue-finding |一次情報の確認/対象読者・問題仮説・読後変化の言語化/ イシュー1文への明示同意|既存コンテンツサーベイ(WebSearch) / 3条件チェック|
| Phase 2: issue-decomposition |分解パターン合意/各サブイシューの仮説の言語化/ ストーリーラインパターン合意/ 主張の1文固定| ストーリーライン妥当性チェック|
| Phase 3: storyboarding |各サブイシューの形式・仕様合意/ 出力スタイル指定| ストーリーボード組み立て/ ストーリーボードレビュー |
| Phase 4: analysis-execution |上流回帰判断/検証実行/ スキル標準を超えた追加確認の指示|検証種別分類/前提条件固定/検証実行/結果構造化|
| Phase 5: output-crafting | タイトル選択 (3案から1つ) |構造組み立て/ TL;DR執筆/各セクション執筆/最終チェック|
| output-proofread | 指摘の採否判断・編集|技術正確性チェック /言語校正/ 校正レポート生成|
| output-review |全体的にユーザー主導(著者が読み返し、質問・編集指示を出す) |質問への根拠ある回答/ユーザー指示時のみ編集|

Phase4検証フェーズはその検証の種類によって主導の比重が変わります。
Implementation (コード実装) / Measurement (性能計測) / Reproduction (バグ再現)のような検証ではベースラインの企画をエージェントが担当し、実際に手を動かしたり別途実装タスクをエージェントに指示したりといった部分はユーザー主導という分業になります。一方Comparison（公開情報の調査）やDiagramming（作図）についてはAI主導で実行までを行います。

本当はユーザーが検証結果までを理解しないとアウトプットができないようなガードもかけたいところですが（例えば検証結果に関してエージェントからユーザーにクイズを出して、正解しないとアウトプット作ってくれない、とか）、その辺はユーザー（自分）の良心に任せることにします。


# 使い方

## インストール

cadenzaのリポジトリ自体がClaude Code marketplaceとして機能しています。
マーケットプレイスを登録してプラグインをインストールするだけで使えるようになります。

```bash: Terminal
claude plugin marketplace add github.com/n-yokomachi/cadenza
claude plugin install cadenza@cadenza
```

インストール後、 `/reload-plugins` でプラグインを再読み込みしたあと、 `/plugins`でcadenzaがインストールされていることを確認してください。

## 起動

技術アウトプットを書きたいプロジェクトのディレクトリでClaude Codeを起動し、`/cadenza:issue-finding` を実行することでフローが始まります。

```
/cadenza:issue-finding
```

## 状態管理

cadenzaは作業ディレクトリ直下に `./.cadenza/` ディレクトリを作成し、ここに状態と成果物を集約します。

```
./.cadenza/
├── state.md          # 各フェーズの確定情報を集約
└── output.md         # 最終成果物
```

`state.md` にはPhase 1からPhase 5までの確定情報が順次追記されていきます。
各スキルは下流に進む前に上流フェーズのセクションが `state.md` に存在することを確認するため、フェーズスキップが構造的にできない作りになっています。

別のプロジェクトディレクトリで作業すれば自然に `./.cadenza/` も別物になるので、複数記事の同時並行制作も可能です。

## 中断・再開

各フェーズの完了時点で `state.md` に書き出されているので、Claude Codeのセッションが切れても再開可能です。
新しいセッションで `/cadenza:<次のフェーズ>` を実行すれば、`state.md` の内容を読み込んで続きから始められます。


# おまけ：実際のフロー

以降はcadenzaを使用したアウトプット制作の実際の動作を確認するためのサンプルです。
サンプルの題材として「2026年5月時点のAIコーディングエージェント無料枠の量的比較」で、cadenzaがどう振る舞うかを順に追います。
アウトプットの内容に関してもあくまでサンプルです。ちゃんとレビューしたわけではないので話半分に見てもらえればと思います。

## Phase 1: Issue Finding

`/cadenza:issue-finding` を起動するとまずテーマや仮説、イシューの設定から始まります。

以下の5ステップが順に走ります。

| Step |主導|やり取りの中身|
|---|------|----------|
| 1 |ユーザー|一次情報の確認 → 7ツール全使用経験あり/ 詰まった経験なし。「使用経験者の整理(調査・サーベイ系)」として続行を選択|
| 2 |ユーザー|対象読者/読者の問題仮説/読後変化を1〜2文で言語化|
| 3 | AI | WebSearchで既存記事をサーベイ → 「無料枠特化 × 量的 × 日本語」の組み合わせは未充足と判明|
| 4 | AI | 3条件チェック(本質的選択/深い仮説/答えられる)すべて通過 |
| 5 |ユーザー| イシュー1文を確定して明示同意|

最終的に以下のイシューに決まりました。

> 2026年5月時点でAIコーディングエージェントを試したい個人開発者は、主要7ツール(Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Windsurf / Kiro)の無料枠から、自分の用途に合う「最初に試すべきツール」をどう選び、どんな使い方で有料化を検討すべきか？


## Phase 2: Issue Decomposition

`/cadenza:issue-decomposition` を起動すると、ストーリーラインを組み立てる工程に入ります。

以下の5ステップが走ります

| Step |主導|やり取りの中身|
|---|------|----------|
| 1 | AI提案 → ユーザー合意|分解パターンの選択。今回はCompare-Select (Options → Criteria → Decision)を提案 → 採用|
| 2 |ユーザー(今回はAIによる下書き → ユーザー添削) |各サブイシューへの仮説 1文。私がPhase 1で「詰まった経験なし/ユニーク要素なし」と回答済みだったので、AIが下書きを出してそのまま採用|
| 3 | AI提案 → ユーザー合意|ストーリーラインパターン。長文記事向きのSky-Rain-Umbrellaを提案 → 採用|
| 4 |ユーザー| 主張を1文に固定。3案から選択|
| 5 | AI主導| ストーリーライン妥当性チェック (5項目)。全項目通過 |

以下のストーリーラインに決まりました。

|役割|問い|
|------|------|
| ☁️ Sky (事実) |各ツールの無料枠の制限値を共通単位で並べるとどうなるか？ |
| 🌧️ Rain (解釈) |制限値の差は各社のビジネスモデルから来ているのか？ (普及優先/課金誘導/プラットフォーム侵食 の3系統分類は成り立つか) |
| ☂️ Umbrella (行動) |用途別(補完/ agent /リファクタ)に「最初に試すべき」「有料化前提」をどう仕分けるか？ |

主張は以下
> 各社の無料枠は**3系統のビジネス戦略** (普及優先/課金誘導/プラットフォーム侵食) **の反映**であり、読者の用途と各社の戦略系統を照らし合わせて選ぶのが正解。


## Phase 3: Storyboarding

`/cadenza:storyboarding` を起動すると、各サブイシューを 「何で見せるか」(コード/図/表/ベンチマーク等)と「何を検証する必要があり、何は検証しないか」を設計します。

| Step |主導|やり取りの中身|
|---|------|----------|
| 1, 2 | AI提案 → ユーザー合意|各サブイシューの形式 (見せ方) と仕様 (中身)を提案|
| 3 | AI提案 → ユーザー合意| 出力スタイルに合わせた調整。今回は「Zennにフラット投下、図は使わず表のみ」と私が指定|
| 4 | AI主導| 全検証項目と除外項目 (やらないこと)を整理|
| 5 | AI主導| ストーリーボードレビュー (5項目)。全項目通過 |

各サブイシューを1つの表で表現する方針(Mermaid図表は不採用)。

| サブイシュー | 形式 | 仕様の概略|
|----------|------|------------|
| ☁️ Sky (サブイシュー 1) |比較表|行= 7ツール/列=公称制限値・共通単位換算(タスク/日) ・課金トリガ・クレカ要否|
| 🌧️ Rain (サブイシュー 2) | 3系統分類表|行= 7ツール/列=戦略系統・制限値の太さ・提供形態・判定根拠|
| ☂️ Umbrella (サブイシュー 3) | 意思決定マトリクス + 読み下し段落|行= 3用途 × 列= 7ツール の21セルに判定(◎ / ○ / △ / ×)を入れて、下に意思決定ガイダンスを段落で添える|


## Phase 4: Analysis Execution

`/cadenza:analysis-execution`では、実際の検証作業を実行します。
今回の検証は全てWeb調査のみで完結するように調整しています。サンプルなので。

### 検証実行と主な発見

7ツールの公式料金ページと各社のビジネスモデル背景をWebSearchで集約し、「コーディング1タスク= 1ファイル編集+ ~5回の補完 または1回のagent起動」という基準単位を著者の使用経験ベースで定義。これに沿って各ツールの無料枠を「タスク/日」換算しました。

主な発見:

- Tab補完の太さではWindsurf (無制限)とGitHub Copilot Free (2,000/月相当)が突出
- Agent駆動ではGemini CLI (1,000 req/日)が予想以上に太い
- Claude Code / Codex CLIの無料枠は実質ゼロ (本格利用にはPro $20/月 必須)
- リファクタ・大規模タスクは全社で無料枠不足、有料化前提

### イシュー再考 (部分発生)

Phase 2で立てた3系統名(普及優先/課金誘導/プラットフォーム侵食)はデータから見ると不正確で、「プラットフォーム引き込み型/純粋ツール課金誘導型/補完特化解放型」の方が説得力ある分類だと判明しました。

cadenzaには上流回帰シグナルが3種類定義されています(ストーリーライン崩壊/新しいイシュー発見/ 形式不適合)。今回の発見はいずれにも該当せず ── 3系統に分かれるという骨格は維持されたまま、ラベルだけ更新する形 ── なのでPhase 2への後戻りは不要、Phase 4内で仮説名のみ更新する判断にしました。

データからストーリーラインが部分的に揺れるのは想定範囲内で、cadenzaはその揺れを「全部上流に戻る vs その場で更新」のどちらで処理すべきかをユーザーに問う設計になっています。

### Phase 5へ引き継ぐ材料

- 比較表(7ツール × 4列:公称制限値/タスク換算/課金トリガ/クレカ要否)
- 3系統分類表(改訂版、各ツールへの判定根拠付き)
- 意思決定マトリクス (3用途 × 7ツール= 21セルの ◎/○/△/× 判定)
- 主張の更新候補(3系統ラベルを差し替えた版)

これでPhase 4完了。次はPhase 5 (Output Crafting)で `./.cadenza/output.md` を生成します。

## Phase 5: Output Crafting

`/cadenza:output-crafting` は、ここまでのPhase 1〜4の確定情報をもとに最終Markdownを `./.cadenza/output.md` に書き出します。

| Step |主導|やり取りの中身|
|---|------|----------|
| 1 | AI主導|構造の骨格を組み立て(Title / TL;DR /背景/各サブイシュー 1セクション/結論/参考) |
| 2 | AI提案 → ユーザー選択|タイトル候補3案を提案、ユーザーが選択|
| 3 | AI主導| TL;DR /冒頭(主張 +対象読者+読後変化を3〜5行で) |
| 4 | AI主導|各サブイシューを1セクションずつ執筆。Phase 3のストーリーボードで決めたビジュアル (表)をそのまま使い、ストーリーボード忠実性を守る|
| 5 | AI主導| コード/図/個人情報の最終チェック。最終確認の7項目を通過 |


### Output本文

Outputの内容を以下にそのまま貼り付けます。

:::details output.md
# AI コーディングエージェントの無料枠は 3 つの戦略の反映：用途別に 7 ツールを仕分ける

## TL;DR

主要 AI コーディングエージェント 7 ツール (Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Windsurf / Kiro) の無料枠を「タスク/日」共通単位で並べると、各社の制限値設計には 3 つのビジネス戦略 (プラットフォーム引き込み / 純粋ツール課金誘導 / 補完特化解放) が反映されています。個人開発者は単一ツールではなく、用途 (補完中心 / agent 駆動 / リファクタ大規模) ごとに最適な無料枠を組み合わせるのが現実解です。

対象読者は AI コーディングエージェントを試したい個人開発者・少人数チーム開発者で、有料化前に複数ツールを量的に比較して試用判断したい層です。読了後、各ツールの無料枠の実用性を共通単位で把握し、自分の用途に合う「最初に試すべき」「無料では足りないので有料化前提」のツールを切り分けられるようになります。

## 本記事のスタンス

この比較は使用経験者による研究/サーベイ系の整理です。著者は 7 ツールすべてを実際に触った経験を持ちますが、無料枠で「詰まった」体験は特になく、これから試す読者が制限値を量的に把握できるよう情報を整理することを目的としています。「自分が困った話」ではなく「試しに行く人のための地図」と捉えて読み進めてください。

## 共通単位「コーディング 1 タスク」の定義

各社の制限値はバラバラの単位 (requests / completions / tokens / premium requests / messages 等) で公開されており、そのままでは横断比較できません。本記事では以下の基準単位で正規化します。

> **コーディング 1 タスク = 1 ファイル編集 + 約 5 回の補完 または 1 回の agent 起動**

ここでいう「補完」はインライン補完 (Tab で受け入れる短い候補) を、「agent 起動」はチャット経由の指示や複数ファイルにまたがる Edit / Cascade 系の操作を 1 単位とします。換算精度は ±50% 程度を想定し、概算で実用感を比較する設計です。

## 各ツールの無料枠制限値 (2026年5月時点)

各社公式 pricing ページを横並びで整理した結果が以下です。

| ツール | 公称制限値 | 共通単位換算 (タスク/日) | 課金トリガ | クレカ要否 |
|--------|-----------|------------------------|------------|-----------|
| Claude Code | Pro $20/月 (年契約 $17/月) 必須。Free tier では使えない。新規 API アカウントには $5 程度の API credit が付与されるという情報がある | 約 5 タスク/日 ($5 の API credit を Claude Sonnet 4.x の中間料金で換算、1 タスク = 約 5,000–10,000 tokens 想定で 30 日に薄めた概算) | Pro 加入 / API credit 枯渇 | API 経由 / Pro 加入 ともに要 |
| Codex CLI | ChatGPT Free / Go に Codex は含まれるが、Free / Go の具体的な使用上限は ChatGPT 使用ダッシュボードで個別に確認する形 (公式 pricing 表には記載なし) | 評価不能 (上限が公開されていないため定量化できない) | ChatGPT Plus $20/月 へ | 任意 |
| Cursor (Hobby) | 公開情報では 2,000 completions + 50 slow premium model requests / 月 (公式 pricing ページからは直接抽出できず、レビュー記事を参照) | 約 13 タスク/日 (補完) + 約 1.7 premium/日 | 月内 quota 枯渇 → Pro $20 | 不要 |
| Gemini CLI | 1,000 requests/日、60 requests/分、約 250,000 tokens/分 (Flash モデル中心、Pro モデルは限定。具体値は Google AI Studio のダッシュボードで個別に確認) | 約 200 タスク/日 (1 タスク = 5 requests 換算) | 1 日上限 / 1 分あたりの token 上限 | 不要 (Google アカウントのみ) |
| GitHub Copilot Free | 公式記載で 2,000 completions/月 + 50 agent mode or chat requests/月 | 約 13 タスク/日 (補完) + 約 1.7 agent/chat 要求/日 | 月内 quota 枯渇 → Pro $10 | 不要 |
| Windsurf (Free) | Tab 補完は usage quota の対象外という公開情報あり。Cascade などの高度機能は quota 制 (公式 pricing ページからは直接抽出できず、レビュー記事を参照) | 補完: 概ね無制限 / advanced: 数回/日 | advanced 機能利用 → Pro $20 | 不要 |
| Kiro (Free) | 公式記載で月 50 credits + 初回 500 credits (30 日内利用) bonus、超過は $0.04/credit | 永続: 約 1.7 credit/日 / 初回: 約 17 credit/日 (vibe mode 1 = 1 credit、spec mode は数 credits 消費) | credit 枯渇 → Pro $20 / 追加 $0.04/credit | 不要 |

> **注**: 上記の数値は 2026 年 5 月時点の各社公式 pricing ページおよびレビュー記事を集約したものです。公式 pricing ページが Free tier の具体値を表で公開しているのは GitHub Copilot Free と Kiro のみで、それ以外 (Claude Code / Codex / Cursor / Gemini CLI / Windsurf) は別ページや使用ダッシュボードでの個別確認、あるいは公開された制限値の情報源は外部レビュー記事に依存しています。実際の試用前に各社公式の最新情報をご確認ください。

数値の幅は **5〜10 倍** に開きます。同じ「無料枠」と一括りにするには差が大きすぎます。

並べてみると、無料枠の太さには大きな偏りがあるのがわかります。Anthropic と OpenAI は実質ゼロ、Google と Microsoft (GitHub) は太め、Windsurf は補完だけ無制限、Amazon の Kiro は credit 制という変則設計です。これは技術的制約ではなく、**各社のビジネスモデルの反映** です。

## 無料枠の 3 系統分類

> **注**: 以下の 3 系統分類は本記事独自の整理であり、業界で確立された taxonomy ではありません。各社が公式に表明している戦略 (引用は各社の判定根拠を参照) を、本記事の視点で 3 つにグルーピングしたものです。読者の方は別の軸 (IDE 内蔵 / CLI / 機能成熟度 など) で再分類していただいて構いません。

7 ツールの無料枠設計を戦略観点で本記事独自に分類すると、以下の 3 つの系統が見えてきます。

| 系統 | 名称 | 特徴 | 該当ツール |
|------|------|------|----------|
| A | プラットフォーム引き込み型 | 太い無料枠で自社の他サービス (GitHub / Google Cloud / AWS) に誘導する。本業はクラウド/プラットフォームで、コーディングエージェントは入口 | GitHub Copilot, Gemini CLI, Kiro |
| B | 純粋ツール課金誘導型 | 細い無料枠でお試しは可能だが本格使用は有料前提。本業がツールそのもので、サブスク収益が主 | Cursor, Claude Code, Codex CLI |
| C | 補完特化解放型 | Tab 補完だけは無制限解放、agent / 高度機能は課金で差別化。IDE 採用最大化を狙う戦略的ローダー | Windsurf |

### 各社の判定根拠 (公式ソース引用)

**A. プラットフォーム引き込み型**

- **GitHub Copilot**: Microsoft CEO Satya Nadella は「Any per user business of ours, whether it's productivity or coding or security, will become a per user and usage business」と発言し、Copilot を Microsoft 全社の per-user + usage 戦略の一環として位置付けています ([GitHub Blog: usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/))。Copilot Free はその入口として、GitHub アカウント・リポジトリへの粘着 + Enterprise 連携での収益化が狙いと解釈できます。
- **Gemini CLI**: Google 公式 blog の発表で「industry's largest allowance with 60 model requests per minute and 1,000 requests per day at no charge」を明示し、追加 quota が必要になったら「Google AI Studio や Vertex AI key で usage-based billing」に進む tiered funnel を表明しています ([Google Blog: Introducing Gemini CLI](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/))。Free → Standard → Vertex AI Enterprise という Cloud 移行の入口として設計されています。
- **Kiro**: AWS は Kiro を Amazon Q Developer の後継として位置付け、新規 Q Developer Free Tier の作成を停止する戦略変更を公表しています ([AWS Blog: Q Developer end-of-support](https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement/))。AWS Builder ID で sign-in すると Amazon Q や AWS エコシステムとの直接統合が有効になる設計で ([Kiro Authentication docs](https://kiro.dev/docs/getting-started/authentication/))、AWS 開発者の取り込みが目的と読み取れます。

**B. 純粋ツール課金誘導型**

- **Cursor**: Anysphere は Cursor 単体で **$1B annualized revenue + 100 万人以上の paying users** を達成しており、$20 Pro のサブスクが収益主軸です。Hobby Free は「a real comparison... most developers who give it a serious two-week test either upgrade to Pro or decide the tool is not for them」と評価試用枠と位置付けられています (公開ベンチマーク + レビュー記事による解釈)。
- **Claude Code**: Anthropic Head of Growth の Amol Avasare は「Max launched a year prior, it didn't include Claude Code, and the company later bundled Claude Code into Max after it took off」と Pro/Max への bundle 戦略を公式に説明 ([The Register による報道](https://www.theregister.com/2026/04/22/anthropic_removes_claude_code_pro/))。Claude Code はサブスク engagement を上げる装置として位置付けられています。
- **Codex CLI**: OpenAI 公式 blog で「Codex is included with ChatGPT Plus, Pro, Business, and Enterprise plans—no separate subscription needed」と明示しており ([OpenAI: Introducing Codex](https://openai.com/index/introducing-codex/))、Plus / Pro に sign-in すると Free API credit ($5/$50) も付与される設計です。Free / Go の制限が厳しいのは ChatGPT サブスクへの移行を促すための前提と読み取れます。

**C. 補完特化解放型**

- **Windsurf**: Cognition (Devin の親会社) が 2025年12月に Windsurf を約 $250M で買収。Cognition CEO Scott Wu は公式 blog で「start by integrating Cognition's autonomous AI-powered engineer Devin into Windsurf's IDE」「developers can plan tasks in Windsurf and launch a team of Devins」と戦略を表明 ([Cognition Blog: Windsurf acquisition](https://cognition.ai/blog/windsurf))。Tab 補完無制限の Free プランは IDE 流入を加速する装置で、advanced 機能 (Cascade / Devin 統合) で課金を回収する構造と解釈できます。

戦略系統が見えると、同じ 2,000 completions/月 という似た数値でも、**戦略によって役割が反転する** のが理解できます。GitHub Copilot にとっては「ユーザー定着の入口 (GitHub エコシステムへ長く居てもらうための定常給付)」、Cursor にとっては「有料化への足切りライン (本気で使うなら Pro $20/月 へ進ませる装置)」として機能している、という対比になります。

## 用途別 × ツールの仕分け

戦略系統を踏まえて、3 つの典型用途で 7 ツールがどこまで使えるかを判定したのが下表です。

| 用途 | Claude Code | Codex CLI | Cursor | Gemini CLI | GitHub Copilot | Windsurf | Kiro |
|------|-------------|-----------|--------|------------|----------------|----------|------|
| 補完中心 (Tab 補完を主軸) | × | × | △ | ○ | ◎ | ◎ | △ |
| Agent 駆動 (タスクを委任) | △ | × | △ | ◎ | △ | △ | ○ |
| リファクタ・大規模 (複数ファイル編集) | × | × | × | △ | × | △ | × |

凡例: ◎ 最初に試す / ○ 試す価値あり / △ 課金前提 / × Skip

### 用途別の読み下し

**補完中心ユーザー** (IDE で打鍵しながら Tab 補完を多用するスタイル) は、**GitHub Copilot Free と Windsurf の二強** です。Copilot Free は月 2,000 completions、Windsurf は Tab 完全無制限。Copilot は GitHub エコシステムとの統合が強く、Windsurf は IDE 自体としての完成度が高い特徴があります。Gemini CLI も補完用途で 1,000 req/日 の太さは捨てがたいですが、CLI ベースなので IDE 補完体験とは別物です。Cursor / Kiro は補完中心では quota 枯渇が早く、Claude Code / Codex CLI は補完用途を主目的としていません (どちらも agent 寄り)。

**Agent 駆動ユーザー** (チャットでタスクを委任、複数ファイルの自動編集) は、意外にも **Gemini CLI Free が最有力** になります。Flash モデル中心ながら 1,000 requests/日は agent タスクの試用に十分で、Google アカウントだけで使えるのが大きい点です。Kiro も spec mode で agent 委任に向きますが credit 制で消費が早く、Claude Code は agent 設計の質が高いものの無料枠が実質ゼロ、本格利用には Pro 必須です。Cursor は 50 premium requests/月 では agent 駆動の試用には足りず、Codex CLI は無料枠の上限が公開されておらず評価対象外です。

**リファクタ・大規模ユーザー** (複数ファイルにまたがる構造変更、大量の Edit) は、残念ながら **どの無料枠でも構造的に不足します**。Cursor 50 premium は数日で枯渇、Kiro 50 credits も同様、Copilot Free の 50 agent / chat requests も同じ。Windsurf の Cascade も無料枠では数回/日。Gemini CLI の 1,000 requests/日は理論上余裕がありますが、複数ファイル編集を 1 task 5 requests で抑えるのは実用上困難で、結局 quota を消費します。**この用途で AI エージェントを本格活用したいなら、いずれかのツールの有料化は前提に組み込むべき** です。

## おわりに

3 系統に分かれる無料枠戦略は、選択する側にとって **「自分の用途と各社の戦略系統を照らし合わせる」** という指針を提供します。

- **補完中心の試用** → A 系統 (GitHub Copilot Free / Windsurf) で十分回せる。プラットフォーム引き込みの恩恵を受けつつ無料の枠内に収まる
- **Agent 駆動の試用** → A 系統 (Gemini CLI Free または Kiro 初回 bonus) で短期検証
- **リファクタ・大規模の本格運用** → B 系統 (Cursor Pro / Claude Code Pro) のいずれかへの課金が前提

つまり、**個人開発者は単一ツールに絞らず、用途別に無料枠を組み合わせて使う**のが 2026年5月時点の現実解です。各社の戦略を読み解いた上で自分の用途と照らし合わせれば、有料化のタイミングも自然に見えてきます。

## 番外: OSS BYO API 系

本記事のスコープからは外しましたが、以下の OSS ツールは **「OSS だから 0 円で開始できるが LLM API の課金は別途必要」** という別軸の存在として認識しておく価値があります。

- **Cline**: VS Code 拡張で、人気が急上昇中の OSS。Anthropic / OpenAI / Google など各種 API key を持ち込んで動かす形式です
- **Aider**: ターミナル CLI ベースの OSS で、power user 向けです
- **Continue**: VS Code / JetBrains の拡張機能として動作する OSS です

これらは「ツールは無料、API は実費」というモデルなので、本記事の「無料枠の量的比較」軸には乗りません。ただし、API の月額固定費を払いたくない / 自前で課金管理したい開発者には選択肢になります。

## 参考リンク

- [Claude Code Pricing (Anthropic)](https://claude.com/pricing)
- [Codex Pricing (OpenAI Developers)](https://developers.openai.com/codex/pricing)
- [Cursor Models & Pricing](https://cursor.com/docs/models-and-pricing)
- [Gemini CLI Quotas (Google AI)](https://ai.google.dev/gemini-api/docs/rate-limits)
- [GitHub Copilot Plans](https://github.com/features/copilot/plans)
- [Windsurf Pricing](https://windsurf.com/pricing)
- [Kiro Pricing](https://kiro.dev/pricing/)

:::
