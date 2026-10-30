# Claim → Evidence Ledger — ACIIDS 2027

Cập nhật: 2026-10-30 (audit). Bản 2026-10-29 còn trong Git history; các claim CLM-01..03 cũ đã được đánh giá lại dưới đây.
Mọi số trong `paper/main.tex` phải xuất hiện ở bảng này với run ID, artifact, commit và config.

| Claim ID | Nội dung | Trạng thái | Bằng chứng | Ghi chú |
|---|---|---|---|---|
| CLM-01 | Scorer có điều kiện (không phải TFM) chạy trên CPU ~0.06–0.1 ms/ô trên fixture 400 ô | MEASURED (software fixture) | `experiments/archive/run_pilot_001/metrics.json` timings; config cùng thư mục | Không ngoại suy cho benchmark; không phải TFM |
| CLM-02 (cũ) | Influence trimming > matched random (+0.0167) | **WITHDRAWN** | run 001 không paired (1/400 base context trùng); run 002 paired: 0.6905 < 0.6981 | Thay bằng CLM-06 |
| CLM-03 (cũ) | Guardrail/CRIC-ED giảm báo động giả rare-valid 25% | **WITHDRAWN** | Arm không trim cũng 3/4; khác MAD 1 ô; danh sách rare-valid là oracle | — |
| CLM-04 | Conditional TFM scoring / cross-fitting là mới | NOT ESTABLISHED | `docs/literature/CLOSEST_WORK_MATRIX.md` | Không claim |
| CLM-05 | Vượt CDC trên RAHA | PENDING / không có run | — | Không đưa vào bài |
| CLM-06 | Trên fixture, MAD 1.000 > mọi arm scorer có điều kiện; untrimmed 0.365 ≥ influence trimming 0.357 (proxy stop: Rule 1 không đánh giá được theo nguyên văn (uTabPFN/CDC chưa chạy, không có benchmark); proxy untrimmed ≥ influence trimming) | MEASURED (software fixture, 4 positives, 1 seed) | `experiments/archive/run_pilot_003_evalfix/metrics.json` (commit `06ded05` + audit diff; config ghi dirty state, scorer sha256; 1.000 bootstrap theo entity, 990 hợp lệ) | CI 95%: untrimmed [0.292, 1.0]; random [0.294, 1.0]; trim [0.278, 1.0]. Paired: trim−random −0.008 [−0.081, 0.048]; trim−untrimmed −0.008 [−0.042, 0.000]; untrimmed−MAD −0.635 [−0.708, 0.000] |
| CLM-07 | Tái lập predictions và metrics ngoài thời gian của pilot gốc | MEASURED (read-only recheck 2026-10-30) | `experiments/runs/run_pilot_001_repro_20261030/` (local), run ID/config trong thư mục, so với `experiments/archive/run_pilot_001/`; snapshot đối soát: `docs/handoffs/COORDINATOR_INTAKE_20261030.json` | `predictions.csv` giống từng byte; `metrics.json` chỉ khác `timings`. Thu hồi phát biểu metrics giống toàn file |
| CLM-09 | AUPRC 0.698 (run 001/002) là artifact của evaluator cũ: 6 ô hoà ở điểm kẹp 25 (2 lỗi) được xếp theo thứ tự đầu vào | MEASURED | `sklearn.average_precision_score` trên cùng điểm = 0.3647 (kiểm 2026-10-30, Python hệ thống sklearn 1.8.0); run 003 | Run 001/002 giữ nguyên trong archive như bằng chứng lịch sử |
| CLM-08 | (Exploratory) trên `movies_1`, purification cấp ô không hơn matched-random; context sạch oracle cao hơn context bẩn | EXPLORATORY ONLY | `experiments/exploratory/explore_cced_movies_001.json` | Pivot chưa phê duyệt; không phải confirmatory |

## Provenance

### Design diagnostics (not model performance)

- **DES-01 — DERIVED, conditional mathematical scenario:** for four independent equiprobable table-level null signs and an all-positive maximal statistic, enumeration gives 16 assignments and minimum one-sided p = 0.0625; three repeated conditions per table do not increase the number of independent signs. Run/config/source revision/script hash: `experiments/validation/inference_resolution_20261030.json` (`design_resolution_20261030`, HEAD `06ded051a382bee8e6db47c582e46145fe544515` + script SHA-256). Source code/test: `tools/check_inference_resolution.py`, `tests/test_inference_resolution.py`. This is not benchmark evidence or proof that sign-flipping applies to RAHA. Proposed consequence: `docs/proposals/V2_AMENDMENT_20261030.md` §4; no current preregistration rule was changed.

- Pilot gốc: chạy 2026-10-29 22:04 ICT trong worktree `implement` trước commit `eae8065`; bản sao: `experiments/archive/run_pilot_001/` (SHA256 trong `experiments/archive/SHA256SUMS`).
- Bib: `docs/literature/CITATION_AUDIT_20261030.md`.
