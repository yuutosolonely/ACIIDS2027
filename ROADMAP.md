# Kế hoạch điều phối CRIC-ED — ACIIDS 2027

Cập nhật: 2026-10-30, sau tiếp nhận `docs/handoffs/HANDOFF_20261030_CLAUDE_TO_CODEX.md`.
Quyết định đang hiệu lực: **NO-GO cho hạn ACIIDS này**, theo `docs/DECISION_BRIEF_20261030.md`.
Hướng nghiên cứu tiếp theo chưa được xác nhận nhất quán trong hồ sơ. Không tự chuyển hướng theo kết quả pilot.

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
