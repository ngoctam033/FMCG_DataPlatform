from odoo import api, models


class EmployeeSimulatorInternal(models.AbstractModel):
    _inherit = 'employee.simulator'

    @api.model
    def cron_process_internal_missing_lot_activities(self):
        """Xử lý activity thiếu Lot/Serial cho phiếu chuyển kho nội bộ."""
        return self.cron_process_missing_lot_activities([
            ('picking_type_id.code', 'in', ['internal']),
        ])
