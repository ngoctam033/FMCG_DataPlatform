# TASK-001: Tự động gom nhóm phiếu kho thành Batch (Cron Job)

## 1. Mô tả (Description)
Xây dựng một Scheduled Action (`ir.cron`) để tự động tìm kiếm các phiếu xuất kho (`stock.picking`) đã sẵn sàng (trạng thái `assigned`) và tự động gom chúng vào các lô hàng (`stock.picking.batch`). Việc này giúp tiết kiệm thời gian gom đơn thủ công cho quản lý kho.

## 2. Tiêu chí gom nhóm dự kiến
- Các phiếu kho phải ở trạng thái `assigned`.
- Các phiếu kho có chung Đơn vị vận chuyển (Carrier).
- Giới hạn tối đa (ví dụ: 50 phiếu / 1 Batch) để đảm bảo khối lượng công việc lấy hàng hợp lý.

## 3. Kịch bản kiểm thử (Test Scenarios - Áp dụng TDD)
Kịch bản kiểm thử cần được thông qua trước khi viết implementation code:
- **Test Case 1.1:** Tạo 3 phiếu kho (Picking) trạng thái `assigned` với cùng một Carrier "Giao Hàng Nhanh". Chạy cron. Kết quả mong đợi: Hệ thống tạo ra 1 `stock.picking.batch` chứa đủ 3 phiếu này.
- **Test Case 1.2:** Tạo 60 phiếu kho (Picking) trạng thái `assigned` cùng một Carrier. Giới hạn là 50 phiếu/Batch. Chạy cron. Kết quả mong đợi: Hệ thống tạo ra 2 Batches (1 Batch 50 phiếu, 1 Batch 10 phiếu).
- **Test Case 1.3:** Tạo các phiếu kho ở trạng thái `draft`, `waiting`, hoặc `confirmed` (chưa giữ đủ hàng). Chạy cron. Kết quả mong đợi: Hệ thống bỏ qua các phiếu này, không đưa vào Batch.
- **Test Case 1.4:** Tạo 2 phiếu kho `assigned` với 2 Carrier khác nhau. Kết quả mong đợi: Hệ thống tạo ra 2 Batches riêng biệt.
