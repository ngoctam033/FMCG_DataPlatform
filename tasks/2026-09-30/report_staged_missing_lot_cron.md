# Báo cáo đối chiếu Staged Changes với Backlog

**Ngày:** 30/09/2026  
**Phạm vi kiểm tra:** `git diff --cached`  
**File đang stage:** `odoo/custom_addons/employee_simulator/models/stock_picking_utils.py`

## 1. Tóm tắt thay đổi đang stage

Thay đổi nằm trong hàm `cron_find_missing_lot_pickings`, thuộc luồng xử lý
phiếu kho thiếu Lot/Serial:

- Giới hạn picking type ở `incoming` và `mrp_operation`.
- Loại trừ picking đã có Activity loại thiếu Lot/Serial đang mở.
- Loại trừ picking đã từng hoàn tất Activity loại này.
- Bỏ giới hạn tối đa 30 picking được xử lý trong vòng lặp; phần giới hạn hiện
  chỉ còn là comment.

## 2. Kết quả đối chiếu backlog

### Không có nhiệm vụ khớp hoàn toàn

Không tìm thấy backlog nào mô tả chính xác tập thay đổi trên.

### Mục gần nhất

`backlog/2026-09-30/ir_filters_cron_domains.md`

Mục này cùng đề cập đến `cron_find_missing_lot_pickings`, domain lọc theo
`picking_type_id.code`, `activity_ids` và `message_ids`. Tuy nhiên, mục tiêu
chính của backlog là chuyển domain tĩnh từ Python lên `ir.filters`, đồng thời
đọc domain bằng `safe_eval` và ghép domain động bằng `expression.AND`.

Staged change hiện tại **chưa thực hiện** các phần đó; domain vẫn được khai báo
trực tiếp trong Python. Vì vậy không nên xem staged change là hoàn thành
`ir_filters_cron_domains`.

### Các backlog liên quan nhưng không khớp

- `backlog/2026-09-29/simulator_auto_lot_outgoing.md`: yêu cầu bỏ lọc
  `picking_type_id.code` để hỗ trợ `outgoing` và `internal`, trong khi staged
  change vẫn giữ và làm rõ giới hạn chỉ xử lý `incoming`/`mrp_operation`.
- `backlog/2026-09-29/simulator_split_serial_lines.md`: nói về tách dòng Serial
  có số lượng lớn, không được thay đổi trong staged diff.
- Các backlog về Cancel picking: không liên quan đến cron thiếu Lot/Serial.

## 3. Kết luận

Staged change nên được ghi nhận là một thay đổi riêng liên quan đến việc lọc
candidate và chống tạo Activity thiếu Lot/Serial trùng lặp. Thay đổi này chưa
khớp hoàn toàn với nhiệm vụ nào trong `backlog/`, do đó báo cáo này được tạo để
đính kèm commit.

## 4. Lưu ý trước khi commit

- Việc bỏ giới hạn tối đa 30 record làm thay đổi chủ đích batch processing đã
  được ghi nhận trong `backlog/2026-09-29/TASK-003_employee_simulator_cron_log.md`
  (backlog này khuyến nghị giữ giới hạn nếu đó là chủ đích mô phỏng).
- Nếu mục tiêu thật sự là triển khai `ir_filters_cron_domains`, cần bổ sung
  `ir.filters`, cập nhật module manifest và sửa code đọc domain từ database.
- Nếu mục tiêu là hỗ trợ picking `outgoing`/`internal`, staged change hiện tại
  đi ngược yêu cầu của `simulator_auto_lot_outgoing`.

