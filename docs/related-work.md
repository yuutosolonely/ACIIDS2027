# SOTA / closest-work scan cho Idea 3 — 28/10/2026

## Kết luận đọc trước
Card gốc chưa đủ để tuyên bố novelty. Phải phân biệt **cell error detection** (CDC/ZeroED/ForestED), **row anomaly detection** (TACTIC/ZEN/TaskBridge/FoMo-0D/OUTFORMER), **label-error/context curation** (TICDA) và backbone capabilities (TabPFN/TabICL). Không có một bảng “SOTA chung” có thể ghép F1 ô với AUROC dòng hoặc nhãn.

Các paper mới nhất trong scan là TICDA (06/10), ZEN/FOCUS (05/10), TaskBridge (29/09/2026). Đây là preprint theo bản ghi đã đọc, không tự gán venue/acceptance. SOTA số học cần tái lập cùng dataset/split/label budget/metric/coverage/cost; **repo này chưa đo**.

## Thứ tự đọc đề nghị
Đọc CDC → unsupervised TabPFN code → TACTIC → ZEN/FOCUS → TICDA → TaskBridge → ZeroED/ForestED; sau đó classical DDC/cellMCD và backbone/license. Liên kết và phạm vi kiểm ở từng mục dưới.


## From Data Imputation to Data Cleaning — Automated Cleaning of Tabular Data Improves Downstream Predictive Performance

