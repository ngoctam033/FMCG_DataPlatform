# Báo cáo Cập nhật: Sửa lỗi Company Crossover & Tối ưu hóa Simulator

**Ngày:** 2026-09-28
**Module:** `employee_simulator`
**File bị ảnh hưởng (Vùng Staged):** 
- `odoo/custom_addons/employee_simulator/models/action_simulator.py`

## 1. Mục đích
Cập nhật này tập trung giải quyết triệt để lỗi xung đột công ty (Company Inconsistencies) trong môi trường Multi-Company khi giả lập thao tác của nhân viên kho. Đồng thời, tái cấu trúc (refactor) lại logic sinh dữ liệu giả lập nhằm tăng hiệu suất và hỗ trợ truy vết lỗi (traceability) dễ dàng hơn.

## 2. Chi tiết và Lý do Thay đổi

### 2.1. Khắc phục lỗi "Company Crossover" (Lỗi Khác Công ty)
- **Vấn đề cũ:** Khi tạo phiếu kho (`stock.picking`), hệ thống query `stock.picking.type` trên toàn hệ thống mà không lọc theo công ty của User thực thi. Dẫn đến việc Phiếu kho thuộc Công ty A nhưng Loại hoạt động (Picking Type) lại thuộc Công ty B. Odoo chặn lại bằng lỗi `UserError`.
- **Giải pháp:** Bổ sung `company_domain` để bắt buộc Loại phiếu kho được chọn phải cùng thuộc về công ty của User hiện tại (`selected_user.company_id`), hoặc là loại dùng chung (`company_id = False`).
- **Lý do:** Tuân thủ chặt chẽ ràng buộc toàn vẹn dữ liệu trong môi trường đa công ty của Odoo.

### 2.2. Đổi từ Random ngẫu nhiên sang thuật toán Xác định (Deterministic)
- **Vấn đề cũ:** Việc chọn User, Product, Số lượng,... sử dụng thư viện `random` (`random.choice`, `random.randint`). Khi cron job chạy thất bại, rất khó để tái hiện lại chính xác dữ liệu nào đã gây ra lỗi.
- **Giải pháp:** Thay thế hoàn toàn `random` bằng toán tử chia lấy dư (`%`) kết hợp với `minute` và `second` của thời gian chạy cron. 
- **Lý do:** Đảm bảo tính lặp lại (repeatability) trong giả lập. Dữ liệu tuy vẫn phong phú nhưng hoàn toàn có thể tính toán hoặc dự đoán được nếu biết thời gian cron job kích hoạt, giúp việc debug dễ dàng hơn gấp nhiều lần.

### 2.3. Tối ưu hóa hiệu năng bằng Odoo Command
- **Vấn đề cũ:** Tạo Phiếu kho (Picking) trước, sau đó dùng vòng lặp gọi hàm `.create()` nhiều lần để tạo từng dòng Chi tiết (Stock Move) và tự gán ngược `picking_id`.
- **Giải pháp:** Khởi tạo danh sách `move_commands` bằng cú pháp `Command.create()`. Sau đó truyền toàn bộ vào trường `move_ids` trong duy nhất một lệnh `create()` của Phiếu kho.
- **Lý do:** 
  1. Tăng tốc độ thực thi (Bulk insert thay vì Insert từng dòng).
  2. Để Odoo ORM tự động kế thừa và tính toán các field liên quan từ Picking xuống Move (ví dụ: `location_id`, `company_id`), giảm thiểu code thủ công và rủi ro sai sót.

### 2.4. Cải tiến định dạng mã Origin
- **Vấn đề cũ:** `origin` mang hậu tố random 3 số, rất dễ bị trùng lặp.
- **Giải pháp:** Sử dụng chuỗi thời gian chính xác tới giây: `SIM-MANUAL-YYYYMMDDHHMMSS`.
- **Lý do:** Đảm bảo tính Unique cho mã đối chiếu và dễ dàng biết ngay thời điểm phiếu được sinh ra chỉ bằng cách nhìn vào tên origin.
