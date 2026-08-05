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

    

    score = fields.Integer(
        string="Score",
        default=0,
    )


    def write(self, vals):
        res = super().write(vals)

        if self.env.context.get("skip_employee_sync"):
            return res

        if "value" in vals:
            self._redistribute_targets()

        return res


    def _redistribute_targets(self):
        for line in self:
            if line.allocation != "team":
                line.employee_target_ids.write({
                    "value": line.value,
                })
                continue

            targets = line.employee_target_ids

            member_count = len(targets)

            if not member_count:
                continue

            base = line.value // member_count
            remainder = line.value % member_count

            member_map = {
                member.id: index
                for index, member in enumerate(line.kpi_id.team_id.member_ids)
            }

            targets = targets.sorted(
                key=lambda t: member_map.get(t.employee_id.id, 9999)
            )

            for index, target in enumerate(targets):
                value = base

                if index < remainder:
                    value += 1

                target.with_context(skip_kpi_sync=True).write({
                    "value": value,
                })


    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)

        EmployeeTarget = self.env["employee.target"]

        for line in lines:
            kpi = line.kpi_id

            if not kpi.team_id:
                continue

            members = kpi.team_id.member_ids
            member_count = len(members)

            vals = []

            if line.allocation == "team" and member_count:
                base = line.value // member_count
                remainder = line.value % member_count

                for index, member in enumerate(members):
                    value = base

                    if index < remainder:
                        value += 1

                    vals.append({
                        "kpi_id": kpi.id,
                        "kpi_line_id": line.id,
                        "employee_id": member.id,
                        "parameter_id": line.parameter_id.id,
                        "value": value,
                    })

            else:
                for member in members:
                    vals.append({
                        "kpi_id": kpi.id,
                        "kpi_line_id": line.id,
                        "employee_id": member.id,
                        "parameter_id": line.parameter_id.id,
                        "value": line.value,
                    })

            if vals:
                EmployeeTarget.create(vals)

        return lines




    