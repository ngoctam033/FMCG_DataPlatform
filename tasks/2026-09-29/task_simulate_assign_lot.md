# Chức năng: Giả lập khai báo Lot/Serial tự động (MVP)

## 1. Ngữ cảnh (Context)
Khi giả lập thao tác Validate (Xác nhận) phiếu kho, hệ thống Odoo chặn lại và văng lỗi (UserError) nếu phiếu chứa sản phẩm có theo dõi Lot/Serial nhưng chưa được khai báo. Để luồng mô phỏng chạy trơn tru, cần một cron job chạy trước bước Validate để "điền hộ" các thông tin Lot/Serial còn thiếu.

## 2. Mục tiêu (Objectives)
Giả lập thao tác thủ kho nhập mã Lot hoặc bấm nút "Assign Serial Numbers" trên phiếu kho:
1. Lọc ra các phiếu kho đang bị kẹt vì thiếu Lot/Serial (Nhận diện thông qua `mail.activity` nhắc việc đã sinh ra trước đó).
2. Tự động sinh tên Lot/Serial bằng cơ chế dễ đọc (Thời gian thực + Salt + Random).
3. Đóng (Mark as Done) activity sau khi khai báo thành công để tránh lặp lại.

## 3. Phạm vi triển khai (Scope - MVP)
Hiện tại, chức năng này (được code trong hàm `cron_process_missing_lot_activities`) được giới hạn ở mức cơ bản để chạy thử (MVP):
- **Chỉ áp dụng** cho phiếu luồng Nhập (`incoming`, `mrp_operation`).
- **Chỉ xử lý** khai báo Serial cho các dòng sản phẩm có số lượng `qty <= 1`.
- Các case nằm ngoài phạm vi này sẽ bị bỏ qua (Giữ nguyên activity) và đã được ghi nhận thành các Backlog riêng biệt:
  - Tách dòng cho Serial có số lượng > 1 (`simulator_split_serial_lines.md`).
  - Lấy Lot từ tồn kho có sẵn cho luồng Xuất (`simulator_auto_lot_outgoing.md`).

## 4. Kịch bản kiểm thử (Test Cases)
**Kịch bản 1: Phiếu nhập kho cần mã Lot**
- **Pre-condition:** Phiếu Nhập kho chứa sản phẩm tracking = `lot`, đang có activity nhắc việc.
- **Action:** Đợi Cron chạy.
- **Expected Result:** Dòng chi tiết (move line) tự động có `lot_name` (định dạng `SIM-LOT-...`), activity tự động báo Done.

**Kịch bản 2: Phiếu nhập kho cần Serial (Số lượng = 1)**
- **Pre-condition:** Phiếu Nhập kho chứa sản phẩm tracking = `serial`, số lượng yêu cầu = 1.
- **Action:** Đợi Cron chạy.
- **Expected Result:** Dòng chi tiết tự động có `lot_name` (định dạng `SIM-SN-...`), activity tự động báo Done.
