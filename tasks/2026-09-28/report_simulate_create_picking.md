# Báo cáo thay đổi: Nâng cấp hàm tạo dữ liệu giả lập (simulate_create_picking)
**Ngày thực hiện:** 28/09/2026
**Module:** `employee_simulator`

## 1. Yêu cầu và Bối cảnh
- **Bối cảnh cũ:** Hàm `simulate_create_picking` sử dụng thuật toán băm dựa trên thời gian (Time-based Deterministic) với độ phân giải tới phút (`minute`, `hour`, `day`, `month`).
- **Vấn đề:** Nếu hàm được gọi liên tục qua một vòng lặp (hoặc được Cron gọi yêu cầu tạo nhiều bản ghi cùng lúc), do các biến thời gian không thay đổi, dữ liệu sinh ra bị trùng lặp (trùng User, Product, Qty) và trùng luôn mã `origin`.
- **Yêu cầu mới:** Nâng cấp cấu trúc hàm để có thể tạo hàng loạt (ví dụ: 100 bản ghi) không trùng lặp trong một lần chạy duy nhất (Single Run).

## 2. Chi tiết các thay đổi
### 2.1. Cập nhật hàm Python (`action_simulator.py`)
- **Bổ sung tham số:** Thêm `record_count=1` vào tham số của hàm `simulate_create_picking` để hỗ trợ tương thích ngược (nếu không truyền gì thì tạo 1, có truyền thì tạo nhiều).
- **Tối ưu hóa (Performance):** Di dời các lệnh truy vấn ORM (`search` Users, Products, Partners) ra khỏi vòng lặp `for` để giảm tải cho Database.
- **Biến xáo trộn (Salt):** Bổ sung vòng lặp `for i in range(record_count):` và tạo biến `salt = random.randint(1, 10000) + i`. Biến `salt` này được cộng vào các phép tính chia lấy dư (`%`) để chọn ngẫu nhiên Partner, User, Product cho từng bản ghi.
- **Đảm bảo Unique Origin:** Nối biến `salt` vào mã phiếu chuyển kho: `f'SIM-MANUAL-{now.strftime("%Y%m%d%H%M%S")}-{salt}'`.
- **Loại bỏ Return:** Đã loại bỏ/điều chỉnh lệnh `return` ở cuối hàm do không cần thiết (Cron job không yêu cầu trả về giá trị ID).

### 2.2. Cập nhật cấu hình Cron (`cron_data.xml`)
- Sửa đổi XML Record `ir_cron_simulate_stock_picking`.
- Cập nhật trường `code`:
  - **Từ:** `env['employee.simulator'].simulate_create_picking()`
  - **Thành:** `env['employee.simulator'].simulate_create_picking(record_count=100)`

## 3. Kịch bản kiểm thử (Test Scenarios - TDD)
- **Test Case 1 (Tương thích ngược):** 
  - Kích hoạt hàm từ nơi khác mà không truyền tham số.
  - Kỳ vọng: Chỉ sinh 1 record thành công, hệ thống không báo lỗi tham số.
- **Test Case 2 (Chạy hàng loạt):** 
  - Vào Odoo > Settings > Technical > Scheduled Actions.
  - Chạy thủ công Cron `Simulator: Auto Create Stock Picking`.
  - Kỳ vọng: Quá trình load diễn ra nhanh chóng. Phân hệ Inventory sinh ra chính xác 100 phiếu chuyển kho với dữ liệu được xáo trộn đa dạng và mã Origin khác biệt hoàn toàn.
