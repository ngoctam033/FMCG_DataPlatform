from odoo import models, api, fields, Command
import random
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class EmployeeSimulatorDelivery(models.AbstractModel):
    _inherit = 'employee.simulator'

    @api.model
    def cron_simulate_delivery_picking_create(self):
        """Create one draft delivery order (outgoing)."""
        now = fields.Datetime.now()
        stock_user_group = self.env.ref('stock.group_stock_user')

        # Lấy danh sách user kho
        users = self.env['res.users'].search([
            ('id', '>', 1),
            ('share', '=', False),
            ('active', '=', True),
            ('all_group_ids', 'in', stock_user_group.id),
        ])

        # Chọn ngẫu nhiên một user và công ty của họ
        user = random.choice(users)
        company = random.choice(user.company_ids)

        # Lấy picking type xuất kho (outgoing)
        picking_types = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('company_id', 'in', [False, company.id]),
        ])
        picking_type = random.choice(picking_types)

        # Kho mặc định của picking type
        source_location = picking_type.default_location_src_id
        destination_location = picking_type.default_location_dest_id
        
        # Lấy sản phẩm
        products = self.env['product.product'].search([
            ('active', '=', True),
            ('is_storable', '=', True),
            ('company_id', 'in', [False, company.id]),
        ], limit=50)

        # Lấy một khách hàng ngẫu nhiên
        partners = self.env['res.partner'].search([
            ('customer_rank', '>', 0),
            ('company_id', 'in', [False, company.id])
        ], limit=50)
        
        # Nếu không có khách hàng, lấy ngẫu nhiên 1 partner bất kỳ
        if not partners:
            partners = self.env['res.partner'].search([
                ('company_id', 'in', [False, company.id])
            ], limit=50)

        partner = random.choice(partners)
        product = random.choice(products)
        demand_qty = random.randint(5, 50)
        salt = random.randint(1, 10000)
        origin = f'SIM-OUT-{now.strftime("%Y%m%d%H%M%S")}-{salt}'

        picking_vals = {
            'picking_type_id': picking_type.id,
            'company_id': company.id,
            'origin': origin,
            'partner_id': partner.id,
            'location_id': source_location.id if source_location else False,
            'location_dest_id': destination_location.id if destination_location else False,
            'scheduled_date': now + timedelta(days=random.randint(1, 3)),
            'move_ids': [Command.create({
                'name': f'Xuất hàng giả lập: {product.name}',
                'product_id': product.id,
                'product_uom_qty': demand_qty,
                'product_uom': product.uom_id.id,
                'location_id': source_location.id if source_location else False,
                'location_dest_id': destination_location.id if destination_location else False,
            })],
        }
        
        picking = self.env['stock.picking'].with_user(user).with_company(company).create(picking_vals)
        return picking.id

    @api.model
    def cron_simulate_internal_transfer_confirm(self):
        """
        [CRON] Giả lập nhân viên: Xác nhận phiếu chuyển nội bộ (INT-PUT-002).
        Tái sử dụng hàm simulate_confirm_picking với các tham số lọc cụ thể.
        """
        self.simulate_confirm_picking(
            picking_type_code='internal'
        )
