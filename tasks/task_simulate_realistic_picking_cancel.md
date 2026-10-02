# Task: Nghiên cứu và giả lập hủy phiếu kho sát thực tế

## 1. Bối cảnh

Cron hiện tại dự kiến chọn ngẫu nhiên các `stock.picking` ở trạng thái có thể hủy
và gọi `action_cancel()`. Cách này phù hợp để kiểm tra kỹ thuật, nhưng chưa phản
ánh đầy đủ các tình huống vận hành thực tế: khách hủy đơn, tạo nhầm phiếu,
thiếu hàng, giao trùng, thay đổi kế hoạch giao hàng hoặc phát hiện sai thông tin
trước khi xuất kho.

Mục tiêu của backlog này là nghiên cứu và mở rộng logic simulator để việc hủy
phiếu có lý do, xác suất, thời điểm và điều kiện nghiệp vụ gần với thực tế hơn.

## 2. Mục tiêu

1. Xác định các tình huống thực tế dẫn đến việc hủy picking.
2. Mô hình hóa lý do hủy và điều kiện chọn phiếu.
3. Bổ sung logic vào simulator dựa trên hành vi và dữ liệu sẵn có của
   `stock.picking`, không làm thay đổi quy tắc hủy native của Odoo.
4. Bảo đảm không hủy nhầm picking đã `done`, đã `cancel`, đang xử lý ngoại lệ
   hoặc không còn phù hợp với kịch bản mô phỏng.
5. Có thể kiểm tra/audit vì sao một picking được chọn để hủy.

## 3. Các tình huống thực tế cần nghiên cứu

### 3.1. Khách hàng hủy đơn

- Áp dụng chủ yếu cho picking xuất kho.
- Picking chưa hoàn tất: `draft`, `confirmed`, `waiting`, `assigned`.
- Có thể ưu tiên phiếu liên kết với đơn bán hàng đang bị hủy hoặc đã hủy.
- Không nên hủy nếu đơn bán hàng vẫn đang ở trạng thái hợp lệ và chưa có dấu hiệu
  hủy.

### 3.2. Tạo nhầm phiếu kho

- Picking có `origin` hoặc nguồn tạo mang dấu hiệu simulator/test.
- Picking không có hoạt động xử lý thực tế hoặc chưa có move `done`.
- Có thể áp dụng tỷ lệ nhỏ để tránh làm cạn dữ liệu kiểm thử.

### 3.3. Hết hàng hoặc không đủ hàng

- Picking ở `confirmed`, `waiting` hoặc `partially_available`.
- Sản phẩm có tồn khả dụng thấp hơn nhu cầu.
- Nên cân nhắc hủy sau một khoảng thời gian chờ, không hủy ngay khi vừa tạo.

### 3.4. Không thể giao đúng lịch

- Picking có `date_deadline` đã quá hạn.
- Picking chưa được hoàn tất và chưa bắt đầu thao tác thực tế.
- Cần phân biệt picking trễ do hệ thống với picking đã được gia hạn hoặc đang có
  kế hoạch xử lý.

### 3.5. Phát hiện trùng hoặc sai tuyến giao hàng

- Có nhiều picking cùng `origin`, đối tác, địa chỉ giao hoặc đơn hàng.
- Chỉ giữ lại một phiếu hợp lệ và đưa các phiếu trùng vào kịch bản hủy.
- Cần tránh hủy các picking đã được gộp batch hoặc đã bắt đầu đóng gói.

### 3.6. Sai thông tin đối tác hoặc địa chỉ

- Thiếu `partner_id`, địa chỉ giao hàng hoặc picking type không phù hợp.
- Chỉ dùng cho dữ liệu simulator hoặc dữ liệu test được đánh dấu rõ ràng.

### 3.7. Hủy do can thiệp vận hành

- Phiếu đã được `assigned` nhưng nhân viên phát hiện sai hàng trước khi xác nhận.
- Có reservation thì phải xác minh `action_cancel()` nhả đúng số lượng.
- Không áp dụng cho phiếu đã có move `done`.

## 4. Dữ liệu nên dùng để quyết định hủy

Nghiên cứu khả năng sử dụng các trường sau trên `stock.picking` và model liên
quan:

- `state`
- `picking_type_id.code`
- `origin`
- `partner_id`
- `scheduled_date`
- `date_deadline`
- `user_id`
- `move_ids.state`
- `move_ids.quantity`
- `move_ids.product_uom_qty`
- `move_ids.forecast_availability`
- `move_ids.move_line_ids`
- `activity_ids`
- `batch_id` hoặc quan hệ batch tương ứng nếu module đang sử dụng
- Đơn bán hàng liên kết nếu database có module `sale_stock`

Không nên thêm field nghiệp vụ mới vào `stock.picking` chỉ để phục vụ simulator
nếu có thể dùng Activity, `origin`, context hoặc dữ liệu test hiện hữu.

## 5. Đề xuất thiết kế simulator

### 5.1. Tách quyết định khỏi hành động hủy

Nên có một bước quyết định riêng:

```text
Candidate picking
        |
        v
Đánh giá tình huống thực tế
        |
        v
Chọn lý do hủy + xác suất + thời điểm
        |
        v
Tạo Activity chờ xử lý
        |
        v
Kiểm tra lại điều kiện
        |
        v
action_cancel()
```

### 5.2. Lý do hủy

