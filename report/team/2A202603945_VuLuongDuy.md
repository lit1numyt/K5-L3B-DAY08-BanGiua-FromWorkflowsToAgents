# Báo cáo cá nhân — 2A202603945_VuLuongDuy

## 1. Thông tin thành viên

- Họ tên: Vũ Lương Duy
- MSSV: 2A202603945
- Email: duybaodap@gmail.com
- GitHub: https://github.com/vuduy21

## 2. Phần việc phụ trách

- **Shape C `orchestrator`** (`src/lab8/shapes/orchestrator.py`): rà soát bản cài đặt ban đầu của nhóm (commit `62932fd`, thành viên `lit1numyt`) và bổ sung xử lý lỗi cho investigator.
- **Kiểm thử handoff và trace** của shape C: thêm bộ test riêng cho ranh giới bảo mật giữa orchestrator và investigator.
- Nhánh làm việc: `duy`.

Shape C chia việc thành hai vai. Orchestrator đọc claim qua `get_claim_view`, dựng handoff bằng `make_handoff` (allowlist, chỉ tool đọc), giao cho investigator tra order và lịch sử hoàn tiền, rồi tự tính quote bằng `compute_compensation` và gọi `durability.issue_refund` với quote đầy đủ. Investigator không có registry ghi.

## 3. Đóng góp cụ thể

Commit chính: **`b472332`** — `feat(orchestrator): fail closed on rejected investigator tool, add handoff tests`.

**Sửa code (`orchestrator.py`):**
- Bọc `run_readonly_investigators` trong `try/except ToolRejected`. Nếu investigator yêu cầu tool ngoài registry chỉ-đọc, shape trả `failed` với lý do `investigator_tool_rejected`, không gọi `issue_refund`, không ghi ledger, và ghi sự kiện `error` vào trace. Trước đó ngoại lệ này sẽ làm run thoát bằng exception.
- Giữ `facts={}` trong handoff: lúc dựng handoff, orchestrator chưa có dữ liệu order (investigator mới là bên tra), nên truyền thêm fact chỉ làm tăng lượng dữ liệu qua ranh giới mà không có lợi.

**Test thêm (`src/tests/test_orchestrator_handoff.py`, 4 test):**
1. `test_trace_has_sanitized_readonly_handoff`: handoff trong trace chỉ có tool chỉ-đọc, không có `CANARY_SECRET_`, `parent_secret`, `raw_headers`.
2. `test_trace_does_not_copy_ticket_or_claim_row`: trace không chép nội dung ticket hay header của claim.
3. `test_rejected_tool_in_investigator_fails_closed`: tool bị từ chối thì `failed`, không refund, không audit `refund_committed`, có sự kiện `error`.
4. `test_escalated_does_not_leak_order_fields`: claim C-005 (T05, principal không sở hữu đơn) trả `escalated` và không lộ `phone` hay `internal_note`.

**Quyết định kỹ thuật:**
- Fail closed khi investigator vi phạm: thà không xử lý claim còn hơn để tool ghi lọt qua.
- Truyền quote đầy đủ vào host (host tự trừ phần đã hoàn theo đơn), không tự trừ ở shape, để T14 không bị trừ hai lần.

## 4. Bằng chứng

- Commit: `b472332` trên nhánh `duy` của repo nhóm `lit1numyt/K5-L3B-DAY08-BanGiua-FromWorkflowsToAgents`.
- Kết quả chạy trong `src/` (Python 3.11.9, Windows) sau commit:
  - `python -m pytest -q` (cổng host): **58 passed**, không có failed (trước khi thêm test là 54 passed).
  - `python -m pytest -q -m student -o addopts= -k orchestrator`: **62 passed**.
  - `python -m lab8.crash_test --count 20 --out <file tạm>`: `crash_safety 20/20`. Lệnh này chạy để kiểm tra nhanh, chưa phải bản `reports/crash.json` nộp bài.
- Chưa có: `reports/benchmark.json` và `reports/crash.json` chính thức (nhóm sẽ sinh ở CP4–CP5), nên báo cáo này không nêu số pass rate hay cost.

## 5. Công cụ AI đã dùng

- **Claude Code (Claude Sonnet 5.5)** trong VS Code. Dùng vào:
  - Đọc repo và phân tích đề, đề xuất cách chia việc cho nhóm 3 người.
  - Đọc và đánh giá bản `orchestrator.py` của nhóm; viết đoạn xử lý `ToolRejected` và file `test_orchestrator_handoff.py`; chạy test và commit.
  - Soạn kịch bản demo và bản nháp báo cáo này.
- **Cách kiểm tra:** chạy lại `smoke`, cổng host và ma trận student (số liệu ở mục 4); test đầu tiên dùng nhầm claim C-007 (kết quả `denied`, không phải `escalated`) nên đã đối chiếu `expected` trong `data/public_claims.jsonl` và đổi sang C-005 trước khi commit.
- Không sửa các file thước đo (`metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`).

## 6. Tự đánh giá

- **Làm được:** shape C qua 62/62 test student; thêm xử lý lỗi và 4 test về handoff/trace; cổng host vẫn xanh.
- **Hạn chế:** phần lõi orchestrator do thành viên khác viết ở `62932fd`, đóng góp của mình là rà soát, bổ sung xử lý lỗi và test. Test chỉ chạy trên dữ liệu public (14 claim) với MockLLM, chưa chạy trên bộ hidden; chưa có số benchmark để so orchestrator với workflow/single/swarm.
- **Việc tiếp theo:** rà `CANARY_SECRET_*` trong trace và stdout ở CP4, tham gia benchmark và ADR ở CP5.

