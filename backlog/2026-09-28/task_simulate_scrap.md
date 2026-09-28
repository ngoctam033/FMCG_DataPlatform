# Task: Implement `cron_simulate_picking_scrap`

## Mục tiêu (Objective)
- Giả lập kịch bản nhân viên đang xử lý phiếu kho thì phát hiện hàng hỏng/rách bao bì.
- Tự động lấy ngẫu nhiên (hoặc theo quy tắc) một số lượng hàng hóa trên phiếu để tạo action Scrap, đẩy hàng lỗi sang địa điểm phế liệu (Scrap Location).

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Tạo Phiếu kho A ở trạng thái `assigned` hoặc `done` (có chứa hàng hóa).
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_scrap()`.
3. **Assert (Kiểm tra kết quả):**
   - Hệ thống tự động tạo ra một bản ghi trong `stock.scrap` liên kết với Phiếu kho A và địa điểm đích phải là loại địa điểm scrap (phế liệu).

## Gợi ý triển khai Logic
- Tìm kiếm phiếu kho hợp lệ: `pickings = self.env['stock.picking'].search([('state', 'in', ['assigned', 'done'])], limit=5)`
- Khởi tạo Wizard hoặc trực tiếp tạo record `stock.scrap` cho một dòng `stock.move` ngẫu nhiên trong phiếu kho.
