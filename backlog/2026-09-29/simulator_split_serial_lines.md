# Backlog: Xử lý "Tách dòng" (Split Line) cho sản phẩm Serial có số lượng > 1

**Ngày ghi nhận:** 2026-09-29
**Module:** `employee_simulator`
**Tác vụ:** Cập nhật `cron_process_missing_lot_activities`

## Mô tả
Đối với sản phẩm quản lý theo số Sê-ri (Serial), nếu phiếu nhập yêu cầu số lượng (qty) lớn hơn 1, hệ thống Odoo bắt buộc phải xé nhỏ thành nhiều dòng `stock.move.line` (mỗi dòng có số lượng hoàn thành = 1 và mang 1 số Serial riêng biệt). Cron hiện tại chỉ đang xử lý cho điều kiện `qty <= 1.0` và để lại các trường hợp `qty > 1.0` (không đóng activity).

## Yêu cầu khi triển khai
- Bỏ lệnh `continue` ở nhánh `else` của phần kiểm tra tracking Serial.
- Lưu trữ lại thông tin dòng tổng (`move_id`, `product_id`, `location_id`...).
- Xóa dòng tổng ban đầu chưa có thông tin Serial (`line.unlink()`).
- Chạy vòng lặp `for` theo tổng số lượng yêu cầu để gọi hàm `self.env['stock.move.line'].create(...)` tạo mới hàng loạt dòng chi tiết.
- Đảm bảo cơ chế sinh tên Serial mới phải đưa thêm bộ đếm vòng lặp (index) vào tham số Salt để các mã sinh ra hoàn toàn khác biệt.
