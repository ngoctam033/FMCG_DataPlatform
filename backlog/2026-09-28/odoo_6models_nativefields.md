# 🔍 Fields Có Sẵn Trong 6 Odoo Models — Dùng Ngay Cho FMCG

> **Nguyên tắc**: Trước khi tạo field vật lý mới, khai thác tối đa những gì Odoo đã có.  
> **Kết luận nhanh**: 6 models này đã cover ~70% nhu cầu FMCG nếu dùng đúng cách.

---

## 1. `res.partner` — Đối tác / Khách hàng / Nhà cung cấp

| Field / Tính năng có sẵn | Kiểu | Dùng cho FMCG như thế nào |
|---|---|---|
| `category_id` (`res.partner.category`) | Many2many (Tags) | ✅ Phân loại kênh: tạo tag `GT`, `MT`, `HoReCa`, `NPP`, `Region-North/South/Central` |
| `customer_rank` | Integer | ✅ Tự động tăng mỗi lần xác nhận SO → dùng để xếp hạng khách hàng hoạt động |
| `supplier_rank` | Integer | ✅ Tương tự cho NCC |
| `credit_limit` | Float (company_dependent) | ✅ Hạn mức công nợ cho từng nhà phân phối/đại lý |
| `property_payment_term_id` | Many2one (company_dependent) | ✅ Điều khoản thanh toán riêng: N30, N45, N30-EOM, COD |
| `property_supplier_payment_term_id` | Many2one (company_dependent) | ✅ Điều khoản thanh toán với NCC |
| `property_product_pricelist` | Many2one (company_dependent) | ✅ Gán Bảng giá mặc định cho từng khách hàng (Pricelist MT, GT, NPP) |
| `ref` | Char | ✅ Mã nội bộ đối tác (mã NPP, mã khách hàng GT) |
| `property_stock_customer` / `property_stock_supplier` | Many2one (Location) | ✅ Địa chỉ giao hàng / nhận hàng mặc định map vào Location cụ thể |
| `picking_warn` + `picking_warn_msg` | Selection + Text | ✅ Cảnh báo khi tạo phiếu kho cho đối tác (VD: "Chỉ giao hàng sáng thứ 2, 4, 6") |
| `sale_warn_msg` | Text | ✅ Ghi chú cảnh báo khi mở Sale Order cho KH này |
| `comment` (Notes) | Html | ✅ Ghi chú nội bộ: đặc điểm kênh, lịch giao hàng, người liên hệ kho |
| `barcode` | Char | ✅ Mã vạch đối tác → dùng cho mobile barcode scan tại điểm giao hàng |
| `partner_latitude` / `partner_longitude` | Float | ✅ Toạ độ địa lý → tuyến giao hàng, optimize route |
| `street`, `city`, `state_id`, `country_id` | Char / Many2one | ✅ Phân vùng địa lý theo tỉnh/thành (thay thế Territory field) |

> [!TIP]  
> **Kỹ thuật thay thế Territory**: Thay vì tạo `fmcg.sales.territory`, dùng **`state_id` (Tỉnh/Thành)** + **Tags kênh** trên `res.partner`. Filter báo cáo theo `state_id.name` group by là đủ cho 80% use case.

---

## 2. `product.template` — Sản phẩm

| Field / Tính năng có sẵn | Kiểu | Dùng cho FMCG như thế nào |
|---|---|---|
| `categ_id` | Many2one (product.category) | ✅ Phân cấp Brand → Line → SKU bằng Category hierarchy (tối đa không giới hạn cấp) |
| `product_tag_ids` | Many2many (product.tag) | ✅ Tag bổ sung: `Seasonal`, `New-Launch`, `Phaseout`, `Promo-Active` |
| `product_properties` | Properties (dynamic) | ✅ **Killer feature**: Thêm field động tùy ý theo Category *mà không cần migration DB* |
| `description_sale` | Text | ✅ Mô tả trên đơn bán: tên thương mại, quy cách |
| `description_purchase` | Text | ✅ Mô tả trên PO: spec kỹ thuật, tiêu chuẩn chất lượng |
| `description_picking` / `description_pickingout` / `description_pickingin` | Text | ✅ Hướng dẫn thao tác kho khi nhập / xuất / nội bộ |
| `sale_ok` / `purchase_ok` | Boolean | ✅ Phân biệt NVL (chỉ mua) vs Thành phẩm (bán được) vs Bao bì (mua, không bán) |
| `tracking` | Selection (none/lot/serial) | ✅ Theo dõi Lô / Serial theo từng loại SP |
| `sale_delay` (Customer Lead Time) | Integer | ✅ Thời gian chuẩn bị hàng xuất kho → ảnh hưởng Scheduled Date trên Delivery |
| `route_ids` | Many2many (stock.route) | ✅ Gán route Buy/MTO/Resupply trực tiếp trên SP |
| `responsible_id` | Many2one (res.users) | ✅ Người phụ trách quản lý sản phẩm (Product Manager theo ngành hàng) |
| `volume` / `weight` | Float | ✅ Thể tích / Khối lượng → tính capacity kho, chi phí vận chuyển |
| `uom_ids` (Packagings) | Many2many (uom.uom) | ✅ Các quy cách đóng gói bổ sung (Lốc, Thùng, Pallet) |
| `seller_ids` → `product.supplierinfo` | One2many | ✅ Nhiều NCC, nhiều mức giá, nhiều lead time cho 1 SP |
| `use_expiration_date` | Boolean (`product_expiry` addon) | ✅ Bật/tắt kiểm soát HSD per-product |
| `expiration_time` | Integer (days) | ✅ Tổng hạn sử dụng (ngày) → tự động tính `expiration_date` khi nhập lô |
| `use_time` | Integer (days) | ✅ Hạn "Best Before" (ngày trước expiry) → cảnh báo sắp hết hạn |
| `removal_time` | Integer (days) | ✅ Hạn cần loại bỏ khỏi kho (ngày trước expiry) |
| `lot_properties_definition` | PropertiesDefinition | ✅ Thêm field động vào từng Lô (VD: Certificate of Analysis, NSX, Nhà máy sản xuất) |