- Record: 2024 / AISTATS; task: cell error detection / cleaning.
- Primary link: [cdc](https://proceedings.mlr.press/v238/jager24a.html).
- Kiểm thực tế: Primary proceedings page checked; methods full-text still to audit; chưa reproduce.
- Ý nghĩa cho Idea 3: Closest task baseline: imputation plus conformal calibration. Replacing the imputer with a TFM alone is a weak contribution.

## ZeroED: Hybrid Zero-shot Error Detection through Large Language Model Reasoning

- Record: 2025 / ICDE listing checked; task: cell error detection.
- Primary link: [zeroed](https://arxiv.org/abs/2504.05345).
- Kiểm thực tế: arXiv abstract + ICDE 2025 research listing; chưa reproduce.
- Ý nghĩa cho Idea 3: LLM reasoning generates/propagates pseudo-labels and trains a detector. Compare same row universe, label availability and token budget; zero-shot is not training-free.

## Ensembling LLM-Induced Decision Trees for Explainable and Robust Error Detection

- Record: 2025 preprint / v3 updated 2026-07-29; task: cell error detection.
- Primary link: [forested](https://arxiv.org/abs/2512.07246).
- Kiểm thực tế: arXiv metadata/abstract and HTML inspected; acceptance not established; chưa reproduce.
- Ý nghĩa cho Idea 3: TreeED/ForestED uses LLM-induced trees and ensembles. Important newer direct-task baseline beyond ZeroED; audit sampled-versus-full-table protocols before importing scores.

## Accurate predictions on small data with a tabular foundation model

- Record: 2025 / Nature; task: backbone / density / anomaly.
- Primary link: [tabpfn](https://doi.org/10.1038/s41586-024-08328-6).
- Kiểm thực tế: Publisher search extracts and official repository checked; full publisher page access limited; chưa reproduce.
- Ý nghĩa cho Idea 3: Already includes density estimation and anomaly detection abilities. A claim of first using TFM for anomalies is untenable; inspect its conditional/joint construction.

## TabPFN unsupervised extension (implementation)

- Record: code / checked 2026-10-28; task: imputation / density / row anomaly.
- Primary link: [utabpfn](https://github.com/PriorLabs/tabpfn-extensions/blob/main/src/tabpfn_extensions/unsupervised/unsupervised.py).
- Kiểm thực tế: Official implementation opened; not reproduced; chưa reproduce.
- Ý nghĩa cho Idea 3: Inspect conditional feature scoring and feature-order aggregation before defining a new masked likelihood method. Pin a commit and API; row scores do not establish cell localization.

## TACTIC for Navigating the Unknown: Tabular Anomaly deteCTion via In-Context inference

- Record: 2026-03-15 / preprint; task: row anomaly / noisy context.
- Primary link: [tactic](https://arxiv.org/abs/2603.14171).
- Kiểm thực tế: arXiv abstract and HTML checked; acceptance not established; chưa reproduce.
- Ý nghĩa cho Idea 3: Explicitly studies instability of unsupervised TabPFN with noisy/contaminated context and computational cost. Contamination as a broad failure mode is already studied.

## Adapting prior-data fitted networks for tabular anomaly detection

- Record: 2026-10-05 / preprint; task: row anomaly / clean and contaminated reference.
- Primary link: [zen](https://arxiv.org/abs/2610.06693).
- Kiểm thực tế: arXiv metadata and HTML sections 2.1–2.3 inspected; chưa reproduce.
- Ý nghĩa cho Idea 3: ZEN uses frozen representations and nearest-neighbor scoring; FOCUS adapts weights. Section 2.1 includes leave-one-fold-out reference embeddings. Neither cross-fitting nor training-free PFN anomaly scoring is novel by itself.

## TaskBridge: Bridging Unsupervised Tabular Anomaly Detection and In-Context Learning via Virtual Tasks

- Record: 2026-09-29 / preprint; task: row anomaly / virtual ICL tasks.
- Primary link: [taskbridge](https://arxiv.org/abs/2609.36968).
- Kiểm thực tế: arXiv metadata and HTML sections 3–4 inspected; code not reproduced; chưa reproduce.
- Ý nghĩa cho Idea 3: Builds normality-anchored virtual tasks and selection around pretrained TFMs. Strong recent candidate in row anomaly literature; its benchmark ranking is paper-reported, not a cell-ED ranking.

## TICDA: Tabular In-Context Data Attribution

- Record: 2026-10-06 / preprint; task: label-error detection / context attribution.
- Primary link: [ticda](https://arxiv.org/abs/2610.07996).
- Kiểm thực tế: arXiv metadata and HTML sections 2, 3.1–3.3 inspected; chưa reproduce.
- Ý nghĩa cho Idea 3: Influence from linear surrogates on embeddings supports labeling-error detection and context curation. Relevant to choosing/pruning context, but supervised target labels differ from arbitrary dirty table cells.

## Model-Aware Data Cleaning for Tabular Foundation Models

- Record: 2026-04 / v2 2026-09-17; task: cleaning for downstream TFM prediction.
- Primary link: [modelaware](https://arxiv.org/abs/2604.25154).
- Kiểm thực tế: Current v2 abstract and change note checked; chưa reproduce.
- Ý nghĩa cho Idea 3: RL chooses cleaning operators for downstream use. v2 corrects earlier prior-alignment framing; do not cite obsolete v1 claims as proven alignment.

## Noise Immunity in In-Context Tabular Learning: An Empirical Robustness Analysis of TabPFN's Attention Mechanisms

- Record: 2026-04 / v2; task: binary classification robustness.
- Primary link: [noise](https://arxiv.org/abs/2604.04868).
- Kiểm thực tế: arXiv metadata/abstract checked; full method audit pending; chưa reproduce.
- Ý nghĩa cho Idea 3: Controlled irrelevant/correlated features and noisy labels are not the same as heterogeneous cell-level errors. Useful mechanistic background, not a direct RAHA error detector.

## FoMo-0D: A Foundation Model for Zero-shot Tabular Outlier Detection

- Record: 2024 preprint / v4 2025-09; task: row outlier detection.
- Primary link: [fomo](https://arxiv.org/abs/2409.05672).
- Kiểm thực tế: arXiv current record/abstract checked; chưa reproduce.
- Ý nghĩa cho Idea 3: Anomaly-specific synthetic pretraining and zero-shot detection. Distinguish its clean-reference assumptions from unsupervised polluted-context settings.

## From Zero to Hero: Advancing Zero-Shot Foundation Models for Tabular Outlier Detection

- Record: 2026-02 / v2 2026-05; task: row outlier detection.
- Primary link: [outformer](https://arxiv.org/abs/2602.03018).
- Kiểm thực tế: arXiv metadata/abstract checked; chưa reproduce.
- Ý nghĩa cho Idea 3: OUTFORMER extends anomaly-specific pretraining with mixed priors/curriculum. A newer comparator to FoMo-0D if a row-level experiment is added.

## TabICL: A Tabular Foundation Model for In-Context Learning on Large Data

- Record: 2025 / ICML; task: backbone / classification.
- Primary link: [tabicl](https://arxiv.org/abs/2502.05564).
- Kiểm thực tế: arXiv metadata and official repo checked; chưa reproduce.
- Ý nghĩa cho Idea 3: Original TabICL is classification-only. Current repository also offers v2 regression; that is a separate checkpoint capability and should not be silently attributed to v1.

## Detecting Deviating Data Cells

- Record: 2018 journal / online 2017; task: numeric cellwise deviations.
- Primary link: [ddc](https://doi.org/10.1080/00401706.2017.1340909).
- Kiểm thực tế: Publisher primary metadata/abstract and author manuscript link found; chưa reproduce.
- Ý nghĩa cho Idea 3: Classical cellwise prediction using cross-variable dependence. Numeric-only baseline can reveal whether TFM gains exceed robust correlation-based detection.

## The Cellwise Minimum Covariance Determinant Estimator

- Record: 2023 online; final citation to resolve; task: robust numeric cellwise estimation.
- Primary link: [cellmcd](https://doi.org/10.1080/01621459.2023.2267777).
- Kiểm thực tế: Publisher primary abstract and author manuscript found; chưa reproduce.
- Ý nghĩa cho Idea 3: Cellwise robust likelihood/penalty formulation. Useful classical reference; mixed-type semantic errors remain a separate scope.

## Single-Pass Conformal Cross-Modal Anomaly Screening with Tabular Foundation Models

- Record: repository lead / 2026-09 claim; task: cross-modal reconstruction / calibration.
- Primary link: [spcad](https://github.com/jose-melo/single-pass-conformal-calibration).
- Kiểm thực tế: Official author repo read; OpenReview browser challenge blocked paper verification; chưa reproduce.
- Ý nghĩa cho Idea 3: Very close implementation lead: feature-from-others reconstruction and leave-one-out calibration. Do not treat repository headline results or venue/date as independently verified paper evidence.

## Contextual Learning for Anomaly Detection in Tabular Data

- Record: 2025-09 / v2 2025-11; task: contextual row anomaly / conditional autoencoder.
- Primary link: [contextual](https://arxiv.org/abs/2509.09030).
- Kiểm thực tế: arXiv primary record/abstract checked after live CLI discovery; chưa reproduce.
- Ý nghĩa cho Idea 3: Models conditional normality for heterogeneous contexts. Relevant to rare-valid behavior in brainstorming; it is not a PFN/TabICL method and should not be conflated with ICLAD.

## Anomaly Detection of Tabular Data Using LLMs

- Record: 2024 / workshop acceptance reported in arXiv record; task: batch-level row anomaly using LLMs.
- Primary link: [llmad](https://arxiv.org/abs/2406.16308).
- Kiểm thực tế: arXiv primary record/abstract checked after live CLI discovery; chưa reproduce.
- Ý nghĩa cho Idea 3: Studies pretrained LLM anomaly detection and optional fine-tuning on synthetic tasks. Contextual background for a semantic detector; not a direct heterogeneous-cell F1 baseline.

## Closest-work delta cần chứng minh

1. CDC và uTabPFN làm weak novelty cho “đổi imputer thành TFM/conditional likelihood”.
2. TACTIC và ZEN đã xét contaminated context; ZEN còn dùng fold-out embeddings. Cross-fitting một mình là protocol requirement, không contribution mới.
3. TICDA làm overlap rõ với context pruning/influence. Cần khác ở heterogeneous target-cell localization và information boundary, không chỉ tên trimming.
4. Rare-valid patterns có thể bị trimming loại nhầm. Đây là hypothesis cần paired intervention, không hiện tượng đã đo trong repo.
5. SPCAD gần về reconstruction/LOO nhưng paper chưa mở được. Giữ là lead unresolved, đọc thêm trước khi chốt novelty; không bỏ qua chỉ vì repo nhỏ.

## Baseline đề xuất, chưa khóa
Cell-level: CDC + uTabPFN scoring + classical per-column/robust DDC numeric subset; ZeroED và ForestED khi đủ code/budget. Supervised Raha dùng label budget riêng. Với row-level auxiliary study mới xét TACTIC/ZEN/TaskBridge; không biến row scores thành cell scores bằng lặp lại.

## Giới hạn scan
Đã đọc metadata/abstract và chọn lọc các section HTML của paper sát nhất; chưa đọc toàn bộ PDF và appendix mọi paper, chưa audit/reproduce code hoặc license toàn bộ. Nature full page gặp access issue; DADIT extractor rỗng, ADMTA timeout, OpenReview SPCAD challenge. Paper card ghi VERIFIED không tự chuyển thành verification lần này. Phân biệt submitted/updated date và online/final publication year.

Query log: `docs/literature/SEARCH_LOG.json`. Metadata entries: `docs/literature/papers.json`. Các kết luận delta là phân tích của agent, không claim của tác giả paper. Chưa có bằng chứng phương pháp nào tốt nhất cho toàn bộ protocol Idea 3.
