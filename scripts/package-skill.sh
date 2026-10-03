#!/usr/bin/env bash
# Đóng gói vi-humanizer thành hai artifact từ cùng một public payload:
# - dist/vi-humanizer.skill cho Skills CLI và cài đặt skill thông thường;
# - dist/vi-humanizer-claude-org.zip để upload skill vào Claude Org.
# Cả hai chứa LICENSE, SKILL.md cùng các thư mục mà skill cần khi chạy.
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
CANDIDATE_ORG_ARCHIVE="$ARCHIVE_STAGE/vi-humanizer-claude-org.zip"
RELEASE_ORG_ARCHIVE="$DIST/vi-humanizer-claude-org.zip"

cp -P "$ROOT/SKILL.md" "$ROOT/LICENSE" "$STAGE/"
cp -RP "$ROOT/profiles" "$ROOT/references" "$ROOT/calibration" "$STAGE/"
cp -RP "$ROOT/agents" "$ROOT/assets" "$STAGE/"
mkdir -p "$STAGE/advisor"
cp -P "$ROOT/advisor/__init__.py" "$ROOT/advisor/__main__.py" "$ROOT/advisor/cli.py" "$ROOT/advisor/client.py" "$ROOT/advisor/models.py" "$ROOT/advisor/questions.py" "$STAGE/advisor/"
python3 "$ROOT/scripts/validate-package.py" --payload-root "$STAGE"

# Cấu trúc gói: vi-humanizer/SKILL.md cùng các thư mục con.
( cd "$STAGE_PARENT" && zip -qr "$CANDIDATE_ARCHIVE" vi-humanizer -x '*.DS_Store' )
python3 "$ROOT/scripts/validate-package.py" \
  --archive "$CANDIDATE_ARCHIVE" \
  --payload-root "$STAGE"
( cd "$STAGE" && zip -qr "$CANDIDATE_ORG_ARCHIVE" . -x '*.DS_Store' )
python3 "$ROOT/scripts/validate-package.py" \
  --archive "$CANDIDATE_ORG_ARCHIVE" \
  --payload-root "$STAGE" \
  --root-layout
mv -f "$CANDIDATE_ARCHIVE" "$RELEASE_ARCHIVE"
mv -f "$CANDIDATE_ORG_ARCHIVE" "$RELEASE_ORG_ARCHIVE"

echo "Đã đóng gói: $RELEASE_ARCHIVE"
unzip -l "$RELEASE_ARCHIVE"
echo "Đã đóng gói cho Claude Org: $RELEASE_ORG_ARCHIVE"
unzip -l "$RELEASE_ORG_ARCHIVE"
