# Task: Implement `cron_simulate_picking_assign`

## Mục tiêu (Objective)
- Giả lập việc nhân viên kho bấm nút 'Kiểm tra khả dụng' để giữ hàng (Reserve).
- Khi nhấn nút này, hệ thống sẽ gọi `action_assign()`.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A ở trạng thái `confirmed` (Chờ xử lý) và có đủ tồn kho trong DB.
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_assign()`.
3. **Assert (Kiểm tra kết quả):**
   - Phiếu kho A chuyển sang trạng thái `assigned` (Sẵn sàng).

## Gợi ý triển khai Logic
- Tìm kiếm phiếu kho: `pickings = self.env['stock.picking'].search([('state', '=', 'confirmed')], limit=20)`
- Gọi method: `pickings.action_assign()`
