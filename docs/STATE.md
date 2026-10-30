# Trạng thái nghiên cứu CRIC-ED — ACIIDS 2027

Cập nhật: 2026-10-30 (candidate v2: CPU remediation, attempt journal và đề xuất phương pháp).
Trạng thái tổng: **NO-GO FOR THIS DEADLINE (quyết định tác giả 2026-10-30) / NOT READY.** Chưa có bằng chứng confirmatory được đối soát. Có artifact smoke/dev TFM bổ sung sau bàn giao; quyền hạn, nguồn run và protocol v2 đang chờ làm rõ, không dùng để nâng gate.
Bản ghi trước (2026-10-29, "G6 READY") đã bị thu hồi; vẫn còn trong Git history (commit `06ded05`).

## 1. Gate (đã hiệu chỉnh theo evidence)

| Gate | Ghi trước đây | Trạng thái hiện hành | Căn cứ |
|---|---|---|---|
| G0 Setup/interface | PASS | **PENDING RECONCILIATION** | Hai checkpoint v2 và hai license file có ở local, hash/size khớp manifest; có JSON smoke nhưng phiên Codex chưa chạy lại model. `AUTHORIZATION.md` và decision brief chưa xác nhận hướng A; artifact tồn tại không xác lập quyền tải hoặc G0 PASS |
| G1 Protocol/baseline | PASS | **CONDITIONAL, điều kiện chưa đáp ứng** | `docs/review/G1_CRITIC_REPORT.md:35-42` yêu cầu subset 100 dòng `beers` + profile TabPFN; chưa làm. Baseline DDC/CDC/uTabPFN chưa chạy |
| G2 Pilot/falsification | PASS | **STOP (proxy)** | Rule 1 không đánh giá được theo nguyên văn (cần raw uTabPFN/CDC trên pilot benchmark; cả hai chưa chạy). Proxy: run 003 untrimmed 0.365 ≥ influence trimming 0.357; MAD 1.000. AUPRC 0.698 của run 001 là artifact thứ tự điểm bằng nhau |
| G3 Confirmatory data | PASS | **NOT ESTABLISHED** | Không thấy run entry tại `experiments/runs/v2/`; file khóa v2 chưa tồn tại. Pilot đã đối soát là fixture tổng hợp; smoke/dev JSON không phải confirmatory evidence |
| G4 Independent review | PASS | **REVOKED** | Critic G2 không xét Rule 1; commit 49 s sau pilot |
| G5 Manuscript | PASS | **REVOKED** | Bản thảo cũ chứa claim sai; bản hiện tại là internal draft ghi kết quả âm |
| G6 Submission readiness | READY | **NOT READY** | Xem `docs/context/conference/SUBMISSION_READINESS_REPORT.md` |

## 2. Artifact hiện có trong R1

- `experiments/archive/run_pilot_001/` — bản sao hash-identical của pilot gốc (worktree `implement`); tái lập chính xác ngày 2026-10-30.
- `experiments/archive/run_pilot_002_fixedrng/` — chạy lại sau khi tách RNG stream; có `context_ids.csv`.
- `experiments/archive/run_pilot_003_evalfix/` — thêm evaluator sửa lỗi (AUPRC bất biến khi hoà điểm = sklearn, coverage penalty, 1.000 bootstrap theo entity, top-k chính xác) và hiệu paired có CI. Số liệu trong draft lấy từ run này.
- `experiments/exploratory/explore_cced_movies_001.json` — thăm dò pivot chưa phê duyệt (exploratory, chỉ `movies_1`).
- `data/manifests/raha_download_20261030.json` — RAHA tải về local (gitignored), kèm hash và mức độ đã truy cập.
- `data/manifests/tabpfn_v2_checkpoints_20261030.json`, `experiments/tfm/`, `prereg/PREREGISTRATION_V2.md`, `src/cric_ed/{conditional,baselines,benchmark}.py` — bổ sung ngoài danh sách bàn giao. Prereg/weights/result cũ giữ nguyên; code candidate được sửa trong lượt CPU remediation, chưa thành protocol được duyệt. Tuyên bố đã chọn A trong v2 chưa được decision brief hỗ trợ; v2 chưa được xác nhận đóng băng.

## 3. Kiểm tra

