# INT-PUT-002 — Xác nhận phiếu chuyển nội bộ

## User action được mô phỏng

Nhân viên mở phiếu chuyển nội bộ nháp và bấm **Mark as Todo/Confirm**.

## Cron dự kiến

`cron_simulate_internal_transfer_confirm`

## Một action duy nhất

Gọi action xác nhận trên một picking nháp, tương ứng `action_confirm()`.

Cron **không được** kiểm tra khả dụng, nhập quantity, đổi vị trí đích hoặc validate.

## Pre-condition

- `picking_type_id.code = 'internal'`.
- `state = 'draft'`.
- `origin` bắt đầu bằng `SIM-INT-`.
- Có ít nhất một move với nhu cầu lớn hơn 0.

## Kết quả mong đợi

- Picking rời `draft` và chuyển sang trạng thái phù hợp do Odoo quyết định, thường là `confirmed`, `waiting` hoặc `assigned` tùy cấu hình reservation.
- Không có số lượng thực tế được simulator tự điền.

## Tiêu chí nghiệm thu

- Mỗi picking chỉ được gọi `action_confirm()` một lần.
- Không giả định cứng trạng thái sau confirm luôn là `confirmed`.
- Picking không đúng pre-condition được bỏ qua.
- Test chứng minh cron không gọi `action_assign()` hay `button_validate()`.
