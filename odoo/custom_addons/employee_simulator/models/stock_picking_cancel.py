from odoo import api, fields, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class EmployeeSimulatorCancel(models.AbstractModel):
    _inherit = "employee.simulator"

    @api.model
    def cron_find_picking_cancel_candidates(self):
        activity_type = self.env.ref("employee_simulator.mail_activity_simulate_cancel", raise_if_not_found=False)

        pickings = self.env["stock.picking"].search(
            [
                (
                    "state",
                    "in",
                    ["draft", "confirmed", "waiting", "assigned", 'cancel'],
                ),
                (
                    "activity_ids",
                    "not any",
                    [("activity_type_id", "=", activity_type.id)],
                ),
            ],
            limit=5,
        )

        for picking in pickings:
            picking.activity_schedule(
                activity_type_id=activity_type.id,
                summary="Simulator: Chờ hủy phiếu kho",
                note=(
                    f"Simulator đã chọn phiếu {picking.name} để hủy. "
                    f"Trạng thái lúc chọn: {picking.state}"
                ),
                user_id=picking.user_id.id or self.env.ref("base.user_admin").id,
            )

    @api.model
    def cron_simulate_backorder_cancel(self):
        """
        [CRON] Giả lập nhân viên: Xử lý Activity Backorder - Tự động chọn "Không tạo phần dư" (Cancel Backorder)
        """
        activity_type = self.env.ref('employee_simulator.mail_activity_backorder', raise_if_not_found=False)
        missing_lot_act_type = self.env.ref('employee_simulator.mail_activity_missing_lot', raise_if_not_found=False)
        # Ưu tiên các phiếu có activity Backorder quá hạn lâu nhất.
        overdue_activities = self.env['mail.activity'].search([
            ('res_model', '=', 'stock.picking'),
            ('activity_type_id', '=', activity_type.id),
            ('date_deadline', '<', fields.Date.context_today(self)),
        ], order='date_deadline asc, id asc')

        picking_ids = list(dict.fromkeys(overdue_activities.mapped('res_id')))
        pickings = self.env['stock.picking'].browse(picking_ids).exists().filtered(
            lambda picking: not any(
                activity.activity_type_id == missing_lot_act_type
                for activity in picking.activity_ids
            )
        )[:5]

        for picking in pickings:
            target_activities = picking.activity_ids.filtered(lambda a: a.activity_type_id.id == activity_type.id)
            activity_user = target_activities[0].user_id if target_activities else self.env.user
            
            # Kiểm tra quyền: nếu user không có quyền Kho thì tìm một user khác có quyền để đóng thế
            if activity_user.has_group('stock.group_stock_user'):
                user_id = activity_user.id
            else:
                stock_group = self.env.ref('stock.group_stock_user')
                stock_user = self.env['res.users'].sudo().search([
                    ('active', '=', True),
                    ('all_group_ids', 'in', [stock_group.id]),
                    ('company_ids', 'in', [picking.company_id.id]),
                ], order='id', limit=1)
                stock_user.ensure_one()
                user_id = stock_user.id

            simulated_picking = picking.with_user(user_id)
            
            context = {
                'button_validate_picking_ids': [simulated_picking.id],
                'default_pick_ids': [(4, simulated_picking.id)],
                'default_company_id': simulated_picking.company_id.id,
            }
            
            wizard = self.env['stock.backorder.confirmation'].with_user(user_id).with_company(picking.company_id.id).with_context(context).create({
                'pick_ids': [(4, simulated_picking.id)]
            })
            
            try:
                wizard.process_cancel_backorder()
            except UserError as e:
                if 'Lot/Serial' in str(e):
                    simulated_picking.activity_schedule(
                        'employee_simulator.mail_activity_missing_lot',
                        summary='Thiếu Lot/Serial khi Cancel Backorder',
                        note=f'Hủy Backorder thất bại do thiếu Lot/Serial: <b>{str(e)}</b>',
                        user_id=user_id
                    )
                else:
                    _logger.exception("[CRON SIMULATE BACKORDER CANCEL] Phiếu %s bị lỗi khi xử lý: %s", picking.name, str(e))
                continue
                
            # Đóng activity khi phiếu kho đã chốt thành công
            if simulated_picking.state == 'done':
                for activity in target_activities:
                    activity.action_done()

    @api.model
    def cron_close_stale_backorder_activities(self):
        """Close backorder activities left on completed or cancelled pickings."""
        activity_type = self.env.ref(
            'employee_simulator.mail_activity_backorder',
            raise_if_not_found=False,
        )

        overdue_activities = self.env['mail.activity'].search([
            ('res_model', '=', 'stock.picking'),
            ('activity_type_id', '=', activity_type.id),
            ('date_deadline', '<', fields.Date.context_today(self)),
        ], order='date_deadline asc, id asc')

        picking_ids = list(dict.fromkeys(overdue_activities.mapped('res_id')))
        pickings = self.env['stock.picking'].browse(picking_ids).exists().filtered(
            lambda picking: picking.state in ('done', 'cancel')
        )[:100]

        state_labels = dict(self.env['stock.picking']._fields['state'].selection)
        for picking in pickings:
            activities = picking.activity_ids.filtered(
                lambda activity: activity.activity_type_id == activity_type
            )
            activities.action_feedback(feedback=(
                'Phiếu kho đã ở trạng thái "%s". Yêu cầu xác nhận Backorder '
                'không còn hiệu lực và được hệ thống tự động đóng.'
            ) % state_labels[picking.state])
