#!/usr/bin/env bash
set -euo pipefail

# 引数: 実行ファイルパス (デフォルト: ./mpiemses3D)
EXEC=${1:-./mpiemses3D}

# 移動対象の gprof ファイル名 (デフォルト: gprof.txt)
GPFILE=${2:-gprof.txt}

# バージョン取得
raw=$("$EXEC" --version | head -n1 | tr -d '[:space:]')
VERSION=${raw%%-*}

# ホスト名取得
HOST=$(hostname)

# プロジェクトルートと実験名を自動検出
ROOT=$(git -C "$(dirname "${BASH_SOURCE[0]}" )/.." rev-parse --show-toplevel)
EXP=$(basename "$PWD")

# 移動先ディレクトリ
DEST_DIR="$ROOT/results/$EXP"
mkdir -p "$DEST_DIR"

# gprof ファイルの存在確認
if [ ! -f "$GPFILE" ]; then
  echo "Error: $PWD/$GPFILE が見つかりません。" >&2
  exit 1
fi

# 移動
mv "$GPFILE" "$DEST_DIR/gprof_${VERSION}_${HOST}.txt"

echo "✅ $GPFILE → $DEST_DIR/gprof_${VERSION}_${HOST}.txt に移動しました。"
