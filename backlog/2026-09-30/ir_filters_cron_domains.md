# Refactor Cron Domains to `ir.filters`

## Mục tiêu (Goal)
Tách rời các điều kiện lọc (domain) đang bị hardcode cứng trong code Python của các hàm cron (như `cron_find_missing_lot_pickings`, `cron_process_missing_lot_activities`) và chuyển chúng lên cơ sở dữ liệu (Database) thông qua model `ir.filters`.

## Lý do (Motivation)
- **Tính linh hoạt:** Người quản trị hệ thống có thể thay đổi, mở rộng hoặc thu hẹp điều kiện lọc của Cron (ví dụ thêm các loại phiếu kho mới, loại trừ một số kho đặc thù) ngay trên giao diện Odoo mà không cần sửa code hay khởi động lại Server.
- **Tính tập trung:** Quản lý tất cả các "Saved Searches" ở cùng một nơi.
- **Hiệu năng & Best Practice:** Tránh việc lặp lại code (DRY - Don't Repeat Yourself) giữa các cron tìm kiếm và cron xử lý.

## Các bước triển khai (Action Items)

### 1. Định nghĩa file XML Data
Tạo một file XML mới (ví dụ: `data/filter_data.xml`) và thêm vào `__manifest__.py`. Trong file này, định nghĩa các bản ghi `ir.filters`:

```xml
<odoo>
    <data>
        <!-- Filter cho Cron tìm phiếu thiếu Lot -->
        <record id="filter_cron_find_missing_lot" model="ir.filters">
            <field name="name">Simulator - Tìm phiếu thiếu Lot</field>
            <field name="model_id">stock.picking</field>
            <field name="user_id" eval="False"/>
            <field name="domain">[
                ('state', '=', 'assigned'), 
                ('move_line_ids.product_id.tracking', '!=', 'none'),
                ('picking_type_id.code', 'in', ['incoming', 'mrp_operation'])
            ]</field>
        </record>
        
        <!-- (Tùy chọn) Có thể định nghĩa thêm các filter khác cho các cron khác -->
    </data>
</odoo>
```

### 2. Sửa code Python
Sử dụng `odoo.tools.safe_eval` và `odoo.osv.expression` để đọc domain từ cơ sở dữ liệu và ghép nối các điều kiện động an toàn.

**Ví dụ sửa file `stock_picking_utils.py`:**
```python
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression

def cron_find_missing_lot_pickings(self):
    activity_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)
    
    # Đọc Filter từ DB
    my_filter = self.env.ref('employee_simulator.filter_cron_find_missing_lot')
    base_domain = safe_eval(my_filter.domain)
    
    # Nối thêm các điều kiện mang tính dynamic (phụ thuộc vào ID được sinh ra ở runtime)
    dynamic_domain = [
        ('activity_ids', 'not any', [('activity_type_id', '=', activity_type.id)]),
        ('message_ids', 'not any', [('mail_activity_type_id', '=', activity_type.id)])
    ]
    
    # Gộp domain an toàn
    final_domain = expression.AND([base_domain, dynamic_domain])
    
    pickings = self.env['stock.picking'].search(final_domain, limit=500)
    # ... phần còn lại giữ nguyên
```

**Ví dụ sửa file `action_simulator.py`:**
```python
def cron_process_missing_lot_activities(self):
    activity_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)
    
    my_filter = self.env.ref('employee_simulator.filter_cron_find_missing_lot')
    base_domain = safe_eval(my_filter.domain)
    
    dynamic_domain = [
        ('activity_ids.activity_type_id', '=', activity_type.id)
    ]
    
    final_domain = expression.AND([base_domain, dynamic_domain])
    pickings = self.env['stock.picking'].search(final_domain, limit=500)
    # ... phần còn lại giữ nguyên
```

### 3. Kiểm thử (Testing)
- Chạy cập nhật module (Upgrade module).
- Vào giao diện: *Settings -> Technical -> User-defined Filters*.
- Sửa trực tiếp domain trên giao diện và quan sát sự thay đổi trong hành vi của Cron.
- Đảm bảo hệ thống không bị lỗi crash do sai cú pháp domain.
