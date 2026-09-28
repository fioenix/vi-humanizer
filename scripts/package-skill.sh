#!/usr/bin/env bash
# Đóng gói vi-humanizer thành dist/vi-humanizer.skill để dùng trên Claude Desktop
# hoặc claude.ai. Gói chỉ chứa SKILL.md cùng các thư mục mà skill cần khi chạy.
#
# Dùng: ./scripts/package-skill.sh
# Cần: python3, zip và unzip.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE_PARENT="$(mktemp -d)"
STAGE="$STAGE_PARENT/vi-humanizer"
DIST="$ROOT/dist"
ARCHIVE_STAGE=""

cleanup() {
  rm -rf "$STAGE_PARENT"
  if [[ -n "$ARCHIVE_STAGE" ]]; then
    rm -rf "$ARCHIVE_STAGE"
  fi
}
trap cleanup EXIT

python3 "$ROOT/scripts/validate-package.py"

mkdir -p "$STAGE" "$DIST"
ARCHIVE_STAGE="$(mktemp -d "$DIST/.vi-humanizer-package.XXXXXX")"
CANDIDATE_ARCHIVE="$ARCHIVE_STAGE/vi-humanizer.skill"
RELEASE_ARCHIVE="$DIST/vi-humanizer.skill"

cp -P "$ROOT/SKILL.md" "$STAGE/"
cp -RP "$ROOT/profiles" "$ROOT/references" "$ROOT/calibration" "$STAGE/"
python3 "$ROOT/scripts/validate-package.py" --payload-root "$STAGE"

# Cấu trúc gói: vi-humanizer/SKILL.md cùng các thư mục con.
( cd "$STAGE_PARENT" && zip -qr "$CANDIDATE_ARCHIVE" vi-humanizer -x '*.DS_Store' )
python3 "$ROOT/scripts/validate-package.py" \
  --archive "$CANDIDATE_ARCHIVE" \
  --payload-root "$STAGE"
mv -f "$CANDIDATE_ARCHIVE" "$RELEASE_ARCHIVE"

echo "Đã đóng gói: $RELEASE_ARCHIVE"
unzip -l "$RELEASE_ARCHIVE"
