---
title: "Goで作った自作言語をAWS Lambdaカスタムランタイムで実行する"
emoji: "⚡"
type: "tech"
topics: [aws, lambda, 自作言語, go]
published: true
---

:::message
この記事は人間が書いていますが、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

ふと思い立ってプログラミング言語を自作してみました。「Sugu」といいます。
JavaScriptに近い仕様のインタプリタ言語で、Goを使用して作っています。

### Repo
https://github.com/n-yokomachi/sugu

### 言語仕様など
https://n-yokomachi.github.io/sugu/

自作といいつつ実装は全部Claude Code+Opus 4.5で行い、レビューも基本はClaude Codeにお任せして自分はざっくり見る感じで作っています。
もともと先に作ってからリバースエンジニアリングして勉強するつもりだったので、これからコードを読むターンです。

それはそれとして、AWS Lambda上でも動かせれば面白そうだなと思うのでやってみます。

# 自作言語「Sugu」の概要

Suguはインタプリタ言語で、REPL／ファイル実行をサポートしています。
👇こんな感じで実行できます。

```bash
# REPL（対話モード）を起動
$ sugu
>> mut x = 1 + 2;
>> outln(x);
3

# ファイルを実行
$ sugu hello.sugu
```

また簡単にSuguの仕様を紹介しておくと、まずデータ型・制御構文は以下の通り
```
データ型： `number`, `string`, `boolean`, `null`, `array`, `map`
制御構文： `if/else`, `while`, `for`, `switch`
```

インタプリタのアーキテクチャは以下の通り
```
入力コード → Lexer → Parser → AST → Evaluator → 結果
```

書き方はこんな感じです
```javascript
// 変数宣言
mut x = 10;       // 再代入可能
const PI = 3.14;  // 再代入不可

// 関数定義
func add(a, b) => {
    return a + b;
}

// 出力
outln("Hello, Sugu!");
outln(add(1, 2));  // 3
```

ざっくりJSと同じ感覚で書ける感じです。
学習目的で作っているので特に思想とかはありません。
また、組み込み関数をはじめいろいろと足りていない要素はあるので、今後もアップデート予定です。


# AWS Lambdaのカスタムランタイム

AWS Lambdaで通常サポートされていない言語を実行する場合カスタムラインタイムを使用します。

カスタムランタイムの仕組みについて詳しくは[AWSのドキュメント](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/runtimes-custom.html)を参照してください。
AWS Lambdaのカスタムラインタイムは2026年1月現在以下がサポートされています。
- Amazon Linux 2023
- Amazon Linux 2（2026年6月30日廃止予定）

カスタムラインタイムの場合エントリポイントはbootstrapという実行ファイルになるので、これを自作言語側に実装する必要がありますが、Goの場合は[aws-lambda-go SDK](https://github.com/aws/aws-lambda-go)が[Lambda Runtime API](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/runtimes-api.html)との通信を抽象化してくれるので、ハンドラー関数を書くだけでOKです。

# Lambda対応の実装

自作言語側にAWS Lambda実行のための対応を入れます。
ここではハンドラーの実装、イベントの受け渡しのみをピックアップしていますが、元のSuguがCLI目的のため出力の制御なども別途入れています。

## Lambdaハンドラー

`main.sugu`ファイルを読み込んで実行するハンドラーを実装します。

```go:lambda/main.go
package main

import (
    "github.com/aws/aws-lambda-go/lambda"
)

func main() {
    lambda.Start(Handler)
}
```

```go:lambda/handler.go
// main.suguの最後に評価された式の値がそのままLambdaのレスポンスになる
func Handler(ctx context.Context, event json.RawMessage) (interface{}, error) {
    // main.sugu を読み込む
    code, err := os.ReadFile("main.sugu")
    if err != nil {
        return map[string]string{"error": "failed to read main.sugu: " + err.Error()}, nil
    }

    return Execute(string(code), event)
}
```


## イベントの受け渡し

Lambdaのテストイベントをevent変数として渡せるようにしました。
JSONをSuguのオブジェクト（Map, Array, Number, String, Boolean）に変換しています。

```go:lambda/handler.go
// JSON → Sugu Objectの変換
func goValueToSuguObject(v interface{}) object.Object {
    switch val := v.(type) {
    case nil:
        return &object.Null{}
    case bool:
        return &object.Boolean{Value: val}
    case float64:
        return &object.Number{Value: val}
    case string:
        return &object.String{Value: val}
    case []interface{}:
        elements := make([]object.Object, len(val))
        for i, elem := range val {
            elements[i] = goValueToSuguObject(elem)
        }
        return &object.Array{Elements: elements}
    case map[string]interface{}:
        pairs := make(map[object.HashKey]object.HashPair)
        for k, v := range val {
            key := &object.String{Value: k}
            pairs[key.HashKey()] = object.HashPair{
                Key:   key,
                Value: goValueToSuguObject(v),
            }
        }
        return &object.Map{Pairs: pairs}
    default:
        return &object.Null{}
    }
}
```


## ビルド

AWS Lambdaのカスタムラインタイムを使用するため、以下のビルド設定でビルドします。

```bash
# Linux/Mac
GOOS=linux GOARCH=amd64 go build -o bootstrap ./lambda
zip sugu-lambda.zip bootstrap
```


# AWS Lambdaの設定・デプロイ

続いてLambda側の設定です。
Lambda関数の作成時にカスタムランタイムを選択して作成します。
![](https://storage.googleapis.com/zenn-user-upload/f5bb2764594d-20260104.png)

Lambdaの作成後、bootstrapをzipにしたものをアップロードし、実行用のmain.suguファイルを作成します。
![](https://storage.googleapis.com/zenn-user-upload/7189f554d8a4-20260104.png)

# 動作確認

以下のテストイベントを渡してみます。
```json
{
  "name": "yoko"
}
```

ちゃんと動いてますね
![](https://storage.googleapis.com/zenn-user-upload/40982bf44a95-20260104.png)





# おしまい

ということで自作言語を作ったついでにAWS Lambda上で動かしてみました。
なんとなくで始めた自作言語ですが結構面白いので今後もアップデートできればと思います。
実装している処理系への理解がまだ足りないのでそのあたりはコードを読みつつ勉強します。
