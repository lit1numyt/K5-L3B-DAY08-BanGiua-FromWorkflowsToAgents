# Team

## Thông tin nhóm

- Tên nhóm: BanGiua
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Le Hai Anh | 001205010998 | lehaianh252005@gmail.com | haianh020505 | Workflow (shape A): kiểm thử, rà hidden case, đo benchmark/crash |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Le Hai Anh | Workflow (shape A) | 36c5da0 | `src/tests/test_workflow_hidden_cases.py` (4 test: ticket injection seed 11/55, approval mượn, trace không lộ secret/PII) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 001205010998_LeHaiAnh

### Phần việc phụ trách

- Shape A (workflow): kiểm thử và rà soát `src/lab8/shapes/workflow.py` (code shape do nhóm trưởng viết ở commit `62932fd`).

### Đóng góp cụ thể

- Thêm `src/tests/test_workflow_hidden_cases.py` (commit `36c5da0`): 4 test chạy workflow end-to-end trên ca hidden mà ma trận public chưa phủ.
- Rà workflow theo `docs/business_rules.md`, `docs/contracts.md`; đo benchmark, crash/resume và quét trace.

### Bằng chứng

- Báo cáo cá nhân: [report/team/001205010998_LeHaiAnh.md](report/team/001205010998_LeHaiAnh.md)
