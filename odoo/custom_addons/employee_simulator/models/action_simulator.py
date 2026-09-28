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
        Giả lập hành vi: Nhân viên kho vào hệ thống tạo thủ công một Phiếu kho.
        """
        now = fields.Datetime.now()
        minute = now.minute
        second = now.second
        
        users = self.env['res.users'].search([('id', '>', 1), ('share', '=', False)])
        selected_user = users[minute % len(users)]

        company_domain = ['|', ('company_id', '=', selected_user.company_id.id), ('company_id', '=', False)]
        
        picking_types = self.env['stock.picking.type'].search(company_domain)
        selected_picking_type = picking_types[(minute + second) % len(picking_types)]
            
        products = self.env['product.product'].search([], limit=20)
        partners = self.env['res.partner'].search([], limit=50)
        
        move_commands = []
        for i in range((minute % 3) + 1):
            selected_product = products[(minute + i) % len(products)]
            demand_qty = 5 + ((second + i) % 45)
            
            if (minute + i) % 3 == 0:
                done_qty = max(0, demand_qty - (((second + i) % 4) + 1))
            else:
                done_qty = demand_qty
            
            move_commands.append(Command.create({
                'description_picking': f"Chi tiết giả lập: {selected_product.name}",
                'product_id': selected_product.id,
                'product_uom_qty': demand_qty,
                'quantity': done_qty,
                'product_uom': selected_product.uom_id.id,
            }))
        
        picking = self.env['stock.picking'].with_user(selected_user.id).create({
            'picking_type_id': selected_picking_type.id,
            'origin': f'SIM-MANUAL-{now.strftime("%Y%m%d%H%M%S")}',
            'partner_id': partners[minute % len(partners)].id if partners else False,
            'scheduled_date': now + timedelta(days=(minute % 3) + 1),
            'date_deadline': now + timedelta(days=(minute % 4) + 4),
            'move_ids': move_commands,
        })
        
        return picking.id