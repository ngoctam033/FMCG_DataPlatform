# Báo cáo review tính năng: Tự động gán Activity xử lý Backorder

## 1. Mô tả tính năng
Trong quá trình mô phỏng thao tác của nhân viên kho (Employee Simulator), khi thực hiện hành động xác nhận phiếu kho (`button_validate` trên model `stock.picking`), hệ thống có thể phát hiện tình trạng thiếu hụt hàng hóa (không đủ số lượng so với yêu cầu). Khi đó, Odoo sẽ trả về một action mở wizard `stock.backorder.confirmation`.

Tính năng mới này được thêm vào nhằm xử lý tình huống trên bằng cách:
- **Ghi nhận Log chi tiết**: Ghi log thông tin về phiếu kho đang được thao tác (ID, mã phiếu, user thực hiện) trước khi gọi hàm validate để dễ dàng theo dõi (traceability).
- **Tạo Activity tự động**: Nếu kết quả trả về của hàm validate là wizard `stock.backorder.confirmation`, hệ thống sẽ tự động lên lịch (schedule) một Activity có nội dung "Xác nhận tạo Backorder" cho user đang xử lý phiếu kho, đi kèm nội dung ghi chú rõ ràng về việc phát hiện thiếu hàng.

## 2. Chi tiết các thay đổi (Code Changes)
Các thay đổi tập trung trong file `odoo/custom_addons/employee_simulator/models/action_simulator.py`, tại phương thức xử lý vòng lặp các phiếu kho:

- **Thêm logging trạng thái**: 
  ```python
  _logger.info(
      '[VALIDATE] Đang thao tác stock.picking: id=%s, mã=%s, user_id=%s',
      simulated_picking.id,
      simulated_picking.name,
      selected_user.id,
  )
  ```
- **Xử lý kết quả trả về từ `button_validate()`**:
  ```python
  if isinstance(action_result, dict):
      if action_result.get('res_model') == 'stock.backorder.confirmation':
          simulated_picking.activity_schedule(
              'employee_simulator.mail_activity_backorder',
              summary='Xác nhận tạo Backorder',
              note='Hệ thống tự động phát hiện thiếu hàng khi Validate. Cần xử lý tạo Backorder.',
              user_id=selected_user.id
          )
          _logger.info(f"[VALIDATE] Đã gắn Activity Backorder cho phiếu {simulated_picking.name}")
  ```

## 3. Đánh giá và Đề xuất (Cố vấn)
- **Đánh giá**: Đoạn mã được viết rõ ràng, kiểm tra đúng điều kiện trả về của `button_validate` theo cơ chế chuẩn của Odoo. Việc sử dụng `activity_schedule` giúp giao việc một cách có hệ thống cho nhân viên trên giao diện Odoo thay vì phải theo dõi qua log, đây là một luồng (workflow) rất phù hợp. Đồng thời, việc bổ sung log giúp quá trình debug và monitor tiến trình giả lập được dễ dàng hơn.
- **Đề xuất / Lưu ý**: 
  - Đảm bảo rằng record `employee_simulator.mail_activity_backorder` đã được định nghĩa (`<record id="mail_activity_backorder" model="mail.activity.type">`) trong file XML data của module. Nếu chưa có, phương thức `activity_schedule` sẽ quăng ra lỗi (Error) khi tìm kiếm External ID này.
  - Về lâu dài, nếu nghiệp vụ giả lập yêu cầu tính tự động hóa cao hơn, bạn có thể cân nhắc việc viết mã giả lập luôn thao tác "click Xác nhận" (Confirm) trên Wizard `stock.backorder.confirmation` thay vì chỉ tạo ra Activity chờ xử lý thủ công.
