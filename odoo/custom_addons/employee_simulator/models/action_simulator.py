from odoo import models, api, fields
import random
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class EmployeeSimulator(models.AbstractModel):
    # Trả lại AbstractModel như thiết kế ban đầu (không tạo bảng)
    _name = 'employee.simulator'
    _description = 'Employee Action Simulator'

    @api.model
    def simulate_create_picking(self):
        """
        Giả lập hành vi: Nhân viên kho vào hệ thống tạo thủ công một Phiếu kho.
        """
        
        users = self.env['res.users'].search([('id', '>', 1), ('share', '=', False)])
            
        random_user = random.choice(users)
        
        # Tìm picking type
        picking_type = self.env['stock.picking.type'].search([], limit=1)
        
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([], limit=1)
            
        products = self.env['product.product'].search([], limit=20)
        partners = self.env['res.partner'].search([], limit=50)
        
        simulated_env = self.env['stock.picking'].with_user(random_user.id)
        now = fields.Datetime.now()
        
        # Tạo Phiếu kho (Kèm các field như trên UI)
        picking = simulated_env.create({
            'picking_type_id': picking_type.id,
            'origin': f'SIM-MANUAL-{random.randint(100, 999)}',
            'partner_id': random.choice(partners).id if partners else False,
            'scheduled_date': now + timedelta(days=random.randint(1, 3)),
            'date_deadline': now + timedelta(days=random.randint(4, 7)),
        })
        
        # Tạo Chi tiết Dòng sản phẩm (Kèm diễn giải và số lượng kiểm đếm)
        move_env = self.env['stock.move'].with_user(random_user.id)
        for _ in range(random.randint(1, 3)):
            random_product = random.choice(products)
            demand_qty = random.randint(5, 50)
            
            move_env.create({
                'product_id': random_product.id,
                'description_picking': f"Chi tiết giả lập: {random_product.name}",
                'product_uom_qty': demand_qty,
                'quantity': max(0, demand_qty - random.choice([0, 0, random.randint(1, 4)])), # Ngẫu nhiên đếm đủ hoặc thiếu
                'product_uom': random_product.uom_id.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })
            
        return picking.id