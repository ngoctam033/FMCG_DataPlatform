# Backlog: giả lập `action_put_in_pack` trong `employee.simulator`

## Phạm vi

Nghiên cứu các kịch bản nhân viên kho có thể thực hiện quanh thao tác **Put in Pack** trên `stock.picking`. Tài liệu này chỉ là backlog/định hướng; không thay đổi mã nghiệp vụ hiện tại.

## Tóm tắt hàm hiện tại

```python
def action_put_in_pack(self, *, package_id=False, package_type_id=False, package_name=False):
    self.ensure_one()
    if self.env.context.get('sml_specific_default'):
        self = self.with_context(clean_context(self.env.context))
    if self.state not in ('done', 'cancel'):
        return self.move_line_ids.action_put_in_pack(
            package_id=package_id,
            package_type_id=package_type_id,
            package_name=package_name,
        )
```

### Diễn giải

1. `self.ensure_one()` bắt buộc chỉ xử lý đúng một phiếu kho. Gọi method trên nhiều picking sẽ phát sinh lỗi singleton.
2. Nếu context có `sml_specific_default`, context được làm sạch trước khi chuyển tiếp xuống move lines. Đây là cơ chế tránh mang theo các default/context đặc thù không phù hợp.
3. Phiếu `done` hoặc `cancel` không được đóng gói thêm; method kết thúc và trả về `None`.
4. Với các trạng thái còn lại, picking ủy quyền cho `stock.move.line.action_put_in_pack`.
5. Ở tầng move line, Odoo sẽ chọn các dòng có số lượng thực tế lớn hơn 0, chưa có `result_package_id`, ưu tiên dòng đã `picked`; sau đó tạo package mới hoặc dùng package/type/name được truyền vào.
6. Nếu thiếu thông tin package và operation type yêu cầu chọn loại bao bì, method có thể trả về action mở wizard thay vì trả về record `stock.package`.
7. `package_id` dùng để đưa hàng vào package đã tồn tại; `package_type_id` tạo package mới theo loại; `package_name` đặt tên package. Các tham số này là keyword-only.

## Các rủi ro cần ghi nhận

- Cron phải lọc phiếu ở `confirmed`, `waiting` hoặc `assigned`; không chọn `done`/`cancel`.
- Cần kiểm tra có move line đủ điều kiện trước khi gọi, nếu không action có thể không tạo package.
- Nếu một picking có nhiều destination location, Odoo có thể trả về wizard chọn destination.
- Nếu operation type bật `set_package_type` mà cron không truyền thông tin package, kết quả có thể là wizard dictionary; simulator phải log và phân biệt dictionary với `stock.package`.
- Không dùng cùng một package cho các picking có operation type khác nhau.
- Cần chạy bằng `with_user(user_id)` để mô phỏng quyền nhân viên; việc này có thể làm action thất bại nếu user thiếu quyền kho.
- Phải tránh chọn lặp picking trong cùng một lần cron và giới hạn batch để không gây lock/timeout.

## Backlog đề xuất

