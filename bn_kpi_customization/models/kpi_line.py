from odoo import models, fields, api, _


class KPILine(models.Model):
    _name = "kpi.kpi.line"
    _description = "KPI Configuration Line"

    kpi_id = fields.Many2one(
        "kpi.kpi",
        string="KPI",
        required=True,
        ondelete="cascade",
    )

    employee_target_ids = fields.One2many(
        "employee.target",
        "kpi_line_id",
        string="Employee Targets"
    )

    parameter_id = fields.Many2one(
        "parameter.master.setup",
        string="Parameter",
        required=True,
    )

    allocation = fields.Selection(
        [
            ("team", "Team"),
            ("person", "Person"),
        ],
        string="Allocation",
        required=True,
    )

    value = fields.Integer(
        string="Value",
        default=0,
    )

    change = fields.Integer(
        string="Change",
        default=0,
    )

    score = fields.Integer(
        string="Score",
        default=0,
    )


    