---
title: "AIエージェントにVRMキャラクターをつけてモーションを制御する"
emoji: "🚶🏻"
type: "tech"
topics: [vrm, threejs, nextjs, typescript, aituber]
published: true
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに
現在進行形で個人開発中のAIエージェントでユーザーインタフェースとして3Dモデルを使ってみることにしました。
とはいえ一から実装する知識がないので、以前から見知っていた[AITuberKit](https://github.com/tegnike/aituber-kit)を利用してフロントエンドの実装を手軽にしてみようと思います。

![](https://storage.googleapis.com/zenn-user-upload/481cdad6c3c1-20260221.png)

# 技術スタック

- VRMモデル作成: [VRoid Studio](https://vroid.com/studio)
- Webフロントエンド: Next.js, TypeScript
- VRM表示・制御: [three-vrm](https://github.com/pixiv/three-vrm) (v3.0.0), Three.js
- ベースキット: [AITuberKit](https://github.com/tegnike/aituber-kit)
- エージェント実装: Strands Agents, Amazon Bedrock AgentCore  ※今回はあまり取り上げません

# VRMとVRoid Studio
VRMは3Dアバター向けのファイルフォーマットです。
[VRoid Studio](https://vroid.com/studio)を使えば、3Dモデリングの知識がなくてもキャラクターを作成してVRM形式でエクスポートできます。
自分の場合だとゲームのキャラクリエイトくらいしかやったことはないですが、1時間くらいで男女のモデル2体が作れるくらいにはお手軽です。

https://x.com/_cityside/status/2019742015617994773

# AITuberKitでできること
[AITuberKit](https://github.com/tegnike/aituber-kit)はVRMモデルをWebブラウザ上に表示し、LLMと連携したチャット機能や表情制御、音声合成などをまとめて提供してくれるOSSです。

AITuberKitが提供する機能を抜粋すると以下の通りです。

- VRMモデルの表示・表情制御・リップシンク制御
- LLMと連携したチャットボット機能
- 音声合成APIとの連携
- YouTube配信連携
- マルチモーダル入力
- etc.

私の個人開発ではあくまで個人用のAIエージェントとして作っているので、
VRMの表示制御やチャットボット機能などのベースを使わせていただき、あとはがっつりカスタマイズを入れています

# モーション制御の実装

ここからが本題です。
AITuberKitはデフォルトで表情の切り替え（笑顔、怒り顔など）ができるので、追加で身体的なモーション（お辞儀、手を差し出すなど）を実装してみることにしました。

https://x.com/_cityside/status/2016874430056845502

## アーキテクチャ概要

モーション制御の全体像はこんな感じです。

```
LLMレスポンス
  ↓ ストリーミング解析
  ├─ [emotion] 感情タグ → ExpressionController → 表情制御
  └─ [bow/present] モーションタグ → GestureController → ボーン制御
                                         ↑
                                    EmoteController（コンフリクト制御）
```

`EmoteController`が表情とモーションの間に立って、コンフリクトを制御しています。

## モーションの定義

モーションはボーンの回転をキーフレームで定義する形で実装しています。

以下はお辞儀の定義例です。

```typescript:src/features/emoteController/gestureController.ts
interface BoneRotation {
  bone: VRMHumanBoneName
  rotation: THREE.Quaternion
}

interface GestureKeyframe {
  duration: number
  bones: BoneRotation[]
}

interface GestureDefinition {
  keyframes: GestureKeyframe[]
  holdDuration: number
  closeEyes?: boolean
}
```

お辞儀の場合はspine、chest、neckの3つのボーンをそれぞれ前方に回転させ、単に腰を曲げただけではない、ちょっと自然寄りのお辞儀を表現しています。
腕のボーンも調整して、自然な姿勢になるようにしています。

```typescript:src/features/emoteController/gestureController.ts
this._gestures.set('bow', {
  keyframes: [
    {
      duration: 1.0,
      bones: [
        {
          bone: 'spine',
          rotation: new THREE.Quaternion().setFromEuler(
            new THREE.Euler(0.25, 0, 0)
          ),
        },
        {
          bone: 'chest',
          rotation: new THREE.Quaternion().setFromEuler(
            new THREE.Euler(0.15, 0, 0)
          ),
        },
        {
          bone: 'neck',
          rotation: new THREE.Quaternion().setFromEuler(
            new THREE.Euler(0.12, 0, 0)
          ),
        },
        // 腕のボーンも調整（省略）
      ],
    },
  ],
  holdDuration: 1.0,
  closeEyes: true, // お辞儀中は目を閉じる
})
```


# LLMレスポンスからのモーショントリガー


LLMに感情とモーションのタグを出力させることで、キャラクターの表現を制御しています。

感情タグはAITuberKitのデフォルトで実装されています。以下のような感じでLLMからレスポンスが返ってきます。
```
[happy]ありがとうございます！
```

モーションタグがカスタマイズで追加したタグです。表情タグと同じようにレスポンスに返ってきます。
```
いらっしゃいませ！[bow]本日はどのような香りをお探しですか？
```

表情タグ・モーションタグは同時に返ってきた場合はどちらもトリガーされます。
[happy][bow]なら、笑顔でお辞儀するように実装しています。


また、システムプロンプトでは以下のように指示しています。

```typescript
`
## 感情表現
会話文の書式は以下の通りです。返答全体に対して最も適切な感情を1つだけ選び、先頭に感情タグを付けてください。
[{neutral|happy|angry|sad|relaxed|surprised}]{会話文}
`
```


# 表情とモーションのコンフリクト対策

表情とモーションは単純に両方を適用すると挙動がおかしくなることがあるため以下の制御を入れています。
例えばお辞儀のモーションの際には目を開いたままだと不自然だったため、`closeEyes: true`を設定してモーション制御側で目を閉じています。

`EmoteController`では以下のようにフラグを受け渡して制御しています。

```typescript:src/features/emoteController/emoteController.ts
public updateExpression(delta: number) {
  const isEmotionActive = this._expressionController.isEmotionActive
  // モーションが目を閉じていて、かつ表情がneutralなら瞬きをスキップ
  const skipAutoBlink =
    this._gestureController.isClosingEyes && !isEmotionActive
  this._expressionController.update(delta, skipAutoBlink)
}

public updateGesture(delta: number) {
  const isEmotionActive = this._expressionController.isEmotionActive
  // 表情がアクティブならモーションの目閉じをスキップ
  this._gestureController.update(delta, isEmotionActive)
}
```

表情の感情とモーションの目閉じは排他関係になってます。
感情が`neutral`のときはモーション側で目を閉じ、感情がアクティブなときはモーションの目閉じを無効化して表情側に制御を委ねます。


# おしまい

AIエージェントのフロントエンドにチャットUIを使用するのは非常に多いケースだと思いますが、こんな簡単なモデルでも動いているだけで生き生きとしている感じが出るのでとても面白いです。
ただモーションの制御は結構癖があるというか、どこをどう回転させればいいのかが結構難しいですね。
多分探せばモーション集なども販売されていたりすると思うので、複雑なモーションをさせる場合はそういったものを利用するのも手かと思います。
