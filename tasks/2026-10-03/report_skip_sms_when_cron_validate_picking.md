# Báo Cáo Bổ Sung `skip_sms` Khi Cron Xác Nhận Phiếu Kho

**Ngày thực hiện:** 03/10/2026  
**Module:** `employee_simulator`  
**Tác vụ:** Cron giả lập xác nhận phiếu kho (`cron_simulate_picking_validate`)  
**File thay đổi:** `odoo/custom_addons/employee_simulator/models/action_simulator.py`

## 1. Mục tiêu

Đảm bảo cron **Simulator: Tự động Xác nhận (Validate) Phiếu kho** có thể hoàn tất phiếu xuất kho mà không bị dừng tại wizard xác nhận SMS vốn chỉ phù hợp với thao tác có giao diện người dùng.

## 2. Hiện trạng và dấu hiệu nhận biết

Khi cron gọi `stock.picking.button_validate()` cho một phiếu xuất kho, hệ thống có thể trả về action sau:

```json
{
    "name": "SMS",
    "type": "ir.actions.act_window",
    "res_model": "confirm.stock.sms",
    "target": "new",
    "context": {
        "button_validate_picking_ids": [5172]
    }
}
```

Đây không phải exception. Nó là yêu cầu mở wizard `confirm.stock.sms` để người dùng chọn gửi hoặc không gửi SMS trước khi tiếp tục xác nhận phiếu.

Cron chạy nền không có giao diện và không thể bấm nút trên wizard. Vì vậy action chỉ được trả về và ghi vào log; lần gọi `button_validate()` kết thúc trước bước hoàn tất phiếu. Phiếu có thể tiếp tục ở trạng thái `assigned` thay vì chuyển sang `done`.

## 3. Phân tích nguyên nhân

Module chuẩn `stock_sms` mở wizard trong hook `_pre_action_done_hook()` khi đồng thời thỏa mãn các điều kiện nghiệp vụ, điển hình gồm:

- Phiếu thuộc loại xuất kho (`outgoing`).
- Đối tác nhận hàng có số điện thoại.
- Công ty đang bật thiết lập SMS khi xác nhận giao hàng.
- Cảnh báo SMS chưa được xác nhận trước đó.
- Context không có cờ `skip_sms`.

Trong luồng giao diện, người dùng xử lý wizard rồi phương thức `send_sms()` hoặc `dont_send_sms()` sẽ gọi lại `button_validate()`. Trong luồng cron, không tồn tại bước tương tác này nên quá trình bị dừng giữa chừng.

## 4. Nội dung chỉnh sửa

Lệnh cũ:

```python
action_result = simulated_picking.button_validate()
```

Lệnh mới:

```python
action_result = simulated_picking.with_context(skip_sms=True).button_validate()
```

Thay đổi chỉ bổ sung `skip_sms=True` vào context của lần validate do cron thực hiện. User giả lập được thiết lập bằng `with_user(selected_user.id)` vẫn được giữ nguyên.

## 5. Cơ chế sau chỉnh sửa

Khi nhận `skip_sms=True`, module `stock_sms` sẽ:

1. Không tạo và không trả về wizard `confirm.stock.sms` tại bước tiền xử lý.
2. Không gửi SMS xác nhận hoàn tất cho lần validate này.
3. Cho phép `button_validate()` tiếp tục chạy các bước nghiệp vụ còn lại để hoàn tất phiếu.

Cờ này chỉ tồn tại trong context của recordset dùng trong lần gọi cron. Nó không sửa cấu hình SMS của công ty và không làm thay đổi hành vi khi người dùng validate phiếu thủ công trên giao diện.

## 6. Phạm vi ảnh hưởng

### Được thay đổi

- Các phiếu được xử lý bởi `cron_simulate_picking_validate` bỏ qua wizard và việc gửi SMS.
- Cron không còn ghi action `res_model = confirm.stock.sms` rồi kết thúc mà chưa hoàn tất phiếu.

### Không bị thay đổi

- Luồng validate thủ công của người dùng.
- Cấu hình SMS cấp công ty.
- Kiểm tra số lượng, lot/serial và các kiểm tra nghiệp vụ khác của `button_validate()`.
- Logic phát hiện và xử lý action backorder trong Employee Simulator.
- Quyền và dấu vết thao tác của user giả lập.

## 7. Kịch bản kiểm thử đề xuất

### Trường hợp 1: Phiếu xuất đủ điều kiện mở wizard SMS

**Chuẩn bị:** Phiếu `outgoing` ở trạng thái `assigned`, đối tác có số điện thoại và công ty bật SMS.  
**Thực hiện:** Chạy cron validate.  
**Kỳ vọng:** Không xuất hiện action `confirm.stock.sms`; phiếu tiếp tục được validate; không có SMS được gửi.

### Trường hợp 2: Validate thủ công trên giao diện

**Thực hiện:** Người dùng bấm Validate trên một phiếu tương tự.  
**Kỳ vọng:** Wizard SMS vẫn xuất hiện theo cấu hình hiện hành vì luồng thủ công không có `skip_sms=True`.

### Trường hợp 3: Phiếu thiếu lot/serial

**Thực hiện:** Cron validate phiếu có sản phẩm yêu cầu lot/serial nhưng chưa khai báo.  
**Kỳ vọng:** Kiểm tra lot/serial vẫn phát sinh `UserError` và logic hiện tại của Employee Simulator tiếp tục tạo Activity cảnh báo.

### Trường hợp 4: Phiếu phát sinh backorder

**Thực hiện:** Cron validate phiếu có số lượng hoàn thành nhỏ hơn nhu cầu.  
**Kỳ vọng:** Luồng backorder vẫn được xử lý theo logic hiện có; việc bỏ qua SMS không bỏ qua wizard hoặc kiểm tra backorder.

## 8. Đánh giá rủi ro

Mức rủi ro thấp vì thay đổi chỉ tác động đến một lần gọi `button_validate()` trong cron và sử dụng cờ context được module chuẩn `stock_sms` hỗ trợ sẵn.

Điểm cần lưu ý: mọi phiếu được cron này hoàn tất sẽ chủ động không gửi SMS, kể cả khi công ty đã cấu hình gửi SMS. Đây là hành vi mong muốn đối với luồng giả lập tự động, nhằm tránh phát sinh thông báo thật cho khách hàng và loại bỏ phụ thuộc vào wizard giao diện.

## 9. Kết luận

Việc bổ sung `with_context(skip_sms=True)` giúp cron validate hoạt động trọn vẹn trong môi trường chạy nền. Giải pháp không bypass toàn bộ `button_validate()` và vẫn bảo toàn các kiểm tra kho quan trọng, đồng thời cô lập ảnh hưởng trong đúng phạm vi Employee Simulator.