> [!IMPORTANT]  
> **`product_properties` (Properties field)** là tính năng cực mạnh của Odoo 17+: bạn định nghĩa schema trên `product.category`, các field đó tự động xuất hiện trên mọi sản phẩm thuộc category đó — **không cần viết code, không cần migration**. Ví dụ: Category "Đồ uống" thêm property `Nồng độ cồn (%)`, `Loại bao bì`, `Chứng nhận Halal`.

---

## 3. `stock.warehouse` — Kho

| Field / Tính năng có sẵn | Kiểu | Dùng cho FMCG như thế nào |
|---|---|---|
| `reception_steps` | Selection (1/2/3 steps) | ✅ Kho CDC: `3_steps` (Input→QC→Store); Kho RDC: `2_steps` (Input→Store) |
| `delivery_steps` | Selection (1/2/3 steps) | ✅ Kho CDC: `pick_pack_ship`; Kho nhỏ: `ship_only` |
| `resupply_wh_ids` | Many2many (stock.warehouse) | ✅ **Chuỗi CDC→RDC**: Kho vùng lấy hàng từ CDC tự động sinh Internal Transfer |
| `code` | Char(5) | ✅ Mã kho ngắn: `CDC`, `HNI`, `HCM`, `DAD` |
| `partner_id` | Many2one (res.partner) | ✅ Địa chỉ kho → in trên phiếu giao hàng |
| `lot_stock_id` | Many2one (stock.location) | ✅ Location mặc định tồn kho chính |
| `route_ids` | Many2many (stock.route) | ✅ Các route được kích hoạt cho kho này |

> [!TIP]  
> Chỉ cần cấu hình đúng `reception_steps`, `delivery_steps` và `resupply_wh_ids` là có thể mô phỏng đầy đủ chuỗi **CDC → 3 Kho vùng** với auto-replenishment mà không cần thêm field nào.

---

## 4. `stock.warehouse.orderpoint` — Quy tắc tái cung ứng

| Field / Tính năng có sẵn | Kiểu | Dùng cho FMCG như thế nào |
|---|---|---|
| `product_min_qty` | Float | ✅ Tồn kho tối thiểu (Safety Stock) |
| `product_max_qty` | Float | ✅ Tồn kho tối đa (Max Stock) |
| `qty_multiple` (trong replenishment_uom) | Float | ✅ Bội số đặt hàng (VD: chỉ đặt theo thùng, không lẻ chai) |
| `replenishment_uom_id` | Many2one (uom.uom) | ✅ Đặt hàng theo UoM cụ thể (Thùng thay vì Chai) |
| `route_id` | Many2one (stock.route) | ✅ Chọn route Buy hoặc Manufacture hoặc Resupply từ kho khác |
| `trigger` | Selection (automatic/manual) | ✅ `automatic` → scheduler tự chạy; `manual` → nhân viên duyệt |
| `snoozed_until` | Date | ✅ Tạm hoãn rule (dịp Tết kho đóng cửa, không cần tái cung ứng) |
| `lead_days` (computed) | Float | ✅ Tự tính số ngày lead time từ rules → biết cần đặt hàng trước bao nhiêu ngày |
| `qty_on_hand` / `qty_forecast` | Float (computed) | ✅ Xem tồn kho thực + dự báo ngay trên màn hình rule |
| `days_to_order` | Float (computed) | ✅ Số ngày cần đặt trước → lên kế hoạch mua hàng |

