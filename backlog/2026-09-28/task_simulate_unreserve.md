# Task: Implement `cron_simulate_picking_unreserve`

## Mục tiêu (Objective)
- Giả lập hành động của nhân viên kho khi tìm kiếm các phiếu kho (`stock.picking`) đang ở trạng thái giữ hàng (assigned) nhưng cần giải phóng hàng hóa.
- Gọi thao tác unreserve trên các phiếu kho đó để trả tồn kho về trạng thái khả dụng.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A ở trạng thái `assigned` (Sẵn sàng/Đã giữ hàng).
   - Tạo Phiếu kho B ở trạng thái `confirmed` (Chờ xử lý/Chưa giữ hàng).
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_unreserve()`.
3. **Assert (Kiểm tra kết quả):**
   - Phiếu kho A phải chuyển trạng thái lùi về `confirmed` và hàng hóa được giải phóng.
   - Phiếu kho B không bị ảnh hưởng (giữ nguyên `confirmed`).

## Gợi ý triển khai Logic
- Tìm kiếm các phiếu kho: `pickings = self.env['stock.picking'].search([('state', '=', 'assigned')], limit=10)`
- Duyệt qua từng phiếu kho hoặc gọi trực tiếp: `pickings.do_unreserve()`
