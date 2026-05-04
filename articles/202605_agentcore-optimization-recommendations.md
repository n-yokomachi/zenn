---
title: "Bedrock AgentCore Optimizationでマルチエージェントのプロンプトを改善・検証してみる"
emoji: "🔬"
type: "tech"
topics: [aws, bedrock, agentcore, strandsagents, aiagent]
published: true
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

2026年4月、Amazon Bedrock AgentCoreに「Optimization」という機能が追加されました。
エージェントの実トレースを入力に、プロンプトなどを改善する仕組みが提供されています。
https://aws.amazon.com/jp/about-aws/whats-new/2026/05/bedrock-agentcore-optimization-preview/

この記事では、Strands AgentsのAgents-as-Toolsパターン（メインエージェントがサブエージェントを`@tool`として束ねる構成）にAgentCore Optimizationを当ててみて、何が起こるかを検証した結果をまとめます。Recommendationsがどんな改善案を出してくるのか、A/Bテストで実トラフィックでの効果はどう出るのか、そして運用に入れるときの所感あたりをまとめています。

# AgentCore Optimizationの中身

まずはOptimizationの中身を整理します。

## 3つの機能

| 機能 | 役割 |
|---|---|
| Recommendations | 実際のトレースログと改善目標とするEvaluatorの指定を入力に、AIがシステムプロンプトやツール説明文の改善案を生成する。手動で試行錯誤する代わりに、AIに改善版を提案させる仕組み |
| Configuration bundles | システムプロンプトやツール説明文などを、ソースコードの外に切り出してAgentCore側でバージョン管理する仕組み。コードを書き換え・再デプロイしなくても、保管した値を差し替えるだけでエージェントの動きを変えられる。後述するA/Bテストで2つの設定を同時運用するときにも使う |
| A/Bテスト | 実際のトラフィックをAgentCore Gateway経由で2つのバリアント（control / treatment）に振り分け、それぞれの結果をEvaluatorでスコアリング。どちらのプロンプトが本番で効くかを統計的に比較できる |

公式ドキュメントではこの3つを「continuous improvement loop（連続改善ループ）」として説明しています。Recommendationsが改善案を生成する→Configuration bundlesでバージョン管理する→A/Bテストで実トラフィックでの効果を検証する、という流れで一周回す想定の機能群です。

## 事前準備

公式ドキュメントに沿って以下の準備をします

- Strands Agentsで作成したエージェント
- AgentCore Runtimeにデプロイ済み + Observabilityが有効化されていること
- CloudWatch Transaction Searchが有効化されていること


# 検証環境の構築

検証用に、天気とニュースをそれぞれ専門のサブエージェントに分割し、Agents-as-Toolsパターンで束ねたマルチエージェント構成のエージェントをStrands Agentsで作りました。

リポジトリは以下です
https://github.com/n-yokomachi/agentcore-optimization-lab


## Configuration bundleの構造

A/Bテストに乗せるためには、プロンプトやツール説明文をagentcore.json内の`configBundles`で外部化する必要があります。今回採用したBundle構造はこんな形です。
なお、プロンプトはRecommendationの結果がわかりやすいようにかなり雑に書いています。

```json: agentcore.json（configBundlesセクション）
{
  "components": {
    "{{runtime:agentsAsToolsLab}}": {
      "configuration": {
        "systemPrompt": "You are an assistant that answers questions about weather and news.",
        "weather_agent": "Get weather",
        "news_agent": "Get news"
      }
    }
  }
}
```

`{{runtime:agentsAsToolsLab}}`はagentcore CLIのプレースホルダーで、deploy時に実Runtime ARNに解決されるようです。

なお、ツール説明文（`weather_agent` / `news_agent`）は`configuration`直下に並列で置く形にしています。これはRecommendations APIがツール説明文のpathを解決する都合に合わせた構造です。AgentCore CLIが`--with-config-bundle`で自動生成するデフォルトの構造（`toolDescriptions`の下にネストする形）のままだとtool description Recommendationのpath解決がうまく動かず、この形式にしたところ動作が確認できたためこんな形になっています

Bundle定義の追加とデプロイはAgentCore CLIで行います。

```bash: BundleをAgentCoreに登録
agentcore add config-bundle
agentcore deploy
```

## bundle integrationを前提にしたエージェント実装

