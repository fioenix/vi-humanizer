# Bằng chứng phân phối plugin — 03/10/2026

## Phạm vi và trạng thái

Version chuẩn: **0.9.7, chưa phát hành**. Thay đổi bổ sung nhận diện, metadata, catalog và
đóng gói; không thay đổi quy tắc biên tập trong `SKILL.md`, `profiles/`, `references/`,
`calibration/` hoặc runtime `advisor/` so với commit cleanup `1107d7a`.

Nguồn giữ một workflow chuẩn ở root. Adapter `.plugin-skills/vi-humanizer/SKILL.md` chỉ
hướng dẫn nạp workflow đó. ZIP sinh ra chứa một full skill dưới `skills/vi-humanizer/`.
`.agents/skills/` vẫn bị ignore; `.agents/plugins/marketplace.json` là catalog public.

## Kiểm chứng đã chạy

- `python3 scripts/validate-package.py`: v0.9.7 hợp lệ, 55 pattern.
- Bộ test offline: **195 test, OK**; không gọi TypeSafe thật.
- Reviewer chạy độc lập 12 test distribution: **OK**, không còn finding cụ thể trong phạm vi.
- SVG thiếu, active hoặc tham chiếu ngoài bị từ chối trên cả ba đường đóng gói; archive tốt
  giữ nguyên byte khi kiểm thất bại. File scratch không lọt vào payload.
- ZIP plugin layout chuẩn qua validator đi kèm Codex. Validator scaffold này không dùng để
  chứng nhận custom adapter layout của repo nguồn; layout nguồn được kiểm bằng runtime thật.
- Codex CLI 0.158.0: cài marketplace/plugin từ bản nguồn và ZIP trong profile tạm; `plugin/read`
  và `skills/list` đều tìm đúng một skill plugin đang bật, đúng namespace và canonical bytes.
  Các đường dẫn icon listing đều tồn tại trong cache.
- Claude Code 2.1.287: thêm marketplace, cài plugin từ bản nguồn và ZIP trong profile tạm;
  manifest qua `claude plugin validate ... --strict`.
- Không gửi model request, không sửa cấu hình plugin của profile thật.
- Gitleaks 8.30.1 quét staged patch với redaction: exit 0, không tìm thấy secret.
- Đã xem bản render của icon sáng, icon tối và wordmark; chưa kiểm UI listing trên mọi nền tảng.

## Artifact tại thời điểm kiểm

SHA-256 dưới đây áp dụng cho archive local đã kiểm. ZIP dựng lại có thể khác byte do timestamp;
phải tính lại checksum của đúng artifact phát hành, không sao chép checksum này sang release mới.

| Artifact | SHA-256 |
|---|---|
| `vi-humanizer.skill` | `9323eed01d5307b1c7590923d8338ffb7ab3e19e48eacd9b2832d6030ee6ec31` |
| `vi-humanizer-claude-org.zip` | `80352e4764288de62863159e9208764aa2e9b51e7ed81fb0993bf735e6f40eb6` |
| `vi-humanizer-plugin.zip` | `526c87101b1e8a330e393297662abbdfbafcbe214b0f44c1e07aa21448645894` |

## Chưa được chứng minh hoặc thực hiện

Chưa kiểm model invocation hay UI listing trong desktop/session thật. Chưa có review pháp lý
độc lập cho `PRIVACY.md` và `TERMS.md`. Chưa submit directory chính thức của OpenAI/Anthropic.
Chưa merge/push/phát hành phần plugin này; URL trỏ tới file mới trên `main` chỉ hoạt động sau
khi merge. Cài thử thành công không đồng nghĩa đã được nền tảng duyệt hoặc đã ship.

Hướng dẫn và ranh giới phân phối: [plugin-distribution.md](plugin-distribution.md).
Audit repo/history trước đó: [public-oss-audit-2026-10-02.md](public-oss-audit-2026-10-02.md).
