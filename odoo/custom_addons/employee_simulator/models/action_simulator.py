from odoo import models, api, fields
import random
import logging
from datetime import timedelta
from odoo import Command

_logger = logging.getLogger(__name__)

class EmployeeSimulator(models.AbstractModel):
    # Trả lại AbstractModel như thiết kế ban đầu (không tạo bảng)
    _name = 'employee.simulator'
    _description = 'Employee Action Simulator'

    @api.model
    def simulate_create_picking(self, record_count=100):
        """
        Nâng cấp: Giả lập tạo hàng loạt phiếu kho trong 1 lần chạy hàm.
        - Tối ưu hóa: Truy vấn DB trước vòng lặp.
        - Xáo trộn: Sử dụng biến `salt` để xáo trộn dữ liệu giữa các record.
        """
        now = fields.Datetime.now()
        minute = now.minute
        hour = now.hour
        day = now.day
        month = now.month
        # Tùy thuộc vào cron chạy, second có thể luôn bằng 0, nên hạn chế dùng second làm biến số chính
        
        # 1. TỐI ƯU HÓA: Kéo dữ liệu từ Database ra ngoài vòng lặp 
        # (Chỉ query 1 lần, giúp hàm chạy cực nhanh kể cả khi tạo 100 record)
        users = self.env['res.users'].search([('id', '>', 1), ('share', '=', False)])
        products = self.env['product.product'].search([])
        partners = self.env['res.partner'].search([])
        
        created_picking_ids = []
        
        for i in range(record_count):
            salt = random.randint(1, 10000) + i
            
            # Chọn user
            selected_user = users[(minute * 3 + hour * 7 + day * 11 + salt) % len(users)]
            
            # (Riêng Picking type phụ thuộc vào company của User, nên phải tìm trong vòng lặp)
            company_domain = ['|', ('company_id', '=', selected_user.company_id.id), ('company_id', '=', False)]
            picking_types = self.env['stock.picking.type'].search(company_domain)
            selected_picking_type = picking_types[(minute * 5 + day * 13 + salt) % len(picking_types)]
            
            # Chọn đối tác
            selected_partner_id = False
            if partners:
                selected_partner_id = partners[(minute * 17 + hour * 23 + month * 31 + salt) % len(partners)].id
            
            move_commands = []
            
            for j in range((minute + hour + salt) % 3 + 1):
                selected_product = products[(minute * 19 + hour * 29 + day * 37 + j * 41 + salt) % len(products)]
                demand_qty = 5 + ((minute * 7 + j * 13 + day * 17 + salt) % 41)
                
                if (minute + j) % 3 == 0:
                    done_qty = max(0, demand_qty - ((hour + j) % 5 + 1))
                else:
                    done_qty = demand_qty
                
                move_commands.append(Command.create({
                    'description_picking': f"Chi tiết giả lập: {selected_product.name}",
                    'product_id': selected_product.id,
                    'product_uom_qty': demand_qty,
                    'quantity': done_qty,
                    'product_uom': selected_product.uom_id.id,
                }))
            
            days_offset = (minute * 11 + hour * 3 + salt) % 5 + 1
            
            # 3. ĐẢM BẢO ORIGIN DUY NHẤT (Mã phiếu chứa mã ngẫu nhiên)
            origin_str = f'SIM-MANUAL-{now.strftime("%Y%m%d%H%M%S")}-{salt}'
            
            # Tạo phiếu
            picking = self.env['stock.picking'].with_user(selected_user.id).create({
                'picking_type_id': selected_picking_type.id,
                'origin': origin_str,
                'partner_id': selected_partner_id,
                'scheduled_date': now + timedelta(days=days_offset),
                'date_deadline': now + timedelta(days=days_offset + (hour % 3) + 1),
                'move_ids': move_commands,
            })
            
            created_picking_ids.append(picking.id)
            
        if record_count == 1 and created_picking_ids:
            return created_picking_ids[0]

    @api.model
    def simulate_confirm_picking(self):
        """
        Cron 2: Giả lập nhân viên thao tác Xác nhận (Confirm) các phiếu kho đang Nháp.
        """
        # Lấy một user ngẫu nhiên để ghi nhận lịch sử thao tác
        users = self.env['res.users'].search([('id', '>', 1), ('share', '=', False)])
        random_user = random.choice(users) if users else self.env.user

        pickings = self.env['stock.picking'].search([('state', '=', 'draft')], limit=20)

        for picking in pickings:

            simulated_picking = picking.with_user(random_user.id)
            simulated_picking.action_confirm()
