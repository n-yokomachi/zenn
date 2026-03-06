---
title: "AIエージェントにツール追加しすぎてコストが重くなったのでサブエージェントに切り出す"
emoji: "🧩"
type: "tech"
topics: [aws, bedrock, strandsagents, aiagent, python]
published: false
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

現在進行形でTONaRiというパーソナルAIエージェントを個人開発しています。Strands Agents + Amazon Bedrock AgentCoreで構築しており、フロントエンドにはAITuberKitを使用したVRM制御を行っています。
（Tonari画像）

パーソナルAIエージェントとして日常的な作業をサポートしてもらうため、様々なツールを作っては直接繋げていたのですが、気づけばエージェント呼び出し時の入力トークンが爆増していてコストがだいぶキツくなっていました。
（月額予想画像）

というわけでこの記事では、ツールの増加による入力トークン爆増の問題と、サブエージェントへの切り出しでなんとか抑えようとしている話をしたいと思います。


# アーキテクチャ概要

まずTONaRi（パーソナルAIエージェント）の全体構成を簡単に紹介します。

```
Frontend (Next.js + VRM 3Dアバター)
  → Next.js API Route
    → AgentCore Runtime（Strands Agent）
      → AgentCore Gateway → Lambda関数（各種ツール）
```

エージェント本体はBedrock AgentCore Runtimeにデプロイされたコンテナとして動作し、外部ツールはAgentCore Gatewayを経由してLambda関数として実装しています。
ツールの追加は、Lambda関数を書いてGatewayにターゲットとして登録するだけです。AgentCore Gatewayはこの手軽さが便利ですね。


# いろんなツールを繋いでみた

AgentCore Gatewayを使うと、Lambda関数をエージェントのツールとして公開できます。GatewayはMCPプロトコルに準拠しており、エージェント側ではGatewayにMCPクライアントで接続するだけで、登録されたすべてのツールが使えるようになります。

```python: agentcore/src/agent/tonari_agent.py
from strands.tools.mcp import MCPClient
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

def create_mcp_client(gateway_url: str, region: str) -> MCPClient:
    def create_transport():
        return aws_iam_streamablehttp_client(
            endpoint=gateway_url,
            aws_region=region,
            aws_service="bedrock-agentcore",
        )
    return MCPClient(create_transport)
```

で、今回追加したツールが以下となります。

| ドメイン | ツール | 個数 |
|---------|--------|------|
| タスク管理 | list_tasks, add_task, complete_task, update_task | 4 |
| カレンダー | list_events, check_availability, create_event, update_event, delete_event, suggest_schedule | 6 |
| Gmail | search_emails, get_email, create_draft, archive_email | 4 |
| Notion | search_pages, get_page, create_page, update_page, query_database, get_database | 6 |
| Twitter | get_todays_tweets, post_tweet | 2 |
| 日記 | save_diary, get_diaries | 2 |
| 日付計算 | get_current_datetime, calculate_date, list_dates_in_range | 3 |
| Web検索 | TavilySearchPost | 1 |
| **合計** | | **28** |

各ツールには単発で呼び出すことももちろん可能ですし、
例えば「Webでレシピ検索してブックマークに保存して買い物メモ作って、タスクに買い物を追加して」という指示をすると、
1. Web検索ツールでレシピを検索
2. NotionのブックマークページにURLを保存
3. レシピの内容から買い物リストを作成してNotionのメモページに保存
4. 買い物タスクをTONaRi自身のタスクリストに追加
の一連の作業をやってくれます。

AIエージェントがツールの間に介在し、ユーザーからの雑なリクエストを解釈して各ツールの橋渡しをしてくれるというのが現在日常的にAIエージェントを使っていて一番便利に感じている点です。


# 入力トークンが爆増していた

しかし、便利になっていくAIエージェントの裏では着実にコストが積み重なっていました。

## なぜツールを増やすとトークンが増えるのか

LLMのAPIを呼び出す際、入力として送られるものは大きく分けて以下の4つです。

1. **システムプロンプト**: エージェントのキャラクター設定、行動ルール
2. **ツール定義**: 全ツールの名前、説明文、パラメータのJSONスキーマ
3. **長期記憶（LTM）**: 過去の会話から抽出されたエピソードや事実情報
4. **会話履歴（STM）**: 現在のセッションの内容

