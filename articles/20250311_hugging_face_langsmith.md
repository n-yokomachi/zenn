---
title: "Hugging Face SpacesにデプロイしたStreamlitアプリをLangSmithと連携する"
emoji: "🐈"
type: "tech"
topics: [localllm, streamlit, huggingface, langchain, langsmith]
published: true
---

前回ファインチューニングしたLLMでチャットボットを作り、  
Hugging Face Spacesにデプロイしました。  
https://zenn.dev/yokomachi/articles/20250224_tutorial_localllm

で、実際このチャットボットがどれくらい使われるのかを見てみたいので、  
このStreamlit製のアプリケーションからLangSmithにトレースログを送れるように連携してみます。

よければチャットボット触ってみてください。  
猫と戯れることができます。  
https://huggingface.co/spaces/yokomachi/catbot

# LangSmith側の設定

## サインアップ
まずはLangSmithにサインアップします。

![](https://storage.googleapis.com/zenn-user-upload/f3318942fb8d-20250311.png)

## APIキーを払い出す
LangSmithのエンドポイントにアクセスするためのAPIキーを払いだします。  
LangChainを使う場合と使わない場合のサンプルコードもあるので控えておきます。
![](https://storage.googleapis.com/zenn-user-upload/ab3cdd886c08-20250311.png)


# 環境変数を設定する

## Hugging Face Spacesに環境変数を設定する
StreamlitアプリをデプロイしているHugging Face SpacesのSettingsに  
Variables and secretsという項目があるのでAPIキーなどを設定します。  
![](https://storage.googleapis.com/zenn-user-upload/3f109c04715e-20250311.png)

## 環境変数を読み込む
続いてStreamlitアプリケーション側に環境変数を読み込んで  
LangSmithの設定を初期化するように設定します。
``` app.py
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")
```
LangSmith連携のために追加したコードは実際これだけでした。  
おそらくLangChain以外から使う場合にはもうちょっとなんかやる必要がありそうです。


# 動かしてみる

## アプリケーション側
チャットボットで何度かLLMで回答を生成します。
![](https://storage.googleapis.com/zenn-user-upload/192a00e858a5-20250311.png)

## LangSmith側
トレースログが収集されています。  
プロンプトやアウトプットはもちろん、トークン数やレイテンシ、アプリケーションのランタイム情報なども参照できます。

![](https://storage.googleapis.com/zenn-user-upload/ab5b6168d374-20250311.png)

また、Dashboardsにグラフを作成するとRunCountやLatencyの遷移もわかりやすくなります。  
試しにRunCountをグラフ化してみるとこんな感じになりました。
![](https://storage.googleapis.com/zenn-user-upload/a543bf30c294-20250311.png)


# おわり
今回はHugging Face Spacesにデプロイしたチャットボットの稼働状況を監視するためにLangSmithと連携を試してみました。
LangSmith事態は初めて触りましたが、今回触った範囲以外にもデータセットの評価やプロンプトの管理などのLLMOpsのための機能があるようなので、また機会を見て触ってみたいと思います。