> [!NOTE]  
> `days_to_order` được tính từ `lead_days` của supplier + security lead time của kho → đây là **lead time planning** built-in, không cần custom.

---

## 5. `stock.picking.type` — Loại Phiếu Kho

| Field / Tính năng có sẵn | Kiểu | Dùng cho FMCG như thế nào |
|---|---|---|
| `reservation_method` | Selection | ✅ `At Confirmation` (FG xuất ngay), `Before scheduled date` (buffer X ngày), `Manually` |
| `reservation_days_before` | Integer | ✅ "Reserve hàng trước 2 ngày so với ngày giao" → đảm bảo SLA giao hàng |
| `reservation_days_before_priority` | Integer | ✅ Đơn hàng ưu tiên (★) được reserve sớm hơn N ngày |
| `create_backorder` | Selection (ask/always/never) | ✅ Kho CDC `never` backorder (phải giao đủ); Kho RDC `ask` |
| `use_create_lots` / `use_existing_lots` | Boolean | ✅ Phiếu nhập: bật `create_lots`; Phiếu xuất: bật `use_existing_lots` |
| `picking_properties_definition` | PropertiesDefinition | ✅ Thêm field động vào phiếu kho theo loại: "Số container", "Tên tài xế", "Nhiệt độ xe lạnh" |
| `auto_print_lot_labels` / `lot_label_format` | Boolean / Selection | ✅ Tự in nhãn lô khi nhập hàng |
| `auto_print_delivery_slip` | Boolean | ✅ Tự in phiếu giao hàng khi validate |
| `print_label` | Boolean | ✅ Bật in nhãn sản phẩm |
| `show_entire_packs` | Boolean | ✅ Hiển thị và di chuyển cả pallet/kiện thay vì từng sản phẩm |
| `move_type` (picking level) | Selection (direct/one) | ✅ `one` = chờ đủ hàng mới giao; `direct` = giao được bao nhiêu hay bấy nhiêu |
| `sequence_code` | Char | ✅ Prefix cho mã phiếu: `WH/IN`, `CDC/OUT`, `HCM/INT` |

---

## 6. `product.supplierinfo` — Thông tin Nhà cung cấp

| Field / Tính năng có sẵn | Kiểu | Dùng cho FMCG như thế nào |
|---|---|---|
| `partner_id` | Many2one (res.partner) | ✅ NCC nào |
| `product_name` | Char | ✅ Tên sản phẩm theo NCC (NCC gọi khác tên SP của mình) |
| `product_code` | Char | ✅ Mã SP theo NCC → in trên PO theo mã NCC |
| `min_qty` | Float | ✅ **MOQ (Minimum Order Quantity)** — đặt tối thiểu bao nhiêu mới bán |
| `price` | Float | ✅ Giá mua theo NCC |
| `discount` | Float | ✅ Chiết khấu thương mại từ NCC |
| `price_discounted` | Float (computed) | ✅ Giá sau chiết khấu (computed tự động) |
| `delay` | Integer (days) | ✅ **Lead time** giao hàng của NCC (ngày) → ảnh hưởng Reorder Rule |
| `date_start` / `date_end` | Date | ✅ Hiệu lực hợp đồng / bảng giá NCC theo thời gian |
| `currency_id` | Many2one | ✅ Giá mua theo ngoại tệ (NCC nhập khẩu tính USD/EUR) |
| `product_id` | Many2one (product.product) | ✅ Gán riêng cho từng **variant** (NCC A chỉ cung cấp chai 500ml, NCC B cung cấp chai 1L) |
| Nhiều dòng cho cùng 1 NCC | (bằng `sequence`) | ✅ **Price breaks**: ≥100 thùng giá A, ≥500 thùng giá B (tạo nhiều dòng, khác `min_qty`) |

---

## Tổng kết — Mức độ coverage

```
res.partner          ████████████████░░  ~85% nhu cầu FMCG (chỉ thiếu Territory model)
product.template     ████████████████░░  ~85% (Properties field bù đắp rất nhiều)
stock.warehouse      ████████████████░░  ~90% (resupply + steps là đủ)
stock.orderpoint     ██████████████░░░░  ~75% (thiếu seasonal adjustment, forecast)
stock.picking.type   ████████████████░░  ~85% (Properties field bù đắp)
product.supplierinfo ████████████████░░  ~90% (min_qty + delay + price breaks đủ dùng)
```

> [!IMPORTANT]  
> **`fields.Properties` (PropertiesDefinition)** là vũ khí số 1 để tránh phải tạo field vật lý. Dùng nó trên:  
> - `product.category` → properties tự động xuất hiện trên Product  
> - `stock.picking.type` → properties tự động xuất hiện trên Picking  
> - `stock.lot` (`lot_properties_definition`) → properties tự động xuất hiện trên Lô hàng