ポイントは**2のツール定義**です。エージェントがどのツールを使うかを判断するために、**登録されているすべてのツールの名前、説明文、パラメータのJSONスキーマが毎回の呼び出しで送信されます**。パラメータが多いツールほどスキーマが大きくなり、トークン消費も増えます。

例えばカレンダーの`suggest_schedule`ツールだけでも、5つのパラメータそれぞれに型と説明文が付いたJSONスキーマが入力に含まれます。これが28ツール分となると、ツール定義だけで約5,000トークンに達します。

これは従来のREST APIとは根本的に異なります。REST APIでは100個のエンドポイントを定義しても、1回のリクエストのコストは変わりません。しかしLLMエージェントでは、ツールが増えるほど**毎回の呼び出しコストが直線的に増加**します。

## 実際の内訳を見てみる

28個のツールを抱えたモノリシックなエージェントの1回あたりの入力トークン内訳を概算してみます。

| 項目 | 推定トークン数 |
|------|-------------|
| システムプロンプト（キャラ設定 + 全ドメインの行動ルール） | ~3,500 |
| ツール定義（28ツール × スキーマ） | ~5,000 |
| LTM検索結果 | ~1,500 |
| 会話履歴（10ターン分） | 可変（~5,000〜30,000） |
| **固定コスト合計**（プロンプト + ツール + LTM） | **~10,000** |

ここで注目すべきは**固定コスト**です。会話履歴は会話の進行で変動しますが、システムプロンプトとツール定義は**ユーザーが何を話しかけようが、毎回必ず送信されます**。「今日の天気は？」という雑談でも、Notionの6つのツール定義やカレンダーの6つのツール定義がまるごと送られるのです。

自分のエージェントは1日に約80回呼び出されるので、月間の固定コストだけでも：

```
10,000 tokens × 80 calls/day × 30 days = 24,000,000 tokens/month
```

Claude Haiku 4.5のBedrock入力トークン単価（$1.00/1M tokens）で計算すると、**固定コストだけで月 ~$24** です。個人開発で毎月3,000円以上が「使いもしないツール定義の送信」に消えていると思うと、さすがに対策が必要でした。


# サブエージェントに切り出す

## 考え方

解決策は「必要なときだけ、必要なツールを読み込む」ことです。

具体的には、ドメインごとに**サブエージェント**を作成し、メインエージェントからは`@tool`としてサブエージェントを呼び出す設計にします。

```
【Before: モノリシック】
メインエージェント
├── システムプロンプト（全ドメインのルール）
└── 28個のツール ← 毎回全部送信

【After: サブエージェント分割】
メインエージェント
├── システムプロンプト（汎用ルールのみ）
├── DateTool（3ツール）      ← 頻出なのでメインに残す
├── TavilySearch（1ツール）  ← 同上
├── task_agent      ← @toolとして定義（中身は4ツール）
├── calendar_agent  ← @toolとして定義（中身は6ツール）
├── gmail_agent     ← @toolとして定義（中身は4ツール）
├── notion_agent    ← @toolとして定義（中身は6ツール）
├── briefing_agent  ← @toolとして定義（中身は複数ドメインのツール）
├── diary_agent     ← @toolとして定義（中身は2ツール）
├── intro_agent     ← @toolとして定義（ツールなし）
└── twitter_agent   ← @toolとして定義（中身は2ツール）
```

メインエージェントから見ると、`task_agent`は「タスク管理をやってくれるツール」で、引数はリクエスト文字列1つだけ。28個あったツール定義が12個（DateTool 3つ + TavilySearch 1つ + サブエージェント8つ）に減り、各サブエージェントのドメイン固有ツール定義は**そのサブエージェントが呼ばれたときだけ**読み込まれます。


## ツールの自動振り分け

AgentCore Gateway経由のツールにはGateway Target名がプレフィックスとして付いています（例: `calendar-tool___list_events`）。このプレフィックスを使って、ツールを自動的にサブエージェント用とメイン用に振り分けます。

