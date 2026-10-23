# Báo cáo Review Cron đóng Activity Backorder hết hiệu lực

**Ngày review:** 2026-10-23  
**Phạm vi:** Các thay đổi đang nằm trong Git staging liên quan đến việc đóng activity Backorder trên phiếu kho đã kết thúc.

## 1. Bối cảnh lỗi

Cron `cron_simulate_backorder_cancel` có thể tìm thấy một phiếu kho vẫn còn activity `employee_simulator.mail_activity_backorder`, mặc dù phiếu đã chuyển sang `done` hoặc `cancel`.

Ví dụ `RDCS/INT/00161`:

- Phiếu đã ở trạng thái `cancel`.
- Move liên quan cũng đã `cancel`, `quantity = 0` và `picked = False`.
- Activity Backorder cũ vẫn còn mở.
- Khi cron gọi `process_cancel_backorder()`, Odoo tiếp tục gọi `button_validate()` và raise lỗi zero quantity transfer.

Activity Backorder trên phiếu `done/cancel` là activity hết hiệu lực và cần được đóng thay vì tiếp tục đưa vào luồng validate.

## 2. Nội dung đã có trong staging

### A. Method dọn activity hết hiệu lực

Tệp: `odoo/custom_addons/employee_simulator/models/stock_picking_cancel.py`

Method mới:

```python
cron_close_stale_backorder_activities()
```

Domain tìm kiếm:

```python
[
    ('state', 'in', ['done', 'cancel']),
    ('activity_ids.activity_type_id', '=', activity_type.id),
]
```

Mỗi lần chạy xử lý tối đa 100 picking. Trên từng picking, method chỉ lọc và đóng activity có đúng loại `mail_activity_backorder` bằng `action_feedback()`.

Thông điệp nghiệp vụ:

> Phiếu kho đã ở trạng thái "Done/Cancelled". Yêu cầu xác nhận Backorder không còn hiệu lực và được hệ thống tự động đóng.

Việc dùng `action_feedback()` phù hợp hơn xóa activity trực tiếp vì hệ thống vẫn lưu lại dấu vết nghiệp vụ trên chatter của phiếu kho.

### B. Khai báo Scheduled Action

Tệp: `odoo/custom_addons/employee_simulator/data/cron_data.xml`

Staging đã có đầy đủ record:

```text
XML ID:        ir_cron_close_stale_backorder_activities
Model:         employee.simulator
Code:          model.cron_close_stale_backorder_activities()
Chu kỳ:        1 phút
Priority:      7
Trạng thái:    Active
```

## 3. Kết quả kiểm tra staging

Hai thành phần bắt buộc của cron đã được stage đầy đủ:

1. Method Python chứa logic tìm và đóng activity.
2. Record XML đăng ký `ir.cron` gọi đúng method.

Các kiểm tra đã thực hiện:

- Python compile: đạt.
- XML well-formed: đạt.
- `git diff --check`: đạt, không có whitespace error.
- Tên method trong XML khớp với method Python.
- Model XML trỏ đúng `model_employee_simulator`.

## 4. Phạm vi tác động

Cron chỉ tác động tới:

- Picking có trạng thái `done` hoặc `cancel`.
- Picking vẫn còn activity `employee_simulator.mail_activity_backorder`.
- Chỉ activity Backorder được đóng; các activity cảnh báo khác như thiếu Lot/Serial không bị đóng theo.

Cron không gọi `button_validate()`, không tạo backorder, không sửa quantity và không thay đổi trạng thái picking.

## 5. Lưu ý về thay đổi chưa stage

Working tree hiện còn một thay đổi **chưa stage** trong `stock_picking_cancel.py`:

```python
["draft", "confirmed", "waiting", "assigned", "cancel"]
```

Đây là thay đổi thêm trạng thái `cancel` vào domain của `cron_find_picking_cancel_candidates`. Thay đổi này không thuộc cron dọn Backorder và không cần thiết cho chức năng được review trong báo cáo này.

Cần kiểm tra riêng trước khi stage vì việc chọn một picking đã `cancel` làm ứng viên cho activity “Chờ hủy phiếu kho” có thể tạo activity dư thừa.

## 6. Kết luận

**Trạng thái staging: ĐẦY ĐỦ cho chức năng đóng activity Backorder hết hiệu lực.**

Sau khi commit/deploy, cần upgrade module `employee_simulator` để Odoo nạp record `ir.cron` mới. Cron sau đó có thể tự động đóng activity Backorder tồn đọng trên các phiếu như `RDCS/INT/00161`.
