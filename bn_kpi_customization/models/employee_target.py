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

    value = fields.Float()

    change = fields.Integer(
        string="Change",
        default=0,
    )

    def write(self, vals):
        res = super().write(vals)

        if "value" in vals:
            for target in self:
                if target.kpi_line_id.allocation != "team":
                    continue

                total = sum(target.kpi_line_id.employee_target_ids.mapped("value"))
                target.kpi_line_id.value = total

        return res


    