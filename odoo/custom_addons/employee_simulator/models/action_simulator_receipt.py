from odoo import api, models


class EmployeeSimulatorReceipt(models.AbstractModel):
    _inherit = 'employee.simulator'

    @api.model
    def cron_simulate_receipt_picking_create(self, record_count=100):
        """Create draft receipts using one incoming operation type."""
        receipt_picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming')],
            limit=1,
        )
        return self.simulate_create_picking(
            record_count=record_count,
            picking_type_id=receipt_picking_type.id,
        )
