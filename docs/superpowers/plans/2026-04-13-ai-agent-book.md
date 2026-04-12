# AIエージェント構築本 — Zenn Book セットアップ & 第1章執筆 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zenn Bookの構造を作成し、第1章「はじめてのAIエージェント」のベースとなる全チャプターの本文を執筆する

**Architecture:** Zenn CLIのBook機能を使い、`books/ai-agent-book-tonari/` 配下に `config.yaml` と各チャプターのMarkdownファイルを配置する。第1章は4つのセクション + 1コラムで構成し、それぞれ独立したチャプターファイルとする。

**Tech Stack:** Zenn CLI, Markdown, Strands Agents SDK（サンプルコード内）

**参照スペック:** `docs/superpowers/specs/2026-04-13-ai-agent-book-design.md`

---

### Task 1: Zenn Book の雛形を作成する

**Files:**
- Create: `books/ai-agent-book-tonari/config.yaml`

- [ ] **Step 1: zenn-cli で本の雛形を生成する**

```bash
cd /Users/Naoki/work/workshop/zenn
npx zenn new:book --slug ai-agent-book-tonari --title "AIエージェント構築入門 ― TONaRiと学ぶ、動くエージェントの作り方" --summary "Strands Agents SDKとAmazon Bedrock AgentCoreを使い、パーソナルAIエージェントを一から構築する実践ガイド。各章が独立したモジュールとして読め、通読すれば複数サービスを連携する完成されたAIエージェントが手に入る。" --price 0
```

Expected: `books/ai-agent-book-tonari/` ディレクトリが生成される

- [ ] **Step 2: config.yaml を本の全体構成に合わせて編集する**

`books/ai-agent-book-tonari/config.yaml` を以下の内容にする:

```yaml
title: "AIエージェント構築入門 ― TONaRiと学ぶ、動くエージェントの作り方"
summary: "Strands Agents SDKとAmazon Bedrock AgentCoreを使い、パーソナルAIエージェントを一から構築する実践ガイド。各章が独立したモジュールとして読め、通読すれば複数サービスを連携する完成されたAIエージェントが手に入る。"
topics: ["ai-agent", "aws", "bedrock", "python", "strands"]
published: false
price: 0
toc_depth: 2
chapters:
  - ch01-01-hands-on
  - ch01-02-what-is-agent
  - ch01-03-why-agent-now
  - ch01-04-how-to-read
  - ch01-column-frameworks
```

注: 第2章以降のチャプターは、各章の執筆時に追加していく。

- [ ] **Step 3: 不要な自動生成ファイルを削除する**

`npx zenn new:book` が `example1.md` 等のサンプルチャプターを生成している場合、削除する。

```bash
rm -f books/ai-agent-book-tonari/example*.md
```

- [ ] **Step 4: プレビューで本が認識されるか確認する**

```bash
npx zenn list:books
```

Expected: `ai-agent-book-tonari` が一覧に表示される

- [ ] **Step 5: コミット**

```bash
git add books/ai-agent-book-tonari/config.yaml
git commit -m "Zenn Bookの雛形を作成"
```

---

### Task 2: チャプター 1.1「まずは動かしてみよう」を執筆する

**Files:**
- Create: `books/ai-agent-book-tonari/ch01-01-hands-on.md`

**方針:** 読者が最短距離でAIエージェントを動かす体験をするチャプター。細かい説明は後回しにし、「写経して動いた！」という感動を優先する。

- [ ] **Step 1: チャプターファイルを作成する**

`books/ai-agent-book-tonari/ch01-01-hands-on.md` を以下の内容で作成する:

