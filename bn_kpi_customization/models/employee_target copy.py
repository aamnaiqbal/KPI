from odoo import models, fields, api
from datetime import date, datetime, time
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
    
    achieved = fields.Float(
        string="Current Actual", 
        compute="_compute_achieved", 
        store=True)
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

    def _refresh_auto_targets(self, record):
        if record._name == "hr.attendance":
            if not record.employee_id.user_id or not record.check_in:
                return

            user_id = record.employee_id.user_id.id
            record_date = record.check_in.date()

        else:
            if not record.create_uid or not record.create_date:
                return

            user_id = record.create_uid.id
            record_date = record.create_date.date()

        targets = self.search([
            ("parameter_type", "=", "auto"),
            ("employee_id", "=", user_id),
            ("parameter_id.model_id.model", "=", record._name),
            ("kpi_id.from_date", "<=", record_date),
            ("kpi_id.to_date", ">=", record_date),
        ])

        targets._compute_achieved()


    @api.depends(
        "parameter_id",
        "parameter_id.type",
        "parameter_id.model_id",
        "parameter_id.calculation",
        "parameter_id.field_value",
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

            # Build domain according to model
            if rec.parameter_id.model_id.model == "hr.attendance":
                domain = [
                    ("employee_id.user_id", "=", rec.employee_id.id),
                ]

                if rec.kpi_id.from_date:
                    domain.append((
                        "check_in",
                        ">=",
                        datetime.combine(rec.kpi_id.from_date, time.min),
                    ))

                if rec.kpi_id.to_date:
                    domain.append((
                        "check_in",
                        "<=",
                        datetime.combine(rec.kpi_id.to_date, time.max),
                    ))

            else:
                domain = [
                    ("create_uid", "=", rec.employee_id.id),
                ]

                if rec.kpi_id.from_date:
                    domain.append((
                        "create_date",
                        ">=",
                        datetime.combine(rec.kpi_id.from_date, time.min),
                    ))

                if rec.kpi_id.to_date:
                    domain.append((
                        "create_date",
                        "<=",
                        datetime.combine(rec.kpi_id.to_date, time.max),
                    ))

            # Perform calculation
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

                if result:
                    rec.achieved = result[0].get(field_name, 0.0) or 0.0

#     def _refresh_auto_targets(self, record):
#         targets = self.search([
#             ("parameter_type", "=", "auto"),
#             ("employee_id", "=", record.create_uid.id),
#             ("parameter_id.model_id.model", "=", record._name),
#             ("kpi_id.from_date", "<=", record.create_date.date()),
#             ("kpi_id.to_date", ">=", record.create_date.date()),
#         ])

#         targets._compute_achieved()

#     @api.depends(
#     "parameter_id",
#     "parameter_id.type",
#     "parameter_id.model_id",
#     "parameter_id.calculation",
#     "parameter_id.field_value",
#     "employee_id",
#     "kpi_id.from_date",
#     "kpi_id.to_date",
# )
#     def _compute_achieved(self):
#         for rec in self:
#             rec.achieved = 0.0

#             if (
#                 rec.parameter_type != "auto"
#                 or not rec.parameter_id.model_id
#             ):
#                 continue

#             Model = self.env[rec.parameter_id.model_id.model]

#             domain = [
#                 ("create_uid", "=", rec.employee_id.id),
#             ]

#             if rec.kpi_id.from_date:
#                 domain.append((
#                     "create_date",
#                     ">=",
#                     datetime.combine(rec.kpi_id.from_date, time.min),
#                 ))

#             if rec.kpi_id.to_date:
#                 domain.append((
#                     "create_date",
#                     "<=",
#                     datetime.combine(rec.kpi_id.to_date, time.max),
#                 ))

#             if rec.parameter_id.calculation == "count":
#                 rec.achieved = Model.search_count(domain)

#             elif (
#                 rec.parameter_id.calculation == "sum"
#                 and rec.parameter_id.field_value
#             ):
#                 field_name = rec.parameter_id.field_value.name

#                 result = Model.read_group(
#                     domain,
#                     [f"{field_name}:sum"],
#                     [],
#                 )

#                 if result:
#                     rec.achieved = result[0].get(field_name, 0.0) or 0.0



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


    