Bundleの値をRuntimeに動的注入するには、Strandsのhook機構を使います。`ConfigBundleHook`クラスで、`BeforeInvocationEvent`でメインエージェントのシステムプロンプトを、`BeforeToolCallEvent`で各ツール説明文をBundleから動的に上書きしています。

```python: app/agentsAsToolsLab/main.py（抜粋）
class ConfigBundleHook(HookProvider):
    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeInvocationEvent, self._inject_system_prompt)
        registry.add_callback(BeforeToolCallEvent, self._override_tool_description)

    def _inject_system_prompt(self, event: BeforeInvocationEvent) -> None:
        config = BedrockAgentCoreContext.get_config_bundle()
        event.agent.system_prompt = config.get("systemPrompt", DEFAULT_SYSTEM_PROMPT)

    def _override_tool_description(self, event: BeforeToolCallEvent) -> None:
        config = BedrockAgentCoreContext.get_config_bundle()
        override = config.get(event.tool_use["name"])
        if override and event.selected_tool:
            spec = event.selected_tool.tool_spec
            if spec and "description" in spec:
                spec["description"] = override
```

このHookクラスはAgentCore CLIが`--with-config-bundle`で自動生成するテンプレートをベースにしています。Bundle構造をフラットにした関係で、ツール説明文のlookup部分（`config.get(event.tool_use["name"])`）だけ簡略化しています。


# Recommendations, A/B Test検証

検証用に英語クエリ8種類を5回 = 40セッション分の会話を流してトレースログを貯めたあと、両エージェントに対してsystem-prompt / tool-descriptionそれぞれのRecommendationを実行しました。

```bash: Recommendationの実行
agentcore run recommendation --type system-prompt
agentcore run recommendation --type tool-description
```

## Recommendations(system-prompt)検証

元のシステムプロンプトとRecommendationsが出したプロンプトはAWSコンソール上で確認できます。
「call both tools in parallel」「use news_agent to find related news」のようにツールの呼び出しも考慮したプロンプトに改善されています

![](/images/202605_agentcore-optimization-recommendations/image1.png)


## Recommendations(tool-description)検証

ツール説明に関しての元とRecommendationsの結果も同様に確認できます。
説明の充実化とともに、「Often used alongside news_agent」「Often used alongside weather_agent」のように他のサブエージェントとの並列呼び出しの可能性が書かれています。

![](/images/202605_agentcore-optimization-recommendations/image2.png)


## A/Bテストでの効果実証

Recommendationsで得られた改善結果を検証するためA/Bテストも実施します。

- コントロールバリアント（C）: 人間版のプロンプトとツール説明文が入ったBundle version
- トリートメントバリアント（T1）: Recommendationsの出力を反映したBundle version
- トラフィック分割: 50/50（セッションIDベースのスティッキー割り当て）
- オンラインEvaluator: `Builtin.GoalSuccessRate`
- トラフィック量: 8クエリ × 5回 = 40セッション

A/Bテストを動かすにはHTTP GatewayとOnline evaluation configの追加が必要です。HTTP Gatewayはagentcore.jsonの`httpGateways`に手動で書く必要があります（現時点でCLIのaddサブコマンドが見当たらないため）。Online evaluation configは`agentcore add online-eval`で追加できます。

```json: agentcore.json（httpGatewaysセクション）
"httpGateways": [
  {
    "name": "agentsAsToolsLabGateway",
    "runtimeRef": "agentsAsToolsLab"
  }
]
```

```bash: Online evaluation configの追加
agentcore add online-eval
```

その後、A/Bテスト自体を追加してdeployで一括登録します。

```bash: A/Bテストの作成と起動
agentcore add ab-test
agentcore deploy
```

トラフィック生成はAgentCore GatewayのURLにSigV4でPOSTする形になります。
`agentcore invoke`はRuntimeを直接叩くので、A/BテストのためにはGateway URLを経由する必要があります。
以下はA/Bテストのために流したスクリプトになります。

