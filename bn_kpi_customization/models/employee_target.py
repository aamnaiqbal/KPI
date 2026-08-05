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


    