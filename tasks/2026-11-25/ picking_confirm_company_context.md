Confirm Picking với đúng Company Context
Vấn đề
Khi hoàn thành Activity Confirm Draft Picking, Server Action gọi picking.action_confirm() trong ngữ cảnh công ty đang hoạt động (env.company).

Ở môi trường Multi-company, env.company có thể khác picking.company_id. Trong quá trình Confirm, Odoo có thể tự động phân bổ hàng và tạo Wave Transfer. Nếu Wave nhận công ty mặc định từ môi trường thay vì công ty của Picking, _sanity_check() sẽ từ chối liên kết vì khác công ty.

Ví dụ: Picking và Operation Type thuộc Company 2, nhưng env.company là Company 1, khiến Wave được tạo dưới Company 1.
Thay đổi
- Thêm ir.filters để nhận diện các Picking ở trạng thái draft có thông tin Company và Operation Type Company.
- Trong Server Action action_confirm_draft_picking, kiểm tra Picking có khớp bộ lọc và công ty của Picking có khác env.company hay không.
- Nếu khác, gọi picking.with_company(picking.company_id).action_confirm(); nếu không, giữ cách gọi picking.action_confirm().
- Giữ nguyên xử lý thiếu Stock Move, tạo lại Activity và kiểm tra trạng thái sau Confirm.
Ý nghĩa nghiệp vụ
with_company() chỉ thay đổi Company context của thao tác, không sửa company_id trên Picking và không đổi công ty đang chọn trên giao diện. Nhờ đó, quy trình Confirm và Auto Wave sử dụng ngữ cảnh phù hợp với Picking, trong khi _sanity_check() tiếp tục bảo vệ tính nhất quán Multi-company.
Kiểm thử
1. Chọn Company 1 trên giao diện, dùng Picking draft thuộc Company 2, có Stock Move và cấu hình Auto Wave: hoàn thành Activity Confirm, kiểm tra Wave được tạo với Company 2.
2. Dùng Picking draft thuộc công ty đang hoạt động: xác nhận vẫn hoạt động như trước.
3. Dùng Picking draft không có Stock Move: kiểm tra Activity bổ sung Stock Move vẫn được tạo và Activity Confirm được kích hoạt lại.
Lưu ý kỹ thuật: Đoạn Server Action trước đó sử dụng filter_record._get_eval_domain(). Cần xác minh phương thức này có tồn tại trên ir.filters trong source Odoo 19 đang chạy trước khi commit; tài liệu này mô tả hành vi dự kiến, không xác nhận đoạn code đã chạy thành công.