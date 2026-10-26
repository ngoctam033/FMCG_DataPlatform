from odoo import models, api, fields, Command
import random
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class EmployeeSimulatorDelivery(models.AbstractModel):
    _inherit = 'employee.simulator'

    @api.model
    def cron_process_outgoing_missing_lot_activities(self):
        """Assign available existing lots/serials to overdue deliveries."""
        activity_type = self.env.ref(
            'employee_simulator.mail_activity_missing_lot',
            raise_if_not_found=False,
        )
        replenish_activity_type = self.env.ref(
            'employee_simulator.mail_activity_replenish_lot_stock'
        )

        pickings = self.env['stock.picking'].search([
            ('activity_ids', 'any', [
                ('activity_type_id', '=', activity_type.id),
                ('date_deadline', '<', fields.Date.today()),
            ]),
            ('picking_type_id.code', '=', 'outgoing'),
        ], limit=500)

        Quant = self.env['stock.quant']
        for picking in pickings:
            is_fully_processed = True
            unavailable_lines = self.env['stock.move.line']

            for line in picking.move_line_ids:
                product = line.product_id
                if product.tracking == 'none' or line.lot_id or line.lot_name:
                    continue

                candidate_quants = Quant.search([
                    ('product_id', '=', product.id),
                    ('location_id', 'child_of', line.location_id.id),
                    ('lot_id', '!=', False),
                    ('quantity', '>', 0),
                    ('company_id', '=', picking.company_id.id),
                ], order='in_date, id')

                selected_lot = self.env['stock.lot']
                required_qty = line.quantity_product_uom
                for lot in candidate_quants.lot_id:
                    available_qty = Quant._get_available_quantity(
                        product,
                        line.location_id,
                        lot_id=lot,
                        strict=False,
                    )
                    has_enough_stock = product.uom_id.compare(
                        available_qty,
                        required_qty,
                    ) >= 0
                    is_valid_serial = (
                        product.tracking != 'serial'
                        or product.uom_id.compare(required_qty, 1.0) <= 0
                    )
                    if has_enough_stock and is_valid_serial:
                        selected_lot = lot
                        break

                if selected_lot:
                    line.write({'lot_id': selected_lot.id})
                else:
                    is_fully_processed = False
                    unavailable_lines |= line

            if unavailable_lines:
                existing_activity = picking.activity_ids.filtered(
                    lambda activity:
                        activity.activity_type_id == replenish_activity_type
                )

                if not existing_activity:
                    product_details = '<br/>'.join(
                        (
                            f'- {line.product_id.display_name}: '
                            f'{line.quantity_product_uom} '
                            f'{line.product_uom_id.name}'
                        )
                        for line in unavailable_lines
                    )

                    assignee = (
                        picking.user_id
                        or self.env.ref('base.user_admin')
                    )

                    picking.activity_schedule(
                        activity_type_id=replenish_activity_type.id,
                        summary='Không có Lot/Serial đủ tồn để xuất kho',
                        note=(
                            'Cần nhập bổ sung hàng có Lot/Serial '
                            'cho các sản phẩm:<br/>'
                            f'{product_details}'
                        ),
                        user_id=assignee.id,
                    )

            if is_fully_processed:
                activities = picking.activity_ids.filtered(
                    lambda activity: activity.activity_type_id == activity_type
                )
                activities.action_done()

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
                'description_picking': f'Xuất hàng giả lập: {product.name}',
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

    @api.model
    def cron_simulate_internal_transfer_assign(self):
        """
        [CRON] Giả lập nhân viên: Check Availability (Kiểm tra khả dụng) cho điều chuyển nội bộ.
        """
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
        self.cron_simulate_picking_assign(picking_type_id=picking_type.id)
