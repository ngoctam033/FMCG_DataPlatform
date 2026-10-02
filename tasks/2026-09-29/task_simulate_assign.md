# [Completed] Task: Implement `cron_simulate_picking_assign`

## Mục tiêu (Objective)
- Đã hoàn thành giả lập việc nhân viên kho bấm nút 'Kiểm tra khả dụng' để giữ hàng (Reserve).
- Hệ thống tự động gọi `action_assign()` thông qua cron job.

## Kịch bản kiểm thử (Test Scenarios - Đã pass)
1. **Setup (Chuẩn bị):** 
   - Có các Phiếu kho ở trạng thái `confirmed` (Chờ xử lý) hoặc `waiting`, có đủ tồn kho trong hệ thống.
2. **Action (Thực thi):** 
   - Chạy hàm `env['employee.simulator'].cron_simulate_picking_assign()`.
3. **Assert (Kết quả đạt được):**
   - Các phiếu kho tự động chuyển sang trạng thái `assigned` (Sẵn sàng).
   - Lịch sử phiếu kho (chatter) lưu vết hành động được thực hiện bởi một nhân viên kho ngẫu nhiên.

## Logic Đã Triển Khai (Advanced Implementation)
Hệ thống đã được thiết kế sử dụng thuật toán thời gian (pseudo-random) để tối ưu hóa và phân tán tải, mô phỏng tự nhiên nhất có thể:
- **Truy xuất dữ liệu:** Quét tập hợp phiếu kho hợp lệ `[('state', 'in', ['confirmed', 'waiting'])]`.
- **Phân bổ dao động:** Tính số lượng phiếu cần xử lý ngẫu nhiên từ 1 đến 3 phiếu mỗi chu kỳ. Công thức sử dụng phép chia lấy dư (modulo) kết hợp thời gian (`minute`, `hour`, `day`) và biến ngẫu nhiên `salt`.
- **Trích xuất User:** Dùng thuật toán thời gian tương tự để chọn ra 1 nhân viên ngẫu nhiên từ danh sách thay vì Admin.
- **Thực thi action:** Kế thừa quyền (`with_user`) và gọi `action_assign()`.