| ID | Ưu tiên | Hạng mục | Kịch bản giả lập | Điều kiện chọn | Kết quả mong đợi |
|---|---|---|---|---|---|
| PACK-001 | P0 | Đóng gói cơ bản | Nhân viên đóng các dòng đã `picked` của picking `assigned` | `state='assigned'`, có quantity > 0, chưa có package | Tạo một `stock.package`; các dòng đủ điều kiện có cùng `result_package_id` |
| PACK-002 | P0 | Đóng gói theo package type | Nhân viên chọn thùng/carton/pallet | Có `stock.package.type` hợp lệ cùng company | Tạo package với đúng `package_type_id`; ghi log package và picking |
| PACK-003 | P0 | Chỉ đóng gói phần đã pick | Picking có cả dòng `picked` và chưa pick | Có ít nhất một dòng `picked` | Chỉ dòng đã pick được đóng gói; dòng chưa pick vẫn chưa có `result_package_id` |
| PACK-004 | P0 | Bỏ qua picking không hợp lệ | Cron gặp picking `done`, `cancel`, không quantity hoặc đã đóng gói | Lọc trước và kiểm tra lại trước khi gọi | Không tạo package; log lý do bỏ qua |
| PACK-005 | P1 | Đặt tên package | Sinh tên theo mã picking/ca/ngày | Tên không trùng trong phạm vi nghiệp vụ | Package có `name` dễ truy vết, không làm lộ dữ liệu nhạy cảm |
| PACK-006 | P1 | Đưa vào package có sẵn | Nhân viên gộp thêm dòng vào thùng đang mở | Package tồn tại, cùng operation type/company, còn khả năng nhận hàng | Dòng được gán vào package chỉ định; không tạo package dư |
| PACK-007 | P1 | Wizard chọn loại bao bì | Không truyền `package_id`, `package_type_id`, `package_name` trong operation type yêu cầu wizard | `_should_display_put_in_pack_wizard()` trả true | Simulator log action dictionary; không coi wizard action là package đã tạo |
| PACK-008 | P1 | Destination khác nhau | Picking có move lines đến nhiều location | Nhiều `location_dest_id` | Log/đưa vào backlog xử lý wizard destination; không tự gán sai location |
| PACK-009 | P1 | In nhãn package | Picking type bật auto print package label | Cấu hình label là PDF hoặc ZPL | Log action in nhãn và package; không làm cron crash nếu action là dictionary |
| PACK-010 | P1 | Quyền nhân viên | Chạy cùng action bằng nhiều user kho | User có/không có quyền stock | User hợp lệ đóng gói được; user thiếu quyền có lỗi được bắt và log, cron tiếp tục |
| PACK-011 | P2 | Đóng gói từng nhóm | Một picking có nhiều nhóm sản phẩm/lô | Quy tắc nhóm theo product, lot hoặc package type | Mỗi nhóm tạo package riêng; không trộn sai lot/serial |
| PACK-012 | P2 | Đóng gói hàng tracking | Dòng sản phẩm tracking lot/serial đã có lot/serial | Có lot/serial hợp lệ và quantity > 0 | Giữ nguyên lot/serial; package gán đúng dòng |
| PACK-013 | P2 | Đóng gói partial/backorder | Validate thiếu một phần, phát sinh backorder | Picking còn quantity đã xử lý | Chỉ phần đã xử lý được đóng gói; backorder không bị đóng nhầm |
| PACK-014 | P2 | Idempotency | Cron chạy lại trên cùng picking | Picking đã có `result_package_id` | Không tạo package trùng; lần chạy sau ghi nhận “nothing to pack” |
| PACK-015 | P3 | Đóng gói từ batch | Nhân viên thao tác trên `stock.picking.batch` | Batch có các picking tương thích | Chỉ đóng các dòng hợp lệ và xử lý đúng giới hạn singleton của batch method |

## Thứ tự triển khai khuyến nghị

1. PACK-001, PACK-003, PACK-004 và PACK-014: luồng cơ bản, lọc an toàn, chạy lại không tạo dữ liệu rác.
2. PACK-002, PACK-005, PACK-012: dữ liệu package thực tế và truy vết.
3. PACK-007, PACK-008, PACK-009: các trường hợp action/wizard và in nhãn.
4. PACK-006, PACK-010, PACK-011, PACK-013, PACK-015: nâng cao, quyền và nghiệp vụ phức tạp.

## Gợi ý contract cho cron mới

Tên dự kiến: `cron_simulate_picking_put_in_pack`.

- Tìm picking trong `assigned` trước; có thể mở rộng `confirmed`/`waiting` nếu simulator có bước chuẩn bị quantity/picked.
- Chọn tối đa 1–3 picking mỗi lần, không lặp record trong cùng batch.
- Chọn user nội bộ ngẫu nhiên nhưng có fallback `env.user`.
- Với mỗi picking, chọn một scenario rõ ràng: package mới, package type, package có sẵn hoặc wizard.
- Gọi `with_user(selected_user.id).action_put_in_pack(...)`.
- Nếu kết quả là record `stock.package`, log `id`, `name`, `package_type_id` và số dòng đã đóng gói.
- Nếu kết quả là dictionary action, log `type`, `res_model`, `res_id`/context và đánh dấu là “wizard/action returned”.
- Bắt lỗi theo từng picking, ghi `_logger.exception`, không rollback toàn bộ batch do một picking lỗi.

## Tiêu chí nghiệm thu chung

- Không gọi method trên recordset nhiều picking.
- Không tạo package cho `done`/`cancel`, picking không có quantity hợp lệ hoặc đã được đóng gói hoàn toàn.
- Không tạo package trùng khi chạy lại cron.
- Có log đủ để truy từ simulator user → picking → move lines → package/action.
- Có test cho kết quả là `stock.package`, wizard dictionary và trường hợp không có kết quả.
