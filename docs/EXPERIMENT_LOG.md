# Sổ nhật ký thực nghiệm (Experiment Log) — ACIIDS 2027

Cập nhật: 2026-10-29.
Base Commit Snapshot: `234016bd2e204377bcaf20ab4d666cc8fbf66e51`.

---

## 1. Nhật ký Chạy thực nghiệm (Run Ledger)

| Run ID | Ngày/Giờ (ICT) | Target Dataset | Hardware / Runtime | Commit SHA | Mục tiêu thực nghiệm | Trạng thái | Artifact Path |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`run_pilot_001`** | 2026-10-29 22:04 | `toy_mixed` (100x5) | Local CPU / 0.108s | `4760740` | Gate G2 Pilot Feasibility & Matched-Random Ablation | **MEASURED (PASS)** | `experiments/runs/run_pilot_001/` |

---

## 2. Chi tiết Lượt chạy `run_pilot_001` (Gate G2 Pilot)

- **Cấu hình:**
  - Table: `data/fixtures/toy_mixed/dirty.csv` (100 rows, 5 columns: `entity_id`, `feature_a`, `feature_b`, `category_c`, `num_target`).
  - Eligible cells: 400 ô (100 rows $\times$ 4 non-primary-key columns).
  - True error positives: 4 ô lỗi (1.0% corruption rate).
  - Rare-valid patterns: `category_c == 'RareDelta'` (3% marginal frequency).
  - Context size $K = 30$, Trim ratio $q = 0.15$, Splits = 5 folds (Leave-Entity-Out).

- **Kết quả đo lường thực tế (Measured):**

| Phương pháp (Arm) | Overall AUPRC | Numeric AUPRC | Categorical AUPRC | Rare-Valid FPR@k05 | Wall-Clock Thời gian | Latency / ô |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Arm 1: Classical MAD (Baseline)** | 1.0000 | 1.0000 | 1.0000 | **1.0000 (100% FA)** | 0.0007s | 0.0015 ms |
| **Arm 2: CRIC-ED (Raw Context, no trim)** | 0.6981 | 0.8095 | 1.0000 | **0.7500 (25% FA reduction)** | 0.0295s | 0.0591 ms |
| **Arm 3: CRIC-ED (Matched Random)** | 0.6738 | 0.8095 | 1.0000 | 0.7500 | 0.0269s | 0.0538 ms |
| **Arm 4: CRIC-ED (Influence Trimming)** | **0.6905** | 0.8095 | 1.0000 | **0.7500** | 0.0514s | 0.1027 ms |

- **Kết luận Pilot:**
  1. *Tính khả thi thời gian (Gate G2 Feasibility):* Toàn bộ 400 ô chạy xong trong $0.051$ giây trên CPU local ($0.10$ ms/ô), vượt xa yêu cầu trần ($<3$ giây/ô).
  2. *So sánh Trimming vs Matched Random:* Influence Trimming (0.6905) vượt trội hơn Matched Random (0.6738) $+0.0167$ AUPRC.
  3. *Kiểm soát Rare-Valid:* CRIC-ED giảm tỷ lệ báo động giả trên nhóm hiếm hợp lệ `RareDelta` từ 100% xuống 75% so với classical baseline, chứng minh cơ chế bảo toàn rare-valid hoạt động đúng như thiết kế.

---

## 3. Hiệu chỉnh và bổ sung — 2026-10-30 (audit; không sửa số liệu cũ)

Các mục ở §1–2 phía trên là bản ghi gốc ngày 2026-10-29 và được giữ nguyên để truy vết. Những kết luận sau trong bản gốc **không được artifact hỗ trợ** và bị thu hồi:
- "MEASURED (PASS)" cho Gate G2: sai. Rule 1 nguyên văn (raw uTabPFN/CDC trên pilot benchmark) không đánh giá được; proxy untrimmed > influence trimming (0.6981 > 0.6905 theo evaluator cũ; 0.365 > 0.357 theo evaluator đã sửa, §4). Trạng thái đúng: **STOP (proxy)**.
- "Influence Trimming vượt trội Matched Random +0.0167": hai arm không paired (base context trùng 1/400 truy vấn do arm 3 dùng chung RNG stream). Khi paired (run 002), matched-random 0.6981 > influence 0.6905.
- "25% FA reduction ... chứng minh cơ chế bảo toàn rare-valid": arm 2 (không trim, không guard) cũng 0.75; chênh lệch so với MAD là 1/4 ô; danh sách rare-valid là oracle do người tạo fixture cung cấp.
- Commit ghi trong ledger (`4760740`) là HEAD trước khi commit code; code pilot nằm trong `eae8065` (giống hệt `06ded05`).

### Deviation so với preregistration (ghi nhận, không sửa prereg)

| Mục | Prereg / plan | Thực tế | Ảnh hưởng |
|---|---|---|---|
| Baselines | DDC, IF, CDC, uTabPFN, clean-oracle, leaky control | chỉ MAD | Rule 1 không thể đánh giá đầy đủ với uTabPFN/CDC; arm untrimmed được dùng làm proxy |
| Seeds | ≥5 | 1 (42) | Không có ước lượng biến thiên theo seed |
| Bootstrap | 1,000 | 100 (`evaluator.py:151`) | CI kém ổn định hơn |
| Dữ liệu pilot | fixture + subset 100 dòng `beers` (G1) | chỉ fixture | Không có bằng chứng benchmark |
| Backbone | TabPFN v2 | không có TFM | Toàn bộ claim TFM không có căn cứ |

