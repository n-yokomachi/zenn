---
title: "自作エージェントに喋りかけるだけでアプリ開発｜MastraとClaude Code Actionで音声バイブコーディング"
emoji: "🎙️"
type: "tech"
topics: [mastra,typescript,claude,github,vivecoding,]
published: false
---

今回はGitHub ActionsのClaude Code連携を試します。
また、音声入力でIssue作成とかできれば、今一番アツいClaude CodeでどこでもラフにVibe Codingができるんじゃないかと思ったのでやってみます。

# 発端
[Claude Codeの勉強会](https://kddi-agile.connpass.com/event/357337/)でこんなこと👇を言ったので、言ったらやるの精神でやります。
https://x.com/_cityside/status/1930107043396104563

実際はGitHubのMCPサーバ設定したClaude Desktopに、なんかのツールで音声入力するだけでも実現できると思うのですが、以前からMastraを触ってみたかったのでこの機会に自前でAIエージェントアプリを作ることにしました。
音声入力ツールはすでにLLMを活用したちゃんとしたのがあるっぽいので気になる方はそちらもチェック。

# まずは成果物から

## アプリはこちら
実際のアプリケーションはこちらから使えます。

https://voice2issue.vercel.app/
[![](https://storage.googleapis.com/zenn-user-upload/71c70a6713d6-20250608.png)](https://voice2issue.vercel.app/)

:::message
LLM(Anthropic)の料金はユーザー側が負担する設計です。
普通に動かす分には0.1USDもかかりません。

また、アプリの仕様上、GitHub Access Token、Anthropic API Keyの入力が必要です。
トークンやキーは逐一入力するのが面倒なので、暗号化してSessionStorageに入れています。セキュリティが気になる方は使用をお控えください。

なお、設定で「デモモード」にチェックを入れるとトークンやキーを入力しなくてもUIの動作確認だけできるので良ければやってみてください。
:::

## 動画もあるよ
デモ動画を作ったので大体何やろうとしているのかがわかるかと
https://www.youtube.com/watch?v=3NxOoiMK664

スマホでも
https://x.com/_cityside/status/1931388312843088120


# 要件・設計の整理
## 要件整理
まず簡単に要件を整理すると以下の通りです。
- アプリ
    - 音声入力をテキストに変換する（STT）
    - そのまんまのテキストだと話し言葉すぎるので、LLMにテキストを投げてIssueの原稿を作ってもらう
    - 作ってもらった原稿でIssueを作成する
    - なお、LLMのアカウントはユーザー自身のものを使う。
- GitHub
    - Issueを検知してClaude Codeが実装する
    - Pull Requestが作成されたらプレビューデプロイして実装結果をチェックできるようにする

## 技術スタック
主要なものだけ
- フロントエンド
    - Next.js 15.3.3
    - TypeScript 5
    - Tailwind CSS 4
    - Headless UI 2.2.4
- エージェント・ワークフロー
    - Mastra 0.10.3
    - Anthropic Claude SDK 0.53.0
- API
    - Octokit REST 22.0.0
    - Web Speech API
- デプロイ
    - Vercel
- コーディングエージェント
    - [Claude Code Actions](https://github.com/anthropics/claude-code-action)
    - 実装に使ったのはCursor(Claude Sonnet 4)

:::message
PCでもスマホでも使えるように、手っ取り早くWebアプリで実装します。
音声入力はWeb Speech APIでの実装としましたが、Mastraには音声認識機能もあるみたいです。
そっちも使ってみたかったけど、アプリ側でLLMの料金負担したくなかったので今回は見送り。
:::


## シーケンス図
今回のシーケンス図、つまりこういうことになります。

WebアプリによるIssue作成と、Claude Codeによる実装は非同期になります。
Issue案作成LLMはなんでもよかったんですが、課金先を統一したかったのでClaude一本に絞ってます。
![](https://storage.googleapis.com/zenn-user-upload/7105ab6e2fca-20250607.png)


# 実装する

## Webアプリの実装
ソースコードはこちら
https://github.com/n-yokomachi/voice2issue

以下の主要な部分だけ簡単な説明を書きます。
    - 音声入力
    - Mastra Workflow
    - GitHub APIでのIssue作成

### 音声入力部分

音声入力は[Web Speech API](https://developer.mozilla.org/ja/docs/Web/API/Web_Speech_API)を使ってブラウザの音声認識機能を利用しています。

初期化部分
```typescript: VoiceInput.tsx
const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = 'ja-JP';
recognition.continuous = true;      // 連続認識
recognition.interimResults = true;  // 中間結果も取得
recognition.maxAlternatives = 1;
```

認識結果取得部分
```typescript: VoiceInput.tsx
recognition.onresult = (event) => {
  for (let i = event.resultIndex; i < event.results.length; i++) {
    const transcriptText = event.results[i][0].transcript;
    if (event.results[i].isFinal) {
      sessionFinalTranscript += transcriptText;
    } else {
      sessionInterimTranscript += transcriptText;
    }
  }
};
```


### Mastra Workflow

[Mastra](https://mastra.ai/)はAIエージェントやワークフローを構築するためのTypeScript向けフレームワークです。
Next.jsはもちろん他のフレームワークのサポートもありますし、メモリやRAG、MCPなどエージェント開発に必要な機能が盛り込まれています。

今回はMastraのWorkflowを作成しています。
大してステップはありませんが、LLMでIssue案作成→GitHub API実行、っていう順番はあるのでWorkflowだと開発しやすいかなと思ったためです。
また、エージェントにリモートMCPサーバを統合できればGitHubの操作もLLMに投げられるじゃん、と思ったものの、GitHubのMCPサーバはDockerを使ったりとちょっと癖がありそうで断念しました（ローカルで動かす分なら全然問題ないけど、自前のアプリケーションに統合してホスティングサービスにデプロイするのを考えるとどうすればいいのかわからなかった）

というわけでコードの話ですが、

まずMastraの初期化はこんな感じ。
```typescript: mastra/index.ts
export const mastra = new Mastra({
  agents: {}, 
  workflows: { voiceToIssueWorkflow },
  storage: new LibSQLStore({
    url: ":memory:",
  }),
});
```

音声入力結果を分析してIssueの案を考えるステップは以下の部分
```typescript: issueWorkflow.ts
const analyzeVoiceInput = createStep({
  id: "analyze-voice-input",
  execute: async ({ inputData }) => {
    const anthropic = new Anthropic({
      apiKey: inputData.anthropicApiKey,
    });

    const prompt = `
        音声入力: "${inputData.voiceInput}"
        音声入力内容を分析して、GitHub Issueの情報を生成してください。
        // ... （中略）
        `;
    
    const result = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1000,
      messages: [{ role: "user", content: prompt }]
    });
  },
});
```

でその分析結果を使ってGitHub Issueを作成するステップはこう
```typescript: issueWorkflow.ts
const createGitHubIssue = createStep({
  id: "create-github-issue",
  execute: async ({ inputData }) => {
    const octokit = new Octokit({ auth: token });

    const fullBody = `
        ${inputData.body}
        ---

        @claude
        このIssueの実装をお願いします。
        実装タスクを分割し、ステップバイステップで実装してください。

        ---
        *この依頼は Voice2Issue アプリケーションによって自動生成されました*`;

    const issueResponse = await octokit.rest.issues.create({
      owner,
      repo,
      title: inputData.title,
      body: fullBody,
      labels: allLabels,
    });
  },
});
```

上記２つのステップをWorkflowとして以下のように定義します。
```typescript: issueWorkflow.ts
export const voiceToIssueWorkflow = createWorkflow({
  id: "voice-to-issue",
  // スキーマ定義...
})
  .then(analyzeVoiceInput)  // 音声認識ステップ
  .then(createGitHubIssue); // GitHub Issue作成ステップ
```

で、作ったWorkflowはAPI経由で呼び出す必要があります。
※下記リンクは日本語だと表示が不十分の可能性があります
https://mastra.ai/en/docs/frameworks/next-js#create-test-api-route


``` typescript: src/app/api/mastra/workflow/route.ts
import { NextRequest, NextResponse } from "next/server";
import { mastra } from "../../../../../mastra";

export async function POST(request: NextRequest) {
  try {
    // (中略)
    
    // Mastraワークフローを実行
    let result;
    try {
      const workflow = mastra.getWorkflow("voiceToIssueWorkflow");
      
      // Mastraワークフローの実行 - createRun()からstart()を使用
      const run = workflow.createRun();
      result = await run.start({
        inputData: {
          voiceInput,
          repository,
          githubToken,
          anthropicApiKey,
        }
      });
      
      // Mastraワークフロー結果の構造に合わせて処理
      if (result.status === 'success' && result.result) {
        return NextResponse.json({});
      } else {
        throw new Error(`Workflow execution failed with status: ${result.status}`);
      }
      
    } catch (workflowError) {
      //
    }
  } catch (error) {
    //
  }
} 
```

### GitHub APIでのIssue作成

Issueの作成はOctokitライブラリを使用しています。

クライアントの初期化部分
```typescript: issueWorkflow.ts
const token = inputData.githubToken;
const octokit = new Octokit({ auth: token });
```

Issue本文の定義部分
`inputData.body`にはLLMに生成してもらった整理された要件が入ります。
@claudeをIssueの本文に入れることでClaude Codeの実行をフックします
```typescript: issueWorkflow.ts
const fullBody = `${inputData.body}

---

@claude
このIssueの実装をお願いします。
実装タスクを分割し、ステップバイステップで実装してください。
なお、Issueへのコメントは日本語を使用してください。

---
*この依頼は Voice2Issue アプリケーションによって自動生成されました*`;
```

Issueの作成部分
```typescript: issueWorkflow.ts
const issueResponse = await octokit.rest.issues.create({
  owner,
  repo,
  title: inputData.title,
  body: fullBody,
  labels: allLabels,
  assignees: [],
});
```


## GitHub ActionsのClaude Code設定

GitHub ActionsでClaude Codeを設定する方法は大きく分けて二つあります。

１つがまずローカルにClaude Codeをインストールし、ターミナルから`/install-github-app`でセットアップを開始する方法。
もう１つがGitHub AppのClaudeを画面からインストールし、手動でAPI Keyの登録やワークフローの作成をする方法です。

前者の場合、まずClaude Codeがインストールできるのが以下のOSとなっています。
- macOS 10.15+
- Ubuntu 20.04+/Debian 10+
- WSL経由のWindows

今回私はWindowsで作業しているのでWSL経由でインストールしてもいいのですが、なんとなくで後者の方法でやっていきます。

### Claude GitHub Appのインストール

https://github.com/apps/claude
こちらからインストール
Appがアクセスできるリポジトリを選択
![](https://storage.googleapis.com/zenn-user-upload/7b71aef39c5c-20250608.png)


### Anthropic API Keyの登録
まずAnthropicのAPI Keyを払い出します
https://console.anthropic.com/dashboard

対象のリポジトリの`Setting > Secrets and variables > Actions`から払いだしたAPI Keyを登録
![](https://storage.googleapis.com/zenn-user-upload/b7869b257221-20250608.png)


### GitHub Actions用ワークフローの作成
下記のリンクからサンプルのymlをコピーして、リポジトリの`.github/workflows/`に設定
https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml

ただし上記は与えているpermissionsがreadなので、要件に応じて編集します
私は今回以下のように設定しています
（タスク完了後にPRを自動作成できないかと試行錯誤していた名残があるので、適宜変えてください）
``` markdown: .github/workflows/claude.yml
name: Claude Assistant
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]

jobs:
  claude-response:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
      id-token: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Run Claude Code Action
        uses: anthropics/claude-code-action@beta
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          
          trigger_phrase: "@claude"
          timeout_minutes: "60"
```

Claude Codeの設定はこれだけです。


## Vercelの設定

今回Claude Codeをワークフローに入れたリポジトリ（個人のポートフォリオサイト）は元々Vercelで自動デプロイするように設定済みです。
設定自体はこの辺りが参考になります。
https://typescriptbook.jp/tutorials/vercel-deploy

あとVercelの公式
https://vercel.com/docs/git/vercel-for-github?utm_source=github

# 動かしてみる
では動かしてみます（やることは冒頭の動画と同じです）

## 現状確認
現在の個人ポートフォリオは以下のようなセクションに分かれています。
これにProductsとして個人の成果物を紹介するセクションを作ります。
![](https://storage.googleapis.com/zenn-user-upload/1bb8f0509fb0-20250608.png)

## 音声入力でIssue作成
今回作ったWebアプリで音声を入力し、Issue作成ボタンを押します
![](https://storage.googleapis.com/zenn-user-upload/8fa7fe60f647-20250608.png)

## Issueの作成確認
こんな感じでちゃんとしたIssueが作成されました
![](https://storage.googleapis.com/zenn-user-upload/0864d1afc412-20250608.png)

## Claude Codeの実装確認
無事Claude Codeが実装を完了してくれました
![](https://storage.googleapis.com/zenn-user-upload/d11bcb1abc64-20250608.png)

## PR作成からプレビューデプロイの確認
PRを作成するとVercelがプレビュー環境のURLをコメントしてくれます。
![](https://storage.googleapis.com/zenn-user-upload/2a8642ff03ee-20250608.png)

プレビュー環境を見ると、ヘッダにProductsが追加されています。
![](https://storage.googleapis.com/zenn-user-upload/95ab200bb916-20250608.png)

Productsセクションの中身もちゃんと作られています。
（Voice2IssueでWhisper APIは使ってないけど）
![](https://storage.googleapis.com/zenn-user-upload/2122c42d39d2-20250608.png)



# おしまい
## まずWebアプリについての感想

この記事を書いている途中で思いましたが、Issue投げる前にどんなIssue作ろうとしてるか表示したほうがよかったですね。
思ったのと違うIssueが作成されて、「あっ…待って…そういう意味じゃないの…」ってなってる間にClaude Codeが実装しちゃったりするので。

また、今回音声入力はWeb Speech APIを使いましたが制御がちょっと難しかったので、Mastraの音声認識とかも使ってみたいですね。
あとMastraに関して言うと、Workflowとかは作っちゃえば意外とすっきりした実装になるんですが、ドキュメントを読み解くのが結構大変でした。
やっぱりドキュメント丸ごとLLMに投げて必要なところだけ聞くのが楽です。


## Claude Code Actionについての感想

Claude Code Actionは一度走り始めるとこちらからの介入ができないので、
実装の経過を見たり、適宜指示を出したり、日常遣いをするにはやっぱりターミナルやエディタで動かすClaude Codeがいいですね。
ただ、出先や散歩中やお風呂の中で思いついたアイデアとかをとりあえず実装させてみる、とか単発のリクエストをするにはClaude Code Actionを使うのも結構いいんじゃないかと思います。
多少雑な実装でも実際の画面とかで動作確認したりとかは早くしたいですしね。


