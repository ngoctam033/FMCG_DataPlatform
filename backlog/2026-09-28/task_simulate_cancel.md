# Task: Implement `cron_simulate_picking_cancel`

## Mục tiêu (Objective)
- Giả lập tình huống khách hủy đơn hoặc tạo nhầm phiếu, người dùng bấm nút 'Hủy'.
- Khi nhấn nút này, hệ thống gọi `action_cancel()`.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A ở trạng thái `assigned` hoặc `confirmed`.
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_cancel()`.
3. **Assert (Kiểm tra kết quả):**
   - Phiếu kho A chuyển sang trạng thái `cancel` (Đã hủy).
   - Số lượng hàng hóa đang giữ (nếu có) bị trả về.

## Gợi ý triển khai Logic
- Tìm kiếm phiếu kho: `pickings = self.env['stock.picking'].search([('state', 'in', ['draft', 'confirmed', 'assigned'])], limit=5)`
- Tránh chọn tỷ lệ hủy quá cao làm cạn kiệt data test.
- Gọi method: `pickings.action_cancel()`
