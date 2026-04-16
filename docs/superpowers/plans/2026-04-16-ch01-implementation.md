# 第1章「はじめてのAIエージェント」執筆計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** spec `docs/superpowers/specs/2026-04-16-ch01-redesign.md` に基づき、第1章「はじめてのAIエージェント」の本文（Zenn Book形式の.mdファイル）とサンプルコードを完成させる。

**Architecture:**
書籍本文は `books/ai-agent-with-strands-agents/ch01-first-agent.md` に1ファイルで配置する。サンプルコードは別リポジトリ `building-ai-agents-on-aws-samples` の `ch01/` ディレクトリに置き、本文中のコードブロックはこのリポジトリ上のパスを参照する。本文の各節（1.1〜1.3）はspecの該当節に1対1で対応する。スタイルガイド `docs/superpowers/writing-style-guide.md` への準拠を全タスク共通の制約とする。

**Tech Stack:**
- Zenn Book（Markdown形式、`:::message` ブロック等のZenn固有記法）
- Strands Agents 最新版
- Bedrock Claude Haiku 4.5（モデルID `jp.anthropic.claude-haiku-4-5-20251001-v1:0`）
- uv（Python パッケージマネージャ）
- AWS CLI v2（2.32.0以上）

---

## File Structure

### 作成するファイル

- `books/ai-agent-with-strands-agents/ch01-first-agent.md`
  - 役割: 第1章本文。1.1〜1.3 の3節構成
  - 命名: ch00-introduction.md と同じハイフン区切りパターン

### 修正するファイル

- `books/ai-agent-with-strands-agents/config.yaml`
  - 役割: Zenn Book のチャプター登録
  - 修正点: `chapters` リストに `ch01-first-agent` を追加

### 参照する既存ファイル（修正対象外）

- `docs/superpowers/specs/2026-04-16-ch01-redesign.md` — spec
- `docs/superpowers/writing-style-guide.md` — スタイルガイド
- `books/ai-agent-with-strands-agents/ch00-introduction.md` — 文体・記法のリファレンス
- `/tmp/building-ai-agents-on-aws-samples/ch01/agent.py` — サンプルコード本体（既存）

---

## Task 1: チャプターファイルの足場と config 登録

**Files:**
- Create: `books/ai-agent-with-strands-agents/ch01-first-agent.md`
- Modify: `books/ai-agent-with-strands-agents/config.yaml`

- [ ] **Step 1: チャプターファイルを新規作成（フロントマターと節見出しのみ）**

`books/ai-agent-with-strands-agents/ch01-first-agent.md` を以下の内容で作成:

```markdown
---
title: "はじめてのAIエージェント"
---

## 1.1 開発環境の準備

## 1.2 はじめてのエージェントを動かす

## 1.3 AIエージェントとは
```

意図: フロントマターと3節の見出しだけ先に置き、後続タスクで各節を埋める。

- [ ] **Step 2: config.yaml の chapters リストに ch01 を追加**

`books/ai-agent-with-strands-agents/config.yaml` を以下のように修正:

修正前:
```yaml
chapters:
  - ch00-introduction
```

修正後:
```yaml
chapters:
  - ch00-introduction
  - ch01-first-agent
```

- [ ] **Step 3: Zenn CLI でプレビュー可能か確認**

実行: `cd /Users/Naoki/work/workshop/zenn && npx zenn list:books`

期待出力: 「AWSで作るパーソナルAIエージェント入門 ―...」が表示される。エラーが出る場合は config.yaml の YAML 文法を見直す。

- [ ] **Step 4: コミット**

```bash
cd /Users/Naoki/work/workshop/zenn
git add books/ai-agent-with-strands-agents/ch01-first-agent.md books/ai-agent-with-strands-agents/config.yaml
git commit -m "scaffold ch01 chapter file and register in config"
```

---

## Task 2: 1.1 開発環境の準備 を執筆

**Files:**
- Modify: `books/ai-agent-with-strands-agents/ch01-first-agent.md`

参照: spec の `## 1.1 開発環境の準備` セクション全体（1.1.1〜1.1.6）

- [ ] **Step 1: 1.1冒頭の導入文を追加**

`## 1.1 開発環境の準備` の直後に、本節で何を行うかを2〜3文で予告する導入を1段落書く。
内容: 「本節では、第1章で動かすエージェントを実行できる状態までの環境構築を行う。AWSアカウントとBedrockモデルアクセスの準備、AWS CLI と uv のインストール、`aws login` でのサインインまでを扱う」のような要約を、ですます調で記述。

