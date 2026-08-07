from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval

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
    kpi_name = fields.Char(
        related="kpi_id.name",
        string="Name",
        store=True,
        readonly=True,
        )
    kpi_code = fields.Char(
        related="kpi_id.code",
        string="Code",
        store=True,
        readonly=True, 
        )

    value = fields.Integer(string="Current Target")
    
    achieved = fields.Float(
        string="Current Actual", 
        compute="_compute_achieved", 
        store=True)
    current_achievement = fields.Float(
        string="Current Achievement (%)",
        compute="_compute_current_progress",
        store=True,
    )

    current_score = fields.Integer(
        string="Score",
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

    def _refresh_auto_targets(self, record):
        targets = self.search([
            ("parameter_type", "=", "auto"),
            ("parameter_id.model_id.model", "=", record._name),
        ])

        targets._compute_achieved()

    @api.depends(
        "parameter_id",
        "parameter_id.type",
        "parameter_id.model_id",
        "parameter_id.calculation",
        "parameter_id.field_value",
        "parameter_id.domain",
        "employee_id",
        "kpi_id.from_date",
        "kpi_id.to_date",
    )
    def _compute_achieved(self):
        for rec in self:
            rec.achieved = 0.0

            if (
                rec.parameter_type != "auto"
                or not rec.parameter_id.model_id
            ):
                continue

            Model = self.env[rec.parameter_id.model_id.model]

            domain = []

            if rec.parameter_id.domain:
                domain = safe_eval(
                    rec.parameter_id.domain,
                    {
                        "rec": rec,
                        "datetime": datetime,
                        "time": time,
                    },
                )

            if rec.parameter_id.calculation == "count":
                rec.achieved = Model.search_count(domain)

            elif (
                rec.parameter_id.calculation == "sum"
                and rec.parameter_id.field_value
            ):
                field_name = rec.parameter_id.field_value.name

                result = Model.read_group(
                    domain,
                    [f"{field_name}:sum"],
                    [],
                )

                rec.achieved = result and result[0].get(field_name, 0.0) or 0.0


    @api.depends("value", "achieved", "kpi_line_id.score")
    def _compute_current_progress(self):
        for rec in self:
            if rec.value > 0:
                percentage = (rec.achieved / rec.value) * 100
            else:
                percentage = 0


            # Cap at 100%
            percentage = min(percentage, 100)

            rec.current_score = int(
                round((percentage / 100) * rec.kpi_line_id.score)
            )
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


    