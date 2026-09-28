# Task: Implement `cron_simulate_picking_validate`

## Mục tiêu (Objective)
- Giả lập việc nhân viên kho đã lấy/giao xong hàng và bấm 'Xác nhận' để chốt sổ giao dịch.
- Khi nhấn nút này, hệ thống gọi `button_validate()`.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A ở trạng thái `assigned` (Sẵn sàng) và cập nhật số lượng `quantity_done` bằng với `product_uom_qty`.
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_validate()`.
3. **Assert (Kiểm tra kết quả):**
   - Phiếu kho A chuyển sang trạng thái `done` (Hoàn thành).

## Gợi ý triển khai Logic
- Tìm kiếm phiếu kho: `pickings = self.env['stock.picking'].search([('state', '=', 'assigned')], limit=15)`
- Trước khi gọi `button_validate()`, có thể cần gán random `quantity_done` để giả lập nhặt đủ hoặc nhặt thiếu hàng.
- Xử lý wizard xác nhận hoàn thành (Immediate Transfer wizard) nếu cần.