```markdown
---
title: "まずは動かしてみよう"
---

この本を手に取ったあなたは、AIエージェントに興味を持っているはずだ。「AIエージェントとは何か」を語る前に、まずは実際に動かしてみよう。細かい理屈は後で説明する。今はただ、手を動かしてほしい。

## 準備するもの

このハンズオンに必要なものは3つだけだ。

- Python 3.12以上
- AWSアカウント
- ターミナル（コマンドライン）

## AWSの準備

Amazon Bedrockでモデルを利用するために、最低限の準備を行う。

### モデルアクセスの有効化

1. AWSマネジメントコンソールにログインする
2. リージョンを **us-east-1（バージニア北部）** に切り替える
3. Amazon Bedrockのコンソールを開く
4. 左メニューから「モデルアクセス」を選択する
5. 「モデルアクセスを管理」をクリックする
6. **Claude Haiku（Anthropic）** にチェックを入れ、アクセスをリクエストする

通常、数分以内にアクセスが有効化される。

### AWS CLIの設定

AWS CLIがまだインストールされていない場合は、公式ドキュメントに従ってインストールする。

インストール済みであれば、認証情報を設定する。

```bash
aws configure
```

`AWS Access Key ID`、`Secret Access Key`、リージョン（`us-east-1`）を入力する。IAMユーザーの作成方法が分からない場合は、AWSの公式ドキュメント「IAMユーザーの作成」を参照してほしい。

:::message
AWS SSOを使用している場合は `aws configure sso` で設定できる。組織のAWSアカウントを使用する場合は、管理者にBedrock利用の許可を確認しよう。
:::

## エージェントを作る

準備ができたら、さっそくエージェントを作ろう。

### パッケージのインストール

```bash
pip install strands-agents strands-agents-tools
```

### コードを書く

以下のコードを `agent.py` として保存する。

```python:agent.py
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
print(response)
```

たった10行だ。これだけでAIエージェントが動く。

### 実行する

```bash
python agent.py
```

少し待つと、エージェントが天気情報を取得して回答してくれるはずだ。

:::message
初回実行時にBedrockへの接続エラーが出る場合は、AWS CLIの認証情報とリージョン設定を確認しよう。`aws bedrock list-foundation-models --region us-east-1` が正常に動作するかを先に確認するのがおすすめだ。
:::

## 何が起きたのか？

今、あなたが動かしたプログラムは、こんなことをしていた。

1. 「東京の今の天気を調べて」というリクエストを受け取った
2. LLM（Claude）が「天気を調べるにはHTTPリクエストが必要だ」と**自分で判断**した
3. `http_request` ツールを使って天気情報を**自分で取得**した
4. 取得した情報をもとに、人間にわかりやすい回答を**自分で組み立てた**

ポイントは「自分で判断した」という部分だ。あなたは「HTTPリクエストを送れ」とは指示していない。エージェントが自ら考え、道具を選び、行動した。

これがAIエージェントだ。

次のチャプターでは、この「自分で考えて行動する」仕組みをもう少し詳しく見ていこう。
```

- [ ] **Step 2: プレビューで表示を確認する**

```bash
npx zenn preview
```

ブラウザで `http://localhost:8000` を開き、本の一覧から「AIエージェント構築入門」→ チャプター「まずは動かしてみよう」が正しく表示されることを確認する。

- [ ] **Step 3: コミット**

```bash
git add books/ai-agent-book-tonari/ch01-01-hands-on.md
git commit -m "第1章 1.1 まずは動かしてみよう を執筆"
```

---

### Task 3: チャプター 1.2「今あなたが動かしたものは何か」を執筆する

**Files:**
- Create: `books/ai-agent-book-tonari/ch01-02-what-is-agent.md`

**方針:** 1.1で動かしたコードを振り返りながら、チャットボットとエージェントの違い、エージェントの構造（脳・手・判断力）を解説する。

- [ ] **Step 1: チャプターファイルを作成する**

`books/ai-agent-book-tonari/ch01-02-what-is-agent.md` を以下の内容で作成する:

