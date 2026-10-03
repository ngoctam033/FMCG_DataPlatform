# Báo cáo thay đổi quyền xử lý Cancel Backorder

**Ngày thực hiện:** 03/10/2026

**Module:** `employee_simulator`

**Chức năng:** Cron giả lập từ chối tạo Backorder

**Phạm vi báo cáo:** Thay đổi chức năng đang nằm trong Git staging area

---

## 1. Bối cảnh

Cron `cron_simulate_backorder_cancel` giả lập thao tác của nhân viên khi xử lý activity xác nhận Backorder. Với mỗi picking được chọn, cron tạo wizard `stock.backorder.confirmation` và gọi `process_cancel_backorder()` để xác nhận số lượng thực tế, đồng thời không tạo phiếu giao phần còn thiếu.

Để giữ đúng ngữ cảnh người thao tác, wizard được tạo bằng user đang được giao activity. Tuy nhiên, activity có thể được giao cho user không có quyền Kho hoặc user không được phép làm việc với công ty của picking. Khi đó Odoo có thể từ chối việc tạo hoặc xử lý wizard bằng lỗi phân quyền.

## 2. Nguyên nhân thay đổi

Logic fallback trước đây lấy trực tiếp danh sách user từ nhóm `stock.group_stock_user` và chọn phần tử đầu tiên:

```python
stock_users = self.env.ref('stock.group_stock_user').sudo().users
```

Cách chọn này chỉ kiểm tra user có thuộc nhóm Kho, nhưng chưa đảm bảo:

- User vẫn đang hoạt động.
- User được phép truy cập công ty của picking.
- Kết quả được chọn ổn định giữa các lần chạy.

Với môi trường nhiều công ty, một user có quyền Kho nhưng không thuộc `picking.company_id` vẫn có thể gây lỗi AccessError hoặc lỗi company consistency khi tạo wizard và xử lý chứng từ.

## 3. Nội dung thay đổi

### 3.1. Tìm user Kho theo điều kiện cụ thể

Khi user được giao activity không thuộc nhóm `stock.group_stock_user`, cron chuyển sang tìm một user thay thế bằng truy vấn trên `res.users`:

```python
stock_user = self.env['res.users'].sudo().search([
    ('active', '=', True),
    ('all_group_ids', 'in', [stock_group.id]),
    ('company_ids', 'in', [picking.company_id.id]),
], order='id', limit=1)
```

User thay thế phải đồng thời đáp ứng các điều kiện:

1. Đang hoạt động.
2. Có quyền Kho, bao gồm cả quyền được kế thừa từ nhóm khác.
3. Có quyền truy cập công ty của picking.

Kết quả được sắp xếp theo `id` và giới hạn một bản ghi để việc lựa chọn có tính ổn định.

### 3.2. Giữ quyền thực tế khi xử lý nghiệp vụ

`sudo()` chỉ được sử dụng cho thao tác tìm user thay thế. Sau khi tìm được user, picking và wizard vẫn được xử lý bằng quyền thực tế của user đó:

```python
simulated_picking = picking.with_user(user_id)
```

Wizard tiếp tục được tạo bằng cả user và company context tương ứng:

```python
.with_user(user_id).with_company(picking.company_id.id)
```

Thiết kế này tránh bypass toàn bộ cơ chế bảo mật của Odoo trong bước xác nhận Backorder.

### 3.3. Xử lý lỗi nghiệp vụ khi hủy Backorder

File được bổ sung `UserError` và logger để xử lý lỗi phát sinh từ `process_cancel_backorder()`:

- Nếu lỗi có nội dung `Lot/Serial`, cron tạo activity `mail_activity_missing_lot` để yêu cầu bổ sung Lot/Serial.
- Với các `UserError` khác, cron ghi exception kèm tên picking vào log.
- Picking lỗi được bỏ qua để cron tiếp tục xử lý bản ghi tiếp theo.
- Activity Backorder chỉ được đóng khi picking đã chuyển sang trạng thái `done`.

## 4. Luồng xử lý sau thay đổi

1. Tìm tối đa năm picking có activity Backorder và không có activity thiếu Lot/Serial.
2. Lấy user đang được giao activity Backorder.
3. Nếu user có quyền Kho, tiếp tục sử dụng user đó.
4. Nếu user không có quyền Kho, tìm một user Kho đang hoạt động và thuộc công ty của picking.
5. Tạo wizard trong đúng user context và company context.
6. Gọi `process_cancel_backorder()`.
7. Nếu thiếu Lot/Serial, tạo activity cảnh báo và chuyển sang picking tiếp theo.
8. Nếu xử lý thành công và picking ở trạng thái `done`, đóng các activity Backorder tương ứng.

## 5. Kết quả mong đợi

- Giảm lỗi phân quyền khi activity được giao cho user không có quyền Kho.
- Tránh chọn nhầm user Kho không thuộc công ty của picking.
- Đảm bảo user thay thế vẫn đang hoạt động.
- Giữ đúng cơ chế access control vì thao tác nghiệp vụ không chạy bằng `sudo()`.
- Không làm dừng toàn bộ lượt cron khi một picking gặp `UserError` trong bước xử lý.
- Không đóng activity khi picking chưa hoàn tất.

## 6. Điểm cần lưu ý

Sau truy vấn, code hiện gọi:

```python
stock_user.ensure_one()
```

Nếu hệ thống không có bất kỳ user đang hoạt động nào vừa có quyền Kho vừa thuộc công ty của picking, `ensure_one()` sẽ phát sinh lỗi và làm dừng cron. Đây là khác biệt so với logic cũ, vốn fallback về `self.env.user` khi danh sách user Kho rỗng.

Vì vậy, trước khi triển khai cần bảo đảm mỗi công ty có ít nhất một user Kho đang hoạt động, hoặc bổ sung một chiến lược fallback phù hợp cho trường hợp không tìm thấy user.

Ngoài ra, việc nhận diện lỗi thiếu Lot/Serial hiện dựa trên chuỗi `'Lot/Serial'` trong nội dung exception. Nếu ngôn ngữ giao diện hoặc thông báo chuẩn của Odoo thay đổi, nhánh xử lý chuyên biệt này có thể không được kích hoạt.

## 7. File thay đổi

- `odoo/custom_addons/employee_simulator/models/stock_picking_cancel.py`

## 8. Trạng thái kiểm tra

- Đã đọc và đối chiếu staged diff với phiên bản tại `HEAD`.
- Đã xác nhận truy vấn sử dụng field `all_group_ids` có tồn tại trên `res.users` trong source code Odoo của repository.
- Đã xác nhận user được lọc theo `active`, nhóm Kho và `company_ids`.
- Chưa chạy cron trên database Odoo.
- Chưa có kiểm thử tự động cho trường hợp không tìm được user Kho phù hợp.
- Chưa có kiểm thử tự động cho thông báo Lot/Serial theo nhiều ngôn ngữ.

## 9. Kết luận

Thay đổi làm cho việc lựa chọn user thay thế trong cron Cancel Backorder chặt chẽ hơn, đặc biệt trong môi trường nhiều công ty. User được chọn phải đang hoạt động, có quyền Kho và có quyền truy cập đúng công ty của picking.

Thay đổi giải quyết trường hợp chọn nhầm user không phù hợp, nhưng vẫn cần xử lý hoặc chấp nhận rõ khả năng cron dừng khi không tìm thấy bất kỳ user Kho hợp lệ nào.
