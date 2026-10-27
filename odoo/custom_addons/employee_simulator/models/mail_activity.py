from odoo import api, fields, models, _


class MailActivity(models.Model):
    _inherit = "mail.activity"

    document_url = fields.Char(compute="_compute_document_url")

    @api.depends("res_model", "res_id")
    def _compute_document_url(self):
        for activity in self:
            activity.document_url = (
                f"/web#model={activity.res_model}&id={activity.res_id}&view_type=form"
            )

    @api.model
    def action_deduplicate_simulator_activities(self):
        activity_type_ids = self.env.context.get(
            "employee_simulator_activity_type_ids", []
        )
        activities = self.with_context(active_test=False).search(
            [
                ("active", "=", True),
                ("activity_type_id", "in", activity_type_ids),
            ],
            order="create_date asc, id asc",
        )

        seen = set()
        duplicates = self.env["mail.activity"]
        for activity in activities:
            key = (
                activity.res_model,
                activity.res_id,
                activity.activity_type_id.id,
            )
            if key in seen:
                duplicates |= activity
            else:
                seen.add(key)

        duplicate_count = len(duplicates)
        duplicates.unlink()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Dọn activity trùng"),
                "message": _("Đã xóa %s activity bị gắn trùng.", duplicate_count),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }
