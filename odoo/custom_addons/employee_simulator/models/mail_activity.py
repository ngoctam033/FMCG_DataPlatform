from odoo import api, fields, models, _


class MailActivity(models.Model):
    _inherit = "mail.activity"

    document_url = fields.Char(compute="_compute_document_url")
    is_repeated_issue = fields.Boolean(
        string="Sự cố tái diễn",
        compute="_compute_is_repeated_issue",
        search="_search_is_repeated_issue",
    )

    @api.depends("res_model", "res_id", "activity_type_id")
    def _compute_is_repeated_issue(self):
        grouped_activities = self.with_context(active_test=False)._read_group(
            [
                ("res_model", "in", self.mapped("res_model")),
                ("res_id", "in", self.mapped("res_id")),
                ("activity_type_id", "in", self.activity_type_id.ids),
            ],
            ["res_model", "res_id", "activity_type_id"],
            ["__count"],
        )
        occurrence_count = {
            (res_model, res_id, activity_type.id): count
            for res_model, res_id, activity_type, count in grouped_activities
        }

        for activity in self:
            key = (
                activity.res_model,
                activity.res_id,
                activity.activity_type_id.id,
            )
            activity.is_repeated_issue = occurrence_count.get(key, 0) > 1

    @api.model
    def _search_is_repeated_issue(self, operator, value):
        if operator not in ("=", "!="):
            raise NotImplementedError(
                "Sự cố tái diễn chỉ hỗ trợ toán tử '=' và '!='."
            )

        grouped_activities = self.with_context(active_test=False)._read_group(
            [],
            ["res_model", "res_id", "activity_type_id"],
            ["id:recordset"],
            having=[("__count", ">", 1)],
        )
        repeated_activities = self.browse()
        for _res_model, _res_id, _activity_type, activities in grouped_activities:
            repeated_activities |= activities

        positive_search = (operator == "=" and value) or (
            operator == "!=" and not value
        )
        id_operator = "in" if positive_search else "not in"
        return [("id", id_operator, repeated_activities.ids)]

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
