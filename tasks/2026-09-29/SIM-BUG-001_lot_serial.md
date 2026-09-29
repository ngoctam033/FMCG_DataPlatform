# Backlog: Xử lý lỗi thiếu Lot/Serial khi Validate phiếu kho

**Mã lỗi**: SIM-BUG-001
**Ngày ghi nhận**: 2026-09-29
**Phân hệ**: Inventory Simulator

## 1. Mô tả vấn đề
Trong quá trình Simulator chạy cron job `cron_simulate_picking_validate` để tự động xác nhận phiếu kho, hệ thống đã gặp lỗi:
`odoo.exceptions.UserError: You need to supply a Lot/Serial Number for product: - Hương Liệu Trái Cây Tổng Hợp (Lít)`

**Nguyên nhân:**
Cron job hiện tại đang trực tiếp gọi `button_validate()` trên các phiếu kho đang ở trạng thái `assigned`. Tuy nhiên, với những phiếu kho chứa sản phẩm có cấu hình quản lý theo Lô (Lot) hoặc Số Sê-ri (Serial), Odoo bắt buộc phải khai báo thông tin Lot/Serial trước khi Validate. Việc gọi thẳng `button_validate()` mà thiếu bước điền Lô/Serial dẫn đến lỗi hệ thống và làm gián đoạn tiến trình.

## 2. Giải pháp thực tế đã triển khai
Thay vì tự động sinh Lot/Serial (có thể dẫn đến sai lệch tồn kho mô phỏng), chúng ta đã thiết kế một cron job **tách biệt** chuyên đóng vai trò "cảnh báo hệ thống" để nhân viên kho kiểm đếm và ghi nhận Lô/Serial, thông qua tính năng Activity của Odoo.

Điều này giúp:
- Tách bạch trách nhiệm (Separation of Concerns) của các bot (cron job).
- Tránh làm sập tiến trình Validate tự động khi gặp phiếu kho thiếu thông tin tracking.
- Mô phỏng thực tế tốt hơn: Hệ thống quét tìm các phiếu lỗi và giao việc (Activity) cho nhân sự xử lý.

### Yêu cầu chi tiết (Acceptance Criteria) - ĐÃ HOÀN THÀNH
1. **Tạo Activity Type mới**: Định nghĩa loại công việc riêng `mail_activity_missing_lot` (Bổ sung Lot/Serial) để dễ dàng theo dõi và lọc.
2. **Tạo Cron Job mới**: Tạo cron job `ir_cron_find_missing_lot_pickings` chạy mỗi 1 phút.
3. **Logic hoạt động tối ưu**:
   - Quét tìm các phiếu kho đang ở trạng thái sẵn sàng (`assigned`), chứa sản phẩm có `tracking != 'none'`.
   - Ứng dụng **Batch Processing**: Lọc tối đa 80 phiếu từ Database và xử lý gán Activity cho tối đa 30 phiếu mỗi phút để chống tràn RAM và khóa DB.
   - Lọc thông minh: Tự động bỏ qua các phiếu kho đã từng được gán Activity này (kể cả đang mở hay đã được đánh dấu Done) bằng cách kiểm tra `activity_ids` và `message_ids` trong Python.
   - Assignee: Tự động gán Activity cho người phụ trách phiếu, hoặc mặc định giao cho Admin.
