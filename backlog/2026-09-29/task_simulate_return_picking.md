# Backlog: Giả lập thao tác Trả hàng (Return Wizard)

## 1. Ngữ cảnh (Context)
Do Odoo không cho phép hủy (cancel) một phiếu kho đã hoàn thành (`done`), nhân viên phải thực hiện thao tác "Trả hàng" (Return) khi giao/nhận sai hoặc hàng bị lỗi. Thao tác này sinh ra một phiếu kho mới đi ngược chiều với phiếu gốc.

## 2. Mục tiêu của Task (Objectives)
Tương tự như Backorder, thao tác Trả hàng yêu cầu xử lý Wizard:
1. Bấm nút Return trên UI sẽ kích hoạt action mở model `stock.return.picking`.
2. Tạo record trên model wizard này, thiết lập số lượng hàng trả lại.
3. Gọi hàm xác nhận để sinh ra phiếu trả hàng mới.

## 3. Kịch bản kiểm thử (Test Cases)
*Nguyên tắc TDD: Cần xác định kịch bản trước khi viết code.*

**Kịch bản 1: Trả lại toàn bộ hàng của một phiếu xuất kho**
- **Pre-condition:** Phiếu xuất kho gốc (`WH/OUT/...`) đã ở trạng thái `done`.
- **Action:** 
  - Khởi tạo object `stock.return.picking` với context trỏ về phiếu xuất gốc.
  - Giữ nguyên số lượng trả mặc định (toàn bộ).
  - Gọi hàm `create_returns()`.
- **Expected Result:** 
  - Một phiếu nhập kho mới (`WH/IN/Return...` hoặc phiếu có tên liên quan) được tạo ra tự động ở trạng thái `draft` hoặc `assigned`.
  - Phiếu mới này trỏ link ngược về phiếu gốc thông qua trường liên kết.
