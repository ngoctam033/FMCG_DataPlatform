# Báo Cáo Cập Nhật Hàm Giả Lập: `simulate_confirm_picking`

**Ngày thực hiện:** 2026-09-28
**File cập nhật:** `odoo/custom_addons/employee_simulator/models/action_simulator.py`

## 1. Mô tả Vấn Đề (Bug/Issue)
Trong mô-đun `employee_simulator`, tiến trình tự động (Cron) `simulate_confirm_picking` được thiết kế để mô phỏng thao tác của nhân viên kho: **Xác nhận (Confirm)** các phiếu kho đang ở trạng thái Nháp (Draft).

Tuy nhiên, hàm `search` nguyên bản đang thiếu điều kiện lọc (Domain Filter):
```python
pickings = self.env['stock.picking'].search([], limit=20)
```

**Hậu quả của việc thiếu bộ lọc:**
- Cron truy vấn cả những phiếu kho đã **Hoàn thành (`done`)**, **Hủy (`cancel`)**, hoặc các trạng thái đang xử lý.
- Mặc dù Odoo không sinh ra lỗi (crash) nhờ cơ chế kiểm tra `draft` ở tầng thấp (của stock.move), nhưng thao tác này sai hoàn toàn so với mô phỏng nghiệp vụ thực tế (người dùng trên giao diện chỉ thấy và bấm được nút *Mark as Todo* khi phiếu có `state == 'draft'`).
- Tốn kém tài nguyên hệ thống do kích hoạt lại các lệnh không cần thiết (vd: `_trigger_scheduler()`) trên các phiếu đã xử lý.

## 2. Giải Pháp Áp Dụng (Solution)
Áp dụng Domain Filter trực tiếp vào câu truy vấn ORM để đảm bảo Cron chỉ tương tác với các phiếu kho đúng trạng thái.

**Code Diff (Staged):**
```diff
- pickings = self.env['stock.picking'].search([], limit=20)
+ pickings = self.env['stock.picking'].search([('state', '=', 'draft')], limit=20)
```

## 3. Kịch Bản Kiểm Thử Đã Định Nghĩa (Test Scenario)
Việc chỉnh sửa này được thực hiện dựa trên phương pháp TDD với kịch bản như sau:
*   **Mục tiêu:** Chỉ cho phép gọi thao tác `action_confirm` đối với phiếu kho hợp lệ (Nháp).
*   **Given:** Hệ thống lưu trữ 30 phiếu kho (5 `draft`, 15 `done`, 10 `cancel`).
*   **When:** Cron `simulate_confirm_picking` được kích hoạt bởi hệ thống.
*   **Then:** Hàm `search` chỉ trả về đúng tối đa 20 phiếu trong tập 5 phiếu `draft`. Các phiếu `done` hay `cancel` bị loại bỏ ở tầng truy vấn cơ sở dữ liệu, không được duyệt qua vòng lặp.

## 4. Kết Quả Kiểm Tra Git (Git Review)
- Trạng thái thay đổi trên hàm `simulate_confirm_picking` đã được kiểm tra (Verified) và đưa vào vùng chờ commit (Staging Area). 
- Các logic cập nhật chính xác và tối ưu, tuân thủ đúng luồng thiết kế UI/Nghiệp vụ của Odoo gốc.
