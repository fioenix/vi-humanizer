# Quickstart: Kiểm chứng multi writing style

## 1. Preconditions

- Branch: `codex/003-multi-writing-style`
- Pattern inventory vẫn là V1–V22, T1–T6, B1–B17, K1–K6.
- Feature 002 report vẫn là `collect_more_labels`; không có runtime call tới TypeSafe.
- Fixture chỉ dùng nội dung trung tính/public.

## 2. Contract RED trước implementation

Trước khi thêm registry, validator phải thất bại vì chưa có `references/bo-giai-phong-cach.md` hoặc thiếu canonical card:

```bash
python3 scripts/validate-package.py
```

Expected: non-zero với lỗi cụ thể về style registry; lỗi này phải xanh sau khi registry và mọi consumer được cập nhật.

## 3. Chạy ma trận bảy phong cách

Đọc các ca `multi-style` trong `calibration/ca-kiem-thu.md`. Với từng card:

1. Xác nhận tín hiệu chọn đúng base profile và card.
2. Chạy edit workflow hiện tại.
3. So với ca đối chứng giữ cùng dữ kiện.
4. Xác nhận không import đại từ, nhịp, thuật ngữ, CTA hoặc register của card khác.
5. Chạy năm chốt chặn cho mọi thay đổi.

Expected: ít nhất 14 ca, mỗi card có một ca dương và một ca chống rò giọng; tất cả giữ facts/intent.

## 4. Chạy mixed-document case

Dùng fixture gồm mở đầu có tác giả, hướng dẫn kỹ thuật, code, bảng tham số, trích dẫn và CTA có sẵn.

Expected:

- functional segments có brief riêng;
- code/schema/table/quote giữ nguyên byte;
- phần kỹ thuật không nhận giọng cá nhân;
- CTA không mạnh hơn bản gốc;
- output không in style label nếu chỉ được yêu cầu viết lại.

## 5. Kiểm precedence

Chạy các ca xung đột trong calibration:

- yêu cầu hiện tại khác memory cũ;
- mẫu đúng người khác default card;
- tone label khác mô tả cụ thể;
- thiếu vai vế làm đổi đại từ;
- một đặc tính chỉ xuất hiện một lần.

Expected: áp đúng thứ tự trong contract; chỉ ca đổi quan hệ mới hỏi một câu.

## 6. Full package gates

```bash
python3 scripts/validate-package.py
npx skills add . --list
claude plugin validate .
git diff --check
```

Expected:

- version trong `SKILL.md`, README và plugin manifest đồng bộ;
- pattern count vẫn là 51;
- registry có đúng bảy canonical card;
- package có `references/bo-giai-phong-cach.md` và không có `specs/`, eval harness hoặc artifact local;
- mọi line budget pass.

## 7. Installed-byte verification

Sau khi đóng gói/cài lại runtime dùng bản chép, so SHA-256 của `SKILL.md`, hai profile và `references/bo-giai-phong-cach.md` giữa source và bản cài. Runtime dùng symlink chỉ cần xác nhận target đúng source checkout.
