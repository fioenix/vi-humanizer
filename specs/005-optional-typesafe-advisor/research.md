# Research: Cố vấn TypeSafe tùy chọn

## Decision 1: Phân phối một advisor CLI tùy chọn trong public package

**Decision**: Thêm `advisor/` vào cả `.skill` và Claude Org ZIP. Host local có Python, shell, HTTPS
và secret injection MAY chạy CLI. Host không có đủ capability chạy core-only dù nhìn thấy các file
adapter trong archive.

**Rationale**: Chỉ viết “đặt API key” không tạo ra integration thật. Ngược lại, biến SDK thành core
dependency sẽ buộc mọi người dùng trả chi phí cài đặt. CLI tùy chọn tạo đường dùng thật trên host
có năng lực nhưng không hạ chất lượng core-only.

**Alternatives considered**:

- Chỉ ghi hướng dẫn gọi một connector do host tự cung cấp: không giải quyết setup cho đa số user.
- Bắt mọi runtime dùng TypeSafe: trái constitution và yêu cầu progressive enhancement.
- Khẳng định Claude Org upload tự dùng được adapter: config/copy presence không phải runtime signal.

## Decision 2: Gọi HTTP API bằng Python standard library, không dùng SDK ở runtime

**Decision**: Runtime client gọi cố định `POST https://api.typesafe.ai/v1/systemone` bằng standard
library, bearer key từ `TYPESAFE_API_KEY`, timeout 8 giây và một attempt. Existing eval lane tiếp
tục dùng SDK pin riêng; public adapter không import dependency đó.

**Rationale**: HTTP API là interface chính thức và response schema nhỏ. Standard library giữ core
dependency rỗng, dùng được từ archive đã giải nén và tránh yêu cầu package manager. Interactive
advisor fail-open nên một lần timeout/rate-limit phải trả control, không chờ retry chain.

**Alternatives considered**:

- Dùng `typesafe-sdk`: error handling tốt hơn nhưng người cài `.skill`/ZIP không có dependency
  environment chung và SDK không được trở thành core dependency.
- Dùng `curl`: khó validate response, kiểm timeout và fake transport ổn định trong unit test.
- Cho phép custom base URL: mở thêm secret/config và SSRF surface ngoài nhu cầu 005.