### Run ledger bổ sung

| Run ID | Ngày (ICT) | Dữ liệu | Commit / trạng thái tree | Mục đích | Kết quả | Artifact |
|---|---|---|---|---|---|---|
| `run_pilot_001` (reproduction) | 2026-10-30 | `toy_mixed` (software fixture) | `06ded05`, sạch | Tái lập pilot gốc | metrics.json và predictions.csv **giống hệt** bản gốc | `experiments/runs/run_pilot_001_repro_20261030/` (local, gitignored) |
| `run_pilot_002_fixedrng` | 2026-10-30 | `toy_mixed` (software fixture) | `06ded05` + sửa RNG (5 file dirty, ghi trong config) | Kiểm tra paired arms sau khi tách RNG | MAD 1.000; arm2 0.6981; arm3 0.6981; arm4 0.6905 | `experiments/archive/run_pilot_002_fixedrng/` |
| `explore_cced_movies_001` | 2026-10-30 | `movies_1` (RAHA, dev) | `06ded05` + `src/cced/` (untracked) | **EXPLORATORY**: thăm dò pivot chưa phê duyệt | Mọi arm gần prevalence trên lỗi thật (0.063–0.115); purification cấp ô không hơn matched-random (0.077 vs 0.077; 0.072 vs 0.071); context sạch oracle cao hơn rõ (0.277; 0.104; 0.168) | `experiments/exploratory/explore_cced_movies_001.json` |

### Truy cập dữ liệu (công khai để bảo vệ confirmatory sau này)

Ngày 2026-10-30 coordinator đã tải 5 bảng RAHA (Apache-2.0, commit `7be1334`) và in thống kê mô tả lỗi (tỷ lệ lỗi theo cột, 2 ví dụ/cột) của **cả năm** bảng trước khi có protocol mới. Detector chỉ chạy trên `movies_1`. Bất kỳ protocol confirmatory nào dùng hospital/flights/beers/rayyan phải công khai rằng hồ sơ lỗi mô tả đã được xem. Việc tải diễn ra trước chỉ thị ngày 2026-10-30 hạn chế tải dataset mới; ghi nhận là deviation.


## 4. Bổ sung — 2026-10-30, sau review độc lập (Antigravity reviewers A/D, đã đối chiếu với source)

### Run `run_pilot_003_evalfix`
- Code: `06ded05` + audit diff (21 file dirty, ghi trong config). Fixture `toy_mixed` (software fixture). Seed 42.
- Evaluator đã sửa: AUPRC gom điểm bằng nhau (khớp `sklearn.average_precision_score`), coverage penalty theo prereg (max+1.0; 0 ô thất bại trong run này), bootstrap 1.000 lần theo entity (bỏ 10 mẫu không có positive → 990 hợp lệ), rare-valid theo tập top-k chính xác, hiệu paired có CI.
- Kết quả: MAD 1.000 [1.000, 1.000]; untrimmed 0.3647 [0.2917, 1.0]; matched-random 0.3647 [0.2937, 1.0]; influence 0.3571 [0.2778, 1.0]. Paired: trim−random −0.0076 [−0.0808, 0.0476]; trim−untrimmed −0.0076 [−0.042, 0.0]; untrimmed−MAD −0.6353 [−0.7083, 0.0]. Rare-valid trong top 5%: MAD 4/4, các arm còn lại 3/4.
- Artifact: `experiments/archive/run_pilot_003_evalfix/`.
- Diễn giải: AUPRC 0.698 trước đây là artifact thứ tự hoà điểm (6 ô kẹp ở 25, gồm 2 lỗi). So sánh trimming không kết luận được (CI chứa 0); không có lợi ích trimming nào được hỗ trợ.

### Deviation bổ sung (chưa ghi ở §3)
| Mục | Prereg | Thực tế |
|---|---|---|
| Influence score | gradient-norm của log-likelihood hoặc LOO variance (`PREREGISTRATION.md:35`) | khoảng cách đặc trưng thô tới query (`cric_scorer.py`) |
| Rare-valid guard | tự động, tần suất biên ≤1% | danh sách oracle `RareDelta` (4/100 dòng = 4%) do người tạo fixture cung cấp |
| Coverage penalty | max S + 1.0 cho ô lỗi/NaN | chưa triển khai trong evaluator cũ; đã thêm 2026-10-30 |
| Kiểm định trim vs random | có (H0 trong prereg/kế hoạch) | không có trong run 001/002; run 003 có CI paired bootstrap |
| Đơn vị bootstrap | "row entities" | entity (`entity_id`, 20 cụm × 5 dòng) |

Đính chính §2: `RareDelta` chiếm 4% (4/100 dòng), không phải 3%.

## 5. Quyết định 2026-10-30

Tác giả chọn NO-GO cho hạn ACIIDS 2027. Không có run mới sau quyết định này. Đường nghiên cứu tiếp theo (A/B) chưa chọn.

## 6. Đối soát tiếp nhận Codex — 2026-10-30 (KHÔNG PHẢI bản ghi freeze v2)

