# Task: Implement `cron_simulate_picking_validate`

## Mục tiêu (Objective)
- Giả lập việc nhân viên kho đã lấy/giao xong hàng và bấm 'Xác nhận' để chốt sổ giao dịch.
- Khi nhấn nút này, hệ thống gọi `button_validate()`.

## Kịch bản kiểm thử (Test Scenarios - TDD)
1. **Setup (Chuẩn bị):** 
   - Các phiếu kho đã ở trạng thái `assigned` (Sẵn sàng) từ bước sinh dữ liệu trước đó. 
   - Số lượng `quantity` (hoàn thành) đã được gán sẵn một cách ngẫu nhiên (khớp 100% số lượng yêu cầu, hoặc bị hụt số lượng).
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_validate()` thông qua Cron.
   - Hàm lặp qua tối đa 3 phiếu ngẫu nhiên (áp dụng thuật toán modulo dựa trên biến thời gian và salt).
   - Bắt lấy dữ liệu trả về từ lệnh `simulated_picking.button_validate()`.
3. **Assert (Kiểm tra kết quả):**
   - **Thành công:** Nếu số lượng hoàn thành khớp yêu cầu, phiếu kho tự động chuyển sang trạng thái `done` (Hoàn thành).
   - **Có Wizard:** Nếu thiếu hàng, Odoo trả về cấu trúc JSON yêu cầu mở Wizard `stock.backorder.confirmation`. Dữ liệu này được log ra Terminal để chuẩn bị cho bước xử lý tiếp theo.

## Triển khai Logic thực tế (Implementation)
- Lọc danh sách các phiếu kho: `pickings = self.env['stock.picking'].search([('state', '=', 'assigned')])`
- Áp dụng công thức tính toán `record_count = (minute + hour + salt) % 3 + 1` để tối ưu hóa phân phối cron job.
- Chặn lỗi chia cho không (`ZeroDivisionError`) bằng việc filter danh sách rỗng, và tránh trùng phiếu bằng cách `pickings -= selected_picking`.
- Cấu hình XML tạo bản ghi `ir.cron` cho phép chạy tự động mỗi 1 phút.
