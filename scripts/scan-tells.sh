#!/usr/bin/env bash
# Quét các pattern vi-humanizer quét được bằng regex, chạy trên chính văn bản của repo.
#
# Đây là bước tự soi mà AGENTS.md yêu cầu trước mỗi commit. Nó KHÔNG thay được
# việc đọc: phần lớn pattern (V1, V2, V3, V13, V19...) cần hiểu ngữ cảnh mới
# kết luận được. Script chỉ lo nhóm quét máy được, để mắt người dồn vào phần còn lại.
#
# Nhiều hit là dương tính giả có chủ đích: ví dụ trong phần định nghĩa pattern,
# trích dẫn trong log, và mục Lịch sử phiên bản đều thuộc ngoại lệ cổng thể loại.
# Đọc từng hit rồi mới sửa.
#
# Dùng: ./scripts/scan-tells.sh [file...]   (mặc định: mọi file nội dung trong repo)

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ $# -gt 0 ]; then
  FILES=("$@")
else
  FILES=(SKILL.md AGENTS.md README.md profiles/*.md references/*.md calibration/*.md)
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
scan "T4 chấm phẩy nối mệnh đề" '; (điều|việc) này'
scan "V10 một cách + tính từ" 'một cách [a-zà-ỹ]'
scan "V11 khung giả chủ ngữ" 'Điều quan trọng cần|Điều đáng chú ý là|Cần lưu ý rằng|Cần nhấn mạnh rằng|Có thể thấy rằng|Không thể phủ nhận rằng'
scan "V16 bị động có tác nhân" 'được [a-zà-ỹ]+ bởi'
scan "V15 chồng động từ rỗng" 'tiến hành thực hiện|thực hiện việc|triển khai thực hiện'
scan "V12 trạng từ nối đầu dòng" '^(Hơn nữa|Ngoài ra|Bên cạnh đó|Đồng thời|Thêm vào đó|Mặt khác|Tuy nhiên|Do đó|Vì vậy|Chính vì thế|Nhìn chung),'
scan "V18 điều này nối mệnh đề" ', (điều|việc) này [a-zà-ỹ]'
scan "V9 cụm giới từ nặng mở câu" '^\*{0,2}(Thông qua|Trong quá trình|Với sự|Trên cơ sở|Nhằm mục đích|Tại thời điểm|Trong khuôn khổ)'

if [ "$hits" -eq 0 ]; then
  echo "Không có hit nào quét máy được."
else
  printf '\n%s hit. Đọc từng chỗ với cổng thể loại trước khi sửa.\n' "$hits"
fi
