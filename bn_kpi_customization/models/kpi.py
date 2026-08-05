from odoo import models, fields, api, _
from datetime import date

class KPI(models.Model):
    _name = "kpi.kpi"
    _description = "KPI"

    name = fields.Char(
        string="Name",
        required=True,
    )

    team_id = fields.Many2one(
        "crm.team",
        string="Team",
    )

    member_ids = fields.Many2many(
        "res.users",
        related="team_id.member_ids",
        string="Members",
        readonly=True,
    )

    from_date = fields.Date(string="From Date", default=fields.Date.today)
    to_date = fields.Date(string="To Date")

    line_ids = fields.One2many(
        "kpi.kpi.line",
        "kpi_id",
        string="Target",
    )

    employee_target_ids = fields.One2many(
        "employee.target",
        "kpi_id",
        string="Employee Targets",
    )

    @api.onchange("team_id")
    def _onchange_team_id(self):
 
        self.employee_target_ids = [(5, 0, 0)]

        if not self.team_id:
            return

        commands = []
        member_count = len(self.team_id.member_ids)

       
        for line in self.line_ids:
            if line.allocation == "team" and member_count:
                base_value = line.value // member_count
                remainder = line.value % member_count

                for index, member in enumerate(self.team_id.member_ids):
                    target_value = base_value

                    if index < remainder:
                        target_value += 1

                    commands.append((0, 0, {
                        "employee_id": member.id,
                        "parameter_id": line.parameter_id.id,
                        "value": target_value,
                        "kpi_line_id": line.id,
                    }))
            else:
                for member in self.team_id.member_ids:
                    commands.append((0, 0, {
                        "employee_id": member.id,
                        "parameter_id": line.parameter_id.id,
                        "value": line.value,
                        "kpi_line_id": line.id,
                    }))

        self.employee_target_ids = commands


    def _sync_employee_targets(self):
        EmployeeTarget = self.env["employee.target"]

        for kpi in self:
            if not kpi.team_id:
                continue

            member_ids = kpi.team_id.member_ids.ids
            existing_ids = kpi.employee_target_ids.mapped("employee_id").ids

            member_count = len(member_ids)

            # Create for new members
            new_ids = set(member_ids) - set(existing_ids)


            member_map = {member.id: index for index, member in enumerate(kpi.team_id.member_ids)}

            for user_id in new_ids:
                vals = []
                index = member_map[user_id]

                for line in kpi.line_ids:
                    if line.allocation == "team" and member_count:
                        base_value = line.value // member_count
                        remainder = line.value % member_count

                        target_value = base_value
                        if index < remainder:
                            target_value += 1
                    else:
                        target_value = line.value

                    vals.append({
                        "kpi_id": kpi.id,
                        "employee_id": user_id,
                        "parameter_id": line.parameter_id.id,
                        "value": target_value,
                        "kpi_line_id": line.id,
                    })

                EmployeeTarget.create(vals)

            # Delete removed members
            removed_ids = set(existing_ids) - set(member_ids)

            if removed_ids:
                kpi.employee_target_ids.filtered(
                    lambda t: t.employee_id.id in removed_ids
                ).unlink()

    def _redistribute_team_targets(self):
        for kpi in self:
            members = kpi.team_id.member_ids

            for line in kpi.line_ids:
                if line.allocation != "team":
                    continue

                targets = kpi.employee_target_ids.filtered(
                    lambda t: t.kpi_line_id == line
                )

                member_count = len(targets)

                if not member_count:
                    continue

                base = line.value // member_count
                remainder = line.value % member_count

                for index, target in enumerate(targets):
                    value = base

                    if index < remainder:
                        value += 1

                    target.with_context(skip_kpi_sync=True).value = value
        
    def write(self, vals):
        res = super().write(vals)

        if "team_id" in vals:
            self._sync_employee_targets()

        return res


    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_employee_targets()
        return records


   