Sửa domain kiểm tra thiếu Lot/Serial
Vấn đề
Domain cũ đánh dấu một stock.picking là thiếu Lot/Serial khi use_existing_lots = True và có stock.move.line với quantity > 0, lot_id = False, dù lot_name đã được khai báo.

Điều này gây lỗi dương tính giả khi picking type cho phép cả sử dụng Lot có sẵn lẫn tạo Lot mới (use_existing_lots = True, use_create_lots = True).

Ví dụ: move line có lot_id = False, lot_name = 'SIM-LOT-1407-2323'. Domain cũ vẫn báo thiếu Lot dù tên Lot mới đã được nhập.
Thay đổi
- Chỉ cho phép dùng Lot có sẵn (use_existing_lots = True, use_create_lots = False): coi là thiếu nếu lot_id = False.
- Cho phép tạo Lot mới (use_create_lots = True, bất kể use_existing_lots): coi là thiếu nếu cả lot_id = False và lot_name = False.
- Giữ điều kiện chỉ xét picking chưa done/`cancel`, sản phẩm có tracking lot/`serial`, và move line có quantity > 0.
Vì sao cần sửa?
lot_id tham chiếu Lot/Serial đã tồn tại; lot_name cho phép khai báo tên Lot/Serial mới trong quy trình được phép tạo Lot. Khi cả hai phương thức được bật, không thể kết luận thiếu Lot chỉ vì lot_id trống.
Kết quả mong đợi
Picking có use_existing_lots = True, use_create_lots = True, lot_id = False nhưng lot_name đã được điền sẽ không còn bị nhận diện nhầm là thiếu Lot/Serial.

Lưu ý: Domain này kiểm tra thiếu thông tin Lot/Serial, không thay thế bước xác thực Lot/Serial hợp lệ khi validate picking. Trường hợp cả hai tùy chọn đều tắt cần được kiểm tra cấu hình riêng nếu nghiệp vụ yêu cầu.