Nguồn: [TypeSafe API reference](https://docs.typesafe.ai/api),
[Python SDK](https://docs.typesafe.ai/sdk/python).

## Decision 3: Pin model thật thay vì alias di động

**Decision**: Runtime request dùng `jev-1.13.0` và từ chối checked result nếu response báo model
khác. Việc nâng model là revision riêng: cập nhật question/model evidence rồi mới đổi pin.

**Rationale**: `jev-latest` có thể đổi mà không đổi code; feature 001–002 và question behavior hiện
được quan sát trên 1.13.0. Typed output không chứng minh semantic parity giữa hai model.

**Alternatives considered**:

- `jev-latest`: setup dễ hơn nhưng làm result drift không để lại diff.
- Chấp nhận mọi observed model: capability probe có thể pass trong khi contract đã đổi.

Nguồn: [TypeSafe models](https://docs.typesafe.ai/models).

## Decision 4: Runtime question contract mới, không sửa frozen v2

**Decision**: `advisor/questions.py` sở hữu state/question shape mới. `candidates` là object keyed
bằng stable ID; mỗi instruction gọi `source.text` hoặc `candidates.<id>.text`, không gọi list index.
Question set có canonical digest riêng. `guard_eval/v2` giữ nguyên bytes và digest lịch sử.

**Rationale**: Probe của noulmes ngày 28–29/09 cho thấy gọi mục giữa batch bằng vị trí làm relevance
và stance trượt mạnh. Sửa v2 in-place sẽ làm evidence lane đổi sau holdout; tái dùng nguyên shape
cũ lại mang anti-pattern vào runtime.

**Alternatives considered**:

- Import trực tiếp `guard_eval/v2/questions.py`: kéo theo evaluation models có label/provenance và
  giữ candidate list shape.
- Refactor v2 sang shared runtime module: consumer chain lớn và làm khó chứng minh evidence cũ bất
  biến.
- Sao chép không version: tạo hai nguồn sự thật không thể audit; runtime contract mới phải có owner
  và digest riêng.

## Decision 5: Trả judgment, không trả recommendation action

**Decision**: `assess` trả context sufficiency, hai source-issue probabilities, ba component scores
và sáu safety scores cho từng candidate. `rank` chỉ nhận shortlist ≥2 do Agent cung cấp và trả
choice distribution. Không response nào chứa `keep`, `replace`, `reject`, prose mới hoặc candidate
text.

**Rationale**: Feature 002 vẫn `collect_more_labels`; policy chưa đủ bằng chứng để điều khiển live
workflow. Agent cần nhìn từng tín hiệu và giữ authority đã duyệt.

**Alternatives considered**:

- Reuse v2 recommendation policy: biến shadow evidence thành runtime gate trước khi đủ coverage.
- Một score “candidate tốt”: che xung đột giữa sửa đúng lỗi, giữ nghĩa và safety.
- Cho Jev viết candidate: trái vai trò System One và yêu cầu owner.

Nguồn: [How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one),
[Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents).

## Decision 6: Readiness dựa trên probe thật, không persist cờ enabled

**Decision**: `probe` dùng fixture trung tính, trả `advisor_verified` chỉ khi response hợp lệ và
observed model đúng pin. Thiếu key trả `core_only`; đã opt-in nhưng call lỗi trả
`advisor_unchecked`. Observation có timestamp nhưng không được lưu như một cấu hình lâu dài; mỗi
`assess`/`rank` vẫn tự xác thực response.

**Rationale**: Key/config presence không chứng minh code đang emit. Persistence sẽ nhanh stale khi
key, network, quota hoặc model thay đổi.

**Alternatives considered**:

- File `enabled=true`: tạo hai nguồn trạng thái và lặp anti-pattern config-enabled/no-signal.
- Probe một lần khi cài rồi tin mãi: không phát hiện credential/quota/model drift.
- Gọi probe trước mọi edit: tốn thêm quota và latency; actual advisory call đã là live signal.

## Decision 7: Strict stdin/stdout contract và sanitized failure

**Decision**: `assess`/`rank` đọc exact JSON từ stdin. Stdout luôn là một sanitized JSON object;
stderr chỉ dùng message hữu hạn không raw exception. Exit 0 = checked, exit 2 = optional layer
unchecked/unavailable, exit 1 = invalid caller input. CLI không nhận key hoặc raw prose qua flag.

**Rationale**: Command-line args và traceback dễ bị lưu vào history/transcript. Exact schema và
allowlisted reason code tạo fail-closed ở boundary nhưng fail-open về core workflow.

**Alternatives considered**:

- Nhận source/candidate qua CLI flags: lộ prose trong process list/history.
- In raw response để Agent tự parse: lộ payload và phụ thuộc provider schema.
- Trả exit 0 khi không có key: biến unchecked thành success.

## Decision 8: Request tối thiểu và output bind theo content digest

**Decision**: State gửi source span, context trước/sau tối thiểu, current intent, genre và candidate
map. Exact request schema từ chối label, provenance, baseline, protected region và field lạ. Output
chứa `case_binding` tính từ normalized canonical input, question versions và observed model; host
phải bỏ response nếu bytes/versions đã đổi.

**Rationale**: TypeSafe cần prose để thẩm định nhưng không cần dữ liệu bảo trì. Binding ngăn Agent
áp một phán đoán cũ lên candidate mới mà không cần log raw text.

**Alternatives considered**:

- Gửi toàn tài liệu: tăng privacy/cost và làm loãng state.
- Chỉ băm text, không gửi text: model không có nội dung để đánh giá.
- Log request để debug: trái public privacy boundary.

Nguồn: [TypeSafe state](https://docs.typesafe.ai/concepts/state),
[TypeSafe legal index](https://docs.typesafe.ai/legal).

## Decision 9: Ranking là lượt riêng do Agent mở

**Decision**: `assess` chỉ hỏi Noul độc lập. Agent tự đọc absolute signals và MAY gọi `rank` với
shortlist ít nhất hai candidate. `rank` không nhận hoặc trả option `keep_original`; nó không làm
thay quyết định có sửa.

**Rationale**: Questions trong một request chạy độc lập, nên ranking không thể thấy absolute
answers của cùng call. Tách lượt giữ đúng thứ tự authority và tránh Choice cứu candidate trượt.

**Alternatives considered**:

- Batch absolute + ranking trong một request: ranking chấm cả candidate chưa qua cổng.
- Policy code tự dựng shortlist: chưa đủ evidence để đưa threshold v2 vào runtime.
- Không có ranking: bỏ một lợi thế TypeSafe khi Agent đã xác định nhiều candidate đều phù hợp.

Nguồn: [TypeSafe state and independent questions](https://docs.typesafe.ai/concepts/state),
[Choice](https://docs.typesafe.ai/primitives/choice).

## Decision 10: Release version là owner gate

**Decision**: Plan không chọn version. Trước task bump/version/package, owner phải chốt version mới;
noulmes đã trả `ASK THE OWNER` cho đề xuất `0.9.6`.

**Rationale**: Owner vừa xác định cách đánh version theo quy mô sản phẩm. Kiến trúc và tasks không
phụ thuộc con số này nên không cần chặn Phase 0/1.

**Alternatives considered**:

- Tự chọn `0.9.6`: nhanh nhưng lặp lại lỗi tự quyết version của revision trước.
- Để implementation tự bump cuối cùng: quyết định thật vẫn bị trì hoãn và dễ lệch ba nguồn version.
