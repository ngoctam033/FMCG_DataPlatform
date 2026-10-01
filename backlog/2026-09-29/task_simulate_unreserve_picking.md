# Backlog: Giả lập thao tác Hủy giữ hàng (Unreserve)

## 1. Ngữ cảnh (Context)
Khi một phiếu kho được "Kiểm tra tình trạng sẵn có" (Check Availability), hệ thống sẽ giữ (reserve) hàng cho nó. Tuy nhiên, nếu có đơn hàng khác quan trọng hơn (VIP) cần gấp, nhân viên phải nhả phần hàng hóa này ra.

## 2. Mục tiêu của Task (Objectives)
Giả lập việc bấm nút "Unreserve" trên giao diện Odoo:
1. Xác định các phiếu kho đang "ôm" hàng (`assigned`).
2. Gọi hàm `do_unreserve()` để nhả hàng.
3. Phiếu quay lại trạng thái chờ và số lượng reserved trong kho được trả lại.

## 3. Kịch bản kiểm thử (Test Cases)
*Nguyên tắc TDD: Cần xác định kịch bản trước khi viết code.*

**Kịch bản 1: Hủy giữ hàng thành công**
- **Pre-condition:** Phiếu kho A đang ở trạng thái `assigned`. Số lượng Reserve của sản phẩm X đang là 10.
- **Action:** Gọi `picking.do_unreserve()`.
- **Expected Result:** 
  - Trạng thái phiếu kho A lùi về `confirmed`.
  - Các dòng chi tiết (`move_line_ids`) bị xóa hoặc được cập nhật số lượng Reserve về 0.
  - Tồn kho `stock.quant` trả lại 10 sản phẩm cho mọi người cùng lấy.
