# Harness vận hành và thực nghiệm

> **Tiếp quản v2.1, 2026-10-30:** accepted author decisions được xác nhận qua checkpoint Claude `0aff63e`. Code WIP đã tích hợp bằng exact Git blobs, manifest `docs/handoffs/WIP_INTEGRATION_20261030.json`. Full scientific suite 68 passed; minimal 37 passed, 3 skipped; static setup PASS, skill mirror MATCH. Capability thật của pinned TFM đã PASS trên synthetic CPU. Dev movies_1 đang chạy; chưa có confirmatory/freeze. Đặc tả thực thi: `prereg/PREREGISTRATION_V2_1.md`; các mô tả “chưa có/chưa quyết định” dưới đây là lịch sử. V2.1 row primary, LEO secondary, final preprocessing transductive và nested outer-isolated pass-1; không thay bằng strict scorer diagnostic.

> **Đối soát 2026-10-30:** mô tả “chưa có” dưới đây là trạng thái setup lịch sử. Working tree hiện có scorer/evaluator sửa lỗi và candidate loader/TFM adapter/analysis v2; code v2 chưa được kiểm định đầy đủ hoặc xác nhận quyền hạn. Suite hiện tại PASS không xác lập validation cho pipeline v2. Xem `docs/STATE.md` và `docs/review/AUDIT_20261030.md` trước khi chạy model.

CPU remediation sau tiếp nhận: candidate v2 có test tổng hợp cho nested pass 1, target omission, paired contexts, oracle-input separation, timing, source freeze và run-grid validation. Toàn suite trong `.venv-tfm`: 40 passed; không chạy TFM/RAHA. Final-pass preprocessing vẫn transductive, group policy và đơn vị thống kê chưa được chốt; test PASS không đóng các finding phương pháp này. Contract kỹ thuật đề xuất: `experiments/tfm/README.md`.

Reliability tiếp nối: `run_record.py` lưu attempt ở `.partial` với stage/source/lỗi; chỉ finalize khi đủ artifact. Runner kiểm 33 declared runtime pins, analysis yêu cầu completed journal khớp metadata. Toàn suite scientific environment hiện 49 passed; môi trường này kế thừa system site packages, không cô lập. Record pin cũ được archive trước khi bổ sung torch. Đề xuất ranh giới/thống kê trước freeze: `docs/proposals/V2_AMENDMENT_20261030.md` (chưa duyệt).

## Đã triển khai cho setup
`tools/check_setup.py`: validate cấu hình, role/skill paths, mirror, policy/source manifest và scope hiện hành. `tools/check_mcp.py`: stdio initialize/list tools và gọi status offline. `tools/sync_skills.py`: manifest-aware mirror không xóa file không được quản lý. `tools/lit.py`, `verify_refs.py`: API công khai, cache trong `.cache/refcache/` của repo.

`src/cric_ed/protocol.py` và tests là primitives CPU cho group cross-fitting/top-k evaluator. Smoke chỉ kiểm phần mềm trên fixture synthetic có nhãn rõ. **Chưa có TabPFN/TabICL adapter, RAHA loader, statistical analysis pipeline hoặc benchmark result**. Không gọi bộ primitives này là đã triển khai đầy đủ CRIC-ED.

## Hợp đồng cần triển khai trước research run
DirtyTable gồm row/group IDs, typed schema và raw strings; evaluator giữ clean/error labels tách riêng. Detector nhận dirty-only inputs + context manifest, trả cell IDs, scores, eligibility/failure status và timing. Mỗi query fold loại group của query khỏi context. Fit transforms/trimming theo information boundary đã khóa.

Scorer phải kiểm target omission, unseen categories, numerical density support, nonfinite predictions, mixed-type normalization và eligible-cell denominator. Không thay NaN bằng score tốt; report failures và dùng failure policy preregistered.

Run record cần run_id, commit/dirty snapshot, config/hash, data/checkpoint/revisions, seeds, protocol, hardware/runtime/cost, status, artifacts. Chạy lại analysis tạo cùng metrics từ raw predictions; bảng trong paper sinh từ artifacts. Clean oracle/synthetic/leaky diagnostic arms có nhãn riêng.

Review test suite nhắm invariants quan sát được: group không lọt context; evaluator không rò clean labels; target feature bị bỏ; budget/ties/exclusions nhất quán; metrics không silently drop lỗi; paired resampling đúng đơn vị. Seed lặp không thay độc lập sampling units.
