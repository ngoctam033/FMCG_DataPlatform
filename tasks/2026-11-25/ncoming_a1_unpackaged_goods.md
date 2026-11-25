Kịch bản A1 — Nhập kho hàng rời (Incoming Unpackaged Goods)
1. Mục đích
Kiểm tra hệ thống có ít nhất một dòng di chuyển hàng hóa (stock.move.line) thuộc phiếu nhập kho (incoming) mà không có kiện hàng nguồn hoặc kiện hàng đích.

Đây là tình huống nhập hàng rời, không quản lý hàng hóa theo package trong giao dịch này. Việc để trống hai field là hợp lệ về mặt nghiệp vụ.
2. Điều kiện nhận diện
Field	Giá trị
picking_id.picking_type_id.code	incoming
package_id	False
result_package_id	False


Domain được lưu trong ir.filters với XML ID:

fmcg_business_automation.ir_filter_incoming_a1_unpackaged
3. Ví dụ
Nhập 100 chai nước từ nhà cung cấp vào WH/Input, không gắn kiện hàng:
{
    'picking_id.picking_type_id.code': 'incoming',
    'product_id': 'SP001',
    'location_id': 'Partners/Vendors',
    'location_dest_id': 'WH/Input',
    'quantity': 100,
    'package_id': False,
    'result_package_id': False,
}
Đây là dữ liệu minh họa nghiệp vụ, không phải dictionary truyền trực tiếp vào create().
4. Cách kiểm tra
Server Action action_check_incoming_a1_unpackaged:
1. Đọc domain trực tiếp từ ir.filters A1 bằng _get_eval_domain().
2. Tìm stock.move.line thỏa mãn domain.
3. Nếu không tìm thấy record nào, raise UserError; nếu có, kết thúc bình thường.
Cron ir_cron_simulate_create_picking gọi Server Action này sau bước tạo các stock.picking demo.

Lưu ý: Cron hiện chỉ tạo stock.picking với picking_type_id, không trực tiếp tạo stock.move.line. Action kiểm tra toàn bộ dữ liệu hiện có theo domain, không giới hạn ở các picking vừa tạo. Vì vậy, kiểm tra thành công không chứng minh lần chạy cron hiện tại đã tạo được move line A1. Nếu action raise lỗi, transaction của cron có thể bị rollback.
5. Kết quả mong đợi
- Có ít nhất một record A1: kiểm tra thành công.
- Không có record A1: phát sinh UserError để thông báo không tìm thấy dữ liệu phù hợp.
Điều kiện A1 chỉ xác nhận cấu trúc dữ liệu package; không tự chứng minh hàng đã được nhập kho thành công hoặc đúng số lượng thực tế.