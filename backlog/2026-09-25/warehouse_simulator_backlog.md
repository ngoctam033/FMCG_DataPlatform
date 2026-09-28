# Backlog: Giả lập thao tác Odoo (Phân hệ Kho - Inventory)

## Mục tiêu
Xây dựng các kịch bản giả lập hành vi của nhân viên kho để phục vụ kiểm thử tải, tạo dữ liệu mẫu và kiểm chứng luồng quy trình (workflow) trong Odoo.

## 1. Nhóm Nghiệp vụ Nhập Kho (Inbound / Receipt)
- [ ] **SIM-IN101**: Tạo phiếu Nhập kho thủ công (không thông qua đơn mua hàng PO).
- [ ] **SIM-IN102**: Tự động Xác nhận (Validate) phiếu Nhập kho đang ở trạng thái Ready (tự điền Done = Demand).
- [ ] **SIM-IN103**: Nhập kho kèm theo khai báo tự động Số Lô / Số Serial / Hạn sử dụng (Lot / Expiration Date).
- [ ] **SIM-IN104**: Giả lập nhận hàng hoàn trả từ khách hàng (Customer Return).
- [ ] **SIM-IN105**: Nhập kho thiếu hàng (cố tình nhập số lượng Done < Demand) và tự động xử lý popup tạo Backorder.

## 2. Nhóm Nghiệp vụ Xuất Kho (Outbound / Delivery)
- [ ] **SIM-OUT101**: Tạo phiếu Xuất kho (Delivery) thủ công.
- [ ] **SIM-OUT102**: Tự động Xác nhận (Validate) phiếu Xuất kho sinh ra từ Sale Order (Kiểm tra hàng khả dụng -> điền Done -> Validate).
- [ ] **SIM-OUT103**: Đóng gói hàng hóa xuất (Put in Pack). Nhóm các sản phẩm thành từng kiện hàng (Package) có mã vạch riêng.

## 3. Nhóm Nghiệp vụ Nội bộ & Quản lý tồn (Internal & Inventory)
- [ ] **SIM-INT101**: Chuyển kho nội bộ (Internal Transfer) từ kho chính sang kho phụ/cửa hàng.
- [ ] **SIM-INT102**: Thực hiện Kiểm kê kho (Cycle Counting/Inventory Adjustment) - Quét ngẫu nhiên và cố tình tạo chênh lệch để hệ thống sinh bút toán hao hụt.
- [ ] **SIM-INT103**: Thiết lập hoặc cập nhật Quy tắc tái cung ứng (Reordering Rule - Min/Max) cho các sản phẩm ngẫu nhiên.

## 4. Chuỗi quy trình liên hoàn (Cross-Department Workflows)
- [ ] **SIM-WF101**: Chuỗi Mua hàng -> Nhập kho -> Kế toán: Bot mua hàng Confirm PO -> Bot thủ kho Validate Receipt -> Bot kế toán tạo Bill.
- [ ] **SIM-WF102**: Chuỗi Bán hàng -> Xuất kho: Lắng nghe các phiếu giao hàng (Delivery) sinh ra từ Sale Order, chờ ngẫu nhiên 5-15 phút rồi tiến hành xuất.
- [ ] **SIM-WF103**: Chuỗi Xuất kho nhiều bước (Pick -> Pack -> Ship): Các bot phối hợp chuyển vai Picker, Packer và Shipper để xử lý tuần tự luồng giao hàng phức tạp.