```markdown
---
title: "今あなたが動かしたものは何か"
---

前のチャプターで、あなたはAIエージェントを動かした。たった10行のコードで、天気を調べて教えてくれるプログラムが出来上がった。

このチャプターでは「今動かしたものは何だったのか」を掘り下げていく。

## チャットボットとの違い

ChatGPTやClaudeをブラウザで使ったことがある人は多いだろう。あれは「チャットボット」だ。では、あなたが先ほど作った「エージェント」とは何が違うのか。

| | チャットボット | AIエージェント |
|---|---|---|
| できること | 知識に基づいて回答する | 外部のツールを使って行動する |
| 情報の範囲 | 学習済みの知識のみ | リアルタイムの情報にアクセス可能 |
| 主体性 | ユーザーの質問に受動的に答える | 目標達成のために能動的に手段を選ぶ |

チャットボットは「賢い回答マシン」だ。どんな質問にもそれらしく答えてくれるが、学習済みの知識の範囲を超えることはできない。「今日の天気」を聞いても、実際の天気を調べることはできず、一般的な知識で答えるしかない。

一方、AIエージェントは「考えて行動するプログラム」だ。目標を達成するために、どんなツールを使えばいいか自分で判断し、実行し、結果を解釈して回答する。

## エージェントの3要素

先ほどのコードをもう一度見てみよう。

```python:agent.py
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
```

このコードには、エージェントの3つの要素が詰まっている。

### 1. 脳（LLM）

```python
model="anthropic.claude-haiku-4-5-20251001-v1:0"
```

エージェントの「脳」にあたるのがLLM（大規模言語モデル）だ。ここではAmazon Bedrock経由でClaude Haikuを使用している。LLMはユーザーのリクエストを理解し、何をすべきか考え、最終的な回答を組み立てる。

### 2. 手（ツール）

```python
tools=[http_request]
```

エージェントの「手」にあたるのがツールだ。LLMだけでは「考える」ことしかできないが、ツールを持たせることで外の世界に「触れる」ことができるようになる。天気情報の取得、データベースの検索、メールの送信——ツール次第で、エージェントにさまざまな能力を与えられる。

### 3. 判断力（エージェントループ）

これはコードには明示的に現れないが、Strands Agents SDKの内部で動いている最も重要な仕組みだ。

エージェントは以下のループを回している。

1. ユーザーの入力を受け取る
2. LLMが「次に何をすべきか」を判断する
3. ツールの実行が必要と判断したら、ツールを呼び出す
4. ツールの結果をLLMに戻す
5. LLMが「まだ作業が必要か」を判断する
6. 十分な情報が集まったら、最終回答を生成する

このループこそが、チャットボットとエージェントを分ける決定的な違いだ。エージェントは一度の思考で終わらず、必要に応じて何度もツールを使い、段階的に目標に近づいていく。

## system_prompt の役割

```python
system_prompt="あなたは親切なアシスタントです。日本語で回答してください。"
```

`system_prompt` はエージェントの「人格」や「行動指針」を定義するものだ。今は簡単な一文だが、ここに詳細な指示を書くことで、エージェントの振る舞いを大きくコントロールできる。これについては第2章で深掘りする。

## まとめ

AIエージェントとは、**LLM（脳）** が **ツール（手）** を使って、**自律的に判断しながら（判断力）** 目標を達成するプログラムのことだ。

この3要素を拡張していくのが、この本のテーマとなる。脳をより賢くし、手を増やし、判断力を磨いていく。その先に、あなただけのパーソナルAIエージェントが待っている。
```

- [ ] **Step 2: プレビューで表示を確認する**

```bash
npx zenn preview
```

ブラウザで `http://localhost:8000` を開き、チャプター「今あなたが動かしたものは何か」が正しく表示されること、表・コードブロックのレンダリングを確認する。

- [ ] **Step 3: コミット**

```bash
git add books/ai-agent-book-tonari/ch01-02-what-is-agent.md
git commit -m "第1章 1.2 今あなたが動かしたものは何か を執筆"
```

---

### Task 4: チャプター 1.3「なぜ今、AIエージェントなのか」を執筆する

**Files:**
- Create: `books/ai-agent-book-tonari/ch01-03-why-agent-now.md`

**方針:** 短くまとめる。長い歴史解説は不要。「今なぜエージェントが作れるのか」に絞り、TONaRiを紹介して本書全体の見通しを示す。

- [ ] **Step 1: チャプターファイルを作成する**

`books/ai-agent-book-tonari/ch01-03-why-agent-now.md` を以下の内容で作成する:

