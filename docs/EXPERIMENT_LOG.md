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
