#!/usr/bin/env bash
# Tìm những dấu hiệu có thể quét bằng biểu thức chính quy trong văn bản của repo.
#
# Đây là một bước rà sơ bộ trước khi phát hành. Kết quả không thay cho việc đọc:
# phần lớn pattern, như V1, V2, V3, V13 và V19, chỉ xác định được khi có ngữ cảnh.
#
# Kết quả có thể trỏ vào ví dụ, trích dẫn hoặc lịch sử phiên bản. Đọc mục
# **Không flag** của pattern liên quan trước khi sửa.
#
# Dùng: ./scripts/scan-tells.sh [file...]   (mặc định: mọi file nội dung trong repo)

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ $# -gt 0 ]; then
  FILES=("$@")
else
  FILES=(SKILL.md AGENTS.md README.md profiles/*.md references/*.md calibration/*.md agents/*.yaml .claude-plugin/*.json)
fi

hits=0
scan() {
  local label="$1" pattern="$2" filter="${3:-}"
  local out
  if [ -n "$filter" ]; then
    out=$(grep -nE "$pattern" "${FILES[@]}" 2>/dev/null | grep -v "$filter")
  else
    out=$(grep -nE "$pattern" "${FILES[@]}" 2>/dev/null)
  fi
  if [ -n "$out" ]; then
    printf '\n### %s\n%s\n' "$label" "$out"
    hits=$((hits + $(printf '%s\n' "$out" | wc -l)))
  fi
}

scan "T2 em dash (loại bỏ mention trong backtick)" '—' '`—`'
scan "T4 dấu phẩy trước và" ', và '
scan "T5 nhãn khái quát rồi diễn giải" '^#{1,6} [^:]{2,50}: |^[[:space:]]*[-*] \*\*[^*]+:\*\*'
scan "V11 câu dẫn không thêm thông tin" 'Điều quan trọng cần|Điều đáng chú ý là|Cần lưu ý rằng|Cần nhấn mạnh rằng|Có thể thấy rằng|Không thể phủ nhận rằng'
scan "V16 bị động có tác nhân" 'được [a-zà-ỹ]+ bởi'
scan "V15 chồng động từ rỗng" 'tiến hành thực hiện|thực hiện việc|triển khai thực hiện'
scan "V12 trạng từ nối đầu dòng" '^(Hơn nữa|Ngoài ra|Bên cạnh đó|Đồng thời|Thêm vào đó|Mặt khác|Tuy nhiên|Do đó|Vì vậy|Chính vì thế|Nhìn chung),'
scan "V18 điều này nối mệnh đề" ', (điều|việc) này [a-zà-ỹ]'
scan "V9 cụm giới từ nặng mở câu" '^\*{0,2}(Thông qua|Trong quá trình|Với sự|Trên cơ sở|Nhằm mục đích|Tại thời điểm|Trong khuôn khổ)'

if [ "$hits" -eq 0 ]; then
  echo "Không tìm thấy dấu hiệu nào trong nhóm có thể quét tự động."
else
  printf '\nTìm thấy %s chỗ. Kiểm tra thể loại và ngữ cảnh trước khi sửa.\n' "$hits"
fi
