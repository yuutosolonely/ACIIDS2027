# Backbone capability intake — checked 2026-10-28

TabPFN official repo: https://github.com/PriorLabs/TabPFN . Nội dung hiện đọc ghi default TabPFN-3.5; card cũ nói v2. Code license và weights license tách riêng; không dùng default constructor rồi ghi v2 trong paper. Xem specific weight license/terms và pin actual package/checkpoint/hash trước G0. Đã tìm được source, chưa tải weights hoặc chấp nhận điều khoản thay người dùng.

TabICL official repo: https://github.com/soda-inria/tabicl . Original v1/v1.1 classification-only; repository hiện có v2 classification/regression. Numeric conditional density/tail API vẫn cần kiểm riêng: regression mean không đủ để tự gọi là likelihood. Tên model và revision phải phản ánh đúng bản dùng, không tự đổi v1 → v2.

Unsupervised extension: https://github.com/PriorLabs/tabpfn-extensions . Kiểm commit/API, conditional scoring, feature-order aggregation và cost trước khi xây scorer mới. Chưa reproduce code hoặc nhận đây là cell-level SOTA.

G0 fields còn thiếu: hardware GPU/VRAM/RAM; package pins; checkpoint URL/revision/hash; code/weights license; target type support; distribution output and failure behavior; fitted context preprocessing; inference runtime; reproducibility. Không có model benchmark run trong setup.
