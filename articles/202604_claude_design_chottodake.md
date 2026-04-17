---
title: "ざっくりClaude Designを触ってみたので共有する"
emoji: "🦀"
type: "idea"
topics: [claude,ai,anthropic]
published: true
---

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに

Claude Designが発表されました。
https://claude.ai/design/
2026/4/18現在はPro, Max, Team, Enterpriseプランでリサーチプレビューとして利用可能です。
https://x.com/claudeai/status/2045156267690213649

FigmaっぽいのかLovableやv0っぽいのかわからなかったのでとりあえずざっくり触ってみます。


# 概観

アクセスするとこんな感じの画面になります。
※すでにいくつかプロジェクト作っていますが、初期はチュートリアルプロジェクトだけが表示されています。
![](https://storage.googleapis.com/zenn-user-upload/bb830ca29a39-20260418.png)

左側のペインからPrototype, Slide deck, From template, Otherと並んでいますが、それぞれざっくり以下のことができそうです。
- Prototype: ワイヤーフレームかモックアップを選択してデザインの作成ができる。
- Slide deck: 展示や発表用のスライドの作成ができる。
- From template: PrototypeやSlide deckで作ったデザインをテンプレートとして保存・使用できる？　なんかAnimationが作れる。
- Other: 空のプロジェクト

また、共通してデザインシステムの管理・適用ができるようです。
すでにプロジェクトに導入しているデザインシステムがあればそれを適用するのもよいですし、プロジェクトの成果物のデザインを統一化するのによさそうです。
![](https://storage.googleapis.com/zenn-user-upload/acf814d08c69-20260418.png)

次のセクションから各機能をざっくり見ていきます。

# Prototype

ワイヤーフレームかモックアップを選択してデザインの作成ができます。
![](https://storage.googleapis.com/zenn-user-upload/8ff9277ad700-20260418.png)

既存のデザインシステムとか、参考にしてほしいスクショとかコードベースがあれば最初のコンテキストとして読ませることも可能です。
もちろんチャットで公開中のWebページを渡すとかしても参照してくれます。
また、最初の指示をすると追加の質問をしてくれるので、全体のテーマのイメージとか、必要な要素とかを選択式で回答するなどしてある程度詰めることができます。

今回は公開済みのポートフォリオのページを渡してみました。
複数のデザインを作って見比べることもできるらしいので、それで作ってもらいました。
ちょっと目を離していたのでざっくりですが、5分かかるかどうかくらいで以下ができました。
![](https://storage.googleapis.com/zenn-user-upload/ca03a4810806-20260418.png)

３パターンあります。
各パターンをクリックすると全画面で表示されます。
![](https://storage.googleapis.com/zenn-user-upload/12f2867879b1-20260418.png)
![](https://storage.googleapis.com/zenn-user-upload/c3f634431fd7-20260418.png)
![](https://storage.googleapis.com/zenn-user-upload/68b9fa3c4c17-20260418.png)

私はデザインがわからないので何も言えませんが、少なくともページは破綻していませんでした。
もう少し業務アプリっぽいもののデザインもさせてみましたが、そちらもめちゃめちゃインプット少ないのにそれなりのものを作ってくれました。
（デザインからAnthropic感が漂ってくる感じはありましたが調整次第でしょう）

作成したデザインは同じOrganizationに共有したり、PDFやHTMLとしてダウンロードしてローカルで開くことができます。
また「Handoff to Claude Code」を選択すると、Claude Codeへ渡すためのリンクやコマンドを作ってくれるので、そのまま開発へ移行もできそうです。
![](https://storage.googleapis.com/zenn-user-upload/46dc2d8fc7e5-20260418.png)


# Slide deck

Prototypeと同じ感覚でスライドの作成ができます。
スピーカーノートの作成も可能です。
![](https://storage.googleapis.com/zenn-user-upload/703127480074-20260418.png)

今回は[Amazon Bedrock AgentCoreのCode Interpreterについて書いた以前のブログ](https://zenn.dev/yokomachi/articles/202603_code-interpreter-with-strands-agents-skills)のリンクを渡して、これを5分LT用のスライドとして作成してもらいました。

プロンプトは以下オンリーです。
「Amazon Bedrock AgentCoreについて5分のLT用のスライドを作って。
特にAgentCore Code Interpreterをメインに取り上げて、以下の私のブログをもとにスライドと発表者用ノートを書いて。」

できたスライドはこちらです。一切手を加えていません。
@[speakerdeck](c66315dca7bf4eb0989bb72cebee85c9)

また、画面下にスピーカーノートの内容も生成されていることがわかります。
![](https://storage.googleapis.com/zenn-user-upload/1c0fc7413340-20260418.png)

作ったスライドの調整は画面上でプロパティをいじることで可能ですし、PPTX, Canvaにエクスポートもできるので、ベースだけ作ってあとは任意で編集も可能です。Canva民かつ、AI生成スライドに何度か挫折している私には新たな光となるかもしれません。
![](https://storage.googleapis.com/zenn-user-upload/f52ea6558012-20260418.png)


# From template

PrototypeやSlide deckで作ったデザインをテンプレートとして保存・使用できる？と思いましたが、テンプレートを保存しても↓ここ↓には表示されませんでした。
![](https://storage.googleapis.com/zenn-user-upload/984efd488db5-20260418.png)

代わりにAnimationが作れるみたいなのでやってみます。
プロンプトは以下オンリーです。
「これは何ができるプロジェクトだ？アニメーション？とりあえず、なんだろ、私が開発しているAIエージェント「TONaRi」の紹介をして。（GitHubのリンク）」（原文ママ）

できたアニメーションは以下です。
https://www.youtube.com/watch?v=-ajoMCt6KZc

エクスポートの形式に動画ファイル形式はない…というかコードのみで描画しているアニメーションなので、動画として使いたければ別途変換する必要はあります。


# Other

特に何も指定しない空のプロジェクトです。
開くとSketch画面のみです。

ここまでSketch画面の説明をしませんでしたが、これはPrototype, Slide deckなどからも使える画面で、FigjamやMiroのように付箋などを自由に貼って情報の発散・整理などに使用できるホワイトボードになっています。

ClaudeからもSketchの内容が見えるので、ワークショップなどの際にラップアップを依頼したりといった活用もできるでしょう。
ちなみに今日の晩御飯を提案してくれと頼んだところ、随分大仰な提案書を作ってくれました（コンティンジェンシープランみたいなものまであります）

![](https://storage.googleapis.com/zenn-user-upload/9a577ad19319-20260418.png)
![](https://storage.googleapis.com/zenn-user-upload/67961eb3e656-20260418.png)


# おしまい

ということで発表されたばかりのClaude Designを試してみました。
デザインが何もわからない自分にとっては、結構感触はいいと思います。
ただ何も指定しない場合、Anthropic感のあるデザインが生成されがちなようなので、そこはきちんと調整する必要がありそうです。
が、一方でこのClaude Design上でガリガリデザインする思想にはなっていなさそうにも感じます。
Figmaの代替にはなりませんが、Lovableの代替にはなるかなというのが今の印象です。
