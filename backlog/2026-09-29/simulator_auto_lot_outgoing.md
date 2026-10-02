# Backlog: Xử lý khai báo Lot/Serial tự động cho luồng Xuất Kho / Chuyển Nội Bộ

**Ngày ghi nhận:** 2026-09-29
**Module:** `employee_simulator`
**Tác vụ:** Cập nhật `cron_process_missing_lot_activities`

## Mô tả
Cron hiện tại chỉ lọc và xử lý các phiếu Nhập kho (`incoming`, `mrp_operation`). Các phiếu luồng xuất (`outgoing`, `internal`) đang cố tình bị bỏ qua để làm đơn giản hóa cơ chế ở giai đoạn hiện tại.

## Yêu cầu khi triển khai
- Gỡ điều kiện lọc `picking_type_id.code` để cron lấy được cả phiếu xuất/nội bộ.
- Viết logic truy vấn bảng `stock.quant` để tìm kiếm mã Lot/Serial hiện đang còn tồn kho (`quantity > 0`) tại đúng vị trí (location) xuất hàng.
- Tự động lấy `lot_id` tìm được gán vào `stock.move.line` (mô phỏng thao tác người dùng chọn Lot từ Dropdown) thay vì tự tạo tên `lot_name` mới.
