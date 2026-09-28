# FMCG ERP Odoo - Master Data Setup Backlog

Danh sách các công việc (Task List) cần thực hiện để khởi tạo dữ liệu chủ (Master Data) cho hệ thống ERP Odoo giả lập mô hình công ty FMCG. 
*Lưu ý: Thực hiện lần lượt từ trên xuống dưới để đảm bảo tính liên kết dữ liệu trong Odoo không bị lỗi.*

## 1. Thiết lập chung (General Settings & Accounting)
- [ ] **Kích hoạt các tính năng cần thiết trong Settings:** Đa tiền tệ, Đa đơn vị tính, Lô/Hạn sử dụng, Bảng giá nâng cao, Chương trình khuyến mãi.
- [ ] **Các loại thuế (Taxes):** Thiết lập Thuế GTGT đầu ra (VAT 8%, 10%) và Thuế GTGT đầu vào.
- [ ] **Điều khoản thanh toán (Payment Terms):** Tạo các điều khoản đặc thù FMCG (Thanh toán ngay, Công nợ 15 ngày, Công nợ 30 ngày chốt cuối tháng).

## 2. Nhóm Dữ liệu Sản phẩm & Hàng hóa (Product Master Data)
- [ ] **Nhóm hàng hóa (Product Categories):** Phân chia danh mục theo ngành hàng (VD: Đồ uống, Thực phẩm khô, Hóa mỹ phẩm...).
- [ ] **Đơn vị tính (Unit of Measure - UoM):** Thiết lập bộ đơn vị tính đa cấp (Ví dụ: Chai -> Lốc (6) -> Thùng (24) -> Pallet).
- [ ] **Tạo Sản phẩm - Nguyên vật liệu (Raw Materials) & Bao bì (Packaging):** Không đánh dấu "Có thể bán" (Can be sold).
- [ ] **Tạo Sản phẩm - Thành phẩm (Finished Goods):** Cấu hình bắt buộc theo dõi theo Lô / Hạn sử dụng (Lot/Serial Number & Expiration Dates).
- [ ] **Định mức nguyên vật liệu (BoM - Tùy chọn):** Tạo công thức đóng gói hoặc sản xuất (VD: 1 Thùng = 24 Chai + 1 Thùng Carton).

## 3. Nhóm Đối tác (Contacts / Partners)
- [ ] **Cấu hình Thẻ phân loại (Contact Tags):** Tạo các tag để phân loại Kênh truyền thống (GT), Kênh hiện đại (MT), Horeca, Nhà phân phối.
- [ ] **Khu vực / Tuyến bán hàng:** Cấu hình các khu vực địa lý để gán cho khách hàng.
- [ ] **Khách hàng (Customers):** Tạo data khách hàng mẫu, gán Tag và Khu vực tương ứng.
- [ ] **Nhà cung cấp (Vendors):** Tạo data các nhà cung cấp nguyên vật liệu, dịch vụ vận tải.

## 4. Nhóm Bán hàng & Chính sách giá (Sales & Pricing)
- [ ] **Bảng giá (Pricelists):** Tạo Bảng giá Bán lẻ, Bảng giá Đại lý/Nhà phân phối (có chiết khấu), Bảng giá Siêu thị.
- [ ] **Chương trình khuyến mãi (Promotions/Coupons):** Thiết lập các kịch bản khuyến mãi (VD: Mua 10 tặng 1, Mua trên 50 thùng giảm 5%).
- [ ] **Đội ngũ bán hàng (Sales Teams):** Tạo và phân bổ nhân sự phụ trách theo khu vực (Bắc, Trung, Nam) hoặc theo ngành hàng.

## 5. Nhóm Kho bãi & Chuỗi cung ứng (Inventory)
- [ ] **Cấu trúc Kho bãi (Warehouses):** Tạo Kho tổng (Central Distribution Center) và Kho chi nhánh (Regional).
- [ ] **Vị trí / Địa điểm kho (Locations):** Chia nhỏ kho thành các khu vực (Khu nhận hàng, Khu lưu trữ, Khu hàng hỏng/hết date).
- [ ] **Quy tắc Tái cung ứng (Reordering Rules / Min-Max):** Thiết lập tồn kho tối thiểu/tối đa để hệ thống tự động gợi ý mua sắm hoặc sản xuất.

## 6. Đưa hệ thống vào hoạt động (Go-live data)
- [ ] **Nhập tồn kho đầu kỳ (Inventory Adjustments):** Cập nhật số lượng đầu kỳ của các sản phẩm vào hệ thống để bắt đầu vận hành các luồng nghiệp vụ.