- [ ] **Step 2: 1.1.1〜1.1.6 の各小節を埋める**

spec の 1.1.1〜1.1.6 の内容に従い、それぞれ `### 1.1.1 前提環境の確認` のような見出し付きで本文を執筆。

各小節で守る制約（スタイルガイドより）:
- ですます調統一、辞書形止め禁止
- 絵文字・太字（強調目的）禁止
- 箇条書きは3〜5項目程度、項目先頭の太字禁止
- AWS CLI のインストールコマンドはmacOS版を本文掲載、Linux/Codespaces版は `:::message` ブロックで補足
- コードブロックは必ず言語指定（`bash`、`python` 等）
- 略語の初出時は正式名称を併記（FTU = First-Time Use等）

具体的に書くべきコマンド例（spec通り）:

macOS版 AWS CLI v2 インストール:
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

Linux/Codespaces版 AWS CLI v2 インストール（補足ブロック内）:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

uv インストール:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

aws login（ブラウザ利用可能時）:
```bash
aws login
```

aws login（Codespaces等ブラウザ利用不可時、補足ブロック内）:
```bash
aws login --remote
```

動作確認:
```bash
aws sts get-caller-identity
uv --version
```

- [ ] **Step 3: スタイルガイド準拠を1.1のみで自己チェック**

書き終えたら以下を読み直して確認:
- ですます調が崩れていないか
- 「〜することができる」「〜を行う」など冗長表現がないか（spec の冗長表現テーブル参照）
- AI特有の言い回し（「〜と言えるでしょう」「素晴らしい」「シームレスな」等）がないか
- 全角コロン（`：`）やダッシュ（`—`、`──`、`―`）がないか

- [ ] **Step 4: コミット**

```bash
cd /Users/Naoki/work/workshop/zenn
git add books/ai-agent-with-strands-agents/ch01-first-agent.md
git commit -m "write ch01 section 1.1 development environment setup"
```

---

## Task 3: サンプルコードの動作確認と実行ログの取得

**Files:**
- Verify: `/tmp/building-ai-agents-on-aws-samples/ch01/agent.py`
- Capture output for use in Task 4

- [ ] **Step 1: 既存サンプルコードの内容確認**

実行: `cat /tmp/building-ai-agents-on-aws-samples/ch01/agent.py`

期待される内容（specの 1.2.3 と一致しているか確認）:
```python
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
print(response)
```

差分があればspecと一致するように修正してコミット（修正不要なら本ステップはスキップ）。

- [ ] **Step 2: サンプルコードの実行に必要な準備（uv プロジェクト初期化）**

実行（サンプルコードリポジトリの ch01 ディレクトリで）:
```bash
cd /tmp/building-ai-agents-on-aws-samples/ch01
uv init --no-readme
uv add strands-agents strands-agents-tools
```

`uv init --no-readme` は README を上書きしないため指定。`pyproject.toml` と `.python-version` が生成される。

- [ ] **Step 3: AWS 認証の確認**

実行: `aws sts get-caller-identity --region ap-northeast-1`

期待出力: アカウントID、ARN、UserIdが表示される。失敗する場合は `aws login` を再実行。

- [ ] **Step 4: サンプルコード実行と出力キャプチャ**

実行:
```bash
cd /tmp/building-ai-agents-on-aws-samples/ch01
uv run python agent.py 2>&1 | tee /tmp/ch01-agent-output.txt
```

期待される挙動: LLMが `http_request` ツールを呼び出し、何らかの天気情報APIにアクセスして結果を返す。ツール呼び出しのログ（`Tool #1: http_request` のような出力）と最終応答が表示される。

エラーが出た場合の対処:
- `Could not find provider` → `strands-agents` が入っていない。`uv add strands-agents strands-agents-tools` を再実行
- `AccessDeniedException` → Bedrock のモデルアクセスが未許可。1.1.2 のFTU送信を完了させる
- `ResourceNotFoundException` → モデルIDが誤り、もしくはリージョンが誤り。`ap-northeast-1` で `jp.anthropic.claude-haiku-4-5-20251001-v1:0` を指定

- [ ] **Step 5: 出力ログを確認して掲載用に整形**

`/tmp/ch01-agent-output.txt` を開き、本文掲載用に以下を抽出:
- LLMの応答冒頭
- ツール呼び出しのログ（短く要約）
- 最終応答

