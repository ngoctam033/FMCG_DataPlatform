from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
class EmployeeSimulatorLotSerial(models.AbstractModel):
    # Kế thừa lại abstract model employee.simulator
    _inherit = 'employee.simulator'

    @api.model
    def cron_find_missing_lot_pickings(self):
        activity_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)


        # Đẩy toàn bộ điều kiện lọc xuống Database
        domain = [
            ('state', '=', 'assigned'),
            # Lọc sơ bộ: Phiếu phải chứa ít nhất 1 line có sản phẩm yêu cầu Lot/Serial
            ('move_line_ids.product_id.tracking', '!=', 'none'),
            ('picking_type_id.code', 'in', ['incoming', 'mrp_operation']),

            # Chưa có Activity đang mở
            (
                'activity_ids',
                'not any',
                [('activity_type_id', '=', activity_type.id)]
            ),

            # Chưa từng hoàn tất Activity loại này
            (
                'message_ids',
                'not any',
                [('mail_activity_type_id', '=', activity_type.id)]
            ),
        ]
        
        pickings = self.env['stock.picking'].search(domain, limit=80)
        
        problematic_pickings = self.env['stock.picking']
        
        for picking in pickings:
            # if len(problematic_pickings) >= 30:
            #     break
            has_open_activity = any(act.activity_type_id.id == activity_type.id for act in picking.activity_ids)
            has_done_activity = any(msg.mail_activity_type_id.id == activity_type.id for msg in picking.message_ids)
            
            if has_open_activity or has_done_activity:
                continue

            for line in picking.move_line_ids:
                if line.product_id.tracking != 'none' and not line.lot_id and not line.lot_name:
                    problematic_pickings |= picking
                    
                    # Ưu tiên gán Activity cho người phụ trách phiếu (user_id), nếu không có thì gán cho Admin
                    assignee_id = picking.user_id.id or self.env.ref('base.user_admin').id
                    
                    picking.activity_schedule(
                        activity_type_id=activity_type.id,
                        note=f'Simulator: Cần khai báo Lot/Serial cho sản phẩm {line.product_id.display_name}',
                        user_id=assignee_id
                    )
                    break

    @api.model
    def cron_process_missing_quantity_activities(self):
        """
        Lọc các phiếu có activity yêu cầu điền số lượng và tự động điền quantity = product_uom_qty.
        """
        activity_type = self.env.ref('employee_simulator.mail_activity_missing_quantity', raise_if_not_found=False)

        domain = [
            ('activity_ids.activity_type_id', '=', activity_type.id),
            ('state', 'in', ['assigned', 'confirmed', 'draft'])
        ]
        
        pickings = self.env['stock.picking'].search(domain, limit=30)
        
        for picking in pickings:
            # Gán user_id cho quá trình thao tác dựa trên activity
            activity = picking.activity_ids.filtered(lambda a: a.activity_type_id == activity_type)[:1]
            user_id = activity.user_id.id if activity and activity.user_id else self.env.uid
            simulated_picking = picking.with_user(user_id)
            
            # Điền số lượng hoàn thành ngẫu nhiên từ 1 đến product_uom_qty
            for move in simulated_picking.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                if move.product_uom_qty > 0 and move.quantity == 0:
                    max_qty = int(move.product_uom_qty)
                    if max_qty >= 1:
                        move.quantity = random.randint(1, max_qty)
                    else:
                        move.quantity = move.product_uom_qty
            
            # Hoàn tất activity
            activity.action_done()