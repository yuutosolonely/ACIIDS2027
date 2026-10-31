# Kế hoạch điều phối CRIC-ED — ACIIDS 2027

> **Trạng thái hiện hành 2026-10-31 (thay cho các checkpoint bên dưới, giữ làm lịch sử):** grid v2.1 60/60 đã xong; bản thảo 15 trang ở snapshot `8b122c2` cộng sửa đổi sau review G4 (chưa commit). NO-GO 2026-10-30 là lịch sử; chỉ thị 11:45 ICT cùng ngày chuyển mục tiêu sang hoàn thiện bài để tác giả tự nộp (xem `docs/AUTHORIZATION.md`, đối soát 2026-10-31). Việc còn lại chỉ thuộc tác giả: Disclosure of Interests, Acknowledgments, session, xác nhận metadata, quyết định nộp. Các mục “đang chạy”, “NO-GO đang hiệu lực” bên dưới là lịch sử.

**Checkpoint10:00ICT:** T1/T2/T3 hoàn tất trong phạm vi đã ghi; T4 freeze `c37e39ab…` lúc02:58:59UTC; T5 fullgrid60 chạy từ02:59:15UTC,4process×2threads. Không sửa các file đã frozen trong lúc chạy. T6 chờgrid đầy đủ và audit; T7 đã có10trang phương pháp/protocol, cònresults và diễn giải từT6; T8 cònkiểm chứng/render/review. Bằng chứngdev lưu cả archive; khôngđưa vào confirmatory.

**Lộ trình hiện hành sau tiếp quản checkpoint `0aff63e` (2026-10-30):** tác giả đã duyệt Path A và bốn quyết định v2.1 trong decision brief; chỉ Codex đang chạy và sở hữu tích hợp. T1 đã tích hợp WIP/test PASS (scientific68; minimal37/3skip; setupPASS; mirrorMATCH). T2 candidate v2.1 đã tích hợp, rà trước freeze. T3 đang chạy movies_1 seed0 ba điều kiện, hai model. Tiếp đến T4 freeze → T5 grid60 → T6 descriptive analysis → T7 manuscript/PDF12–15 trang → T8 kiểm chứng. Các task chờ A/B và strict-v3 bên dưới là lịch sử, không còn điều khiển kế hoạch. Không thay protocol vì mốc 8 giờ; yêu cầu thực nghiệm đầy đủ vẫn áp dụng. NO-GO deadline/submission vẫn giữ.

Cập nhật: 2026-10-30, sau tiếp nhận `docs/handoffs/HANDOFF_20261030_CLAUDE_TO_CODEX.md`.
Quyết định đang hiệu lực: **NO-GO cho hạn ACIIDS này**, theo `docs/DECISION_BRIEF_20261030.md`.
**Goal nghiên cứu/paper đã active theo chỉ thị mới:** tiếp tục Idea 3 bằng CPU/weights sẵn có, không pivot hoặc hồi tố authorization. `docs/PAPER_COMPLETION_PLAN.md` là checklist hoàn tất. Các task chờ bên dưới giữ như lịch sử; chỉ thị mới và `docs/AUTHORIZATION.md` điều chỉnh công việc tiếp nối.

## Căn cứ và quyền hạn

- Thứ tự thiết kế: `docs/IDEA.md` > `docs/experiment-plan.md` > tài liệu này. Protocol gốc `prereg/PREREGISTRATION.md` giữ nguyên làm hồ sơ lịch sử; deviation được ghi riêng.
- `docs/AUTHORIZATION.md`: $0, local CPU validation; chưa có quyền mở rộng compute, chấp nhận điều khoản weights, publication hoặc submission.
- Code và artifact v2 đã có ở local nhưng không thay thế quyết định của tác giả. Chưa tạo file khóa `prereg/PREREGISTRATION_V2.sha256`.

## Task tiếp nhận — COORD-20261030-INTAKE

Owner: Codex coordinator, một phiên; không launch worker hoặc tạo worktree.
Source: HEAD `06ded051a382bee8e6db47c582e46145fe544515` + working tree chưa commit của Claude và các file v2 bổ sung. Snapshot hash được lưu ở `docs/handoffs/COORDINATOR_INTAKE_20261030.json`.

