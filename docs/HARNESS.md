# Harness vận hành và thực nghiệm

## Đã triển khai cho setup
`tools/check_setup.py`: validate cấu hình, role/skill paths, mirror, policy/source manifest và scope hiện hành. `tools/check_mcp.py`: stdio initialize/list tools và gọi status offline. `tools/sync_skills.py`: manifest-aware mirror không xóa file không được quản lý. `tools/lit.py`, `verify_refs.py`: API công khai, cache trong `.cache/refcache/` của repo.

`src/cric_ed/protocol.py` và tests là primitives CPU cho group cross-fitting/top-k evaluator. Smoke chỉ kiểm phần mềm trên fixture synthetic có nhãn rõ. **Chưa có TabPFN/TabICL adapter, RAHA loader, statistical analysis pipeline hoặc benchmark result**. Không gọi bộ primitives này là đã triển khai đầy đủ CRIC-ED.

## Hợp đồng cần triển khai trước research run
DirtyTable gồm row/group IDs, typed schema và raw strings; evaluator giữ clean/error labels tách riêng. Detector nhận dirty-only inputs + context manifest, trả cell IDs, scores, eligibility/failure status và timing. Mỗi query fold loại group của query khỏi context. Fit transforms/trimming theo information boundary đã khóa.

Scorer phải kiểm target omission, unseen categories, numerical density support, nonfinite predictions, mixed-type normalization và eligible-cell denominator. Không thay NaN bằng score tốt; report failures và dùng failure policy preregistered.

Run record cần run_id, commit/dirty snapshot, config/hash, data/checkpoint/revisions, seeds, protocol, hardware/runtime/cost, status, artifacts. Chạy lại analysis tạo cùng metrics từ raw predictions; bảng trong paper sinh từ artifacts. Clean oracle/synthetic/leaky diagnostic arms có nhãn riêng.

Review test suite nhắm invariants quan sát được: group không lọt context; evaluator không rò clean labels; target feature bị bỏ; budget/ties/exclusions nhất quán; metrics không silently drop lỗi; paired resampling đúng đơn vị. Seed lặp không thay độc lập sampling units.