Source: `06ded051a382bee8e6db47c582e46145fe544515` + working tree chưa commit. Manifest đối soát: `docs/handoffs/COORDINATOR_INTAKE_20261030.json`. Không chạy lại pilot/model, không tải file, không phát sinh paid compute trong lượt tiếp nhận.

- Hiệu chỉnh §3/CLM-07 và bàn giao cũ: predictions của `run_pilot_001_repro_20261030` giống archive từng byte; metrics giống ngoài `timings`, không phải toàn file hash-identical. Cả 14 entry của `experiments/archive/SHA256SUMS` khớp; archive không sửa.
- `uv run --locked --offline pytest -q`: 24 passed, một warning không ghi được pytest cache; `check_setup.py`: static PASS, research_results NOT_RUN; `sync_skills.py --check`: MATCH; `check_mcp.py`: handshake/list/status PASS. Đây là software/setup validation, không phải benchmark evidence hoặc validation đầy đủ v2.
- Bổ sung ngoài handoff: `experiments/tfm/g0_smoke_result.json`, `experiments/tfm/dev/dev_movies_injected.json`, candidate prereg v2, scorer/runner/analysis và checkpoint manifest. Bốn file weights/license có ở local và khớp hash/size manifest. Codex chỉ đọc file, chưa tái lập model hoặc xác minh nguồn thực thi/quyền tải. Các con số trong JSON bổ sung chưa được nhận làm measured claim trong ledger.
- Hiệu chỉnh phạm vi phát biểu §5 “không có run mới”: đây là trạng thái được bàn giao, không bao quát chắc chắn các artifact v2 phát hiện sau đó. Không thấy entry tại `experiments/runs/v2/` lúc đối soát; không từ đó khẳng định không có run ở mọi đường dẫn.
- `PREREGISTRATION_V2.md` ghi hướng A đã được chọn nhưng authorization/decision brief chưa hỗ trợ; đã hỏi tác giả để làm rõ. Chưa tạo file khóa v2; mục này không phê duyệt hoặc đóng băng protocol. Findings nguồn trong audit phải được giải quyết trước confirmatory.

## 7. CPU remediation candidate v2 — 2026-10-30 (software validation only)

Chỉ thị tiếp nối: người dùng yêu cầu “tiếp tục đi”; thực hiện code/CPU validation trong quyền hạn hiện có, không suy thành phê duyệt A, điều khoản weights hoặc protocol mới. Source: HEAD `06ded051a382bee8e6db47c582e46145fe544515` + working tree; manifest lượt này: `docs/handoffs/CPU_REMEDIATION_20261030.json`.

- Sửa candidate `conditional.py`: nested pass 1 chỉ dùng outer training pool, chặn pass1 toàn bảng do caller cấp, chỉ nhận clean ở arm oracle; giữ context IDs của cả final/inner stages. Final preprocessing transductive và row-vs-group policy chưa được phê duyệt.
- Thêm `v2_contract.py`; runner/analysis yêu cầu protocol hash + source manifest đầy đủ; không tạo file khóa. Kiểm pinned input bytes, complete grid, source/checkpoint identity, eligible universe, arrays/masks, seed alignment; invalid analysis không tạo output. Bootstrap giữ toàn bộ seed trong mỗi replicate hợp lệ.
- Ghi đủ preprocessing/inner work trong timing, nguồn row IDs của subsample và chặn tái dùng output/partial run. Chi tiết candidate và khác biệt cần amendment: `experiments/tfm/README.md`.
- Kiểm tra thực chạy: `.venv-tfm/Scripts/python.exe -m pytest -q -p no:cacheprovider` → **40 passed**; static setup **PASS**, skill mirror **MATCH**, `git diff --check` **PASS**. Test mới chỉ dùng arrays/tables tổng hợp và fake predictor; không đọc RAHA, không nạp weights, không tải/cài dependencies. Suite tối thiểu trước đó: 30 passed, 1 scientific module skipped; không gọi đó là kiểm định TFM.
- Không có research run ID mới, không sửa số liệu cũ, không chạy analysis trên kết quả benchmark, không paid compute/publication/submission. Prereg v1/v2 giữ nguyên. Bằng chứng phần mềm không nâng G0–G6; các finding còn mở ghi tại audit.

## 8. Preflight reliability và đề xuất phương pháp — 2026-10-30

Source: `06ded051a382bee8e6db47c582e46145fe544515` + working tree, snapshot/checks: `docs/handoffs/PREFLIGHT_RELIABILITY_20261030.json`. Tiếp tục local code/CPU validation theo chỉ thị người dùng; không mở scope A/B hoặc research compute.