```markdown
---
title: "なぜ今、AIエージェントなのか"
---

AIエージェントという概念自体は新しいものではない。しかし「個人開発者が実用的なAIエージェントを作れる時代」は、つい最近始まったばかりだ。

## LLMが変えたもの

従来のAIエージェント開発には、自然言語処理、意図理解、対話管理など、複数の専門分野にまたがる高度な知識が必要だった。

LLMの登場がこれを一変させた。

- **言語理解**: ユーザーの意図を正確に理解する能力がLLMに備わった
- **推論と判断**: 「今何をすべきか」をLLM自身が考えられるようになった
- **ツール選択**: 複数のツールの中から適切なものを選ぶ判断力を獲得した

つまり、エージェントの「脳」をゼロから設計する必要がなくなった。開発者は「脳」の部分をLLMに任せ、「手」であるツールの実装と「どう振る舞ってほしいか」のプロンプト設計に集中できるようになったのだ。

## エージェントフレームワークの成熟

LLMの進化に加え、エージェント開発のためのフレームワークやインフラも急速に整備されてきた。

- **Strands Agents SDK**: AWSが公開したオープンソースのエージェントフレームワーク
- **Amazon Bedrock AgentCore**: エージェントのホスティング、メモリ管理、ツール連携を統合的に提供するマネージドサービス
- **MCP（Model Context Protocol）**: ツール連携の標準プロトコル

これらの登場により、エージェントの構築・運用に必要なインフラを自前で用意する必要がなくなった。

## この本で作るもの — TONaRi

本書では、筆者が日常的に使っているパーソナルAIエージェント **TONaRi** をモデルケースとして、AIエージェントの構築方法を解説していく。

TONaRiは以下のような能力を持つエージェントだ。

- **会話**: 自然な日本語での対話
- **ツール連携**: Googleカレンダー、Gmail、Notion、タスク管理など28種類のツールを操作
- **記憶**: 長期記憶により、ユーザーの好みや過去のやり取りを覚えている
- **分業**: ドメインごとに専門のサブエージェントが連携する
- **身体**: 3Dアバターを通じた視覚的なインタラクション
- **自律行動**: 朝のブリーフィング、ニュース収集、自動ツイートなどをスケジュール実行

「こんな高機能なもの、本当に作れるのか？」と思うかもしれない。大丈夫だ。この本では、一つひとつの能力を独立した章で解説していく。章を読み進めるごとに、あなたのエージェントは新しい能力を獲得していく。

## エージェントは「サービスの橋渡し」

TONaRiを日常的に使っていて感じる最大の価値は、エージェントが**サービス間の橋渡し**をしてくれることだ。

例えば、こんな使い方ができる。

> 「明日の予定を確認して、午前中に空きがあればミーティングを入れておいて。あと、先週のレシピのメモをNotionから探して、材料の買い物リストをタスクに追加して」

一つの自然言語のリクエストで、カレンダー、Notion、タスク管理が連携する。それぞれのサービスを個別に開いて操作する必要がない。これは単なる便利さではなく、情報とアクションの流れを根本的に変えるものだ。

次のチャプターでは、この本の全体構成と読み方を説明する。
```

- [ ] **Step 2: プレビューで表示を確認する**

```bash
npx zenn preview
```

ブラウザで `http://localhost:8000` を開き、チャプターの表示を確認する。

- [ ] **Step 3: コミット**

```bash
git add books/ai-agent-book-tonari/ch01-03-why-agent-now.md
git commit -m "第1章 1.3 なぜ今AIエージェントなのか を執筆"
```

---

### Task 5: チャプター 1.4「本書の歩き方」を執筆する

**Files:**
- Create: `books/ai-agent-book-tonari/ch01-04-how-to-read.md`

**方針:** モジュール型の読み方を説明し、通読でも部分読みでも活用できることを伝える。前提知識・環境の一覧も示す。

- [ ] **Step 1: チャプターファイルを作成する**

`books/ai-agent-book-tonari/ch01-04-how-to-read.md` を以下の内容で作成する:

