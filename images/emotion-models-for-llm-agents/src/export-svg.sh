#!/bin/bash
# src/ の SVG を images/emotion-models-for-llm-agents/ に PNG で書き出す。
# 印刷で350dpi以上になるよう、SVG の大きさの2倍の解像度で書き出す。
# フォントにヒラギノを使うため、macOS の Google Chrome のヘッドレスモードで描画する。
#
#   bash export-svg.sh [SVG ファイル ...]   # 省略時は src/ の SVG をすべて書き出す
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$(dirname "$SRC_DIR")"
SCALE=2

if [ $# -eq 0 ]; then
  set -- "$SRC_DIR"/*.svg
fi

for svg in "$@"; do
  size=$(grep -oE '<svg[^>]*' "$svg" | grep -oE '(width|height)="[0-9]+"' | grep -oE '[0-9]+' | paste -sd, -)
  out="$OUT_DIR/$(basename "${svg%.svg}").png"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --window-size="$size" --force-device-scale-factor="$SCALE" \
    --screenshot="$out" "file://$(cd "$(dirname "$svg")" && pwd)/$(basename "$svg")" 2>/dev/null
  echo "wrote $(basename "$out") ($size x$SCALE)"
done