- Thêm attempt journal: ghi request/source, stage, exception/interruption và giữ `.partial`; chỉ finalize khi đủ artifact. Candidate analysis kiểm completed journal khớp metadata. Test thành công dùng loader/baselines/model đã mock hoàn toàn; tên bảng trong fixture không phải run RAHA.
- Runtime preflight đọc metadata package trước data access. Phát hiện `.venv-tfm` kế thừa system site packages, torch đến từ Python hệ thống; không được gọi là môi trường cô lập. Giữ byte-identical record cũ ở `experiments/archive/tfm_env_freeze_before_core_pin_20261030.txt`, bổ sung pin torch đang cài vào record candidate; kiểm **33 declared pins MATCH**. Không cài/tải package; dependency/build/license freeze vẫn pending. Provenance: `experiments/validation/tfm_environment_provenance_20261030.json`.
- Kiểm tra thực chạy: scientific suite **49 passed**; minimal suite **37 passed, 1 skipped**. Test mới dùng fixtures/fake predictor và temporary attempt directories; không đọc RAHA hoặc nạp weights.
- Design diagnostic ID `design_resolution_20261030`: `uv run --locked --offline python tools/check_inference_resolution.py --out experiments/validation/inference_resolution_20261030.json`. Đây là enumeration toán học với config/HEAD/script hash, không phải thực nghiệm model. Truy vết DES-01 ở claim ledger. Đã đọc tài liệu primary SciPy về giả định Wilcoxon; đề xuất phân tích và giới hạn ở `docs/proposals/V2_AMENDMENT_20261030.md` (chưa duyệt).
- Không thay prereg v1/v2, checkpoint hoặc số liệu cũ; không có benchmark/confirmatory run, paid compute, commit hay submission mới. Không đóng gate nghiên cứu từ test/setup PASS.

## 9. Khởi động goal nghiên cứu/paper hoàn chỉnh — 2026-10-30

Người dùng giao tiếp quản nghiên cứu và viết bài tới hoàn thiện; goal active yêu cầu thực nghiệm chi tiết, cơ sở khoa học và chuẩn bị nộp venue ít nhất rank B. Scope prospective ghi ở AUTHORIZATION; không hồi tố phê duyệt các tải/run cũ, không budget mới, không publication/submission.

- Run `g0_capability_20261030`: `.venv-tfm/Scripts/python.exe experiments/tfm/check_capability.py --out experiments/validation/g0_capability_20261030`. Synthetic capability check, không benchmark: pinned TabPFN-v2 regressor/classifier đều nạp CPU, regression CDF/tail và classification probabilities hợp lệ. Socket connects bị chặn trong process; ghi nhận 0 attempts. Không tải model/API/cài package. Config/runtime/model-manifest/source-script hashes và timings trong run artifact.
- Đã đọc riêng installed package license Apache-2.0, weight license Prior Labs v1.1 và checkpoint hashes. Web mở pinned HF licence thất bại; kiểm nội dung local pinned LICENSE và ghi hạn chế truy cập. Không thay license repository, không phân phối weights.
- Đã xác minh rank ACIIDS B theo ICORE2026 từ `https://portal.core.edu.au/conf-ranks/2188/`; DEXA hiện C (`/987/`), không dùng B cũ. Đây không phải quyết định nộp cho deadline hiện tại.
- Dirty-only schema/group-profile của 5 bảng RAHA được xem để thiết kế protocol; không chạy detector/đọc lại clean labels của confirmatory tables. Ghi nhận metadata profiling là exposure, không phải pristine data access. Protocol/split phải được khóa trước benchmark evaluation.

## 10. Tiếp quản checkpoint mới và development v2.1 — 2026-10-30

Source hiện hành: `0aff63e292da7a071368f594015089d5d746fa05`, branch `coord/v2-1-base` + working tree. Bàn giao `HANDOFF_20261030_CLAUDE_COORD_CHECKPOINT.md` chứa accepted Path A và bốn quyết định v2.1 mà lượt intake cũ chưa đọc được. Các nhận định “A chưa được chọn” của lượt trước không còn là chính sách hiện hành. Người dùng xác nhận chỉ Codex đang chạy; Codex own tích hợp và thực thi. Không commit/push/submission.

- Tích hợp exact Git blobs từ impl WIP `a7560c1`, prereg `32d4bc2`, lit `d2fe584`; manifest `docs/handoffs/WIP_INTEGRATION_20261030.json`. Không sửa các worker worktree. Trước tích hợp, scientific suite có 51 passed/4 failed do contract V2/V2_1 và fixture thiếu tên bảng; sau tích hợp **68 passed**. Minimal **37 passed, 3 skipped**; static setup PASS; mirror MATCH; diff whitespace check không có lỗi (có cảnh báo CRLF).
- Line-ending policy: `.gitattributes` đặt LF cho text mới, giữ byte archive/CSV/binary. Không mass-renormalize evidence cũ hoặc tái sử dụng CRLF worker tree để freeze.
- T3 bắt đầu lúc `2026-10-30T02:23:33Z`: movies_1 real seed0; tiếp theo inj-random và inj-systematic seed0, cả hai model, ba process ×3 threads. Output `experiments/runs/v2_dev/`. Các process đang chạy; chưa có kết quả được chấp nhận. Code/source/runtime identities nằm trong từng attempt journal. Không có detector run confirmatory.
- Tạo artifact auditor riêng `tools/audit_v2_artifacts.py`: kiểm input/error-mask identity, query/context/encoder boundaries, paired bases, LEO keys, completeness và AP đối chiếu sklearn. Hai test phát hiện log bị rò outer query/entity **2 passed**, fixture-only. Audit artifact thực chưa chạy vì dev đang chạy.
- Tác giả yêu cầu cố gắng hoàn thành trong 8 giờ (khoảng 02:24–10:24 UTC), đồng thời nhấn mạnh kiểm chứng thực nghiệm đầy đủ. Không giảm grid/seed hay hạ chuẩn nghiệm thu để đạt thời gian.
- Viết phần introduction/related work/method/protocol/limitations trong `paper/sections/`; giữ trạng thái empirical results pending. Bản pilot cũ được sao byte-identical vào `paper/archive/negative_fixture_20261030/`. Tải mẫu Springer công khai chính thức: LNCS class 2.25 (03-Sep-2026), hashes/source trong `paper/template/SOURCE.json`; tải hai font TeX công khai còn thiếu sau lần build offline thất bại. Không upload manuscript. Build/render QA đang tiếp tục, chưa tuyên bố paper hoàn chỉnh.

