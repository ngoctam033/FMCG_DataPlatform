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