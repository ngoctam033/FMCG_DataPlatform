# Báo Cáo Thay Đổi Hàm Giả Lập Dữ Liệu `simulate_create_picking`

**Ngày thực hiện:** 28/09/2026
**File thay đổi:** `odoo/custom_addons/employee_simulator/models/action_simulator.py`
**Mục tiêu:** Nâng cấp thuật toán sinh dữ liệu giả lập tự động bằng Cron.

## 1. Tóm Tắt Thay Đổi
Hàm `simulate_create_picking` đã được tái cấu trúc (refactor) để thay đổi cách sinh dữ liệu ngẫu nhiên khi giả lập phiếu kho. Thay vì phụ thuộc vào `now.minute` và `now.second` gây ra hiện tượng rập khuôn dữ liệu, hàm mới sử dụng **Thuật toán Băm Thời Gian (Time-based Deterministic Hash)** kết hợp với các số nguyên tố.

## 2. Lý Do Thay Đổi
- **Vấn đề cũ:** Phiên bản trước đây khiến cho các bản ghi sinh ra trong cùng một phút (hoặc giây) bị trùng lặp rất nhiều về User, Partner, Product và số lượng. Điều này dẫn đến tập dữ liệu giả lập bị sai lệch (bias), phân phối không tự nhiên, làm giảm chất lượng khi test hiệu năng hoặc lấy mẫu dữ liệu.
- **Yêu cầu mới:** Cần một thuật toán sinh dữ liệu đa dạng hơn, bao quát toàn bộ Product, Partner, User nhưng vẫn đảm bảo tính ổn định (Deterministic), hạn chế sinh trùng liên tiếp mà không phụ thuộc vào hàm `random` thuần túy.

## 3. Chi Tiết Kỹ Thuật (Technical Details)
- **Loại bỏ phụ thuộc `second`:** Giây (second) thường cố định tại thời điểm kích hoạt Cron, do đó đã được loại bỏ khỏi biến số xoay vòng.
- **Bổ sung `hour`, `day`, `month`:** Khai báo thêm các biến cấu phần thời gian để tính toán xoay vòng dữ liệu, giúp chu kỳ lặp lại kéo dài ra rất nhiều.
- **Áp dụng phép nhân số nguyên tố:**
  - `user_index = (minute * 3 + hour * 7 + day * 11) % len(users)`
  - `picking_type_index = (minute * 5 + day * 13) % len(picking_types)`
  - Sự kết hợp với các số nguyên tố như 3, 5, 7, 11, 13... giúp các trường dữ liệu bị "đánh lệch pha", tránh tình trạng đồng bộ chu kỳ (Cộng hưởng).

## 4. Đánh Giá Hiệu Quả
- **Độ đa dạng (Diversity):** Cực kỳ cao. Dữ liệu bao quát tốt toàn bộ Master Data, thời gian deadline dao động phong phú.
- **Tính lặp lại (Duplicates):** Hầu như không xảy ra hiện tượng xuất hiện hai tổ hợp (User + Picking Type + Product + Qty) giống hệt nhau liên tiếp.
- **Mức độ an toàn:** Việc người dùng quyết định bỏ qua kiểm tra rỗng (`if not users`) đồng nghĩa với việc chấp nhận cho hàm văng lỗi (Crash) nếu thiếu Master Data, phù hợp với yêu cầu ép buộc hệ thống phải có data mẫu trước khi giả lập.

## 5. Trạng Thái Code (Git Status)
- Toàn bộ thay đổi đối với thuật toán băm (Hash logic) của hàm `simulate_create_picking` đã được **Staged** (`git add`) thành công trên vùng tạm (Staging Area).
- Các định nghĩa hàm mới (ví dụ: `simulate_confirm_picking`, `cron_simulate_picking_unreserve`...) hiện đang nằm trong vùng **Unstaged**, chờ xử lý trong các bước tiếp theo.