```python: traffic_gen.py（抜粋）
GATEWAY_URL = "https://agentsastoolslabgateway-XXXXX.gateway.bedrock-agentcore.us-west-2.amazonaws.com/agentsAsToolsLab/invocations"
credentials = Session().get_credentials()

def invoke_one(query: str):
    sid = str(uuid.uuid4())
    payload = json.dumps({"prompt": query}).encode()
    req = AWSRequest(method="POST", url=GATEWAY_URL, data=payload, headers={
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": sid,
    })
    SigV4Auth(credentials, "bedrock-agentcore", "us-west-2").add_auth(req)
    http_req = urllib.request.Request(GATEWAY_URL, data=payload, headers=dict(req.headers), method="POST")
    with urllib.request.urlopen(http_req, timeout=180) as resp:
        return sid, resp.status
```

A/Bテストの結果はAWSコンソールの「Bedrock AgentCore > Optimizations > A/B Tests」から確認できます。

結果がこちら。

| 指標 | 値 | 意味 |
|---|---|---|
| Sessions routed to control | 21 | コントロールバリアントに振り分けられたセッション数 |
| Sessions routed to variant | 19 | トリートメントバリアントに振り分けられたセッション数 |
| Control average (Goal Success Rate) | 0.48 | コントロールバリアントでの目標達成率の平均 |
| Variant average | 0.53 | トリートメントバリアントでの目標達成率の平均 |
| Variant improvement | Not significant: +10.5% (p=0.95) | トリートメントはコントロールに対して+10.5%の改善だが統計的に有意ではない（p>0.05） |

![](/images/202605_agentcore-optimization-recommendations/image3.png)

方向性としてはトリートメントが絶対値で+5pt（=相対+10.5%）の優位、つまりRecommendationsの改善は方向としては効いているのですが、40セッションではサンプル不足で統計的な有意性は確認できませんでした。本来の目的であるRecommendationsの機能確認自体は無事に済んだことですし、これ以上は私のお財布に響くので検証としては中断します。


# Recommendationsとの分業ライン
あくまで今回の検証結果からですが、Recommendationsが出した改善パターンを整理すると、Recommendationsに任せていい部分と開発者が書くべき部分とで以下のように分けられるのではないかと思います。

| アクター | 担当領域 |
| ---- | ---- |
| Recommendations | 並列呼び出しの言及、要素名の明示、多言語サポート言及、応答形式の指示、セーフティ機構、積極性指示 |
| 開発者 | ドメイン文脈、ビジネスロジック、データ解釈方針 |

つまりRecommendationsを運用に入れるとき、人間が書く必要があるのは以下であり、

- ドメイン特有の文脈（特定の顧客の業務プロセス、外部APIの仕様など）
- ビジネスロジック（出力制約、コンプライアンス、料金計算ルールなど）
- データ解釈方針（このフィールドが空のときはこう扱う、など）

上記以外の「プロンプトの書き方として推奨される汎用パターン」はRecommendationsに任せても良いかも、というのが今回の検証から得られた結論です。

# おしまい

ということで、AgentCore OptimizationをAgents-as-Tools構成に当ててみた話でした。今回の検証の収穫として、

- Recommendationsは並列呼び出し、派生トピック処理、応答形式、セーフティ機構などの汎用パターンを抽出してくれる
- 人間が書くべき領域（ドメイン文脈・ビジネスロジック）とRecommendationsに任せる領域の境界が見えた
- A/Bテストの機能や出力は確認できたが、今回の検証レベルだとサンプル不足

以上です。Optimizationを触ってみたい人の参考になれば幸いです。


# おまけ : 日本語のシステムプロンプトがプロンプトインジェクションとして誤判定される？

システムプロンプトのRecommendationを`--inline "あなたは天気とニュースに答えるアシスタント。"`のような日本語プロンプトで実行すると、以下のエラーが返りました。

```
[ValidationException] The provided content was detected as unsafe by 
prompt attack protection. Please review your system prompt and try again.
```

切り分けてみたところ、

- Evaluator（`Builtin.GoalSuccessRate` / `Builtin.Helpfulness`）の違いに依らずfail
- Bundle経由 / inline modeどちらでもfail
- 日本語プロンプトの表現を変えてもfail
- 英語プロンプトにすると通る

という結果でした。
ちなみにツール説明文のRecommendationのほうは日本語でも通ります。

というわけで本記事の検証は最終的にすべて英語プロンプトで実施しています。


# 参考

https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html
https://github.com/aws/agentcore-cli
https://aws.amazon.com/jp/about-aws/whats-new/2026/05/bedrock-agentcore-optimization-preview/
