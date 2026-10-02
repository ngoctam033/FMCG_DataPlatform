from odoo import api, models


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
                    ["draft", "confirmed", "waiting", "assigned"],
                ),
            ],
            limit=5,
        )

        for picking in pickings:
            has_cancel_activity = any(
                activity.activity_type_id == activity_type
                for activity in picking.activity_ids
            )

            if has_cancel_activity:
                continue

            picking.activity_schedule(
                activity_type_id=activity_type.id,
                summary="Simulator: Chờ hủy phiếu kho",
                note=(
                    f"Simulator đã chọn phiếu {picking.name} để hủy. "
                    f"Trạng thái lúc chọn: {picking.state}"
                ),
                user_id=picking.user_id.id or self.env.ref("base.user_admin").id,
            )