```markdown
---
title: "本書の歩き方"
---

この本は全8章で構成されている。最初から通して読むこともできるし、興味のある章だけを拾い読みすることもできる。このチャプターでは、本書の構成と読み方を説明する。

## 各章の概要

本書の各章は、エージェントに一つの「能力」を与えるという構成になっている。

| 章 | タイトル | 身につく能力 |
|----|---------|------------|
| 第1章 | はじめてのAIエージェント | エージェントの基本概念を理解する（本章） |
| 第2章 | エージェントの「脳」を作る | LLMとの接続、プロンプト設計、会話エージェントの構築 |
| 第3章 | エージェントに「手」を与える | ツール連携の設計と実装（MCP、Lambda） |
| 第4章 | エージェントに「記憶」を与える | 短期記憶・長期記憶の設計と実装 |
| 第5章 | エージェントを「分業」させる | マルチエージェントアーキテクチャの構築 |
| 第6章 | エージェントに「身体」を与える | フロントエンド、3Dアバター、音声の統合 |
| 第7章 | エージェントを「自律」させる | スケジュール実行と自動化ワークフロー |
| 第8章 | エージェントを「育てる」 | コスト最適化、運用、継続的な改善 |

## 2つの読み方

### 通読する場合

第1章から順番に読み進めると、最終的に複数のサービスと連携するパーソナルAIエージェントが完成する。各章のハンズオンを積み重ねることで、段階的にエージェントの能力が拡張されていく。

エージェント開発が初めてなら、この読み方を推奨する。

### 拾い読みする場合

各章はモジュールとして独立しているため、興味のある章だけを読んで実践することもできる。

例えば、すでにエージェントの基盤は持っていてメモリ機能を追加したい場合は、第4章だけを読めばよい。マルチエージェント構成に興味があるなら、第5章から始められる。

各章の冒頭には「この章で必要な前提環境」を記載している。拾い読みの場合は、そこに記載された環境を先に整えてほしい。

:::message
**第2章は共通基盤**

唯一の例外として、第2章「エージェントの脳を作る」は全章共通の基盤を構築する章だ。拾い読みする場合でも、第2章の環境構築だけは先に済ませておくことを推奨する。
:::

## 前提知識

本書は以下の知識を前提としている。

- **Python**: 基本的な文法、仮想環境（venv）、パッケージ管理（pip）を理解している
- **ターミナル操作**: コマンドラインでの基本操作ができる
- **Web APIの基礎**: HTTPリクエスト/レスポンスの概念を理解している
- **Git**: 基本的なバージョン管理操作ができる

以下については本書内で解説するため、事前知識は不要だ。

- AWS（Amazon Bedrock、Lambda等）
- LLM / AIエージェントの仕組み
- MCP（Model Context Protocol）
- フロントエンド開発（Next.js）— 第6章のみ

## 必要な環境

| 項目 | 要件 |
|------|------|
| Python | 3.12以上 |
| Node.js | 22以上（第6章のみ） |
| AWSアカウント | Bedrockのモデルアクセスが有効であること |
| AWS CLI | v2 |
| OS | macOS / Linux / WSL2（Windowsの場合） |

## サンプルコード

本書で使用するサンプルコードはGitHubリポジトリで公開している。各章に対応するブランチまたはタグが用意されており、途中の章から始める場合にも対応している。

それでは、第2章からエージェントの構築を始めよう。
```

- [ ] **Step 2: プレビューで表示を確認する**

```bash
npx zenn preview
```

ブラウザで `http://localhost:8000` を開き、チャプターの表示、表のレンダリングを確認する。

- [ ] **Step 3: コミット**

```bash
git add books/ai-agent-book-tonari/ch01-04-how-to-read.md
git commit -m "第1章 1.4 本書の歩き方 を執筆"
```

---

### Task 6: コラム「エージェントフレームワークの選択肢」を執筆する

**Files:**
- Create: `books/ai-agent-book-tonari/ch01-column-frameworks.md`

**方針:** 主要なエージェントフレームワークを簡潔に比較し、本書でStrands Agentsを選んだ理由を説明する。

- [ ] **Step 1: チャプターファイルを作成する**

`books/ai-agent-book-tonari/ch01-column-frameworks.md` を以下の内容で作成する:

