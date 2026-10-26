from odoo import api, models


class EmployeeSimulatorRoutes(models.AbstractModel):
    _inherit = 'employee.simulator'

    @api.model
    def _simulate_route_entry_pickings(self, picking_type_xmlid, record_count=5):
        """Create draft pickings for one explicit route entry operation."""
        picking_type = self.env.ref(picking_type_xmlid)
        return self.simulate_create_picking(
            record_count=record_count,
            picking_type_id=picking_type.id,
        )

    @api.model
    def cron_simulate_recall_route_entry_create(self, record_count=5):
        """Create RECALL pickings that trigger RCQ and RCINSP push rules."""
        return self._simulate_route_entry_pickings(
            'fmcg_inventory_learning.picking_type_recall_receipt',
            record_count=record_count,
        )
