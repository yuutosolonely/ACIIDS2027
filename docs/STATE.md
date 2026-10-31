# Trạng thái nghiên cứu CRIC-ED — ACIIDS 2027

**Cập nhật 2026-10-31 (lượt 2, Claude):** sửa lỗi packaging freeze (blob của file được hash bị chuẩn hóa EOL trong `c3ee807`) bằng `.gitattributes` lồng `-text` + renormalize; `tools/check_checkout_integrity.py` PASS 6/6 trên export sạch của tree đã stage (HEAD `c3ee807` FAIL 6/6). Bản thảo: bổ sung LightGBM purify−random và leaky diagnostic, cập nhật trích dẫn L2C (arXiv v2), chuyển khai báo AI vào khối `credits` LNCS; PDF 15 trang. Các thay đổi đang **staged, chưa commit**.

**Hiện hành — 2026-10-31 (rà soát nhất quán sau grid; Claude, theo yêu cầu người dùng):**
- Source: HEAD `0aff63e` + working tree; freeze snapshot `c37e39ab…` kiểm lại bằng `verify_freeze` 2026-10-31: khớp. Không sửa run, split, seed, prereg hay phân tích confirmatory.
- Grid v2.1: 60/60 units hoàn tất, cả TabPFN-v2 và LightGBM; artifact audit và split audit PASS (63.300 context records). Đây là artifact audit bằng script của chính dự án, không phải review độc lập.
- Fit-failure: chỉ `hospital__inj-random__s4`; 435 lỗi TabPFN (input chứa giá trị vô hạn) ở final pass của cả bốn arm TabPFN và nested pass 1; LightGBM 0. Phạt cực đại phủ 54% ô (raw), 53% (purify), 51% (random), 15% (oracle); AP raw/random/purify của unit này ≈0.11. Sensitivity post hoc (exploratory, không preregister) `experiments/exploratory/v2_1_fit_failure_sensitivity_20261031/results.json`: purify−random inj-random hospital +0.131 (protocol) / +0.163 (bỏ s4) / +0.138 (bỏ ô lỗi); TFM−LGBM raw đổi dấu −0.094 → −0.0002 / +0.016. Real errors không bị ảnh hưởng.
- Phát hiện mới: DDCcore trả điểm **giống hệt** RobustZ trên 20/20 unit real-error (50/60 tổng) vì không cặp cột số nào vượt ngưỡng tương quan; đã khai báo trong bài.
- Phân tích chạy lại cùng script `analyze_v2.py` cho 6 file khớp từng byte: đây là **analysis replay cùng implementation**, không phải phân tích độc lập. Một unit (flights/real/s0) chạy lại cùng code: PASS_EXACT.
- Bản thảo: 15 trang LNCS (template Springer 2.25), build sạch (0 overfull/undefined), đã xem trang 1, 10, 12, 15. Bỏ banner draft/fallback “pending”; thêm related work đã kiểm (Auto-Test, MaTElDa, LUCARIO, Cell-TRICC); viết lại results cân bằng (purify kém random ở 3/4 bảng; không method nào tốt nhất mọi bảng); khai báo gián đoạn grid/throttling ảnh hưởng timing; khai báo AI cụ thể. Text-overlap cục bộ: 0 cụm 12 từ (`docs/review/TEXT_OVERLAP_FINAL_20261031.json`).
- Trạng thái nộp bài (đối soát 2026-10-31): NO-GO ngày 2026-10-30 được giữ làm lịch sử; chỉ thị tác giả 11:45 ICT cùng ngày (DECISION_BRIEF) chuyển mục tiêu sang hoàn thiện bài để **tác giả tự nộp**. Chuẩn bị bản thảo được phép; nộp/không nộp là quyết định riêng của tác giả, chưa được đưa ra. Hạn chính thức 31/10/2026 23:59 AoE = 01/11/2026 18:59 ICT. Agent không nộp, không upload.

## Câu hỏi cho tác giả (chỉ tác giả trả lời được)
1. Nội dung mục bắt buộc “Disclosure of Interests” (LNCS): có xung đột lợi ích/tài trợ nào cần khai báo không?
2. Có nộp bản này vào ACIIDS 2027 trước 01/11/2026 18:59 ICT không (sau khi đọc toàn văn)?
3. Bản nộp để tên tác giả hay ẩn danh (trang chính thức không nêu; cần kiểm tra form EasyChair)?
4. Track chính hay special session (DADIT/ADMTA chưa xác minh chi tiết)?
5. Có cần mục Acknowledgments (tài trợ, hỗ trợ) không?

## 1. Trạng thái các Gate nghiên cứu