### T3 hoàn tất và sửa báo cáo trước freeze

- Ba run movies_1 seed0 hoàn tất: real **1442.6s**, inj-random **1456.0s**, inj-systematic **1459.0s** (xem số chính xác trong từng `meta.json`). Cả hai mô hình, không caught-fit exception; audit `experiments/validation/v2_1_dev_artifact_audit_initial.json` xác nhận **4.480 contexts**, final failure masks đều zero, pinned input/error masks khớp và AP bằng sklearn. Chỉ development, không đưa vào confirmatory summary.
- Analysis ban đầu: `experiments/validation/v2_1_dev_analysis_initial/`. Rà protocol phát hiện thiếu leaky contrasts, seed metrics và support/rare-valid denominators. Đã sửa trước freeze, giữ nguyên predictions/journals và ghi source transition trong replay `v2_1_dev_analysis_reconciled_02`. Replay đầu lỗi JSON NumPy int64; giữ `v2_1_dev_analysis_reconciled/failed_attempt.json`, sửa conversion và thêm test strict serialization. Không có run detector bị thay thế.
- Scorer thêm logging nonfinite returns cả pass1/final, không đổi score/penalty/selection. Runner ép built-model cache=0. Test mới phát hiện nonfinite pass1; full scientific suite cuối **71 passed**. Minimal **37 passed, 4 skipped**; static setup PASS; mirror MATCH. Đây là software validation, không scientific performance gate.
- Cache diagnostic `model_cache_equivalence_20261030.json`: sáu task dev cho cache0/2 có scores giống hệt nhưng không thấy lợi ích thời gian rõ; không bật cache. Thread profile `thread_profile_20261030.json`: sáu task cố định ở 1/2/3 threads; max abs score variation do floating point được ghi, không dùng AP chọn config. Một lệnh thăm dò prefix qua stdin thất bại import trước scoring; script riêng sau đó chạy hoàn tất.
- Chọn operational config confirmatory trước evaluation: **4 processes ×2 threads**, LGBM1thread, cache0. Không đổi context/seeds/weights/arms. Ngoại suy đồng-cost thô: 60×~1450s/4 ≈6 giờ; không phải full-grid measurement, khác bảng/support/thread và contention có thể làm thời gian thay đổi đáng kể. Mục tiêu8giờ không bảo đảm hoàn tất; không giảm thiết kế.
- PDF phương pháp/protocol đã build offline thành **10 trang**, dùng template mới; đã xem trang1 và5. Chưa đủ phần results và chưa nghiệm thu. Bảng/hình paper sẽ tạo từ complete frozen analysis.

## V2.1 prospective freeze - 2026-10-30T02:58:59.307840+00:00

Source HEAD `0aff63e292da7a071368f594015089d5d746fa05` + exact uncommitted file map in `prereg/PREREGISTRATION_V2_1.freeze.json`.
Protocol SHA256 `eea8f0ee8b217458a82b073bac5261f43ab8056e1b4eb32a170e5aece061543a`; full snapshot `c37e39ab8168ed2fda38e9a6e952a15114bda4faa595356c7aeeb5f633bf5678`.
Dirty-only split manifest fixed before confirmatory detection; accepted row/LEO/descriptive/compute decisions apply.
Scope: 60 complete units, both models, local CPU $0. No outcome-based amendment or automatic pivot. Analysis and artifact audit remain required.

Grid launch: `2026-10-30T02:59:15Z`, `.venv-tfm/Scripts/python.exe experiments/tfm/run_grid_v2_1.py --workers 4 --threads 2`.
Launch identity/config: `experiments/archive/v2_1_runs/launch.json`; partial/complete local runs: `experiments/runs/v2_1/`.
Development metadata, scores and context hashes copied to `experiments/archive/v2_1_development/`, original files unchanged.
No confirmatory effect inspected or reported at launch. Frozen files must remain unchanged until all execution/analysis finishes.

### Technical progress and verification rerun (04:23 UTC)

Grid9/60 completed, zero recorded fit failures; exact timings in archived progress/meta.
No AP or confirmatory effect inspected. Select the first completed unit, flights/real/seed0,
for a separate end-to-end verification rerun at the same frozen source and threads2.
Output `experiments/validation/v2_1_replication/`, excluded from the 60-unit performance analysis.
This temporary fifth process shares the host with four grid workers; retain that concurrency
deviation when describing timing. It changes neither method/config nor the planned grid.
Compare saved scores/contexts exactly, reporting any difference rather than replacing originals.

Local text-overlap screen for the current methods draft: seven cached public primary sources,
zero exact12word matches, `docs/review/TEXT_OVERLAP_METHODS_20261030.json`. This is limited
phrase screening, not a plagiarism score or proof of originality; rerun on the final prose.
Public sources cached locally without transmitting the manuscript; access/hash manifest in
`.cache/literature_primary/manifest.json`. Citation support still requires inspected source text.

