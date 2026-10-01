# Backlog: Giả lập xử lý Wizard Backorder (Giao/Nhận thiếu hàng)

## 1. Ngữ cảnh (Context)
Trong quá trình giả lập luồng kho, khi nhân viên kho điền số lượng thực tế (Done Quantity) nhỏ hơn số lượng yêu cầu (Demand Quantity), hành động `button_validate()` sẽ không hoàn thành phiếu ngay mà ngắt luồng và trả về một Action mở Wizard cảnh báo.

**Log ghi nhận từ Odoo:**
```json
{
    "name": "Create Backorder?",
    "type": "ir.actions.act_window",
    "view_mode": "form",
    "res_model": "stock.backorder.confirmation",
    "views": [[940, "form"]],
    "view_id": 940,
    "target": "new",
    "context": {
        "lastcall": null,
        "cron_id": 32,
        "cron_end_time": 7525.563740126,
        "ir_cron_progress_id": 10960,
        "mail_notify_force_send": false,
        "guest": null,
        "button_validate_picking_ids": [9528],
        "default_show_transfers": false,
        "default_pick_ids": [[4, 9528]]
    }
}
```

## 2. Mục tiêu của Task (Objectives)
Giả lập thao tác của nhân viên trên giao diện UI khi gặp bảng cảnh báo này:
1. Xử lý kết quả trả về của hàm `button_validate()`.
2. Bắt điều kiện: Nếu kết quả trả về là một `dict` và có `res_model == 'stock.backorder.confirmation'`.
3. Tái tạo lại Wizard trong code Backend bằng cách truyền `context` nhận được từ Odoo vào record mới của model `stock.backorder.confirmation`.
4. Gọi hàm xử lý tương ứng trên Wizard để giả lập hành động click nút:
   - **Tùy chọn 1:** Bấm nút "Create Backorder" (Thường gọi hàm `process()`).
   - **Tùy chọn 2:** Bấm nút "No Backorder" (Thường gọi hàm `process_cancel_backorder()`).

## 3. Kịch bản kiểm thử (Test Cases)
*Nguyên tắc TDD: Cần xác định kịch bản trước khi viết code.*

**Kịch bản 1: Nhân viên chọn Tạo Backorder**
- **Pre-condition:** Phiếu kho số `WH/OUT/02860` (ID: 9528) đang ở trạng thái `assigned`, số lượng Done < số lượng Demand.
- **Action:** Gọi `button_validate()` -> bắt kết quả -> Tạo object `stock.backorder.confirmation` với context trên -> Gọi hàm `process()`.
- **Expected Result:** 
  - Phiếu gốc `WH/OUT/02860` chuyển sang `done` (với số lượng thực tế).
  - Một phiếu kho mới (Backorder) được tự động sinh ra cho phần số lượng còn thiếu và ở trạng thái `assigned` hoặc `confirmed`.

**Kịch bản 2: Nhân viên chọn KHÔNG Tạo Backorder (Hủy phần thiếu)**
- **Pre-condition:** Tương tự kịch bản 1.
- **Action:** Gọi `button_validate()` -> bắt kết quả -> Tạo object `stock.backorder.confirmation` -> Gọi hàm `process_cancel_backorder()`.
- **Expected Result:** 
  - Phiếu gốc `WH/OUT/02860` chuyển sang `done`.
  - Không có phiếu mới nào được tạo thêm. Phần số lượng thiếu bị hủy bỏ.