> Sửa 2026-10-31: bảng gate trước đó ghi G2–G5 PASS và “G4 Independent review PASS” dù không có review độc lập; đã hạ về trạng thái có bằng chứng. Bản cũ chưa được commit nên không còn trong Git; nội dung cũ: G2–G5 PASS, G6 READY.

| Gate | Trạng thái | Căn cứ |
|---|---|---|
| G0 Setup/interface | **PASS** | `experiments/validation/g0_capability_20261030/` (synthetic, CPU, 0 network attempts). |
| G1 Protocol/baseline | **PASS (frozen)** | `prereg/PREREGISTRATION_V2_1.freeze.json`, protocol SHA `eea8f0ee…`; baseline là bản cài của dự án (DDCcore ≠ DDC gốc, LGBM ≠ CDC). |
| G2 Pilot/falsification | **PASS (development only)** | movies_1 dev runs + audit `v2_1_dev_artifact_audit_initial.json`; không phải bằng chứng hiệu năng. |
| G3 Confirmatory data | **PASS có ghi chú** | 60/60, artifact+split audit PASS; 1 unit có 435 fit-failure (xem trên). |
| G4 Independent review | **PENDING** | Chỉ có self-check của agent, artifact audit, replay cùng script. Chưa có reviewer/replication độc lập. |
| G5 Manuscript | **COMPLETE FOR AUTHOR REVIEW — chờ tác giả xác minh; thiếu Disclosure of Interests (bắt buộc, chỉ tác giả điền)** | `paper/output/cric_ed_v2_1.pdf` 15 trang; mọi số truy về `docs/CLAIM_EVIDENCE.md`. Tác giả chưa đọc/duyệt toàn văn. |
| G6 Human decision | **PENDING** | Quyết định nộp/không, giải quyết NO-GO, track/session, anonymity (trang chính thức không nêu), Disclosure of Interests. |

## 2. Artifact hiện có trong R1

- `experiments/archive/run_pilot_001/` — bản sao hash-identical của pilot gốc (worktree `implement`); tái lập chính xác ngày 2026-10-30.
- `experiments/archive/run_pilot_002_fixedrng/` — chạy lại sau khi tách RNG stream; có `context_ids.csv`.
- `experiments/archive/run_pilot_003_evalfix/` — thêm evaluator sửa lỗi (AUPRC bất biến khi hoà điểm = sklearn, coverage penalty, 1.000 bootstrap theo entity, top-k chính xác) và hiệu paired có CI. Số liệu trong draft lấy từ run này.
- `experiments/exploratory/explore_cced_movies_001.json` — thăm dò pivot chưa phê duyệt (exploratory, chỉ `movies_1`).
- `data/manifests/raha_download_20261030.json` — RAHA tải về local (gitignored), kèm hash và mức độ đã truy cập.
- `data/manifests/tabpfn_v2_checkpoints_20261030.json`, `experiments/tfm/`, `prereg/PREREGISTRATION_V2.md`, `src/cric_ed/{conditional,baselines,benchmark}.py` — bổ sung ngoài danh sách bàn giao. Prereg/weights/result cũ giữ nguyên; code candidate được sửa trong lượt CPU remediation, chưa thành protocol được duyệt. Tuyên bố đã chọn A trong v2 chưa được decision brief hỗ trợ; v2 chưa được xác nhận đóng băng.

## 3. Kiểm tra

- `experiments/validation/g0_capability_20261030/`: chạy mới theo chỉ thị nghiên cứu tiếp nối, CDF/tail và classification probability checks **PASS**, network attempts **0**; chỉ dữ liệu synthetic. Config/package/checkpoint manifest hash/source script hash trong `capability.json` và `attempt.json`.
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

**Chỉ thị mới thay trạng thái chờ phía trên cho công việc tương lai:** người dùng yêu cầu nghiên cứu/viết đầy đủ Idea 3 và đặt goal active. Tiếp tục TFM CPU với weights/dữ liệu sẵn có sau kiểm licence; không chọn pivot, không trả phí/tải weights mới, không hồi tố quyền tải cũ. Protocol v3 sẽ ghi các quyết định kỹ thuật trước evaluation; giữ v1/v2 làm hồ sơ. ACIIDS có ICORE2026 B đã xác minh ở portal chính thức; deadline được chọn sau, không đảo NO-GO cũ.

### Bối cảnh brief

Xem `docs/DECISION_BRIEF_20261030.md`: (i) giữ TFM và cho phép tải checkpoint, hoặc (ii) chấp thuận fallback/pivot với protocol mới, hoặc (iii) dừng cho hạn ACIIDS 31/10/2026 và tiếp tục nghiên cứu sau. Không có submission nào được thực hiện hoặc được phép thực hiện bởi agent.
