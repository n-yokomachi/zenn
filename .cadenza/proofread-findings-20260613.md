# Proofread findings: articles/202606_eveng2_app.md

- Audit date: 2026-06-13
- Article language: ja
- Voice profile in use: no（cadenza ワークフロー外の記事）
- Sources consulted:
  - ~/work/workshop/eveng2 配下のソースコード（TONaRi / eg2-date-with-cool-skeleton / eg2-anger-management）
  - Even Hub SDK 型定義（`even_hub_sdk/dist/index.d.ts` の `OsEventTypeList` / `EventSourceType`）
  - `TONaRi/bridge/g2bridge/stt.py`（Whisper モデル名）、`eg2-anger-management/src/quotes.ts`（（伝）注記）
  - GitHub（`gh repo view` で両リポジトリの PUBLIC を確認）
  - images/202606_eveng2_app/（参照画像の存在確認）

## Summary

- Technical: 0 total（[WRONG]: 0 / [UNVERIFIED]: 0）
- Language: 13
- Voice profile: 0（プロファイルなし）
- 補足: 使用感セクションの体験談（配送期間、つけ心地、標準アプリの挙動等）は筆者の一次体験であり監査対象外とした。コード・SDK・公開情報で照合可能な技術的主張はすべて根拠と一致した。

## Technical accuracy

[WRONG] / [UNVERIFIED] に該当する findings はなし。主な照合結果（抜粋）:

- L122「Whisper V3 TurboでSTT」→ `stt.py:5` の `mlx-community/whisper-large-v3-turbo` と一致
- L130「文字起こしとエージェントへのリクエストは2段階」→ `bridge.ts` の `/stt` と `/ask` 分離実装と一致
- L132「会話がセッションとして継続」→ `bridge.ts:27-44` のセッション管理と一致
- L167「app.jsonのpermissionsが空」→ `eg2-anger-management/app.json` の `"permissions": []` と一致
- L168「ダブルタップで一時停止メニュー、スワイプでカーソル移動、タップで決定」→ `main.ts` のイベント配線と一致
- L169「（伝）の注記」→ `quotes.ts:7` の `traditional` フィールドと一致
- L185-186「SDKのSTT機能は使用不可・生PCMのみ」→ SDK 型定義にSTT APIなし、`audioPcm` イベントのみ。一致
- L191「入力イベントはタップ・ダブルタップ・上下スワイプだけ」→ `OsEventTypeList`（CLICK / DOUBLE_CLICK / SCROLL_TOP / SCROLL_BOTTOM ＋システムイベント）と一致
- L136 / L150 の GitHub リポジトリ → 両方 PUBLIC で実在
- L114 / L141 / L159 の画像 → `images/202606_eveng2_app/` に image2.jpeg / image3.gif / image4.gif すべて存在
  - （参考: image1.jpeg は現在記事中で未参照。意図的でなければ削除またはどこかで使用を）

## Language quality

### L14 — 表記ゆれ（数字の全角・半角）

- Quote: "３つほどちょっとしたアプリを開発してみて"
- Issue: 「３」が全角。記事内の他の数字は半角（L138「2つ目」、L152「3つ目」、L173「3つアプリ」）
- Suggested fix: "3つほど"

### L29 — 表記ゆれ（数の表記）

- Quote: "さらに一週間後くらいにR1が届きました"
- Issue: L24「2週間」と算用数字なのに対しここだけ漢数字。優先度低
- Suggested fix: "さらに1週間後くらいに"

### L38 — 漢字の誤用

- Quote: "ツルの根本のところと"
- Issue: 「根本」は「物事のおおもと」の意。物の付け根は「根元」
- Suggested fix: "ツルの根元のところと"

### L48 — 誤変換＋表記ゆれ（重要）

- Quote: "鶴の幅を変えるのは難しそう？"
- Issue: 「鶴」（鳥）は誤変換。さらに眼鏡のテンプルの表記が「ツル」（L38）/「鶴」（L48）/「つる」（L192）の3種混在
- Suggested fix: "ツルの幅を変えるのは難しそう？" とし、L192 も「ツル」に統一（全体で「ツル」推奨）

### L77 / L40 — 表記ゆれ（三点リーダ）

- Quote: L77 "あまり使わない・・・" / L40 "こすれてレンズが汚れる…"
- Issue: 「・・・」と「…」が混在。優先度低
- Suggested fix: 「…」に統一

### L97 — 不自然な日本語（「アプリ」の重複）

- Quote: "自分で作ったアプリもEven Hubからアプリをアップロードし、自分だけで使うことが可能です"
- Issue: 「アプリも…アプリを」が重複。「Even Hubから」も「に」が自然
- Suggested fix: "自分で作ったアプリをEven Hubにアップロードして、自分だけで使うことも可能です"

### L104 — 慣用句の誤記

- Quote: "そこだけちょっと融通が効かないなと思います"
- Issue: 慣用句としては「融通が利く／利かない」が標準表記
- Suggested fix: "融通が利かない"

### L112 / L121-122 — 表記ゆれ（MacBook）

- Quote: L112 "普段MacBookで" / L121 "音声情報をMacbookに転送" / L122 "Macbook内で"
- Issue: 「MacBook」と「Macbook」が混在。正式表記は MacBook
- Suggested fix: L121, L122 を "MacBook" に修正（あるいは処理フロー内は L126-128 に合わせて「Mac」でも可）

### L122 — 用語（任意）

- Quote: "Whisper V3 TurboでSTT"
- Issue: 誤りではないが、モデルの正式表記は「Whisper large-v3-turbo」。実体は `mlx-community/whisper-large-v3-turbo`
- Suggested fix: 任意。"Whisper large-v3-turbo" とするとより正確

### L126 — 指示対象の曖昧さ

- Quote: "アプリの実体は、EvenアプリとMacの常駐ブリッジの2層構成です"
- Issue: L63「Evenアプリ内での管理」では「Evenアプリ」＝スマホのコンパニオンアプリを指すが、ここでは自作のグラス側アプリを指しており、同じ語が別物を指している
- Suggested fix: "アプリの実体は、グラス側のEven HubアプリとMacの常駐ブリッジの2層構成です" など

### L173-174 — Zenn記法（空行）

- Quote: "…制約や気づきをまとめます。" の直後に ":::message"
- Issue: `:::message` の直前に空行がない。L154-155 では空行を入れており不統一。環境によっては段落に取り込まれて装飾が効かないリスクがある
- Suggested fix: L173 と L174 の間に空行を挿入

### L181 — 表記ゆれ（エミュレータ／シミュレータ）

- Quote: "SDKのエミュレータでは6枚くらいまでは表示できるため"
- Issue: L199 見出し・L201 では「シミュレータ（evenhub-simulator）」。公式パッケージ名も simulator
- Suggested fix: "SDKのシミュレータでは"

### L187 — 表記の不整合（MLX版Whisper）

- Quote: "PCMをそのままMacに転送してMLX版Whisperで文字起こしする構成にしました"
- Issue: L128 では「Macでローカル実行しているWhisper」と言い換え済みだが、こちらは「MLX版Whisper」のまま。意図的に残したのであれば対応不要
- Suggested fix: "PCMをそのままMacに転送して、Mac上のWhisperで文字起こしする構成にしました"

## Voice profile

該当なし（プロファイル未使用）。
