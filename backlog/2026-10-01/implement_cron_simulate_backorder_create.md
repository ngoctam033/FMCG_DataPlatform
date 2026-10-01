# Task: Triển khai Cron Giả lập Tạo Backorder (Create Backorder)

## Mục tiêu
Tạo một hàm cron để tự động xử lý các phiếu kho đang gắn activity `mail_activity_backorder` bằng cách LUÔN CHỌN hành động "Tạo Backorder" (Create Backorder) thông qua popup `stock.backorder.confirmation`.

## Chi tiết công việc
1. **Model**: Thêm một phương thức Python vào mô hình `employee.simulator` trong file `odoo/custom_addons/employee_simulator/models/action_simulator.py`.
2. **Phương thức**: Đặt tên là `cron_simulate_backorder_create`.
3. **Logic**:
    - Lấy ID của activity type `mail_activity_backorder`.
    - Tìm kiếm các `stock.picking` có gắn activity này (có thể đặt `limit=5` hoặc `10`).
    - Gọi model `stock.backorder.confirmation` với `context` chuẩn của picking (`button_validate_picking_ids`, `default_pick_ids`).
    - Gọi phương thức `process()` của wizard để tự động tạo backorder.
    - Duyệt và đóng (mark as done) các activity `mail_activity_backorder` tương ứng của picking đó.
4. **Data XML**: Thêm bản ghi `ir.cron` vào `odoo/custom_addons/employee_simulator/data/cron_data.xml` để cấu hình lịch chạy cho phương thức này (ví dụ: mỗi 2 hoặc 5 phút).

## Ghi chú
Hàm này sẽ cạnh tranh xử lý phiếu kho với hàm từ chối tạo backorder nếu cả hai cùng chạy. Thiết lập `interval_number` hợp lý để cân bằng tỷ lệ xử lý.
