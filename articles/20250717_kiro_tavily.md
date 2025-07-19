---
title: "KiroにTavily Remote MCPを設定する"
emoji: "👻"
type: "tech"
topics: [aws,kiro,mcp,Tavily]
published: true
---

:::message
この記事は主に人間が書き、記事の校正に生成AIを使用しています。
また、本記事の内容はKiroの「プレビュー版」を扱っていることに注意してください。
:::

# はじめに
みなさんKiro、触っていますか？
AWSからリリースされたAI IDE「Kiro」ですが、
リリースから２日経った現在、新規のダウンロードはWaitlist制になってしまいました。
https://kiro.dev/

私は幸いリリース直後にダウンロードだけはしていたので使えています。
触っているだけでなかなか面白いので、興味のある方は今のうちにWaitlistに登録しておくのがおすすめです。

で、今回はタイトルのとおりKiroにWeb検索向けMCPツールである[Tavily MCP](https://github.com/tavily-ai/tavily-mcp)を導入します。

Kiroには2025年7月現在、ビルトインの検索ツールがないようなので、
最新の情報を検索させたり参照させながら開発をするには別途Web検索用のツールが必要になります。

※Add ContextからURLを指定して参照させることは可能です。
![](https://storage.googleapis.com/zenn-user-upload/23cc741b187b-20250717.png)


そんな中、あまりにもちょうど良いタイミングでWeb検索ツールといえばのTavilyからリモートMCPが公開されました。
リモートMCPなので設定もめちゃくちゃ簡単です。


# 設定

## 1. TavilyからAPIキーを発行

[Tavily](https://app.tavily.com/home)にログインします。
ログインするとホーム画面でAPIキーの発行が可能です。
![](https://storage.googleapis.com/zenn-user-upload/89139be91ea6-20250717.png)


## 2. KiroのMCP設定

続いてKiro側でMCPを設定します。
Kiroでは２か所からMCPを設定できます。
１つはSettingsのMCPの項目から
![](https://storage.googleapis.com/zenn-user-upload/29f2446d042b-20250717.png)

もう１つはサイドバーでKiroメニューを開き、MCP Server設定を開くと表示されます。
![](https://storage.googleapis.com/zenn-user-upload/5f52bd873f00-20250717.png)

で画像を見てお気づきかもしれませんが、KiroではUser単位（Kiroそのもの）の設定と、Workspace単位での設定が可能です。

設定ファイルの場所はWindowsの場合👇
User単位の設定は、C:\Users\PC_User\\.kiro\settings\mcp.json
Workspace単位の設定は、そのルートディレクトリ配下の\\.kiro\settings\mcp.json

お決まりでどのプロジェクトでも使うMCPはUser単位で設定、
プロジェクト特有のMCPや、他の人と設定を共有したいときなどはWorkspace単位での設定と使い分けられます。

設定する内容は以下のような形式になります。
autoApproveにツール名を入れると、ツール実行時のユーザー確認をスキップすることができます。

```javascript: mcp.json
"tavily-remote-mcp": {
    "command": "npx -y mcp-remote https://mcp.tavily.com/mcp/?tavilyApiKey={your_api_key}",
    "args": [],
    "env": {},
    "disabled": false,
    "autoApprove": []
}
```

環境によっては上の設定だと動作しないこともあるようです。
その場合以下の設定も試してみることをお勧めします。
※atmanさんからコメントで情報提供いただきました！ありがとうございます！
```javascript: mcp.json
{
  "mcpServers": {
    "tavily-remote-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.tavily.com/mcp/?tavilyApiKey={your_api_key}"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```


設定はこれだけです。
ちゃんとTavilyのサーチツールを使えていますね。

![](https://storage.googleapis.com/zenn-user-upload/030972bbee33-20250717.png)
