#!/usr/bin/env bash
# Đóng gói vi-humanizer thành dist/vi-humanizer.skill để dùng trên Claude Desktop
# hoặc claude.ai. Gói chỉ chứa SKILL.md cùng các thư mục mà skill cần khi chạy.
#
# Dùng: ./scripts/package-skill.sh
# Cần: python3, zip và unzip.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="$(mktemp -d)/vi-humanizer"
DIST="$ROOT/dist"

trap 'rm -rf "$(dirname "$STAGE")"' EXIT

python3 "$ROOT/scripts/validate-package.py"

mkdir -p "$STAGE" "$DIST"
cp "$ROOT/SKILL.md" "$STAGE/"
cp -R "$ROOT/profiles" "$ROOT/references" "$ROOT/calibration" "$STAGE/"

# Cấu trúc gói: vi-humanizer/SKILL.md cùng các thư mục con.
rm -f "$DIST/vi-humanizer.skill"
( cd "$(dirname "$STAGE")" && zip -qr "$DIST/vi-humanizer.skill" vi-humanizer -x '*.DS_Store' )

echo "Đã đóng gói: $DIST/vi-humanizer.skill"
unzip -l "$DIST/vi-humanizer.skill"
