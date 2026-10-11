# INT-PUT-003 — Kiểm tra khả dụng cho chuyển nội bộ

## User action được mô phỏng

Nhân viên mở phiếu đã xác nhận và bấm **Check Availability** để Odoo reserve hàng tại vị trí nguồn.

## Cron dự kiến

`cron_simulate_internal_transfer_assign`

## Một action duy nhất

Gọi `action_assign()` trên picking đủ điều kiện.

Cron **không được** tự điền số lượng thực tế, sửa destination hoặc validate.

## Pre-condition

- Picking simulator loại `internal`.
- Trạng thái thuộc `confirmed`, `waiting` hoặc `partially_available` nếu phiên bản Odoo hỗ trợ.
- Source location có tồn khả dụng cho ít nhất một dòng.

## Kết quả mong đợi

- Odoo thực hiện reservation theo tồn thực tế.
- Picking có thể thành `assigned`, còn `waiting`, hoặc chỉ khả dụng một phần; cron không ép kết quả.
- Không phát sinh dịch chuyển tồn thực tế vì chưa validate.

## Tiêu chí nghiệm thu

- Gọi đúng một action `action_assign()`.
- Có log số lượng yêu cầu và số lượng đã reserve trước/sau action.
- Thiếu tồn là kết quả nghiệp vụ hợp lệ, không phải lý do để cron tự tạo tồn.
- Test xác nhận quantity thực tế không bị cron thay đổi.