**重要:** 出力に個人を特定する情報（IPアドレス、リクエストIDの一部等）が含まれる場合は伏字（`xxx`）に置換する。

整形後の出力サンプルを次のタスク（Task 4 の 1.2.4）で使用するため、本ステップで内容を確定させる。

- [ ] **Step 6: pyproject.toml と uv.lock を本タスクではコミットしない**

サンプルコードリポジトリの `ch01/pyproject.toml` と `uv.lock` は、書籍リポジトリではなくサンプルコードリポジトリ側の管理対象。本タスクではコミットしない（サンプルコードリポジトリ側のコミットは別途扱う）。

---

## Task 4: 1.2 はじめてのエージェントを動かす を執筆

**Files:**
- Modify: `books/ai-agent-with-strands-agents/ch01-first-agent.md`

参照: spec の `## 1.2 はじめてのエージェントを動かす` セクション全体（1.2.1〜1.2.6）

- [ ] **Step 1: 1.2冒頭の導入文を追加**

`## 1.2 はじめてのエージェントを動かす` の直後に、本節の目的を2〜3文で記述。
内容: 「本節では、Strands Agentsを使った最小構成のエージェントを動かす。LLMが自分でツールを呼び出して天気情報を取得する流れを体験する」のような要約。

- [ ] **Step 2: 1.2.1〜1.2.3 の小節を執筆**

spec通りに `### 1.2.1 これから作るもの`、`### 1.2.2 プロジェクトの初期化`、`### 1.2.3 エージェントの実装` を埋める。

1.2.3のコードブロックは以下の形式（言語指定 + ファイルパス）:

````markdown
```python:ch01/agent.py
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
print(response)
```
````

1.2.2 のコマンドブロック（言語指定 `bash`）:
````markdown
```bash
uv init my-first-agent
cd my-first-agent
uv add strands-agents strands-agents-tools
```
````

- [ ] **Step 3: 1.2.4 実行 を執筆（Task 3 で取得した出力を使用）**

`### 1.2.4 実行` の小節に以下を含める:
- 実行コマンド（言語指定 `bash`）
- Task 3で取得した実行ログを bash ブロックで掲載（出力例として明示）
- 「実行のたびに結果が変わる場合がある」旨を1文で注記

実行コマンド例:
```bash
uv run python agent.py
```

- [ ] **Step 4: 1.2.5 解説、1.2.6 何が起きているか を執筆**

spec通りに執筆。1.2.6 の見出しは「何が起きているか」。spec の表現を踏襲。

- [ ] **Step 5: スタイルガイド準拠を1.2のみで自己チェック**

特に注意:
- コードブロックの前後に「なぜそのコードを書くのか」「何が起きるか」の説明文があるか
- インラインコード（バッククォート）の前後に半角スペースが入っているか
- 「以下のコードを見てください」のような空虚な導入をしていないか

- [ ] **Step 6: コミット**

```bash
cd /Users/Naoki/work/workshop/zenn
git add books/ai-agent-with-strands-agents/ch01-first-agent.md
git commit -m "write ch01 section 1.2 first agent hands-on"
```

---

## Task 5: 1.3 AIエージェントとは を執筆

**Files:**
- Modify: `books/ai-agent-with-strands-agents/ch01-first-agent.md`

参照: spec の `## 1.3 AIエージェントとは` セクション全体（1.3.1〜1.3.3）

- [ ] **Step 1: 1.3冒頭の導入文を追加**

`## 1.3 AIエージェントとは` の直後に、本節の目的を1〜2文で記述。
内容: 「1.2で動かしたものは何だったのか、また業界ではAIエージェントがどう定義されているかを整理する」のような要約。

- [ ] **Step 2: 1.3.1 「AIエージェント」という言葉の現状 を執筆**

spec通りに執筆。各社の定義は箇条書きで列挙。

注意:
- 各社名の表記: Anthropic / OpenAI（Agents SDK） / Google（ADK） / AWS（Strands Agents）
- 「業界で統一された定義は存在しない」「本書では特定の定義を『正解』として採用しない」を明記

- [ ] **Step 3: 1.3.2 Strands Agentsのモデル駆動アプローチ を執筆**

`### 1.3.2 Strands Agentsのモデル駆動アプローチ` の下に、以下4つの小見出し（`####`）で構成:
- モデル駆動の発想
- ワークフロー型フレームワークとの違い
- エージェントループ
- この設計の前提

エージェントループは番号付きリストで5ステップを記述（spec通り）。

ConversationManager の段落は「エージェントループ」小見出し末尾に配置し、第4章への接続を1文で示す。