Phạm vi ghi: STATE, roadmap, banner thiết kế/harness, claim ledger và log hiệu chỉnh, audit reconciliation, setup validation và handoff tiếp nhận. Implementation, prereg v1/v2, checkpoints và artifact run hiện có giữ nguyên.

Acceptance checks:

- [x] Đọc state/authorization/prompt/handoff, kiểm cwd/HEAD/local changes.
- [x] Chạy lại suite CPU, static setup, mirror check và MCP handshake offline.
- [x] Đối soát archive hashes và checkpoint manifest bằng đọc file, không chạy model.
- [x] Sửa phát biểu reproduction quá mức; giữ số liệu và log gốc để truy vết.
- [x] Đồng bộ NO-GO, ghi rõ v2 chờ đối soát và điều kiện mở lại nghiên cứu.
- [ ] Tác giả xác nhận có hay chưa phê duyệt hướng A và điều khoản tải weights sau bàn giao.

## Task tiếp nối — COORD-20261030-CPU-REMEDIATION

Theo chỉ thị “tiếp tục đi”, Codex tiếp tục phần code/CPU validation được phép, không suy thành phê duyệt A hoặc điều khoản weights. Owner vẫn là một phiên Codex; không có agent khác.

Own: `src/cric_ed/{conditional,benchmark,v2_contract}.py`, `experiments/tfm/{run_v2,analyze_v2}.py`, README pipeline, hai file test v2 và các bản ghi điều phối. Prereg v1/v2, model weights, artifact run cũ và baseline cũ giữ nguyên.

- [x] Triển khai candidate nested pass 1 và kiểm perturbation/context dependencies bằng fake predictor.
- [x] Kiểm source freeze, complete run grid, denominator/method arrays, seed alignment và refusal trước khi đọc data/ghi output khi chưa freeze.
- [x] Ghi đủ context stages/IDs, giữ source row IDs, tính preprocessing/inner work vào timing.
- [x] Toàn suite scientific environment 40 passed; static setup PASS, skill mirror MATCH.
- [x] Ghi rõ thay đổi candidate chưa được duyệt vào design/plan/harness; giữ nguyên prereg.
- [ ] Quyết định scope/quyền hạn, group/preprocessing boundary, matched compute và thống kê trước freeze.

Snapshot/kết quả: `docs/handoffs/CPU_REMEDIATION_20261030.json`; handoff: `docs/handoffs/HANDOFF_20261030_CPU_REMEDIATION.md`. Không có research run mới.

## Các bước tiếp theo và điều kiện hoàn tất

Task active `RESEARCH-20261030-STRICT-PROTOCOL`: TFM capability CPU đã PASS ở run mới; tiếp theo hoàn thiện closest-method evidence, triển khai group cross-fitting và train-only preprocessing, kiểm invariants, ghi/freeze protocol v3 + input/split/source trước benchmark. Sau đó chạy đủ thiết kế, analysis và viết/render/review paper. Không kết thúc goal ở setup hoặc draft scaffold. Rank ACIIDS ICORE2026 B đã kiểm; không chuẩn bị submission cho deadline NO-GO.

Task tiếp nối `COORD-20261030-PREFLIGHT-RELIABILITY`: Codex own `run_record.py`, runtime checks trong `v2_contract.py`, runner/analysis journal integration, tests và `tools/check_inference_resolution.py`; ghi một amendment đề xuất, không áp dụng phương pháp mới vào prereg. Bản pin môi trường gốc được archive trước thay đổi setup.

- [x] Test failure/interruption journaling, required-artifact finalization và refusal khi runtime chưa khớp.
- [x] Kiểm provenance môi trường; sửa pin torch bị thiếu, giữ record cũ; ghi rõ system-site-packages.
- [x] Toàn suite scientific 49 passed; tối thiểu 37 passed, 1 skipped; declared pins metadata MATCH.
- [x] Đề xuất estimand/group/preprocessing/compute/statistical-unit/failure policy ở `docs/proposals/V2_AMENDMENT_20261030.md`.
- [x] Enumeration DES-01 và snapshot `docs/handoffs/PREFLIGHT_RELIABILITY_20261030.json`; không có benchmark run mới.

