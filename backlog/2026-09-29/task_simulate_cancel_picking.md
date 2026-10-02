# Backlog: Giả lập thao tác Hủy (Cancel) phiếu kho

## 1. Ngữ cảnh (Context)
Trong quá trình vận hành, nhân viên kho có thể phát hiện một phiếu xuất/nhập kho được tạo sai hoặc đối tác hủy giao dịch trước khi hàng được giao. Thay vì hoàn thành, nhân viên sẽ tiến hành Hủy (Cancel) phiếu kho này.

## 2. Mục tiêu của Task (Objectives)
Giả lập thao tác Hủy phiếu trên hệ thống bằng code Backend (Simulator):
1. Tìm và chọn các phiếu kho có trạng thái cho phép hủy (ví dụ: `draft`, `confirmed`, `assigned`).
2. Gọi hàm `action_cancel()` trên đối tượng `stock.picking`.
3. Xác minh rằng phiếu kho chuyển sang trạng thái `cancel` và hệ thống tự động nhả số lượng hàng hóa đang giữ (reserved) về lại kho.

## 3. Kịch bản kiểm thử (Test Cases)
*Nguyên tắc TDD: Cần xác định kịch bản trước khi viết code.*

**Kịch bản 1: Hủy phiếu kho đang giữ hàng (Assigned)**
- **Pre-condition:** Phiếu kho ở trạng thái `assigned` (Sẵn sàng). Có các dòng chi tiết (`stock.move.line`) đang chiếm dụng hàng hóa.
- **Action:** Gọi `picking.action_cancel()`.
- **Expected Result:** 
  - Phiếu gốc và các chi tiết chuyển sang trạng thái `cancel`.
  - Số lượng hàng hóa đang bị "giữ" (reserved) trong kho tự động được trả lại.

**Kịch bản 2: Bắt lỗi khi cố gắng hủy phiếu đã hoàn thành (Done)**
- **Pre-condition:** Phiếu kho ở trạng thái `done` (Đã hoàn thành).
- **Action:** Gọi `picking.action_cancel()`.
- **Expected Result:** Odoo văng lỗi (UserError) ngăn chặn việc hủy phiếu đã hoàn thành.
