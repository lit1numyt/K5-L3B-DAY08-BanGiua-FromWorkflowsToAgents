# Team

## Thông tin nhóm

- Tên nhóm: BanGiua
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-BanGiua-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/lit1numyt/K5-L3B-DAY08-BanGiua-FromWorkflowsToAgents, nhánh `main`, commit chốt ghi trong `report/team/decision_adr.md`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đồng Hữu Nguyên Khoa | 2A202604000 | 26ai.khoadhn@vinuni.edu.vn | [lit1numyt](https://github.com/lit1numyt) | Integration + shape B (single) + benchmark/crash |
|   2 | Lý Hà Trân Trân | 2A202603968 | 26ai.tranlht@vinuni.edu.vn | [TranHa161](https://github.com/TranHa161) | Durability test (crash/resume/retry) cho shape A, C |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đồng Hữu Nguyên Khoa | Integration, shape B `single`, benchmark/crash | `62932fd` (starter cp1 + cp2: ba shape A/B/C), `caebbbe` (shape B cp3 + cp4) | `src/tests/test_single_shape.py` (34 test: approval, secret/PII, crash 3 điểm, ranh giới agent) |
| Lý Hà Trân Trân | Durability test shape A `workflow`, C `orchestrator`; gỡ pack hidden khỏi git | `96d1cb4` (test crash/resume/retry), `415f247` (untrack `instructor/`) | `src/tests/test_crash_resume_shapes.py` (12 test: crash 3 điểm × 2 shape rồi resume + retry, trần theo đơn sau crash T14, trace sạch khi crash, retry claim denied T13) |

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
