# Task: Implement `cron_simulate_picking_lock_unlock`

## Mục tiêu (Objective)
- Giả lập thao tác của quản lý kho đi kiểm tra lại các phiếu kho đã hoàn thành (`done`).
- Thực hiện Lock các phiếu để chốt sổ, hoặc Unlock các phiếu cần điều chỉnh sai lệch số lượng thực tế.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A ở trạng thái `done` và đang ở trạng thái khóa (`is_locked = True`).
   - Tạo Phiếu kho B ở trạng thái `done` nhưng không khóa (`is_locked = False`).
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_lock_unlock()`.
3. **Assert (Kiểm tra kết quả):**
   - Tuỳ theo logic giả lập bạn chọn (lock hay unlock), phiếu A hoặc B sẽ thay đổi trạng thái của field `is_locked`.

## Gợi ý triển khai Logic
- Tìm kiếm: `pickings = self.env['stock.picking'].search([('state', '=', 'done')], limit=10)`
- Lấy một tỷ lệ random để quyết định sẽ gọi `action_toggle_is_locked()` để mở hoặc khóa phiếu.