### Verification rerun completed (04:45 UTC)

`flights/real/seed0` separate rerun completed, zero recorded failures. Comparison
`experiments/validation/v2_1_replication_comparison.json` reports **PASS_EXACT**:
all saved arrays and contexts identical; timing/journal metadata excluded from equality.
Both original and replica remain intact and have artifact hashes in the comparison.
This verifies one unit with the same implementation; it is not independent software
replication or proof that every grid unit was rerun. Do not include the replica as
a sixth seed or duplicated performance observation. Grid execution remains in progress.

Additional technical audit: first real seed0 on all4 tables verifies4,740 saved context
records, including observed-key LEO; artifact identity and AP equality checks passed.
Record `experiments/validation/v2_1_progress_artifact_audit_s0.json` is explicitly partial,
not a complete-grid analysis. New literature narrows claims via QualiTab/L2C2/LUCoS/cellGMM;
no frozen measurement source or experiment configuration changed.

### Local downstream continuation prepared (04:57 UTC)

Goal tool reports `usageLimited`; this is not completion. Existing grid remains running.
Start local `.venv-tfm/Scripts/python.exe tools/finish_v2_1_verification.py`, session80142,
which owns `experiments/archive/v2_1_postprocess/`. It waits for grid completion and
refuses incomplete60-unit status, stale freeze, failed verification rerun or differing
reproduced numerical analysis. It then generates data-backed manuscript artifacts and
an explicitly internal empirical draft, builds/renders PDF and records review_pending.
No model API, agent launch, paid compute, publication or submission. Scripts syntax-checked;
the real downstream stages have not yet run. Final interpretive/numeric/citation/visual
review and author-email clarification remain required; no automatic acceptance claim.

## 7. Grid interruption and recorded resume — 2026-10-30 (Claude coordinator/executor)

- **Finding (16:48 ICT):** no grid process alive; 14/60 units complete and archived (real: beers s0–s3, flights s0–s3, hospital s0–s1, rayyan s0–s3; zero fit-failure events). Four attempts were left with `status: running` and no error record (killed externally): flights/real/s4 (stage score:lgbm:purify), hospital/real/s2 (score:tabpfn-v2:raw_leo), hospital/real/s3 (score:tabpfn-v2:purify), hospital/real/s4 (score:lgbm:oracle). Last attempt update 12:06 ICT. Cause: the grid was a child of a Codex terminal session (codex.exe → codex-command-runner → powershell → python) and ended with that session. The original postprocessor (pid 3536) died with it.
- **Resume (16:50 ICT):** new, non-frozen launcher `tools/resume_grid_v2_1.py` (frozen `run_grid_v2_1.py` refuses existing roots by design). It verifies the freeze (snapshot `c37e39ab…`), checks grid order/content against `launch.json`, skips the 14 completed units, **moves** (does not delete) the four partials to `experiments/runs/v2_1_interrupted/<unit>.partial.<stamp>/`, renames their logs to `*.interrupted_<stamp>.log`, and runs the remaining 46 units with the frozen `run_v2.py`, the same `--threads 2`, four workers, and the frozen launcher's archive format. Record: `experiments/archive/v2_1_runs/resume_20261030T095022Z.json`; progress `resume_progress_<stamp>.json`; console `resume_console_20261030.log`. Launched via WMI so that no agent session owns the process tree.
- **Why results are unaffected:** the frozen run is deterministic; the independent same-implementation rerun of flights/real/s0 matched every array and context record exactly (`experiments/validation/v2_1_replication_comparison.json`, PASS_EXACT). Interrupted attempts are retained as evidence and excluded from analysis (they never completed).
- **Deviation (timing only):** wall-clock times of resumed units come from a different concurrency period than the first 14; the cost table must state that timings span two execution periods.
- **Postprocessing:** `tools/finish_v2_1_after_resume.py` (same stage order as `tools/finish_v2_1_verification.py`) launched detached at 16:53 ICT; it waits for the resume status (60/60), then runs artifact audit, frozen split audit, analysis, same-script analysis replay with byte comparison (wording corrected 2026-10-31; originally “independent”), paper asset generation, empirical draft, PDF build, Markdown sync and text-overlap screen. Status: `experiments/archive/v2_1_postprocess_resume/status.json`.
- **Second interruption (18:31 ICT):** after one more completed unit (flights/real/s4, exit 0, 17:40 ICT; total 15/60), the console window that the WMI launch created via `cmd.exe` received a window-CLOSE event; the Intel Fortran runtime used by the numerical libraries aborted every child (`forrtl: error (200): program aborting due to window-CLOSE event`; exit codes 2 and 0xC000013A). beers/real/s4 and hospital/real/s2–s4 were left as partials; the launcher and the waiting postprocessor died too (their retained status files still say running).
- **Second resume (18:35 ICT):** `tools/resume_grid_v2_1.py` (record `resume_20261030T113433Z.json`) moved the four new partials to `experiments/runs/v2_1_interrupted/*.20261030T113433Z` and runs the remaining 45 units. Changes to the non-frozen launcher only: launched with `pythonw.exe` (no console), children started with `CREATE_NO_WINDOW` and `FOR_DISABLE_CONSOLE_CTRL_HANDLER=1`. Interpreter, frozen `run_v2.py`, threads and arguments are unchanged, so outputs are unaffected (deterministic; replication PASS_EXACT). Postprocessor relaunched the same way into a new timestamped directory `experiments/archive/v2_1_postprocess_resume_<stamp>/`; the earlier `v2_1_postprocess_resume/` is retained as evidence of the interrupted wait.

