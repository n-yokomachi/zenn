---
title: "喋るだけでアプリ開発｜Mastra製WebアプリとClaude Code Actionで作る音声バイブコーディング"
emoji: "🎤"
type: "tech"
topics: [mastra,typescript,claude,github,vivecoding,]
published: false
---

今回はGitHub ActionsのClaude Code連携を試すついでに、
どうせなら音声入力でIssue作成とかできたら、ガチのVibe Codingができるんじゃないかと思ったのでやってみます。
さらについでにMastra触ったことなかったので触ってみます。

# やりたいこと
## 発端
Claude Codeの勉強会でこんなこと👇を言ったので、言ったらやるの精神でやります。
https://x.com/_cityside/status/1930107043396104563

## 要件整理
まず簡単に要件を整理すると以下の通りです。
- アプリ
    - 音声入力をテキストに変換する（STT）
    - そのまんまのテキストだと話し言葉すぎるので、LLMにテキストを投げてIssueの原稿を作ってもらう
    - 作ってもらった原稿でIssueを作成する
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

:::message
PCからもスマホからも利用できるようにと考えて、手っ取り早くWebアプリで実装します。
また、音声入力はWeb Speech APIでの実装としましたが、Mastraには音声認識機能もあるみたいです。
:::


## シーケンス図
今回のシーケンス図、つまりこういうことになります。
WebアプリによるIssue作成と、Claude Codeによる実装は非同期ということになります。
![](https://storage.googleapis.com/zenn-user-upload/7105ab6e2fca-20250607.png)


# 実装する

## Webアプリの実装
ソースコードはこちら
https://github.com/n-yokomachi/voice2issue

主要な部分だけ簡単な説明を書きます。

### 音声入力部分


