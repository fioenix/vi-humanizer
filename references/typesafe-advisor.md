# Cố vấn TypeSafe/Jev tùy chọn

File này chỉ dùng khi host có thể chạy Python 3.10+, gọi HTTPS và inject secret qua environment.
Thiếu một trong ba năng lực đó thì tiếp tục bằng core Markdown; đây là chế độ được hỗ trợ, không
phải lỗi cài đặt.

## Ai làm gì

- Host LLM chạy cổng thể loại và V20, rồi tạo trước một đến ba candidate.
- Advisor gửi source span, context tối thiểu, intent, base-profile ID và candidate đã có tới Jev.
- Jev trả xác suất cho từng phán đoán hoặc xếp hạng một shortlist. Jev không sinh hay sửa câu chữ.
- Agent đọc signal, tự quyết định giữ hay sửa và chịu trách nhiệm cho bản cuối.

Chỉ dùng advisor cho `lexically_incomplete` và `unnatural_collocation` của V20. Không dùng signal
này làm hard gate, không tự thay câu và không mở rộng nó sang pattern hoặc style khác.

## Xác định host đang ở trạng thái nào

1. Không có `TYPESAFE_API_KEY`: `core_only`. Đừng nhắc người dùng cài TypeSafe trong mỗi lượt.
2. Có key nhưng chưa có typed response hợp lệ: `advisor_unchecked`.
3. Probe thật trả đúng model `jev-1.13.0` và đúng schema: `advisor_verified` cho lần quan sát đó.

TypeSafe agent skill chỉ cung cấp tài liệu cho coding agent; nó không tự tạo runtime connector.
Tương tự, việc ZIP Claude Org chứa thư mục `advisor/` không chứng minh Claude Org cho phép chạy
Python, gọi mạng hoặc inject secret.

## Thiết lập trên host local

Lấy API key từ TypeSafe rồi lưu bằng secret manager của host. Khi mở process chạy agent, inject
key thành biến `TYPESAFE_API_KEY`; không dán key vào prompt, file repo, command argument hoặc ZIP.
Advisor không cần `typesafe-sdk` và không có cờ enable thứ hai.

Với shell POSIX, có thể inject tạm cho đúng session mà không ghi key vào history:

```bash
read -r -s TYPESAFE_API_KEY
export TYPESAFE_API_KEY
```

Từ thư mục gốc của skill, chạy:

```bash
python3 -m advisor probe
```

- Exit `0`, `state=advisor_verified`: host vừa quan sát được một typed response thật.
- Exit `2`, `state=core_only`: process không nhận được key.
- Exit `2`, `state=advisor_unchecked`: đã thử gọi nhưng auth, network, quota, model hoặc response
  chưa đạt contract. Core vẫn tiếp tục.

Muốn tắt advisor, bỏ `TYPESAFE_API_KEY` khỏi environment của process. Không sửa file cấu hình.

## Gọi assess

Chỉ gọi sau khi Agent đã xác định V20 và tạo candidate. Truyền JSON qua stdin để prose không xuất
hiện trong command history:

```bash
python3 -m advisor assess < /duong/dan/toi/v20-case.json
```

Input tối thiểu:

```json
{
  "case_id": "v20_case_01",
  "candidates": {
    "candidate_1": {"text": "Câu này đọc lên thấy hụt hẫng."}
  },
  "context": {"after": "", "before": ""},
  "current_intent": "Giữ giọng nhận xét trực tiếp.",
  "genre": "blog-ca-nhan",
  "schema_version": "1.0.0",
  "source": {"pattern": "V20", "text": "Câu này đọc lên thấy hụt."}
}
```

`genre` chỉ nhận `blog-ca-nhan` hoặc `ky-thuat-doanh-nghiep`; candidate là object keyed bằng stable
ID. CLI reject field lạ và reject trước network nếu source/candidate vượt 1.000 ký tự, context
trước/sau vượt 2.000 ký tự mỗi phần hoặc intent vượt 1.000 ký tự.
Provider response lớn hơn 1 MiB bị coi là không hợp lệ; advisor không follow HTTP redirect.

Output checked chỉ có binding, version, model, usage và các score sau:

- source: `lexically_incomplete`, `unnatural_collocation`;
- candidate: `fixes_issue`, `preserves_meaning_and_nuance`, `fits_voice_and_genre`;
- safety: thêm claim, đổi actor/time, causality/commitment, order/concurrency, register và process
  metadata.

Signal không phải action. Nếu source, context, intent, genre hoặc candidate đổi, so
`case_binding`; binding cũ không còn hiệu lực.

## Gọi rank

Chỉ khi Agent đã tự lập shortlist gồm hai hoặc ba candidate đủ chuẩn, thêm
`eligible_candidate_ids` rồi chạy:

```bash
python3 -m advisor rank < /duong/dan/toi/v20-shortlist.json
```

Ranking không có `keep_original` hoặc `none_of_candidates`. Nó chỉ so các candidate đã được Agent
cho phép; quyết định có sửa source hay không vẫn thuộc Agent.

## Ranh giới dữ liệu

- Chỉ gửi source span và context nhỏ nhất còn đủ nghĩa; không gửi toàn tài liệu.
- Không gửi protected region, secret, nhãn đúng/sai, baseline, provenance hoặc định danh người dùng.
- CLI không ghi log/file mặc định; stdout không lặp raw prose, provider body hay exception.
- Người dùng vẫn phải tự xem chính sách dữ liệu của TypeSafe trước khi opt-in gửi văn bản.
