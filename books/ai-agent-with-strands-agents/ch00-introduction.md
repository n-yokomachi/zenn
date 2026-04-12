---
title: "はじめに"
---

本書は、AWSのサービスを使ってパーソナルAIエージェントを構築する方法を解説する技術書です。

## 本書で使用する技術スタック

本書では、以下の技術を中心に使用します。

| 技術 | 概要 |
|---|---|
| Strands Agents SDK | AWSが公開したオープンソースのAIエージェントフレームワーク（Python） |
| Amazon Bedrock | AWSが提供するフルマネージドのLLMサービス。本書ではClaude Haiku 4.5をLLMとして使用します |
| Amazon Bedrock AgentCore | エージェントのランタイム、メモリ管理、ツール連携などをマネージドで提供するサービス |
| AgentCore Gateway | MCP（Model Context Protocol）に対応したツール連携の仕組み |
| AgentCore Memory | エージェントの短期記憶・長期記憶を管理するサービス |
| AWS Lambda | ツールのバックエンド処理を実行するサーバーレスコンピューティング基盤 |

フロントエンドの構築（第6章）では、Next.jsとVRM（3Dアバター）も使用します。

## サンプルコード

本書のサンプルコードは以下のGitHubリポジトリで公開しています。

https://github.com/n-yokomachi/building-ai-agents-on-aws-samples

各章に対応するディレクトリにコードを配置しています。

| ディレクトリ | 対応する章 |
|---|---|
| `ch01/` | 第1章: はじめてのAIエージェント |
| `ch02/` | 第2章: エージェントの「脳」を作る |
| `ch03/` | 第3章: エージェントに「手」を与える |
| `ch04/` | 第4章: エージェントに「記憶」を与える |
| `ch05/` | 第5章: エージェントを「分業」させる |
| `ch06/` | 第6章: エージェントに「身体」を与える |
| `ch07/` | 第7章: エージェントを「自律」させる |
| `ch08/` | 第8章: エージェントを「育てる」 |

本文中のコードブロックには、対応するリポジトリ上のファイルパスを記載しています。

## 前提知識

本書を読むにあたって、以下の知識を前提としています。

- Pythonの基本文法（関数定義、クラス、モジュールのインポート）
- ターミナル操作（コマンドの実行、ディレクトリ移動）
- Web APIの基礎（HTTPメソッド、JSON）
- Gitの基本操作（clone、commit、branch）

以下については本書内で解説するため、事前知識は不要です。

- AWSの各サービス（Amazon Bedrock、AgentCore）
- LLM・AIエージェントの概念と実装
- MCP（Model Context Protocol）
- フロントエンド実装（第6章のみ）

## 開発環境

| 項目 | 要件 |
|---|---|
| Python | 3.12以上 |
| Node.js | 22以上（第6章のみ） |
| AWSアカウント | Anthropicモデルのユースケース提出が完了していること |
| AWS CLI | v2 |
| OS | macOS / Linux / WSL2 |

### Windowsを使用している場合

本書のハンズオンはUnix系の環境を前提としています。Windowsを使用している場合は、以下のいずれかの方法で環境を用意してください。

WSL2（Windows Subsystem for Linux）をインストールすると、Windows上でLinux環境を利用できます。Microsoft Storeからインストール可能で、本書のすべての内容をそのまま実行できます。

ローカルに環境を構築せずに進めたい場合は、GitHub Codespacesも選択肢になります。サンプルコードのリポジトリをCodespacesで開けば、ブラウザ上でPythonとAWS CLIが利用可能な開発環境がすぐに立ち上がります。AWSの認証情報はCodespaces内のターミナルで `aws configure` を実行して設定してください。
