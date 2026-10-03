# Kiểm local trước khi phát hành — 2026-10-03

Phạm vi lượt này: Codex, bản local 0.9.7 chưa phát hành. Không chạy agent từ terminal,
không commit, push hoặc submit. Claude được tạm gác theo yêu cầu của maintainer.

## Metadata và đóng gói

- Codex dùng violet `#9750C4` cho `brandColor`, mint `#7FE2CE` cho `brandColorDark`;
  thêm `composerIconDark` trỏ tới icon tối. SVG vẫn có nền trong suốt.
- Metadata skill độc lập chỉ có một trường màu được hỗ trợ, dùng violet.
- Tương phản tính theo luminance WCAG: violet trên trắng **4.929:1**;
  mint trên `#212121` **10.483:1**, vượt mức 2:1 của checklist Codex.
- Suite đóng gói: **37 test, OK**; log local `output/marketplace-final-tests.log`.
  Có ca kiểm màu từ manifest trong archive thực tế.
- `python3 scripts/validate-package.py`: hợp lệ, 55 pattern.
- `git diff --check`: exit 0.
- Manifest trong `dist/vietnamizer-plugin.zip` đã được đọc lại, có đúng hai màu trên.
  Archive tên cũ trong `dist/` không thuộc bản kiểm này.

SHA-256 của archive hiện tại (khác snapshot trước khi chỉnh màu):

| Archive | SHA-256 |
|---|---|
| `vietnamizer.skill` | `44950368e9cc016427b55deaaf2cccb7d8e5cbea08348a10c9a564145e8fc0d8` |
| `vietnamizer-claude-org.zip` | `76a7811691a4fc0bdfa6862c61a78cd6f588df39ec4685581caed8f54efc605e` |
| `vietnamizer-plugin.zip` | `db5bed005ff957fa8744eafda34467733f98731ee649fa2d187617cef7cd4b12` |

## Ba demo trực tiếp trong phiên Codex

Agent đọc root skill, resolver và các profile/style card liên quan rồi biên tập ngay
trong phiên hiện tại. Đây là demo cùng phiên, không phải phép thử mù hoặc lần gọi
plugin đã cài qua giao diện native. Không gọi TypeSafe trong các demo.

1. Kể trải nghiệm:
   - Trước: “Đã thử ba cách mà vẫn không giải quyết vấn đề.”
   - Sau: “Đã thử ba cách mà vẫn không giải quyết được vấn đề.”
   - V1: chỉ thêm “được”, giữ số cách và không thêm nguyên nhân.
2. Chat công việc:
   - Trước và sau: “Tôi rời công ty lúc sáu giờ.”
   - Giữ nguyên theo trường hợp loại trừ V20; không đổi giờ hoặc đại từ.
3. README:
   - Trước: “Cách xử lý đơn giản nhất tăng số worker.”
   - Sau: “Cách xử lý đơn giản nhất là tăng số worker.”
   - V3: chỉ thêm “là”; giữ thuật ngữ và khối code dưới đây từng byte.

```bash
WORKERS=3 ./run-worker.sh --dry-run
```

Kết quả lưu ở `output/marketplace-demos.json`. Kiểm tất định xác nhận ba phép thay đổi
đúng như trên, bao gồm đối chiếu byte của khối code. Kiểm này không thay thế đánh giá
độc lập chất lượng ngôn ngữ.

## Giới hạn và việc còn chờ

- Harness hiện tại có skill TypeSafe, nên chưa chứng minh được hành vi khi skill
  hoàn toàn vắng mặt. “Không gọi TypeSafe” không đồng nghĩa “đã test harness thiếu TypeSafe”.
- Công cụ thao tác native bị từ chối truy cập app Codex. Không dùng cách khác để vượt
  hạn chế đó. Bản `output/wordmark-review.html` chỉ preview tài sản sáng/tối,
  không phải bằng chứng UI marketplace hay plugin native đã hiển thị đúng.
- Còn review native bởi maintainer, ca harness không có TypeSafe, tích hợp GitHub/CI
  trên commit phát hành, kiểm URL public và portal trước khi gửi.
- Các thay đổi vẫn chưa commit; không coi bản local là bản đã phát hành.

Nguồn yêu cầu màu: [OpenAI plugin submission](https://developers.openai.com/plugins/deploy/submission).