1. **Chốt phạm vi giai đoạn sau — chờ tác giả.** Ghi quyết định A/B, quyền tải/điều khoản/compute cụ thể trong authorization và decision brief; không suy từ câu “Author decisions” trong v2.
2. **Rà protocol mới — đã sửa/kiểm CPU, phương pháp còn chờ.** Candidate đã sửa phụ thuộc qua pass 1 và kiểm grid/source; còn scope, group/fold, preprocessing, matched compute và đơn vị thống kê. Giải quyết finding còn mở trong audit; v2 chưa xác nhận frozen.
3. **Khóa protocol/source — chưa mở.** Đóng băng cả protocol, scorer, runner và analysis; ghi manifest/splits/seeds/thresholds cùng bằng chứng trước confirmatory. Script phân tích phải từ chối bộ run thiếu hoặc trùng unit/seed, failed run phải được ghi đầy đủ.
4. **CPU capability/pilot — phụ thuộc quyền và protocol.** Xác minh package/checkpoint/license riêng, API số/phân loại, context và thông tin không rò qua preprocessing/trimming. Smoke chỉ xác minh khả năng kỹ thuật; pilot benchmark không tự thành confirmatory evidence.
5. **Confirmatory và review — chưa mở.** Chạy đủ thiết kế đã khóa, ghi mọi seed/failure/deviation; review đúng source snapshot khi được giao. Không dùng JSON dev để nâng gate hoặc khẳng định hiệu quả.
6. **Manuscript/venue — chưa mở.** Giữ internal draft kết quả âm; chọn venue và xác minh CFP/policy khi tác giả quyết định. Không có task chuẩn bị gói nộp cho hạn đã NO-GO.

P3 cleanup tên cũ/absolute paths và vendoring template Springer chưa thuộc task hiện tại. R2/R3, installer và builder không được chạy hoặc sửa.

## Current execution plan — 2026-10-30 17:00 ICT (Claude, sole coordinator/executor)

1. [running] Resumed frozen v2.1 grid: 46 remaining units (14/60 done before the 12:06 ICT interruption); ETA about 23:00–24:00 ICT. `docs/EXPERIMENT_LOG.md` §7.
2. [queued, automatic] `tools/finish_v2_1_after_resume.py`: artifact audit, frozen split audit, analysis, analysis reproduction + byte comparison, paper tables/figures, empirical draft, PDF, Markdown, text-overlap screen.
3. [next] Acceptance review: every number vs analysis outputs; claim ledger; citation support; disclose interruption/resume and two timing periods in results/cost text; interpret real results without overclaiming; 12–15 pages incl. references; render and inspect every page; anonymized variant if the author needs double-blind.
4. [author] Decide anonymity (UNVERIFIED), track/session, final read-through and whether to submit by 01/11/2026 18:59 ICT. Agents never submit.

## Status update — 2026-10-31 (Claude, consistency review)

Items 1–3 of the 17:00 ICT plan are done: grid 60/60, audits, analysis, same-script replay, tables, manuscript (15 pages) — see `docs/EXPERIMENT_LOG.md` §9. Acceptance review found and fixed: overstated "independent" wording; gate table inflated (G4 now PENDING, G5 draft complete pending author verification); fit-failure scope (>50% of TabPFN cells in one injected unit) under-reported — post hoc sensitivity added as exploratory; DDCcore ≡ RobustZ on real errors; timing periods undisclosed. Open, author-owned: (a) resolve NO-GO vs submit directive; (b) read and approve full manuscript; (c) session/track; (d) Disclosure of Interests content; (e) anonymity (not stated by official pages; check EasyChair). No independent review exists. Agents never submit.

## Status update — 2026-10-31 (pass 2)
Checkout/freeze packaging fixed in the index (nested `-text` attributes + renormalize; clean-export verification PASS); manuscript completed for author review. Remaining items are author-only: Disclosure of Interests text, submit decision, anonymity, track/session, acknowledgments. Commit pending user approval.