```python: agentcore/src/agent/sub_agents.py
# プレフィックス → サブエージェントバケットのマッピング
SUB_AGENT_PREFIXES = {
    "task-tool": "task",
    "calendar-tool": "calendar",
    "gmail-tool": "gmail",
    "notion-tool": "notion",
    "twitter-read": "twitter",
    "twitter-write": "twitter",
    "diary-tool": "diary",
}

def split_mcp_tools(all_tools: list) -> dict[str, list]:
    """Gateway経由のツールをプレフィックスでサブエージェント用とメイン用に分割する"""
    result = {
        "main": [], "task": [], "calendar": [],
        "gmail": [], "notion": [], "twitter": [], "diary": [],
    }

    for t in all_tools:
        name = t.tool_name
        prefix = name.split("___")[0] if "___" in name else ""
        bucket = SUB_AGENT_PREFIXES.get(prefix)
        if bucket:
            result[bucket].append(t)
        else:
            result["main"].append(t)

    return result
```

マッピングに該当しないツール（DateTool、TavilySearchなど）は自動的に`main`バケットに入ります。


## サブエージェントの実装

Strands Agentsの`@tool`デコレータを使えば、サブエージェントをメインエージェントのツールとして定義できます。

```python: agentcore/src/agent/sub_agents.py
from strands import Agent, tool
from strands.models import BedrockModel

# サブエージェント用ツール（起動時にsplit_mcp_toolsの結果をセット）
_calendar_tools: list = []

@tool
def calendar_agent(request: str) -> str:
    """Googleカレンダーのサブエージェント。予定の一覧取得、空き確認、作成、更新、削除を行う。

    Args:
        request: オーナーのカレンダーに関するリクエスト
    """
    try:
        agent = Agent(
            model=BedrockModel(
                model_id="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
                region_name="ap-northeast-1",
                streaming=True,
            ),
            system_prompt="あなたはGoogleカレンダーの専門アシスタントです。...",
            tools=_calendar_tools,  # カレンダー系ツールのみ
            callback_handler=None,
        )
        result = agent(request)
        return str(result)
    except Exception as e:
        return f"カレンダー操作でエラーが発生しました: {e}"
```

`@tool`デコレータの中で新しいStrands Agentを作り、ドメイン固有のツールだけを渡しています。メインエージェントから見ると`calendar_agent(request="今日の予定を教えて")`のように、引数1つのシンプルなツールとして見えます。

同じパターンで`task_agent`、`gmail_agent`、`notion_agent`、`twitter_agent`、`diary_agent`、`briefing_agent`、`intro_agent`を作成しました。`briefing_agent`はカレンダー・Gmail・タスクのツールを横断的に使う特殊なサブエージェントで、`intro_agent`はツールを持たず自己紹介文の生成のみを行います。


## メインエージェントの変更

起動時にGateway経由のツールを振り分け、メインエージェントにはメイン用ツール + サブエージェントを渡します。

```python: agentcore/app.py
from src.agent.sub_agents import (
    split_mcp_tools, init_sub_agent_tools,
    task_agent, calendar_agent, gmail_agent, notion_agent,
    briefing_agent, diary_agent, intro_agent, twitter_agent,
)

# AgentCore Gatewayからツールを取得して振り分け
mcp_client.start()
all_tools = mcp_client.list_tools_sync()
tool_map = split_mcp_tools(all_tools)
init_sub_agent_tools(tool_map, actor_id=actor_id)

# メインエージェントにはメイン用ツール + サブエージェントを渡す
main_tools = tool_map["main"] + [
    task_agent, calendar_agent, gmail_agent, notion_agent,
    briefing_agent, diary_agent, intro_agent, twitter_agent,
]

agent = create_tonari_agent(
    session_id=session_id,
    actor_id=actor_id,
    mcp_tools=main_tools,
)
```


## システムプロンプトの圧縮

サブエージェントに切り出したドメインの行動ルールは、メインのシステムプロンプトから削除してサブエージェント側に移動しました。

**Before**: メインプロンプトにすべてのドメインルールを記載
```
- カレンダー操作時のルール（重複確認、削除前確認、etc.）
- Gmail操作時のルール（下書きのみ、日付検索の注意点、etc.）
- Notion操作時のルール（プロパティ形式、データベースマッピング、etc.）
- ブリーフィング手順（5セクション分の詳細手順）
- 日記作成手順（ヒアリング → 生成 → 保存のフロー）
- ...
```

