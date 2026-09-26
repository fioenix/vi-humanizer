<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.0.1
- Modified constraints:
  - Evaluation traceability now distinguishes pre-policy judgment runs from policy-applied reports
- Added sections: none
- Removed sections: none
- Deferred items: none
-->
# Constitution của vi-humanizer

## Core Principles

### I. Bằng chứng tiếng Việt đứng trước convention

Mỗi quy tắc MUST mô tả một lỗi tiếng Việt cụ thể, giải thích vì sao đó là lỗi, nêu cách sửa
và chỉ rõ khi nào MUST NOT flag. Quy tắc từ humanizer tiếng Anh, nhận định chung về model và
lựa chọn phong cách không tự trở thành bằng chứng. Nguồn bên ngoài MUST được ghi trong
`README.md` đúng với mức độ tin cậy; suy luận MUST được gọi đúng là suy luận.

### II. Giữ nghĩa và giọng trước khi làm câu hay hơn

Mỗi edit MUST giữ dữ kiện, chủ thể, thời điểm, quan hệ nhân quả, mức chắc chắn, mức cam kết,
thứ tự, quan hệ đồng thời, thể loại và giọng ổn định của bản gốc, trừ khi yêu cầu hiện tại của
người dùng chủ động thay đổi một yếu tố. Edit không gọi tên được pattern hoặc không loại trừ
được mục **Không flag** MUST bị bỏ hoặc chuyển cho người xem. Bản viết lại trôi chảy nhưng đổi
nghĩa vẫn là lỗi.

### III. Tách quy tắc chung khỏi profile thể loại

V-series và T-series trong `SKILL.md` MUST chỉ chứa những lỗi áp dụng được trên mọi thể loại
mà cổng đầu vào cho phép. Phán đoán phụ thuộc thể loại, người đọc hoặc thanh ngữ vực MUST nằm
trong profile tương ứng. Chỉ được chuyển pattern qua ranh giới này khi có bằng chứng gắn nhãn,
các ca chống sửa quá tay và thay đổi đồng bộ trong inventory của `README.md`.

### IV. Hiệu chỉnh từ bằng chứng có nhãn

Mọi thay đổi quy tắc dùng chung MUST bắt đầu từ bằng chứng ở đơn vị nhỏ nhất còn đủ nghĩa:
đoạn gốc, edit đề xuất, ngữ cảnh, phán đoán mong đợi, nguồn nhãn và pattern liên quan. Sở thích
cá nhân MUST nằm trong hồ sơ riêng của đúng người dùng, không nằm trong calibration log dùng
chung. Ngưỡng số MUST được chọn trên tập phát triển có nhãn và đánh giá trên tập holdout tách
biệt; cùng một ca MUST NOT vừa dùng để chỉnh ngưỡng vừa dùng để chứng minh ngưỡng.

### V. Giữ skill Markdown tự đứng được

`SKILL.md` và các profile MUST dùng được mà không cần build, dịch vụ mạng hoặc secret. External
evaluator như TypeSafe MAY bổ sung một lớp kiểm tra tùy chọn, nhưng khi dịch vụ thiếu key, timeout
hoặc lỗi thì quy trình Markdown hiện tại vẫn MUST chạy được và kết quả MUST ghi là *chưa kiểm tra*,
không phải *pass*. Tích hợp tùy chọn MUST NOT làm gói skill phụ thuộc một repo local khác.

## Ràng buộc về gói và dữ liệu

- `SKILL.md` là nguồn chuẩn cho workflow, V-series và T-series.
- Số hiệu V, T, B và K MUST liên tục. Khi thêm, bỏ hoặc đổi số pattern, `README.md` MUST đổi
  trong cùng commit.
- `metadata.version` trong `SKILL.md`, mục lịch sử mới nhất của `README.md` và
  `.claude-plugin/plugin.json` MUST giống nhau.
- Giới hạn dòng giữ nguyên: `SKILL.md` 550, profile blog 320, profile kỹ thuật 220.
- Production evaluator MUST chỉ gửi phần văn bản cần cho phán đoán. Raw prose MUST NOT xuất
  hiện trong telemetry hoặc báo cáo health. Lọc credential không thay thế cho phân loại dữ liệu
  và tối thiểu hóa trường gửi đi.
- Mọi kết quả eval MUST ghi model version và corpus version. Judgment run tạo trước khi fit policy
  MUST ghi evaluation-config version và MUST ghi `policy_version=null`; report hoặc run áp dụng
  policy MUST ghi decision-policy version. Typed output chỉ đảm bảo interface, không chứng minh
  phán đoán là đúng.

## Cổng phát triển và phát hành

1. Hành vi mới bắt đầu từ một ca kiểm thử đỏ và test được độc lập. Parsing, tính toán và policy
   tất định nằm trong code; model chỉ làm phán đoán ngữ nghĩa.
2. Mỗi task MUST tạo một deliverable review được và có verification riêng. Checkbox không kèm
   output mới của lệnh kiểm tra không phải bằng chứng.
3. Behavioral eval MUST báo harmful-edit recall, valid-edit false-block rate, review rate, lỗi
   dịch vụ, latency và cost. Số lượt guard bắn chưa chứng minh guard đúng.
4. Thay đổi dùng external model MUST bắt đầu ở shadow mode. Chỉ được review, loại hoặc hoàn edit
   tự động sau khi có bằng chứng trên holdout và nhãn hậu kiểm từ lượt thật.
5. Trước khi phát hành, MUST chạy và đọc output của `python3 scripts/validate-package.py`,
   `npx skills add . --list` và `claude plugin validate .`. Sau đó cài lại gói cho mọi runtime
   đang dùng bản chép và đối chiếu bytes đã cài.

## Governance

Constitution này chi phối spec, plan và implementation trong repo. `AGENTS.md` vẫn là hợp đồng vận
hành; nếu hai tài liệu xung đột thì MUST dừng và giải quyết trước khi làm tiếp. Mỗi amendment cần
lý do bằng văn bản, impact report, owner approval và semantic version bump: MAJOR khi thay đổi
không tương thích một principle, MINOR khi thêm hoặc mở rộng governance, PATCH khi chỉ làm rõ.
Mọi spec và review MUST kiểm tra các principle này. Complexity không truy ngược được tới outcome
hoặc acceptance criterion MUST bị bỏ.

**Version**: 1.0.1 | **Ratified**: 2026-09-26 | **Last Amended**: 2026-09-26