```markdown
---
title: "[コラム] エージェントフレームワークの選択肢"
---

本書ではStrands Agents SDKを使用するが、AIエージェントを構築するためのフレームワークは他にも存在する。ここでは主要な選択肢を紹介する。

## 主なフレームワーク

### Strands Agents SDK（本書で使用）

AWSが公開したオープンソースのPythonフレームワーク。シンプルなAPIでエージェントを構築でき、Amazon BedrockおよびAgentCoreとの統合が強力。モデルプロバイダーの切り替えも容易で、Bedrock以外のLLMも利用可能。

### LangGraph / LangChain

LLMアプリケーション開発で最も広く使われているエコシステム。グラフベースのワークフロー定義が特徴で、複雑なエージェントの状態管理に優れる。コミュニティが大きく、情報が豊富。

### OpenAI Agents SDK

OpenAIが提供するエージェントフレームワーク。OpenAIのモデルとの統合に最適化されており、Responses APIとの連携が強力。ツール定義のインターフェースがシンプル。

### Google Agent Development Kit（ADK）

Googleが提供するエージェント開発キット。Vertex AIとの統合に優れ、GCPの各種サービスとの連携が容易。マルチエージェントシステムの構築もサポートしている。

## 比較

| 項目 | Strands Agents | LangGraph | OpenAI Agents SDK | Google ADK |
|------|---------------|-----------|-------------------|------------|
| 言語 | Python | Python / JS | Python | Python |
| クラウド統合 | AWS | 汎用 | OpenAI / Azure | GCP |
| 学習コスト | 低い | 中程度 | 低い | 中程度 |
| エコシステム | 成長中 | 大きい | 大きい | 成長中 |
| ライセンス | Apache 2.0 | MIT | MIT | Apache 2.0 |

## なぜStrands Agentsを選んだのか

本書でStrands Agentsを選んだ理由は主に3つだ。

1. **シンプルさ**: エージェントの構築に必要なコードが少なく、学習コストが低い。本書のように段階的にエージェントを拡張していくアプローチと相性が良い
2. **AgentCoreとの統合**: メモリ管理、ツール連携（MCP Gateway）、ランタイムホスティングまでをマネージドサービスとして利用でき、インフラの構築・管理の負担が小さい
3. **柔軟性**: Amazon Bedrockを通じて複数のLLMプロバイダーのモデルを選択でき、特定のモデルにロックインされない

ただし、どのフレームワークを選んでも、本書で解説するAIエージェントの設計思想（脳・手・記憶・分業・自律）は共通して適用できる。フレームワーク固有の実装は変わっても、エージェント設計の考え方は変わらない。
```

- [ ] **Step 2: プレビューで表示を確認する**

```bash
npx zenn preview
```

ブラウザで `http://localhost:8000` を開き、コラムの表示を確認する。

- [ ] **Step 3: コミット**

```bash
git add books/ai-agent-book-tonari/ch01-column-frameworks.md
git commit -m "第1章 コラム エージェントフレームワークの選択肢 を執筆"
```

---

### Task 7: 全体の最終確認とコミット

**Files:**
- Verify: `books/ai-agent-book-tonari/config.yaml`
- Verify: `books/ai-agent-book-tonari/ch01-*.md`

- [ ] **Step 1: ファイル一覧を確認する**

```bash
ls -la books/ai-agent-book-tonari/
```

Expected:
```
config.yaml
ch01-01-hands-on.md
ch01-02-what-is-agent.md
ch01-03-why-agent-now.md
ch01-04-how-to-read.md
ch01-column-frameworks.md
```

- [ ] **Step 2: config.yamlのchapters順序がファイルと一致するか確認する**

```bash
cat books/ai-agent-book-tonari/config.yaml
```

`chapters` の各エントリに対応する `.md` ファイルがすべて存在することを確認する。

- [ ] **Step 3: プレビューで本全体を通して確認する**

```bash
npx zenn preview
```

ブラウザで `http://localhost:8000` を開き、以下を確認する:
- 本のタイトルとサマリーが正しく表示される
- 全5チャプターが目次に正しい順序で表示される
- 各チャプターの内容が正しくレンダリングされる（表、コードブロック、メッセージボックス）
- チャプター間のナビゲーション（前へ/次へ）が動作する

- [ ] **Step 4: 未コミットの変更があればコミットする**

```bash
git status
```

未コミットの変更がある場合のみ:
```bash
git add books/ai-agent-book-tonari/
git commit -m "第1章の最終調整"
```
