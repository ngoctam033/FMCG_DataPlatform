# TASK-003: Module lưu log các lần chạy cron mô phỏng nghiệp vụ kho

## 1. Ngữ cảnh

Module `employee_simulator` đang dùng các Scheduled Action để mô phỏng hành vi của nhân viên kho ngoài đời thực. Các cron này cố ý chỉ xử lý một số lượng bản ghi giới hạn mỗi lần chạy; không yêu cầu quét hết dữ liệu hoặc tạo activity cho toàn bộ record thỏa điều kiện.

Hiện tại hệ thống chỉ có log kỹ thuật qua Python logger. Chưa có dữ liệu bền vững để xem lại cron đã chạy lúc nào, đã chọn record nào, vì sao bỏ qua, activity nào được tạo hoặc lỗi xảy ra ở đâu.

## 2. Mục tiêu

Tạo một module riêng, đề xuất tên kỹ thuật `employee_simulator_cron_log`, để lưu lại lịch sử từng lần chạy cron mô phỏng và chi tiết các record được cron xem xét.

Module log không thay đổi mục tiêu mô phỏng, không ép cron xử lý hết các record và không tự động tạo thêm activity ngoài logic hiện tại của từng cron.

## 3. Phạm vi

### 3.1. Log lần chạy

Đề xuất model: `employee.simulator.cron.run`

Thông tin tối thiểu:

- Tên cron hoặc mã cron.
- Model nghiệp vụ được xử lý.
- Thời điểm bắt đầu và kết thúc.
- Trạng thái: `running`, `done`, `failed`.
- Số record đã chọn để mô phỏng.
- Số record thành công, bỏ qua và lỗi.
- Nội dung exception nếu lần chạy thất bại.
- Người dùng hoặc user chạy cron.

### 3.2. Log chi tiết record

Đề xuất model: `employee.simulator.cron.run.log`

Thông tin tối thiểu:

- Liên kết đến lần chạy.
- Tên model và ID record nghiệp vụ.
- Có thể liên kết trực tiếp đến `stock.picking`, `stock.move.line` hoặc model tương ứng nếu cron xử lý kho.
- Hành động mô phỏng: `selected`, `processed`, `skipped`, `activity_created`, `failed`.
- Lý do bỏ qua hoặc lỗi.
- ID activity được tạo nếu có.
- Thời điểm xử lý.
- Snapshot ngắn các dữ liệu cần học nghiệp vụ: trạng thái phiếu, sản phẩm, tracking, lot/serial, user phụ trách.

Không nên lưu toàn bộ payload lớn hoặc dữ liệu nhạy cảm; chỉ lưu dữ liệu đủ để phân tích hành vi mô phỏng.

## 4. Nguyên tắc giữ nguyên logic mô phỏng

- Giữ nguyên giới hạn chọn record hiện tại, ví dụ `limit=80` và tối đa 30 record được xử lý trong cron thiếu Lot/Serial, nếu đó là chủ đích mô phỏng.
- Log cả record được chọn và record bị bỏ qua trong tập mẫu hiện tại.
- Không dùng log để mở rộng phạm vi truy vấn hoặc bắt cron xử lý các record ngoài mẫu đã chọn.
- Không coi activity đã hoàn tất là lỗi cần tạo lại, trừ khi nghiệp vụ mô phỏng của cron yêu cầu.
- Log phải phản ánh đúng hành động thực tế: không tạo activity thì không ghi là `activity_created`.
- Việc ghi log không được làm hỏng hoặc thay đổi kết quả nghiệp vụ chính của cron.

## 7. Gợi ý thứ tự triển khai

1. Viết test cho model run và model log.
2. Tạo module `employee_simulator_cron_log` và các model lưu trữ.
3. Tạo một service/helper dùng chung để mở và đóng run log.
4. Tích hợp thử trước với `cron_find_missing_lot_pickings`.
5. Kiểm tra giới hạn lấy mẫu vẫn giữ nguyên.
6. Mở rộng sang các cron mô phỏng khác.
7. Thêm tree/form/search view và phân quyền chỉ đọc cho người xem log.
