---
title: "A2Aのチュートリアルを解説しつつ完走してみる"
emoji: "🤝"
type: "tech"
topics: [a2a,ai,mcp,aiagent,]
published: true
---

今回はAIエージェント間の通信・連携を補完するためのオープンプロトコルであるA2A（Agent2Agent）の公式チュートリアルを試しながら、その概要を理解していきます。


# A2Aとは？

A2Aは米国時間2025年4月9日にGoogleから発表されたオープンプロトコルです。
複数のAIエージェント間の連携を定義し、クライアントエージェントがタスクの作成と伝達を、リモートエージェントがそのタスクの実行や情報提供を行うことで、最終的なアーティファクトを生成することを目的としています。

https://a2a-protocol.org/latest/

今年話題のMCP（Model Context Protocol）とは性質が違うものであり、どちらかがどちらかを代替するということはなく、むしろ互いに補完しあうものです。
具体的には、ユーザーから与えられたタスクの実行はA2Aによるマルチエージェントで実行しつつ、それらのエージェントが外部システムやデータと連携を行う際にはMCPを利用してアクセスする、みたいにレイヤーや役割が分かれています。

![](https://storage.googleapis.com/zenn-user-upload/bb8b21b466ec-20250601.png)
*上記のA2A概要リンクから引用*

あとMCPについては自分も記事を書いているので良ければそちらもご覧ください

https://zenn.dev/yokomachi/articles/20250318_tutorial_mcp


# チュートリアルを試してみる

理解のためには手を動かすのが手っ取り早い、ということでやっていきます。  
GoogleからA2A SDKが公開されており、PythonのTutorialもあるのでそれをやってみます。  
Tutorialで使用するサンプルコードは以下のリポジトリを参照ください。

https://github.com/google-a2a/a2a-samples

なお、今回実施するTutorialの内容は2025/6/1時点のものです。  
結構頻繁に内容が変わっているようなので、適宜読み替えていただければと思います。

## Setup

まずは環境構築を行います。
Pythonのバージョンは3.13以上が推奨されています。

```
>python --version
Python 3.13.3

>git clone https://github.com/google-a2a/a2a-samples.git -b main --depth 1
>cd a2a-samples

>python -m venv .venv
>.venv\Scripts\activate
```

で、いきなりですがそのままでは動かないところが…
requirements.txtからインストールを促されますが、実際のtxtはsamples/python内にあります。
また、内容がlatestで書かれているので、以下の内容に書き換えて実行します。

``` text: samples/python/requirements.txt
a2a-sdk>=0.2.4
uvicorn>=0.34.0
```

```
>cd samples/python
>pip install -r requirements.txt
```

で、A2A SDKのインポート確認をしろとあるので下記を実行します。

```
python -c "import a2a; print('A2A SDK imported successfully')"
```

## Agent Skills & Agent Card

A2Aにおいては各エージェントが何をできるか（スキル）、そしてほかのエージェントやクライアントがそのスキルを知る方法（カード）を定義する必要があります。
エージェントを人間とすると、

- スキル：所属や役職
- カード：役職（スキル）やメールアドレス（エンドポイント）を書いた名刺

ですね。

サンプルコード（samples/python/agents/helloworld）には以下のように定義されています。

### エージェントスキル

``` python: __main__.py
skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='just returns hello world',
        tags=['hello world'],
        examples=['hi', 'hello world'],
        # inputModes/outputModesとして入出力でサポートするMIMEタイプの指定も可
        #（ex.text/plain, application/json, etc.）
    )
```

### エージェントカード

``` python: __main__.py
public_agent_card = AgentCard(
        name='Hello World Agent',
        description='Just a hello world agent',
        url='http://localhost:9999/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],     # エージェントスキルを記述
        supportsAuthenticatedExtendedCard=True,
    )
```

## The Agent Executor

A2Aに準拠したリクエスト/レスポンスと、実際のエージェントのロジックの橋渡しを行うのがAgentExecutorです。  
エージェントを人間とすると、AgentExecutorは外部とのやり取りを行うPC（またはメーラーとかチャットツール）、みたいな感じでしょうか。  

AgentExecutorインターフェースクラスを継承して実装します。
AgentExecutorでは主要なメソッドとして以下を提供しています。

    - async def execute(self, context: RequestContext, event_queue: EventQueue): 
        - レスポンスまたはイベントストリームを期待する受信リクエストを処理する。
        - 入力(context)を処理し、event_queueを使用してMessage,Task,TaskStatusUpdateEvent,TaskArtifactUpdateEventのいずれかを返す。
    - async def cancel(self, context: RequestContext, event_queue: EventQueue): 
        - 進行中のタスクをキャンセルする要求を処理する。

サンプルコード（samples/python/agents/helloworld）では以下のように記述されています。

``` python: agent_executor.py
# これが実行対象のエージェント。実際のビジネスロジックを実装するところ
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        return 'Hello World'
```

``` python: agent_executor.py
# これがAgentExecutorのインターフェースを実装するところ
class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    # executeメソッドでリクエストとレスポンスを処理
    # message/send または message/streamリクエストが入ってきた場合発火する
    # ここではHelloWorldAgentを実行し、結果をevent_queueにキューイングして返す
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        event_queue.enqueue_event(new_agent_text_message(result))

    # cancelメソッドでキャンセルリクエストを処理
    # ここでは単に「キャンセルリクエストはサポートされてませんよ」例外を出しているだけ
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
```


## Starting the Server
エージェントのローカルサーバを立てる前に、HelloWorldエージェントが実装しているサーバの内容を確認します。

### DefaultRequestHandler

``` python: __main__.py
request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
```
DefaultRequestHandlerハンドラはAgentExecutorとTaskStoreでインスタンス化する。
受信したA2A RPCコールを、AgentExecutorの適切なメソッド（executeやcancelなど）にルーティングする。
また、TaskStoreによりタスクのライフサイクル（インタラクション、ストリーミング、再サブスクリプションなど）を管理する。

### A2AStarletteApplication

``` python: __main__.py
server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=specific_extended_agent_card,
    )
```
A2AStarletteApplicationクラスは、agent_cardとrequest_handler（上でインスタンス化したハンドラ） でインスタンス化する。
agent_cardの内容はサーバが/.well-known/agent.jsonエンドポイントで公開する。
また、request_handlerに連携してA2Aメソッドのコールの処理を行う。
＊[Starlette](https://www.starlette.io/)はPython用の非同期ウェブ通信を構築するためのASGIフレームワーク

### uvicorn.run(server_app_builder.build(), ...)

``` python: __main__.py
uvicorn.run(server.build(), host='0.0.0.0', port=9999)
```
A2AStarletteApplicationでインスタンス化したサーバの実行部分。
＊[Uvicorn](https://www.uvicorn.org/)はASGI準拠のWebサーバ


ではローカルサーバを立ててみます。

```
# from the a2a-samples directory
>python samples/python/agents/helloworld/__main__.py
INFO:     Started server process [14868]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9999 (Press CTRL+C to quit)
```

## Interacting with the Server
それではテスト用のクライアントから先ほど立てたサーバエージェントにリクエストを送ってみます。
サンプルコードにはテスト用のクライアントのコードもあるのでそれを使っていきます。
まずはクライアントの中身を軽く見てみます。

``` python: test_client.py
# ここでサーバで公開されているエージェントカードをfetch
base_url = 'http://localhost:9999'

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

# (中略)

# 単一のテキストメッセージを送信し、レスポンスを受信
client = A2AClient(
    httpx_client=httpx_client, agent_card=final_agent_card_to_use
)
logger.info('A2AClient initialized.')

send_message_payload: dict[str, Any] = {
    'message': {
        'role': 'user',
        'parts': [
            {'kind': 'text', 'text': 'how much is 10 USD in INR?'}
        ],
        'messageId': uuid4().hex,
    },
}
request = SendMessageRequest(
    id=str(uuid4()), params=MessageSendParams(**send_message_payload)
)
response = await client.send_message(request)
print(response.model_dump(mode='json', exclude_none=True))

# (中略)

# 続けてストリーミングのメッセージも送信し、レスポンスを受信
streaming_request = SendStreamingMessageRequest(
    id=str(uuid4()), params=MessageSendParams(**send_message_payload)
)

stream_response = client.send_message_streaming(streaming_request)

async for chunk in stream_response:
    print(chunk.model_dump(mode='json', exclude_none=True))
```

では別ターミナルから同じく仮想環境を実行して、samples/python/agents/helloworld/test_client.pyを実行します。

```
# ほかのログは省略

INFO:httpx:HTTP Request: POST http://localhost:9999/ "HTTP/1.1 200 OK"
{'id': '2b5dd422-17a6-4e8f-afad-ba941967a6c6', 'jsonrpc': '2.0', 'result': {'kind': 'message', 'messageId': 'dcd8312a-de8d-41f0-b1b4-1d732ec06065', 'parts': [{'kind': 'text', 'text': 'Hello World'}], 'role': 'agent'}}

INFO:httpx:HTTP Request: POST http://localhost:9999/ "HTTP/1.1 200 OK"
{'id': '3250869d-b066-4deb-a1ea-aee56a6eeb4a', 'jsonrpc': '2.0', 'result': {'kind': 'message', 'messageId': '08fe3e84-4d28-44df-b5ee-24db2a4a4d9f', 'parts': [{'kind': 'text', 'text': 'Hello World'}], 'role': 'agent'}}
```

単一メッセージとストリーミングの2回送っているので、レスポンスも2回返ってきています。
（でも、あれ？　公式だとストリーミングのほうは"final":trueっていうフィールドがあるはずなんだけど…）

## Streaming & Multi-Turn Interactions (LangGraph Example)

A2Aの超基本の実装と動作は確認できたので、次はサンプルコードに含まれているLangGraphで構築されたエージェントを試してみます。
このエージェントは通貨の変換を行うもので、ReActパターンで実装されています。
処理フローは以下のグラフで表すことができます。

![](https://storage.googleapis.com/zenn-user-upload/aad59d1d1531-20250601.png)

まずはサンプルコードのsamples/python/agents/langgraphに移動し、依存関係をインストールします

```
cd samples/python/agents/langgraph
pip install -e .[dev]
```

また、GeminiのAPIキーを払い出し、langgraph/.envに記述します。

``` txt: .env
GOOGLE_API_KEY=YOUR_API_KEY
```

先ほど立ち上げたHelloWorldエージェントを停止し、新規にLangGraphのエージェントを含むサーバを立ち上げます
```
python __main__.py
```

続けてテスト用のクライアントを実行してみます。

```
python app/test_client.py
```

以下のようなレスポンスが返ってきました。
textフィールドを見ると処理の段階に応じて分割してメッセージが返っていることがわかります。

```
{'id': '425194e5-74d6-4dfc-8202-465b05cf6ffc', 'jsonrpc': '2.0', 'result': {'contextId': '0a6c011b-a938-4d3d-ac7d-b6ea71f7058b', 'final': False, 'kind': 'status-update', 'status': {'message': {'contextId': '0a6c011b-a938-4d3d-ac7d-b6ea71f7058b', 'kind': 'message', 'messageId': '1312118a-0e3b-42c5-a9ed-da4d71ace6be', 'parts': [{'kind': 'text', 'text': 'Looking up the exchange rates...'}], 'role': 'agent', 'taskId': '6041da17-ebd7-47d9-b492-edbc889e092b'}, 'state': 'working'}, 'taskId': '6041da17-ebd7-47d9-b492-edbc889e092b'}}
{'id': '425194e5-74d6-4dfc-8202-465b05cf6ffc', 'jsonrpc': '2.0', 'result': {'contextId': '0a6c011b-a938-4d3d-ac7d-b6ea71f7058b', 'final': False, 'kind': 'status-update', 'status': {'message': {'contextId': '0a6c011b-a938-4d3d-ac7d-b6ea71f7058b', 'kind': 'message', 'messageId': '8bdc33d8-d347-46c0-a9fe-4fe14f458d91', 'parts': [{'kind': 'text', 'text': 'Processing the exchange rates..'}], 'role': 'agent', 'taskId': '6041da17-ebd7-47d9-b492-edbc889e092b'}, 'state': 'working'}, 'taskId': '6041da17-ebd7-47d9-b492-edbc889e092b'}}
{'id': '425194e5-74d6-4dfc-8202-465b05cf6ffc', 'jsonrpc': '2.0', 'result': {'contextId': '0a6c011b-a938-4d3d-ac7d-b6ea71f7058b', 'final': True, 'kind': 'status-update', 'status': {'message': {'contextId': '0a6c011b-a938-4d3d-ac7d-b6ea71f7058b', 'kind': 'message', 'messageId': 'ff70fc42-b528-4072-9119-f13a4c663eb0', 'parts': [{'kind': 'text', 'text': '10 USD is 855.6 INR'}], 'role': 'agent', 'taskId': '6041da17-ebd7-47d9-b492-edbc889e092b'}, 'state': 'input-required'}, 'taskId': '6041da17-ebd7-47d9-b492-edbc889e092b'}}
```

# おしまい

というわけでA2Aの公式Tutorialを完走してみました。
Tutorialの範囲では1:1でA2Aの仕組みに焦点を当てた感じのサンプルだけを使用しましたが、
同じリポジトリの中には他にも多くのサンプルがあるので、これも試してみたいところです。
特にA2Aの醍醐味って複数のエージェントカードがあってそれを使い分ける、ってところにあると思うので、1:Nの構成もやってみたいですね。

# 参考

https://a2a-protocol.org/latest/tutorials/python/1-introduction/
https://github.com/google-a2a/A2A
https://github.com/google-a2a/a2a-samples