- [ ] **Step 4: 1.3.3 本書での扱い を執筆**

spec通りに執筆。第2章以降への接続を1〜2文で示す。

- [ ] **Step 5: スタイルガイド準拠を1.3のみで自己チェック**

特に注意:
- 概念説明の段落で、無理にStrands Agentsに思想を寄せていないか
- 比喩（「頭脳」等）に逃げていないか
- 「〜と言えるでしょう」のような曖昧表現がないか

- [ ] **Step 6: コミット**

```bash
cd /Users/Naoki/work/workshop/zenn
git add books/ai-agent-with-strands-agents/ch01-first-agent.md
git commit -m "write ch01 section 1.3 what is an AI agent"
```

---

## Task 6: verify-section スキルで本文全体のファクトチェック

**Files:**
- Verify: `books/ai-agent-with-strands-agents/ch01-first-agent.md`

- [ ] **Step 1: verify-section スキルを起動**

実行: `Skill` ツールで `verify-section` を呼び出し、対象として `books/ai-agent-with-strands-agents/ch01-first-agent.md` 全体を渡す。

スキルが行うこと:
- 本文中の技術的主張をすべて抽出
- 各主張をWeb検索で裏取り
- 追加すべきコンテキストの有無を判定
- ✅/⚠️/❌ 形式でレポート

- [ ] **Step 2: スキル報告に基づき本文を修正**

⚠️ や ❌ が出た主張があれば、本文を修正する。修正不要なら本ステップはスキップ。

- [ ] **Step 3: 修正があった場合のみコミット**

```bash
cd /Users/Naoki/work/workshop/zenn
git add books/ai-agent-with-strands-agents/ch01-first-agent.md
git commit -m "fix ch01 based on fact-check findings"
```

---

## Task 7: review-book スキルで最終レビュー

**Files:**
- Verify: `books/ai-agent-with-strands-agents/ch01-first-agent.md`、`books/ai-agent-with-strands-agents/config.yaml`、サンプルコード一式

- [ ] **Step 1: review-book スキルを起動**

実行: `Skill` ツールで `review-book` を呼び出す。

スキルが確認すること:
- A. スタイルガイド準拠
- B. 技術的正確性
- C. 構成の整合性（config.yaml と本文）
- D. サンプルコードとの整合性（本文中のコードブロックと `/tmp/building-ai-agents-on-aws-samples/ch01/agent.py` が一致）
- E. 設計スペックとの整合性（spec通りの章構成になっているか）

- [ ] **Step 2: 指摘事項を反映**

レビュー結果に沿って本文・config.yaml・サンプルコードのいずれかを修正。

- [ ] **Step 3: 修正があった場合のみコミット**

```bash
cd /Users/Naoki/work/workshop/zenn
git add -p
git commit -m "fix ch01 based on review findings"
```

`git add -p` で修正内容を確認してから add する（意図しない変更の混入を防ぐ）。

- [ ] **Step 4: 最終確認**

実行: `npx zenn preview` で第1章をブラウザで確認。

確認項目:
- 章タイトルと節見出しが正しく表示される
- コードブロックがシンタックスハイライトされる
- `:::message` ブロックが正しくレンダリングされる
- 文字化けがない

問題なければ第1章執筆完了。pushはオーナーの明示指示を待つ（CLAUDE.md のルール）。

---

## Self-Review

### スペックカバレッジ

- spec 1.1 開発環境の準備 → Task 2 でカバー
- spec 1.2 はじめてのエージェントを動かす → Task 3 + Task 4 でカバー
- spec 1.3 AIエージェントとは → Task 5 でカバー
- spec 内の「ファクトチェック済み事項」 → Task 6 で再検証
- spec 内の第2章への接続 → Task 5 Step 4 でカバー

### 主張の一貫性

- ファイル名: `ch01-first-agent.md` で全タスク統一
- サンプルコードパス: `/tmp/building-ai-agents-on-aws-samples/ch01/agent.py` で統一
- 本文内コードブロックのファイルパス表記: `ch01/agent.py`（リポジトリ相対）で統一
- モデルID: `jp.anthropic.claude-haiku-4-5-20251001-v1:0` で統一
- リージョン: `ap-northeast-1` で統一

### プレースホルダースキャン

- TBD/TODO/「実装は後で」等の箇所なし
- 「適切なエラー処理を追加」のような曖昧指示なし
- すべてのコード・コマンドは実行可能な完全形で記述
