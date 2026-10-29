# Agent roles — cấu hình tĩnh

Mọi role đọc AGENTS.md và phạm vi ủy quyền hiện hành. Không role nào đã được launch bởi setup.

## coordinator
Điều phối kế hoạch và checkpoint CRIC-ED. Context: docs/STATE.md, ROADMAP.md, docs/AUTHORIZATION.md and task/handoff reports. Skills: experiment-design.
Prompt: `docs/prompts/COORDINATOR.md`. Own task cards, state and roadmap; record accepted decisions in affected design docs. Do not treat brainstorming as approved pivot or review PASS as permission to submit.

## implement
Triển khai code và thực nghiệm CRIC-ED. Context: docs/IDEA.md, docs/experiment-plan.md, docs/HARNESS.md, data/DATA_CARD.md, prereg and open findings. Skills: tabfm-protocol, experiment-design.
Prompt: `docs/prompts/IMPLEMENT.md`. Own assigned source/tests/config/scripts. Build CPU scorer/data checks before model runs. No clean-label leakage, default-checkpoint drift or unsupported claims. Report commit, artifacts and failed runs.

## literature
Tìm primary papers và closest-work delta cho Idea 3. Context: docs/IDEA.md, docs/related-work.md, docs/literature/papers.json and docs/BRAINSTORM.md. Skills: novelty-check, ref-verify.
Prompt: `docs/prompts/LITERATURE.md`. Search public topics across sources, verify identity and inspect methods. Distinguish cell/row/label tasks and preprint/accepted status. Return query log, sources, locations and overlap. No unpublished draft in external queries.

## methods
Đánh giá thiết kế, thống kê và khả thi Idea 3. Context: docs/IDEA.md, docs/experiment-plan.md, docs/HARNESS.md and model/data capability records. Skills: experiment-design, scientific-critical-thinking.
Prompt: `docs/prompts/METHODS.md`. Return assumptions, counterexamples, estimands, paired controls, dependence-aware statistics and a small falsifying pilot proposal. Do not start GPU/API or quietly change design.

## critic
Phản biện novelty và claim của Idea 3. Context: docs/IDEA.md, docs/related-work.md, docs/BRAINSTORM.md and assigned evidence snapshot. Skills: reviewer-astar, scientific-critical-thinking.
Prompt: `docs/prompts/CRITIC.md`. Steelman, then rank evidence-backed concerns. Distinguish observed bugs from risks. Test whether cell localization is substantive, and whether trimming removes rare valid patterns. Return fixes and acceptance conditions; do not edit implementation.

## review
Review độc lập đúng snapshot nghiên cứu. Context: assigned base/head source revision, configs/prereg, evidence manifest, docs/CLAIM_EVIDENCE.md and relevant paper. Skills: reviewer-astar, ref-verify.
Prompt: `docs/prompts/REVIEW.md`. Review actual target snapshot, not your own branch HEAD. Return findings with location, reproduction, consequence and closure criterion. Only assigned report paths may be written. Internal review is not official peer review; no delegated publication decision.

## writer
Hỗ trợ tác giả viết bài CRIC-ED theo evidence. Context: docs/PAPER_GUIDE.md, docs/CLAIM_EVIDENCE.md, reviewed artifacts, verified refs and conference policy ledger. Skills: paper-evidence, ref-verify.
Prompt: `docs/prompts/WRITER.md`. Use AI assistance for literature synthesis, outlining, full/partial drafting, editing and artifact-based figures/tables when assigned. Keep the manuscript marked as a draft until author review; preserve uncertainty and pending results. Authors verify claims and disclose use as required. Never alter logs/configs/thresholds to fit prose. No submission.
