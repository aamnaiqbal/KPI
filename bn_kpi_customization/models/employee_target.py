from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta

class EmployeeTarget(models.Model):
    _name = "employee.target"
    _description = "Employee Target"

    kpi_id = fields.Many2one(
        "kpi.kpi",
        required=True,
        ondelete="cascade",
    )

    kpi_line_id = fields.Many2one(
        "kpi.kpi.line",
        required=True,
        ondelete="cascade",
    )

    employee_id = fields.Many2one(
        "res.users",
        required=True,
    )

    parameter_id = fields.Many2one(
        "parameter.master.setup",
        required=True,
    )
    parameter_type = fields.Selection(
        related="parameter_id.type",
        store=True,
        readonly=True,
    )

    value = fields.Integer(string="Current Target")
    
    achieved = fields.Integer(string="Current Actual")
    current_achievement = fields.Float(
        string="Current Achievement (%)",
        compute="_compute_current_progress",
        store=True,
    )

    current_state = fields.Selection(
        [
            ("danger", "Danger"),
            ("warning", "Warning"),
            ("success", "Success"),
        ],
        string="Current State",
        compute="_compute_current_progress",
        store=True,
    )

    @api.depends("value", "achieved")
    def _compute_current_progress(self):
        for rec in self:
            if rec.value > 0:
                percentage = (rec.achieved / rec.value) * 100
            else:
                percentage = 0

            rec.current_achievement = percentage

            if percentage >= 90:
                rec.current_state = "success"
            elif percentage >= 50:
                rec.current_state = "warning"
            else:
                rec.current_state = "danger"

    
    def write(self, vals):
        res = super().write(vals)

        if self.env.context.get("skip_kpi_sync"):
            return res


        if "value" in vals:
            for target in self:
                if target.kpi_line_id.allocation != "team":
                    continue

                total = sum(target.kpi_line_id.employee_target_ids.mapped("value"))
                # target.kpi_line_id.value = total
                target.kpi_line_id.with_context(skip_employee_sync=True).write({
                    "value": total,
                })

        return res


    