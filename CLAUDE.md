# プロジェクトルール

## サブエージェントのモデル

このプロジェクトのサブエージェントは、`.claude/settings.json` の `env.CLAUDE_CODE_SUBAGENT_MODEL` で最高モデル（2026-07 時点では `fable`）に固定している。書籍のレビュー・ファクトチェック・書誌検証を下位モデルで実行させないための設定。

- ユーザースコープの `~/.claude/settings.json` は `CLAUDE_CODE_SUBAGENT_MODEL` を `sonnet` に設定している。設定の適用順は user → project → local なので、**プロジェクト側の値が勝つ**
- **Agent 呼び出しの `model` パラメータでは上書きできない**。環境変数のほうが強く、`model: "fable"` を渡してもサブエージェントは `claude-sonnet-5` で実行される（2026-07-28 に実測で確認）
- グローバル設定は他プロジェクトに影響するため書き換えない
- **モデルが実際に何で動いたかは、`~/.claude/projects/<sanitized-cwd>/<session-id>/subagents/agent-*.meta.json` の `model` フィールドで確認できる**。パラメータを渡したことを実行されたことと同一視せず、記録で確かめること

## Git 運用

- `git push` は**絶対にユーザーの明示的な指示があるまで実行しない**。コミットまでは許可された範囲で行ってよいが、リモートへの反映は必ずユーザーに確認する
- コミットメッセージに「Co-Authored-By」「Claude Code」「Claude」「Anthropic」などのモデル名・ツール名を著述者として入れない
