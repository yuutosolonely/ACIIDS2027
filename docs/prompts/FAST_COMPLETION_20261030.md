# Fast completion directive — CRIC-ED — 2026-10-30 ICT

Bạn là coordinator và executor duy nhất của nghiên cứu CRIC-ED trong workspace này. Hãy tiếp tục công việc ngay, ưu tiên hoàn thành các deliverable trong hôm nay (giờ ICT), không dừng ở việc lập kế hoạch hoặc chỉ báo cáo tiến độ.

## Trạng thái cần tiếp nhận

Đọc `AGENTS.md`, `docs/STATE.md`, `docs/AUTHORIZATION.md`, `docs/PAPER_COMPLETION_PLAN.md`, `ROADMAP.md` và log mới nhất. Kiểm tra cwd, HEAD, dirty files, grid journal, các tiến trình thực sự đang chạy và `experiments/archive/v2_1_postprocess/status.json`. Ghi nhận snapshot hiện hành trước khi thao tác.

## Thứ tự hành động

1. **Xác minh và đưa grid đã freeze tới hoàn tất.** Không sửa protocol, scorer, runner, analysis, split, seed, threshold hoặc kết quả đã freeze. Xác nhận process sống bằng tiến trình và journal mới; journal ghi `running` nhưng không có process không được tính là đang chạy. Tìm và tiếp tục đúng execution/session hiện hữu nếu có. Nếu grid đã dừng, đối soát từng unit và partial trước khi khởi động lại; chỉ chạy lại unit khi xác định được chính xác trạng thái và tuân thủ cùng frozen config/source. Không tạo run trùng, không xóa partial/evidence, không bỏ unit để tiết kiệm thời gian.
2. **Hoàn tất pipeline sau grid.** Dùng postprocessor đã chuẩn bị nếu source snapshot và điều kiện đầu vào còn khớp. Chạy đầy đủ artifact audit, frozen split/grid checks, phân tích từ predictions đã lưu, lần tái lập phân tích độc lập theo pipeline hiện có, so khớp số liệu, sinh bảng/hình/manuscript và build PDF. Không đọc hoặc chọn kết quả confirmatory để thay protocol.
3. **Rà nghiệm thu paper.** Kiểm claim-evidence ledger, citation support, giới hạn và deviations, tính nhất quán mọi con số, references, layout và PDF đã render. Hoàn tất text-overlap/source review được phép trong máy local. Không upload manuscript hoặc dữ liệu lên dịch vụ bên ngoài.
4. **Cập nhật hồ sơ.** Cập nhật `docs/STATE.md`, `ROADMAP.md`, `docs/EXPERIMENT_LOG.md` và claim ledger theo evidence thực tế. Ghi rõ phần đã xong, lỗi/run failure, giới hạn, xác nhận còn chờ tác giả và việc cần làm tiếp; không đánh dấu research goal complete nếu acceptance criteria chưa đạt.

## Quy tắc ưu tiên và giới hạn

- Tối ưu thời gian bằng cách bỏ việc lặp, tái sử dụng artifact đã được kiểm tra và gom các bước hậu xử lý độc lập khi an toàn. Không giảm số lượt/seed, bỏ baseline hoặc review, nới tiêu chí, chọn lọc dataset, hay gọi draft là paper hoàn tất để kịp hôm nay.
- Giữ quyền hiện có: CPU local và dữ liệu/checkpoint đã được duyệt; ngân sách `$0`. Không cài/tải thêm model hoặc dữ liệu, không dùng paid API/compute, không launch agent/worktree, không publish hoặc submit. Không sửa LICENSE.
- Không sửa/ghi đè file frozen hoặc artifact evidence; chỉ bổ sung artifact mới và log. Bảo toàn dirty work của người dùng.
- Khi một bước chặn bởi process/session không thể truy cập, hỏng artifact, thiếu điều kiện khoa học hoặc cần quyết định tác giả, tiếp tục các bước độc lập được phép; ghi chính xác blocker và không giả định PASS.

## Điều kiện báo hoàn tất

Chỉ báo hoàn tất khi toàn bộ grid đủ 60/60 unit theo freeze và audit hợp lệ; split/source/run checks PASS; analysis tái lập và các paper table/figure nhất quán; manuscript và PDF đã build, render và kiểm tra; citations/claims được đối soát; trạng thái, deviations và unresolved author checks đã ghi. Báo cáo thời điểm ICT, source snapshot, artifact paths, checks thực sự chạy, kết quả và mọi mục còn mở. Nếu chưa đạt, tiếp tục làm việc được phép và nêu rõ phần còn thiếu thay vì tuyên bố đã xong.
