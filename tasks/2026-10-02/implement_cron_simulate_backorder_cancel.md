# Task: Triển khai Cron Giả lập Từ chối Backorder (Cancel Backorder)

## Mục tiêu
Tạo một hàm cron để tự động xử lý các phiếu kho đang gắn activity `mail_activity_backorder` bằng cách LUÔN CHỌN hành động "Không tạo phần dư" (No Backorder / Cancel Backorder) thông qua popup `stock.backorder.confirmation`.

## Chi tiết công việc
1. **Model**: Thêm một phương thức Python vào mô hình `employee.simulator` trong file `odoo/custom_addons/employee_simulator/models/action_simulator.py`.
2. **Phương thức**: Đặt tên là `cron_simulate_backorder_cancel`.
3. **Logic**:
    - Lấy ID của activity type `mail_activity_backorder`.
    - Tìm kiếm các `stock.picking` có gắn activity này (có thể đặt `limit=5` hoặc `10`).
    - Gọi model `stock.backorder.confirmation` với `context` chuẩn của picking (`button_validate_picking_ids`, `default_pick_ids`).
    - Gọi phương thức `process_cancel_backorder()` của wizard để xác nhận chốt số lượng thực tế và từ chối tạo backorder.
    - Duyệt và đóng (mark as done) các activity `mail_activity_backorder` tương ứng của picking đó.
4. **Data XML**: Thêm bản ghi `ir.cron` vào `odoo/custom_addons/employee_simulator/data/cron_data.xml` để cấu hình lịch chạy cho phương thức này (ví dụ: mỗi 3 hoặc 5 phút).

## Ghi chú
Lưu ý về tần suất chạy cron (`interval_number`) của hàm này so với hàm `cron_simulate_backorder_create` để có được tỷ lệ sinh/hủy backorder như mong muốn trong quá trình giả lập.
