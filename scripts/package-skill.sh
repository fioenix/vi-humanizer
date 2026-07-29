#!/usr/bin/env bash
# Đóng gói vi-humanizer thành dist/vi-humanizer.skill để cài vào Claude Desktop
# hoặc claude.ai. Chỉ gói phần runtime; README, AGENTS.md, manifest plugin và
# scripts không thuộc gói vì Claude Desktop chỉ nạp SKILL.md cùng các file nó trỏ tới.
#
# Dùng: ./scripts/package-skill.sh
# Cần: python3 + pyyaml (script tự dùng uv nếu có), và skill-creator của Anthropic.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="$(mktemp -d)/vi-humanizer"
DIST="$ROOT/dist"

trap 'rm -rf "$(dirname "$STAGE")"' EXIT

python3 "$ROOT/scripts/validate-package.py"

mkdir -p "$STAGE" "$DIST"
cp "$ROOT/SKILL.md" "$STAGE/"
cp -R "$ROOT/profiles" "$ROOT/references" "$ROOT/calibration" "$STAGE/"

# Zip thẳng, không phụ thuộc skill-creator. Cấu trúc gói: vi-humanizer/SKILL.md + thư mục con.
rm -f "$DIST/vi-humanizer.skill"
( cd "$(dirname "$STAGE")" && zip -qr "$DIST/vi-humanizer.skill" vi-humanizer -x '*.DS_Store' )

echo "Đã đóng gói: $DIST/vi-humanizer.skill"
unzip -l "$DIST/vi-humanizer.skill"