Có thể biểu diễn lý do trong nội dung Activity trước khi quyết định có cần một
field riêng hay không:

- `customer_cancelled`
- `duplicate_picking`
- `wrong_picking_created`
- `insufficient_stock`
- `delivery_deadline_missed`
- `wrong_partner_or_address`
- `operational_error`

Nếu cần báo cáo hoặc thống kê lâu dài, cân nhắc tạo selection field riêng trên
model simulator hoặc một model log thay vì đưa field simulator vào nghiệp vụ
core của `stock.picking`.

### 5.3. Xác suất và giới hạn

- Mỗi lần chạy chỉ chọn số lượng nhỏ, ví dụ 1–5 picking.
- Có tỷ lệ hủy theo từng tình huống.
- Ưu tiên picking được tạo bởi simulator, ví dụ `origin` bắt đầu bằng `SIM-`.
- Có thể thêm thời gian tối thiểu từ lúc tạo picking đến lúc được chọn.
- Không chọn lại picking đã có Activity cancel đang mở.

## 6. Điều kiện bắt buộc trước khi thực hiện

Trước khi gọi `action_cancel()` phải kiểm tra lại:

```python
picking.state in ["draft", "confirmed", "waiting", "assigned"]
```

Và cần loại trừ:

```python
picking.state in ["done", "cancel"]
```

Ngoài ra:

- Không có move quan trọng ở trạng thái `done`.
- Picking chưa bị người dùng xử lý theo một kịch bản khác.
- Nếu picking thuộc batch, cần xác định có được phép hủy riêng picking hay không.
- Nếu có reservation, phải xác minh sau khi hủy rằng reservation đã được nhả.
- Nếu có liên kết sale order, không tự động hủy sale order nếu task chỉ yêu cầu
  hủy picking.

## 7. Test cases dự kiến

### Case 1: Khách hủy đơn trước khi giữ hàng

- Picking: `confirmed`.
- Kết quả: tạo Activity với lý do `customer_cancelled`, sau đó picking thành
  `cancel`.

### Case 2: Hủy picking đang giữ hàng

- Picking: `assigned`.
- Có reserved quantity.
- Kết quả: picking và move thành `cancel`, reserved quantity được nhả.

### Case 3: Không hủy picking đã hoàn tất

- Picking: `done`.
- Kết quả: không tạo Activity cancel và không gọi `action_cancel()`.

### Case 4: Picking đã bị hủy trước khi cron xử lý

- Activity cancel còn mở nhưng picking đã thành `cancel`.
- Kết quả: không gọi lại `action_cancel()`, Activity được đóng an toàn.

### Case 5: Picking đổi trạng thái sang `done` trước khi xử lý Activity

- Activity đã tạo ở trạng thái `assigned`.
- Trước khi cron xử lý, picking chuyển thành `done`.
- Kết quả: bỏ qua, không làm phát sinh lỗi hủy move done.

### Case 6: Picking quá hạn deadline

- `date_deadline` đã qua, picking chưa `done` hoặc `cancel`.
- Kết quả: chỉ được chọn nếu thỏa quy tắc thời gian chờ và tỷ lệ mô phỏng.

### Case 7: Không tạo Activity trùng

- Picking đã có Activity cancel đang mở.
- Kết quả: cron tìm candidate không tạo thêm Activity.

### Case 8: Picking có move done một phần

- Một move đã `done`, move khác chưa hoàn tất.
- Kết quả: không tự động hủy; cần nghiên cứu riêng về backorder/return trước khi
  hỗ trợ tình huống này.

## 8. Tiêu chí nghiệm thu

- Logic mô phỏng có ít nhất 3 tình huống thực tế khác nhau.
- Mỗi Activity cancel ghi rõ lý do và picking được chọn.
- Có giới hạn số lượng và tỷ lệ hủy mỗi lần chạy.
- Không hủy được picking `done` bằng cron simulator.
- Không tạo Activity trùng.
- Picking `assigned` được nhả reservation sau khi hủy.
- Các cron khác như assign, validate và cancel không tạo ra lỗi nghiêm trọng khi
  cùng chạy trong thời gian gần nhau.
- Có test cho cả trường hợp thành công, bỏ qua và lỗi khi xử lý.

## 9. Phạm vi không làm trong task đầu tiên

- Không tự động hủy `sale.order` hoặc invoice.
- Không tự động tạo return cho picking đã `done`.
- Không thay đổi logic native của Odoo trong `stock.picking.action_cancel()`.
- Không hủy dữ liệu production nếu chưa có cờ cấu hình hoặc giới hạn chỉ chọn
  record simulator.

## 10. Tiến độ triển khai

- [x] 1. Bổ sung Activity Type và cron tạo Activity cancel (Đã implement qua cron `ir_cron_find_picking_cancel_candidates` và model `EmployeeSimulatorCancel`).
- [ ] 2. Bổ sung cron xử lý Activity với bước kiểm tra lại trạng thái (chuẩn bị gọi `action_cancel()`).
- [ ] 3. Ưu tiên picking có `origin` simulator để kiểm thử an toàn.
- [ ] 4. Thêm các rule `customer_cancelled`, `wrong_picking_created` và
   `insufficient_stock`.
- [ ] 5. Thêm test cho reservation, duplicate Activity và race trạng thái.
- [ ] 6. Sau khi ổn định mới mở rộng sang deadline, batch và sale order.