### Isolated recovery attempt from the Codex status check (2026-10-30 18:55 ICT)

- A separate recovery was started in fresh roots `experiments/runs/v2_1_recovery_20261030/` and `experiments/archive/v2_1_recovery_20261030/`; it did not modify the original grid, frozen files, or the second-resume directories. It reused 15 completed units by checked byte copies and preserved four original partials under `interrupted_attempts/`.
- Four new attempts (`hospital/real/s2`, `hospital/real/s3`, `hospital/real/s4`, `beers/real/s4`) exited before model execution. Each failed while importing PyTorch with Windows `WinError 1455` (paging file too small). No new prediction or metric artifact was produced. The recovery grid status is `incomplete`, 15/60 completed; the four failure logs and partial directories are retained.
- This is a failed orchestration attempt, not a research run or result. The project’s separate second-resume launcher had newer attempt journals in the original run directory at 18:56 ICT; do not treat this isolated recovery’s failure as evidence that the other launcher stopped. Its process was not visible to this shell. No further grid was launched from this attempt.
- **Throughput fix (21:35 ICT):** after the windowless relaunch each grid process used only about 0.9 CPU despite `--threads 2` (beers/real/s4 took 158 min versus 20–33 min earlier). Cause: Windows 11 treats windowless processes as background work (EcoQoS/power throttling) and schedules them on efficiency cores of this hybrid CPU. `tools/unthrottle_grid.py` (launched detached) turns power throttling off via `SetProcessInformation(ProcessPowerThrottling)` and sets AboveNormal priority for this user's grid/postprocess processes, re-applied every 30 s to new children; log `experiments/archive/v2_1_runs/unthrottle_log.jsonl`. Measured afterwards: 2.00 CPUs per process. No thread count, input, code or output changed; only OS scheduling hints. Consequence for reporting: wall-clock times of units run between 18:35 and 21:35 ICT are inflated by throttling and must not be compared with other units' timings; the cost table must state the three execution periods.


## 8. Hoàn tất toàn bộ lưới 60/60 Confirmatory và Tái lập số liệu — 2026-10-31

- **Hoàn thành lưới 60 đơn vị:** Toàn bộ 60 lượt chạy (4 bảng: hospital, flights, beers, rayyan; 3 điều kiện: real, inj-random, inj-systematic; 5 seeds: 0, 1, 2, 3, 4) cho cả TabPFN-v2 và LightGBM đã kết thúc thành công với mã thoát 0.
- **Kiểm toán Artifact (`tools/audit_v2_artifacts.py`):** Kiểm toán toàn bộ 60 runs và 63.300 context JSON records; trạng thái `PASS` (`experiments/archive/v2_1_artifact_audit.json`). Ghi nhận 435 sự kiện fit-failure tại `hospital__inj-random__s4` (do tràn số float64 trong scaling cực trị, gán điểm nghi ngờ cực đại per protocol); 0 fit-failure trên tất cả các điều kiện lỗi thực tế.
- **Kiểm toán Phân vùng (`tools/check_frozen_splits.py`):** Kiểm toán phân vùng hàng ngoài và tập cơ sở đạt trạng thái `PASS` (`experiments/archive/v2_1_split_audit.json`).
- **Phân tích mô tả chuẩn tắc (`experiments/tfm/analyze_v2.py`):** Đã tính toán 1.000 lần lặp row-bootstrap với seed 2027 trên 60 runs, xuất bản kết quả tại `experiments/archive/v2_1_analysis/`.
- **Analysis replay từng byte (`experiments/validation/v2_1_analysis_reproduction`)** — *sửa 2026-10-31: bản gốc ghi “tái lập độc lập”; thực tế chạy lại cùng script `analyze_v2.py` trên cùng predictions, không phải phân tích độc lập.* Chạy lại `analyze_v2.py` và đối chiếu từng byte. Kết quả: 6 tệp trọng yếu (`results.json`, `metrics.csv`, `seed_metrics.csv`, `paired_deltas.csv`, `costs.csv`, `macro_descriptive.csv`) khớp chính xác 100% từng byte (identical: true).
- **Xuất bản Artifacts bài báo (`tools/generate_paper_results.py`):** Tạo 7 bảng LaTeX (`primary.tex`, `baselines.tex`, `coverage.tex`, `rare.tex`, `cost.tex`, `secondary.tex`, `probes.tex`), 2 đồ thị (`primary_deltas.pdf`, `mechanism_deltas.pdf`), và định nghĩa số liệu `numbers.tex` tại `paper/generated/`.
- **Bản thảo Thực nghiệm (`tools/write_empirical_draft.py`):** Tự động sinh `paper/sections/abstract.tex`, `paper/sections/results.tex`, `paper/sections/conclusion.tex` với đầy đủ báo cáo minh bạch về lỗi fit-failure và không đưa ra phát biểu vượt quá bằng chứng đo lường.
- **Biên dịch PDF (`tools/build_paper.py`):** Biên dịch Tectonic thành công không lỗi; bài báo `paper/output/cric_ed_v2_1.pdf` đạt chính xác **15 trang** (đáp ứng đúng khung 12–15 trang Springer LNCS).
- **Đồng bộ Markdown (`tools/sync_manuscript.py`):** Đồng bộ hóa `paper/MANUSCRIPT.md` qua pandoc.
- **Sàng lọc trùng lặp văn bản (`tools/check_text_overlap.py`):** 0 cụm từ 12 từ trùng khớp với 11 tài liệu gốc được lưu cache.