**After**: メインプロンプトにはサブエージェントの一覧と委任ルールだけ
```
## サブエージェント連携
- task_agent: タスク管理（一覧取得、追加、完了、更新）
- calendar_agent: Googleカレンダー（予定の取得、作成、更新、削除）
- gmail_agent: Gmail（メール検索、取得、下書き作成）
- ...

### 委任のルール
- サブエージェントへのリクエストは具体的に記述する
- サブエージェントの結果はそのまま伝えず、自分の言葉で言い換える
```

これでシステムプロンプトは約7,400文字 → 約3,800文字に**48%削減**できました。


# 実装時のハマりどころ

## サブエージェントが「今日」を知らない

デプロイして動作確認したところ、日記のサブエージェントに「昨日の日記を見せて」と頼んだら「2026年3月5日はまだ先の日付です」と返ってきました。

原因は単純で、メインエージェントはユーザーメッセージのタイムスタンプから現在日時を把握していますが、サブエージェントにはその情報が渡っていませんでした。LLMのトレーニングデータのカットオフ日時を「今日」だと認識してしまっていたのです。

対策として、日付が関わるサブエージェントのシステムプロンプトに現在日時を動的に注入するようにしました。

```python: agentcore/src/agent/sub_agents.py
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))

def _current_datetime_str() -> str:
    return datetime.now(JST).strftime("%Y年%m月%d日 %H:%M")

@tool
def calendar_agent(request: str) -> str:
    """..."""
    prompt = f"現在日時: {_current_datetime_str()}（JST）\n\n{CALENDAR_AGENT_PROMPT}"
    agent = Agent(
        model=_create_sub_agent_model(),
        system_prompt=prompt,
        tools=_calendar_tools,
        callback_handler=None,
    )
    # ...
```

小さなことですが、見落としやすいポイントです。メインエージェントでは当たり前に使えていた文脈情報が、サブエージェントでは別のLLM呼び出しになるため引き継がれません。

## ツールの排他的割り当て

Twitter系ツール（`get_todays_tweets`、`post_tweet`）とDiary系ツール（`save_diary`、`get_diaries`）は、メインエージェントが直接使うことはなくサブエージェント経由でしか使いません。そのためメインエージェントのツールリストからは完全に除外し、サブエージェント専用にしました。

一方、DateToolとTavilySearchはメインエージェントが直接使う場面もあるため、メインに残しています。どのツールをメインに残し、どのツールをサブエージェント専用にするかは、実際の利用パターンを見て判断するのがよいと思います。


# コスト削減効果

## Before / After 比較

まず、メインエージェントの1回あたりの固定入力コストを比較します。

| 項目 | Before（モノリシック） | After（サブエージェント分割） |
|------|---------------------|--------------------------|
| システムプロンプト | ~3,500 tokens | ~2,000 tokens |
| ツール定義 | 28ツール（~5,000 tokens） | 12ツール（~2,500 tokens） |
| **固定コスト合計** | **~10,000 tokens** | **~6,000 tokens** |
| 固定コスト削減率 | — | **-40%** |

ここで注意すべきは、**サブエージェントが呼ばれたときの追加コスト**です。サブエージェントも内部でLLMを呼び出すため、そのLLM呼び出しにもシステムプロンプトとツール定義が入力されます。つまり、ツール定義のコストはメインから消えたのではなく、**サブエージェント側に移動した**形です。

ではサブエージェント側の入力コストを見てみます。

| サブエージェント | プロンプト | ツール定義 | リクエスト | **合計** |
|----------------|-----------|-----------|-----------|---------|
| task_agent | ~400 | 4ツール（~400） | ~100 | **~900** |
| calendar_agent | ~400 | 6ツール（~850） | ~100 | **~1,350** |
| gmail_agent | ~400 | 4ツール（~400） | ~100 | **~900** |
| notion_agent | ~400 | 6ツール（~700） | ~100 | **~1,200** |
| briefing_agent | ~500 | 複数ドメイン（~2,500） | ~100 | **~3,100** |
| diary_agent | ~400 | 2ツール（~200） | ~100 | **~700** |
| intro_agent | ~400 | なし | ~100 | **~500** |
| twitter_agent | ~400 | 2ツール（~150） | ~100 | **~650** |

