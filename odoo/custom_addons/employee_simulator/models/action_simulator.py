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
    def simulate_create_picking(self):
        """
        Giả lập hành vi dựa trên hàm băm thời gian (Time-based Deterministic)
        """
        now = fields.Datetime.now()
        minute = now.minute
        hour = now.hour
        day = now.day
        month = now.month
        # Tùy thuộc vào cron chạy, second có thể luôn bằng 0, nên hạn chế dùng second làm biến số chính
        
        users = self.env['res.users'].search([('id', '>', 1), ('share', '=', False)])
            
        # Dùng công thức nhân số nguyên tố để tạo sự xáo trộn (hash)
        selected_user = users[(minute * 3 + hour * 7 + day * 11) % len(users)]

        company_domain = ['|', ('company_id', '=', selected_user.company_id.id), ('company_id', '=', False)]
        
        picking_types = self.env['stock.picking.type'].search(company_domain)
        selected_picking_type = picking_types[(minute * 5 + day * 13) % len(picking_types)]
            
        products = self.env['product.product'].search([])
        partners = self.env['res.partner'].search([])
        
        selected_partner_id = False
        if partners:
            selected_partner_id = partners[(minute * 17 + hour * 23 + month * 31) % len(partners)].id
        
        move_commands = []
        
        for i in range((minute + hour) % 3 + 1):
            selected_product = products[(minute * 19 + hour * 29 + day * 37 + i * 41) % len(products)]
            
            # Số lượng dao động từ 5 đến 45, tính toán đa dạng hơn
            demand_qty = 5 + ((minute * 7 + i * 13 + day * 17) % 41)
            
            # Cứ 3 dòng thì 1 dòng có done_qty thấp hơn demand_qty
            if (minute + i) % 3 == 0:
                done_qty = max(0, demand_qty - ((hour + i) % 5 + 1))
            else:
                done_qty = demand_qty
            
            move_commands.append(Command.create({
                'description_picking': f"Chi tiết giả lập: {selected_product.name}",
                'product_id': selected_product.id,
                'product_uom_qty': demand_qty,
                'quantity': done_qty,
                'product_uom': selected_product.uom_id.id,
            }))
        
        # Thời gian scheduled dao động từ 1 đến 5 ngày
        days_offset = (minute * 11 + hour * 3) % 5 + 1
        
        picking = self.env['stock.picking'].with_user(selected_user.id).create({
            'picking_type_id': selected_picking_type.id,
            'origin': f'SIM-MANUAL-{now.strftime("%Y%m%d%H%M")}',
            'partner_id': selected_partner_id,
            'scheduled_date': now + timedelta(days=days_offset),
            'date_deadline': now + timedelta(days=days_offset + (hour % 3) + 1),
            'move_ids': move_commands,
        })
        
        return picking.id