- Lượt reliability: toàn suite `.venv-tfm` **49 passed**; môi trường tối thiểu **37 passed, 1 skipped** (scientific module). Run-attempt journal giữ stage/lỗi và partial artifacts; preflight runtime kiểm pins trước data loading; analysis kiểm completed journal/source identity. Test chỉ dùng fixtures/fake predictor.
- Phát hiện môi trường: `.venv-tfm` có `include-system-site-packages=true`, torch từ Python hệ thống. Đã archive nguyên bản record cũ, bổ sung pin theo package thực cài; **33 declared pins khớp metadata**. Chưa pin đầy đủ dependency/build/license hoặc xác lập tính cô lập. Provenance: `experiments/validation/tfm_environment_provenance_20261030.json`.
- Đề xuất chưa duyệt: `docs/proposals/V2_AMENDMENT_20261030.md` gồm group/inductive boundary, matched-compute control, thống kê theo source table và failure/freeze policy. DES-01 là suy diễn toán học có enumeration, không phải model performance. Manifest lượt này: `docs/handoffs/PREFLIGHT_RELIABILITY_20261030.json`.
- Lượt CPU remediation: `.venv-tfm/Scripts/python.exe -m pytest -q -p no:cacheprovider` → **40 passed**. Các test mới dùng fixture tổng hợp và fake predictor, không tải/nạp weights hoặc truy cập RAHA. Đây là validation phần mềm giới hạn, không phải xác nhận TFM API, đầy đủ scientific validity hay benchmark performance.
- Candidate đã thêm nested pass 1 loại outer query fold, chặn ma trận pass 1 bên ngoài, phân tách input oracle, ghi context đầy đủ, tính preprocessing/nested work vào thời gian, và kiểm source freeze/run grid trước phân tích. Phạm vi thay đổi và phần chưa giải quyết: `experiments/tfm/README.md`; manifest lượt này: `docs/handoffs/CPU_REMEDIATION_20261030.json`.
- Codex chạy lại `uv run --locked --offline pytest -q`: **24 passed**, một warning không ghi được pytest cache (2026-10-30, Python 3.12.6 `.venv`). Đây là kiểm tra phần mềm, không phải bằng chứng nghiên cứu hoặc validation cho toàn bộ code v2.
- `check_setup.py`: static **PASS** (`research_results=NOT_RUN`); `sync_skills.py --check`: **MATCH**; `check_mcp.py`: handshake/list/status **PASS**. Các lệnh qua `uv run --locked --offline`, cache đặt trong `.cache/uv`.
- Đối soát read-only: **14/14** hash trong `experiments/archive/SHA256SUMS` khớp. Predictions của reproduction giống archive từng byte; metrics giống nếu bỏ `timings`, không giống toàn file như bàn giao cũ ghi. Bốn file checkpoint/license khớp hash/size manifest; đây không phải kiểm định điều khoản hoặc model performance.
- LaTeX/PDF (2026-10-30): build thử `paper/main.tex` bằng tectonic trong thư mục tạm (không ghi file phụ vào repo); class `llncs` 2022/01/12 v2.21 lấy từ bundle TeX Live — chưa đối chiếu đây có phải bản mới nhất Springer phát hành; PDF 4 trang (bản có số liệu run 003), mọi citation và mã arXiv hiển thị, đã mở và xem trang 2. Đây là internal draft, không phải bản nộp.

## 4. Quyết định

- 2026-10-30: tác giả chọn **NO-GO cho hạn ACIIDS 31/10/2026** (ghi trong `docs/DECISION_BRIEF_20261030.md`).
- Còn chờ: chọn Đường A (TFM) hoặc B (fallback/pivot với protocol mới) cho giai đoạn tiếp theo, và venue mục tiêu.
- Codex đã hỏi tác giả về chênh lệch quyền hạn v2; khi chưa có trả lời, tiếp tục công việc local không phụ thuộc quyết định, không chạy model hoặc đóng băng v2. Xem findings tiếp nhận trong `docs/review/AUDIT_20261030.md` và task card trong `ROADMAP.md`.

### Bối cảnh brief

Xem `docs/DECISION_BRIEF_20261030.md`: (i) giữ TFM và cho phép tải checkpoint, hoặc (ii) chấp thuận fallback/pivot với protocol mới, hoặc (iii) dừng cho hạn ACIIDS 31/10/2026 và tiếp tục nghiên cứu sau. Không có submission nào được thực hiện hoặc được phép thực hiện bởi agent.