`briefing_agent`はカレンダー・Gmail・タスクのツールを横断的にロードするため突出してコストが高いですが、1日1回のブリーフィング時にしか呼ばれないため月間への影響は限定的です。`intro_agent`はツールを持たないため最小コストです。CalendarやNotionはスキーマが複雑な分、呼び出し時のコストが大きくなります。`briefing_agent`を除くと、平均1回あたり約900 tokensです。

**ポイントは「毎回 vs 必要なときだけ」の違い**です。モノリシック構成では28ツール分の定義が全呼び出しに含まれますが、サブエージェント構成ではドメイン固有のツール定義はそのサブエージェントが呼ばれたときだけ発生します。

## 月間コストへの影響

1日約80回の呼び出しで計算します。

```
【メインエージェントの固定コスト削減（毎回発生）】
  4,000 tokens/call × 80 calls/day × 30 days = 9,600,000 tokens/month

【サブエージェント呼び出しの追加コスト（呼ばれた時だけ発生）】
  呼び出しの約60%（48回/日）でサブエージェントが1回起動すると仮定
  平均 900 tokens/call × 48 calls/day × 30 days = 1,296,000 tokens/month
  ※briefing_agent（~3,100 tokens）は1日1回のみのため平均から除外し別計上
  briefing: 3,100 tokens × 30 days = 93,000 tokens/month

【差し引き】
  9,600,000 - 1,296,000 - 93,000 = 8,211,000 tokens/month
```

Claude Haiku 4.5のBedrock入力トークン単価（$1.00/1M tokens）で計算すると：

**月間 約$8（約1,200円）の入力トークン削減**

「たかが1,200円」と思うかもしれませんが、これは入力トークンの固定コスト部分だけの話です。さらに重要なのは**スケーラビリティ**です。今後ツールを50個、100個と追加していった場合、モノリシック構成ではコストが線形に増加しますが、サブエージェントパターンならメインエージェントのコストはほぼ一定のまま新しいドメインを追加できます。

## 他の施策との組み合わせ

実際にはサブエージェント分割と並行して、他の入力トークン削減施策も実施しました。参考までに一覧を紹介します。

| 施策 | 内容 | 推定月間削減 |
|------|------|------------|
| **サブエージェント分割**（本記事） | ツール28→12個、プロンプト圧縮 | ~$8 |
| 会話ウィンドウ縮小 | `SlidingWindowConversationManager`の`window_size`を15→10に | ~$3-5 |
| LTM検索結果の削減 | 各Namespaceの`top_k`を引き下げ（合計18→10件） | ~$2-3 |
| パイプライン軽量エージェント | 自動ツイート・ニュース収集を最小プロンプト+フィルタ済みツールで実行 | ~$2-3 |
| **全施策合計** | | **~$15-19（約2,300〜2,900円）** |

サブエージェント分割が最も効果が大きいですが、会話ウィンドウやLTMの`top_k`はコード1行の変更で効果が出るので、まずそちらから試すのもよいと思います。ただし精度とのトレードオフがあるため、削りすぎには注意が必要です。

## コスト以外のメリット

サブエージェント分割にはコスト削減以外にもメリットがありました。

- **関心の分離**: 各ドメインのプロンプトとツールが独立し、個別にチューニングできる
- **LLMの判断精度の向上**: メインエージェントは28個のツールから選ぶ代わりに12個から選べばよく、ツール選択の精度が上がった
- **拡張性**: 新ドメインの追加がサブエージェント1つ追加するだけで完結する


# おしまい

ということで、LLMエージェントにツールを追加しすぎた結果、入力トークンが爆増した問題をサブエージェント分割で解決した話でした。

振り返ると、従来のソフトウェアアーキテクチャで言うところの「モノリスからマイクロサービスへ」と似た流れを、エージェント開発でも経験したのが面白かったです。ただしLLMエージェントの場合は「エンドポイントの数がそのままコストに直結する」という、従来とは違う制約が動機になっている点が独特でした。

Strands Agentsの`@tool`デコレータでサブエージェントを簡単にツール化できるのは非常に便利です。同じようにツールが増えてきたエージェントを運用している方の参考になれば幸いです。
