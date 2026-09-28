# TASK-002: Tự động phân công Batch cho nhân viên kho (Cron Job)

## 1. Mô tả (Description)
Xây dựng một Scheduled Action (`ir.cron`) để tự động rà soát các Batch Transfer (`stock.picking.batch`) mới được tạo ra chưa có người phụ trách, sau đó tiến hành phân bổ đồng đều cho các nhân viên kho đang làm việc trong ca.

## 2. Tiêu chí phân công dự kiến
- Tìm các Batch ở trạng thái `draft` hoặc `in_progress` nhưng có trường `user_id` bị trống.
- Phân bổ theo dạng vòng lặp (Round-robin) hoặc dựa vào tải công việc hiện tại của nhóm nhân viên lấy hàng (Pickers).

## 3. Kịch bản kiểm thử (Test Scenarios - Áp dụng TDD)
Kịch bản kiểm thử cần được thông qua trước khi viết implementation code:
- **Test Case 2.1:** Tạo 2 `stock.picking.batch` trạng thái `in_progress` có `user_id` rỗng. Giả định có 2 nhân viên kho đang rảnh. Chạy cron. Kết quả mong đợi: Batch 1 gán cho Nhân viên A, Batch 2 gán cho Nhân viên B.
- **Test Case 2.2:** Batch đã có sẵn `user_id` (được gán thủ công từ trước). Chạy cron. Kết quả mong đợi: Hệ thống bỏ qua, không ghi đè `user_id` của Batch này.
- **Test Case 2.3:** Tạo 1 Batch trạng thái `done` hoặc `cancel` có `user_id` rỗng. Chạy cron. Kết quả mong đợi: Hệ thống bỏ qua, chỉ xử lý các batch còn đang xử lý.
