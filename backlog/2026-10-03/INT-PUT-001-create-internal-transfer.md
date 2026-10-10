# INT-PUT-001 — Tạo phiếu chuyển nội bộ nháp

## User action được mô phỏng

Nhân viên mở **Inventory > Operations > Transfers**, bấm **New**, chọn Operation Type là Internal Transfer, nhập nguồn/đích và sản phẩm, sau đó lưu phiếu.

## Cron dự kiến

`cron_simulate_internal_transfer_create`

## Một action duy nhất

Tạo một `stock.picking` loại `internal` cùng các dòng nhu cầu, để phiếu dừng ở trạng thái `draft`.

Cron **không được** gọi `action_confirm()`, `action_assign()` hoặc `button_validate()`.

## Pre-condition

- Có user nội bộ thuộc nhóm nhân viên kho và có quyền trên company được chọn.
- Có `stock.picking.type` với `code = 'internal'`.
- Có ít nhất hai location nội bộ hợp lệ và khác nhau.
- Có sản phẩm lưu kho phù hợp company.

## Kết quả mong đợi

- Tạo đúng một picking nháp với `origin` theo mẫu `SIM-INT-*`.
- `location_id` và `location_dest_id` khác nhau.
- Có ít nhất một `stock.move` với `product_uom_qty > 0`.
- Không làm thay đổi tồn kho và không reserve hàng.

## Tiêu chí nghiệm thu

- Chỉ chọn operation type `internal`, không chọn ngẫu nhiên incoming/outgoing.
- Không tạo phiếu khi thiếu nguồn, đích, sản phẩm hoặc user hợp lệ.
- Có log liên kết simulator user, picking, source và destination.
- Test xác nhận picking vẫn là `draft` sau khi cron kết thúc.
