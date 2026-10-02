# Backlog: Giả lập thao tác Xóa (Delete) phiếu kho

## 1. Ngữ cảnh (Context)
Xóa phiếu kho là thao tác "dọn dẹp" database đối với các phiếu nháp tạo nhầm hoặc các phiếu đã bị hủy. Odoo kiểm soát cực kỳ nghiêm ngặt việc xóa dữ liệu.

## 2. Mục tiêu của Task (Objectives)
Giả lập thao tác người dùng xóa một phiếu kho, và xác minh cơ chế bảo vệ dữ liệu của Odoo:
1. Xóa thành công đối với phiếu Hợp lệ (`draft`, `cancel`).
2. Bị chặn lại đối với phiếu Không Hợp lệ (các trạng thái còn lại).
3. Sử dụng hàm `unlink()` để giả lập.

## 3. Kịch bản kiểm thử (Test Cases)
*Nguyên tắc TDD: Cần xác định kịch bản trước khi viết code.*

**Kịch bản 1: Xóa phiếu kho đã hủy (Hợp lệ)**
- **Pre-condition:** Phiếu kho ở trạng thái `cancel`.
- **Action:** Gọi `picking.unlink()`.
- **Expected Result:** Phiếu kho bị xóa vĩnh viễn khỏi Database. Không có lỗi phát sinh.

**Kịch bản 2: Cố gắng xóa phiếu đang chờ (Không hợp lệ)**
- **Pre-condition:** Phiếu kho đang ở trạng thái `confirmed` hoặc `assigned`.
- **Action:** Gọi `picking.unlink()`.
- **Expected Result:** Odoo văng ra ngoại lệ (`UserError` hoặc `AccessError`), ngăn cản việc xóa.
