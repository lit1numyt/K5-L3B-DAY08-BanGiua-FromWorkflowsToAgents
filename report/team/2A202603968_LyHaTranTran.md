# Báo cáo cá nhân — 2A202603968_LyHaTranTran

## 1. Thông tin thành viên

- Họ tên: Lý Hà Trân Trân
- MSSV: 2A202603968
- Email: 26ai.tranlht@vinuni.edu.vn
- GitHub: TranHa161

## 2. Phần việc phụ trách

Durability, tức crash/resume/retry, cho hai shape nhóm viết mà chưa có test crash riêng: shape A `workflow` và shape C `orchestrator`. Shape B đã có test crash trong `test_single_shape.py`. Ngoài ra tôi rà repo trước khi nộp và sửa việc pack hidden của giảng viên bị commit lên repo nhóm.

Tôi không viết code shape. Code của ba shape do nhóm trưởng viết ở commit `62932fd`.

## 3. Đóng góp cụ thể

- **Commit `96d1cb4`**: thêm `src/tests/test_crash_resume_shapes.py`, gồm 12 test. Mỗi test chạy `run_claim` của `workflow` và `orchestrator` end-to-end trên DB public:
  - `test_crash_then_resume_then_retry_pays_once[shape-point]` (6 test, 3 điểm crash × 2 shape): claim `C-012` (T12) crash ở `before_effect`, `after_effect_before_checkpoint` hoặc `after_checkpoint`, rồi resume và gọi lại thêm một lần trên cùng store. Test kiểm:
    - Ngay sau crash: `before_effect` chưa có dòng ledger nào, hai điểm còn lại có đúng 1 dòng.
    - Sau resume và retry: `status` = `resolved`, `proposal_amount` = 35.000, ledger đúng một dòng `(35000, "refund:C-012")`, đúng một audit `refund_committed`.
  - `test_crash_on_partial_refund_keeps_order_cap[shape]`: claim `C-014` (T14) crash sau khi đã ghi effect, rồi resume. Đơn đã được hoàn trước 30.000, quote đầy đủ là 150.000, nên ledger chỉ được có 120.000. Test này kiểm trần theo đơn vẫn đúng khi có crash, và `proposal_amount` vẫn giữ quote đầy đủ.
  - `test_crash_flushes_clean_trace[shape]`: khi crash, shape vẫn phải ghi trace với `run_id` đúng. Trace không được chứa `CANARY_SECRET_`, `CANARY_INTERNAL_`, `Authorization`, `parent_secret`.
  - `test_denied_claim_retry_never_writes_ledger[shape]`: claim `C-013` (T13), đơn đã hoàn đủ. Chạy lại ở seed 11 và 55 thì vẫn `denied` và không ghi ledger.
- **Commit `415f247`**: tôi phát hiện thư mục `instructor/` đã nằm trong git từ commit `40eaf79` và đã lên `origin/main`. Thư mục này chứa `hidden_labels.json`, `generate_hidden.py` và README giảng viên. `.gitignore` cũ chỉ chặn `src/eval/instructor/`. Tôi thêm `instructor/` vào `.gitignore` và chạy `git rm -r --cached instructor` để gỡ thư mục khỏi git mà vẫn giữ bản trên máy.
- **Quyết định kỹ thuật:**
  - Test chỉ dùng claim public có sẵn (`C-012`, `C-013`, `C-014`). Không sửa `data/*`, không sửa host (`durability.py`, `policy.py`, `metrics.py`).
  - Mỗi test kiểm cả `RunResult` lẫn bảng `refund_ledger` và `audit_events` trong SQLite, vì grader chấm theo ledger chứ không tin số shape tự báo.
  - Sau khi crash, test chạy thêm một lần retry ngoài lần resume, để kiểm idempotency key `refund:{claim_id}` chứ không chỉ kiểm checkpoint.
  - Chỉ untrack `instructor/` chứ không viết lại lịch sử git. RULES.md cấm force-push và xoá commit. Commit `40eaf79` vẫn còn trong lịch sử, nên cần báo nhóm trưởng và giảng viên.

## 4. Bằng chứng

- Test mới: `python -m pytest -q tests/test_crash_resume_shapes.py` → `12 passed`.
- Cổng host: `python -m pytest -q` → `108 passed, 248 deselected`. Khi bỏ file test mới thì ra `96 passed, 248 deselected`.
- Test bắt được lỗi thật. Tôi chạy cùng file test với hai lỗi cố tình cài vào `durability.issue_refund` qua một plugin pytest tạm, không sửa code repo:

  | Lỗi cài vào | Kết quả |
  | --- | --- |
  | Shape nuốt `InjectedCrash` thay vì để nó lan ra (vi phạm CP3) | `10 failed, 2 passed` |
  | Shape tự trừ phần đã hoàn trước khi gọi host (lỗi T14, host trừ hai lần) | `8 failed, 4 passed` |

- Run id trong trace mà test đọc: `R-workflow-C-012-s33`, `R-orchestrator-C-012-s33`.
- Crash suite của host: `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
- `.gitignore`: `git check-ignore instructor/hidden_labels.json` khớp rule `instructor/`. Sau `git rm --cached` thì `git ls-files instructor` không còn file nào.

## 5. Công cụ AI đã dùng

- **Claude Code (Claude Opus)**, dùng để:
  - Đọc code host (`durability.py`, `tools.py`, `crash_test.py`) và các test có sẵn.
  - Viết nháp `test_crash_resume_shapes.py`.
  - Phát hiện `instructor/` đang được track trong git.
  - Chạy các lệnh tự kiểm.
- **Cách tôi tự kiểm tra:**
  - Chạy lại file test và cổng host, rồi so số passed trước và sau khi thêm test (96 → 108).
  - Chạy thử với hai lỗi cố tình cài vào (bảng ở mục 4) để chắc test fail khi shape làm sai, chứ không phải test lúc nào cũng xanh.
  - Đọc từng assert và đối chiếu với `docs/business_rules.md`: T12 crash rồi resume vẫn một refund; T13 đơn đã hoàn đủ thì `denied`; T14 chỉ hoàn phần chênh 120.000 và `proposal_amount` vẫn là quote đầy đủ.
  - Mọi số liệu ở mục 4 lấy từ output lệnh chạy thật.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** đã xong phần được giao: test durability cho shape A và C, và gỡ pack hidden khỏi repo nhóm.
- **Điểm làm tốt:**
  - Bộ test phủ đúng must-pass 3 (crash không tạo hơn một refund) cho hai shape chưa có test crash riêng.
  - Thử với lỗi cài vào cho thấy test bắt được hai lỗi hay gặp: nuốt crash và tự trừ phần đã hoàn.
  - Phát hiện sớm rủi ro liêm chính: nhãn hidden nằm trên repo nhóm.
- **Điểm còn hạn chế:**
  - Tôi không trực tiếp viết logic shape. Đóng góp nằm ở tầng kiểm thử và vệ sinh repo.
  - Commit `40eaf79` vẫn còn trong lịch sử git, vì xoá hẳn thì phải force-push, mà điều này bị cấm. Cần báo giảng viên.
  - Phần lớn code test do AI viết nháp. Tôi tự kiểm bằng cách chạy test và thử với lỗi cài vào như mô tả ở mục 5.
