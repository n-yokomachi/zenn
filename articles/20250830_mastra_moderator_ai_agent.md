---
title: "Mastra/Next.jsで作るモデレータAIが治安維持するSNS"
emoji: "📺"
type: "tech"
topics: [aws,aiagent,mastra,typescript,nextjs]
published: true
---

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
先日社内ハッカソンがありまして、
そこでAIエージェントを組み込んだSNSアプリを作ってみたので紹介します。

なおハッカソンへは個人参加で、成果物の提出までに費やした時間は、
インフラの設定とかも含めて開発に9時間、ドキュメントや動画作成に1時間くらいです。

# 成果物

## リポジトリ
https://github.com/n-yokomachi/failnet_app

## このアプリについて
作ったものはこんな感じのSNS風Webアプリです。
「失敗談ややらかし話を共有することで学びに変えていこう」というテーマで、
以下の特徴を持たせています。

1. ユーザーのエンティティがなく誰でも投稿できる
![](https://storage.googleapis.com/zenn-user-upload/edd859da2ef8-20250830.png)

---

2. アプリ外への共有をしやすくするため、URLコピーのほか、画像に変換してクリップボードにコピーをもできるようにする
![](https://storage.googleapis.com/zenn-user-upload/67588bf5f358-20250830.png)

---

3. **投稿に個人情報などのセンシティブ情報や倫理的に問題のある内容が含まれていないかをチェックする→今回ここにAIエージェントを使用しています。**

![](https://storage.googleapis.com/zenn-user-upload/ff9c999fc8a6-20250830.png)

このブログでは上記の2, 3をメインに実装について記述します。

## その他資料
紹介動画とエレベーターピッチ資料も作成したのでついでに置いておきます。

### 紹介動画
https://www.youtube.com/watch?v=UAb5pZ-bsIU

### エレベータピッチ
@[speakerdeck](85c8b08802a14a258c5544a7f918fc1a)

# プロジェクト情報

## 構成図
![](https://storage.googleapis.com/zenn-user-upload/34a76c493d01-20250830.png)

## 技術スタック
- フロントエンド：Next.js 15.5.0, Tailwind CSS 3.4.17
- バックエンド：AWS AppSync, DynamoDB
- インフラ,CI/CD：AWS Amplify Gen2 6.15.5
- AIエージェントFW：Mastra 0.10.23
- LLM基盤,モデル：Amazon Bedrock, Claude 3.7 Sonnet

:::message
開発・資料作成に使用したツール
- コーディング：Claude Code (Claude Sonnet 4)
- ツール・MCP：Gemini CLI, Serena MCP, PlayWright MCP
- 資料作成：[Marp](https://marp.app/) (Claude Codeでベース生成)
- 動画作成：[Kite](https://kite.video/)
:::


AIエージェントに関してはStrands AgentsをBedrock AgentCoreにデプロイしようと思っていたのですが、Next.jsからの使用するための実装に時間かかりそうだなと思って今回は見送りました。
TypeScript向けのMastraに切り替えたおかげでAIエージェント実装自体はClaude Codeにほぼ丸投げで実装できています。
結果的に時間短縮できたので正解だったと思います。

## MVP
ハッカソンの時間が限られていることもあり、実装する機能は以下の内容に絞りました。
:::message
## 投稿機能
- 匿名でのやらかし体験投稿
- 投稿ボタン -> 投稿をSubmitして一覧画面へ遷移
- **センシティブ情報検知機能**
  - 投稿ボタン押下時にテキストをAIに送り、個人名、メールアドレス、電話番号等のセンシティブ情報が含まれないかを分析
  - センシティブ情報が含まれる可能性があるとAIから回答があった場合、投稿を中断し、ユーザーに「この部分大丈夫ですか？」の確認メッセージを表示
- **カテゴリ判別機能**
  - 技術系、コミュニケーション系、作業系、判断系等をAIにより自動分類

## 一覧機能
- ユーザーの投稿を一覧表示できる画面。以下のソート、フィルターが可能
  - 投稿日時順のタイムライン表示
  - リアクション数順のおすすめ表示
  - 特定のカテゴリにフィルターする機能
- リアクション機能。誰でも何回でも可能。リアクション数はカウントする
- URLコピー機能
  - 投稿の詳細画面を開くためのURLをコピーするボタン
- 画像クリップ機能
  - クリップボードに、投稿を画像化して保存
  - MiroやCacoo、スクラムボードに張り付けるなど、ユーザーが画像として共有できるようにする

## 詳細モーダル
- 一覧画面上でモーダルを表示し、URLパラメータで指定した投稿IDに紐づく投稿を表示する
- 表示される情報は一覧に表示される内容と変わりなし
- あくまで共有したURLからアクセスすることを想定
- もちろん一覧画面上で選択した投稿を表示することも可能にしたい

## ヘッダ
- FailNetのアイコン・ロゴ
- Github Repoリンク
- ドキュメントの表示ボタン
  - クリックでこのアプリケーションの使い方をモーダル表示する
:::


# 1. ユーザーエンティティを廃し、完全に１画面にする
本アプリは個人を特定できる要素をできるだけ減らしてみようと考え、ユーザーというエンティティ自体を取り入れていません。
Webアプリにアクセスするとサインアップやサインインをすっとばして投稿・一覧画面に飛びます。
というか投稿・一覧画面しかありません。

あとメタ的な狙いとして、ハッカソンの評価期間中に触る人にわざわざサインアップしてもらったりのも体験が悪いと思ったのもシンプルな構成にした要因です。

ちなみにアイコンにはこちらのサイト様のイラストを使用させていただいております。
[かわいいフリーアイコン・イラストの無料素材サイト｜フリーペンシル](https://iconbu.com/)
ユーザーが存在しないのでアイコン自体は不要なんですが、なんとなくでイラスト入れてみたらこれだけでアプリの見た目が優しくなってて良かったと思います。


# 2. モデレータとして機能するAIエージェント

先述した通り今回は、**投稿に個人情報などのセンシティブ情報や倫理的に問題のある内容が含まれていないかをチェックする**ためにAIエージェントを作りました。
まあ正直なことを言うと以下の理由からそういうテーマを後付けした側面が強いです。
- AIエージェント主体のアプリケーションを作っても自分のアイデアが乏しく、どうやったって車輪の再発明になりそう
- 今回のハッカソンはAI活用をテーマとしているが、AIエージェント主体だと他のチームと差別化できなさそう
- 個人参加かつ早く夏休みに入りたかったので、とにかく実装を簡易にしつつ、プレゼンにテーマを持たせたかった

## 実装したAIエージェント

コードは以下の通りです。
ご覧の通りめちゃシンプルです。
```typescript:contentModerator.ts
import { Agent } from '@mastra/core';
import { createAmazonBedrock } from '@ai-sdk/amazon-bedrock';

// Set environment variable for Bedrock API key authentication
if (process.env.BEDROCK_API_KEY) {
  process.env.AWS_BEARER_TOKEN_BEDROCK = process.env.BEDROCK_API_KEY;
}

// Configure Bedrock provider
const bedrockProvider = createAmazonBedrock({
  region: process.env.AWS_REGION || 'us-west-2',
});

export const contentModeratorAgent = new Agent({
  name: 'contentModerator',
  instructions: `あなたは投稿内容の適切性を判定する専門のAIです。以下の基準で投稿内容を分析してください：

1. 不適切な内容の検出:
   - 差別的表現や憎悪表現
   - 過度に攻撃的な言葉遣い
   - 個人を特定可能な情報
   - 違法性のある内容
   - その他社会的に不適切な表現

2. 応答形式:
   - isAppropriate: true/false（適切かどうか）
   - confidence: 0.0-1.0（判定の信頼度）
   - reason: 不適切な場合の理由（日本語）
   - suggestedEdit: 不適切な場合の修正提案（日本語）

常に日本語で応答し、JSON形式で結果を返してください。`,
  model: bedrockProvider('us.anthropic.claude-3-7-sonnet-20250219-v1:0'),
});
```

## Bedrock APIキーの利用
2025年7月にAmazon BedrockでAPIキーの利用が可能になりました。
今回は期間限定の検証開発なのでLong termのキーを払い出して使用しています。
しかし、APIキーを使用する場合の環境変数名が「AWS_BEARER_TOKEN_BEDROCK」である一方で、AWS Amplifyでは環境変数の頭に「AWS」を使用できないので、別名の環境変数から読みだして設定しなおす、みたいな微妙な実装になってます。
> Amplify では、AWS プレフィックスを使用して環境変数名を作成することはできません。
> このプレフィックスは Amplify の内部でのみ使用されるよう予約されています。
> https://docs.aws.amazon.com/ja_jp/amplify/latest/userguide/environment-variables.html

あと今更だけどなんでClaude 3.7 Sonnet使ってるんだろう？　普通にSonnet 4でよかった。
（別にAIが勝手に3.7で実装したとかじゃなく、ちゃんと自分が3.7で指示してた。謎。）

## モデレータ的役割
ネガティブな投稿が多くなりそうなSNSなので、投稿前のワンクッションとしてLLMによるレビューを機能させ、SNSの治安維持を運営に代わってサポートするモデレータ的な役割を任せています。
プロンプトで投稿の内容を渡しつつ、それがセンシティブ情報を含んでいたり、表現に問題がないかを判定させています。
一応パラメータとしてconfidence（信頼度）を返してもらっており、精度に問題があれば開発者側でパラメータを調整して、どのくらいまで信頼するかを判定できます。
また、suggestedEditとして修正案を生成させ、ユーザーはその修正案をそのまま適用するか、もしくは自分で修正するかして投稿することができます。



## おまけ：自動カテゴリ分類
モデレータ機能と同じように、投稿に対して自動でカテゴリタグをつけるエージェントも実装しています。
こっちはおまけ的なものですが、ユーザーの主観に寄らない運営として今回のテーマにも合致しています。

```typescript:categoryClassifier.ts
export const categoryClassifierAgent = new Agent({
  name: 'categoryClassifier',
  instructions: `あなたは投稿内容を適切なカテゴリに自動分類する専門のAIです。以下のカテゴリから最も適切なものを1つ選んでください：

利用可能なカテゴリ:
1. 仕事・職場 - 仕事のミス、職場の人間関係、業務上の失敗など
2. 人間関係 - 友人、家族、恋人との関係でのやらかしなど  
3. お金・買い物 - 無駄遣い、投資失敗、買い物の失敗など
4. 健康・生活 - 健康管理のミス、生活習慣の失敗、体調管理など
5. 学習・スキル - 勉強、資格取得、スキルアップでの失敗など
6. 趣味・娯楽 - 趣味活動、ゲーム、スポーツでの失敗など
7. 技術・IT - プログラミング、システム、デジタルツールでの失敗など
8. 日常生活 - 日々の生活での小さなミス、うっかりミスなど
9. その他 - 上記に当てはまらない内容

分析基準:
- 投稿の主要なテーマを特定
- 失敗やトラブルの文脈を理解
- 最も関連性の高いカテゴリを選択
- 迷った場合は「その他」を選択

応答形式:
カテゴリ名のみを日本語で返してください（例：「仕事・職場」）`,
  model: bedrockProvider('us.anthropic.claude-3-7-sonnet-20250219-v1:0'),
});
```

# 3. 画像共有機能
また、共有することで学びに変えるというテーマに沿って、アプリ外への投稿の共有も簡単にできる工夫をしてみました。
各投稿に紐づけられたURLのコピーはもちろん、投稿を画像に変換してクリップボードにコピーする機能を実装しています。
コピーした画像をSlackなどに貼るのはもちろん、MiroとかFigjamなどのボードに貼ることでスクラムボードで共有しやすくなる、みたいな効果を狙っています。

実装には[html2canvas](https://html2canvas.hertzen.com/)ライブラリを使用し、投稿内容を画像化しています。

```typescript:ShareImageGenerator.tsx
// 画像化するための一時containerを作る
const container = document.createElement('div');

// containerに画像化するDOMを定義
container.innerHTML = `
  // ここに画像化前のDOMを定義
`;

// html2canvasで画像化
const canvas = await html2canvas(container, {
  // 画像のサイズとかの設定
});

return new Promise((resolve) => {
  // blobに変換
  canvas.toBlob(async (blob) => {
    if (!blob) {
      resolve(false);
      return;
    }

    try {
      // クリップボードにコピー
      await navigator.clipboard.write([
        new ClipboardItem({
          'image/png': blob
        })
      ]);
      resolve(true);
    } catch (error) {
      // エラーハンドリング
    }
  }, 'image/png');
});
```



# おしまい
というわけでSNSの治安維持をするAIエージェントをテーマにハッカソン向けに開発したプロダクトを紹介しました。
ただそのテーマが仇となって、ほとんどの常識的なユーザーにとってはエージェントの存在を感じられないプロダクトにもなりました。
そのためハッカソン的にはだいぶ地味な成果物となってしまったのが今回の反省点です。
次の機会があればもっと派手派手に主張してくるAI機能を考えてみたいと思います。