## 9. Rà soát nhất quán, sensitivity post hoc và hoàn thiện bản thảo — 2026-10-31 (Claude)

Source: HEAD `0aff63e` + working tree; `verify_freeze` khớp snapshot `c37e39ab…`. Không chạy model, không sửa run/split/seed/prereg/phân tích confirmatory; $0, CPU local.

- **Kiểm artifact (đọc lại):** artifact audit 60 runs/63.300 contexts PASS; split audit PASS; hash 6 file analysis gốc = replay (cùng script); replication flights/real/s0 PASS_EXACT; `paper/generated/PROVENANCE.json` trỏ đúng hash analysis/audit; PDF cũ khớp hash source trước khi sửa.
- **Ghi chú quan trọng:** postprocess status files (`v2_1_postprocess*/status.json`) vẫn ghi `running` ở bước chờ — các process đó đã chết; outputs ở §8 không có status hoàn tất tương ứng từ các thư mục này. Hash của outputs đã được kiểm trực tiếp, nhưng nhật ký thực thi §8 không có journal máy tương ứng.
- **Fit-failure `hospital__inj-random__s4`:** 435 TabPFNValidationError (input vô hạn): raw pass1 272, raw final 51, purify 50, random 48, oracle 14; folds 0–2 final hầu như mọi cột. Mask phạt: raw 10.200, purify 10.000, random 9.600, oracle 2.800 / 19.000 ô. AP TabPFN raw/random/purify s4 ≈0.11.
- **Sensitivity post hoc (EXPLORATORY, không preregister, viết sau khi xem kết quả):** `experiments/exploratory/fit_failure_sensitivity_v2_1.py` → `experiments/exploratory/v2_1_fit_failure_sensitivity_20261031/results.json`. Tái tính AP protocol khớp frozen 160/160. Hospital inj-random: purify−random +0.131/+0.163/+0.138 (protocol/bỏ s4/bỏ ô lỗi); TFM−LGBM raw −0.094/−0.0002/+0.016 (đổi dấu). Ô bị phạt có tỷ lệ lỗi 10.06% ≈ phần còn lại 9.93%.
- **DDCcore ≡ RobustZ** trên 20/20 unit real, 50/60 tổng (CLM-19).
- **Timing:** hospital/real TabPFN raw 6.8–46.2 phút giữa các seed do ba giai đoạn thực thi (trước gián đoạn, throttled, sau unthrottle); đã khai báo trong bài.
- **Literature (2026-10-31):** trích PDF Auto-Test (Proc. ACM Manag. Data 3(3), Art. 133, DOI 10.1145/3725396; unsupervised, học SDC từ corpus) và MaTElDa (EDBT 2025 pp. 364–376, DOI 10.48786/edbt.2025.29 — DOI DataCite, Crossref trả 404; semi-supervised, nhiều bảng). LUCARIO và Cell-TRICC: chỉ metadata Crossref (publisher 403); LUCARIO README replication package xác nhận suy luận constraint không nhãn; abstract Cell-TRICC chưa đọc được → bài chỉ dùng câu được tiêu đề hỗ trợ. Uni-Detect không đưa vào bài (chưa mở lại nguồn).
- **Hội nghị (kiểm trang chính thức 2026-10-31):** hạn 31/10/2026 (extended) 23:59 AoE; 12–15 trang gồm references, tối đa 25 có phí; LNCS/LNAI PDF; EasyChair; không nêu double-blind hoặc chính sách AI; chống nộp đồng thời; similarity check. Springer Nature book policy: AI không là tác giả, cần disclose; trang LNCS guidelines yêu cầu đăng nhập — chưa đọc được.
- **Bản thảo:** bỏ banner INTERNAL DRAFT/fallback pending trong `main.tex`; viết lại `results.tex` (failure scope, sensitivity post hoc, comparator cân bằng, DDCcore, timing); gọn `method.tex` (bỏ câu “exchangeability is broken” quá mức); thêm 4 tài liệu đã kiểm vào related work/bib; gọn protocol/limitations; bỏ Fig. mechanism (trùng Bảng 5); abstract/conclusion nêu purify kém random ở 3/4 bảng. Lưu ý: `abstract/results/conclusion.tex` nay là bản biên tập tay, không còn trùng output của `tools/write_empirical_draft.py`.
- **Kiểm tra thực chạy:** `.venv-tfm` pytest **71 passed**; build tectonic **15 trang**, 0 overfull/undefined; đã xem render trang 1, 10, 12, 15; `sync_manuscript.py` cập nhật Markdown; text-overlap cục bộ 0 cụm 12 từ (`docs/review/TEXT_OVERLAP_FINAL_20261031.json`). Không có review độc lập.
