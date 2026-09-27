# Calibration RED

**Ngày chạy**: 2026-09-28
**Baseline**: 0.8.0, 51 pattern

Structural check:

```text
ARG cases=6 positive=3 negative=3
QUAL cases=6 positive=3 negative=3
REL cases=6 positive=3 negative=3
AUTH cases=6 positive=3 negative=3
missing owners V23-V25 and K7: RED as expected
Gói vi-humanizer v0.8.0 hợp lệ, gồm 51 pattern
```

Manual contract result:

- 12/12 ca dương chưa có owner trực tiếp trong inventory 0.8.0.
- B5 không sở hữu việc thiếu đối tượng phản biện; V17/V20 không sở hữu modal trùng chức năng; V9
  không sở hữu việc mất quan hệ; B8/K2 chưa tách claim thuyết phục khỏi attribution làm bằng chứng.
- 12/12 ca âm được giữ: có đối tượng tranh luận thật, modal khác phạm vi, nguồn vốn mơ hồ/đòi ẩn
  danh, hoặc authority đã được định danh.
- Không expected label nào được suy từ pattern sẽ viết; labels đã khóa trước implementation.
