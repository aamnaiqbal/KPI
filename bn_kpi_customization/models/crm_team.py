from odoo import models, fields, api
from odoo.exceptions import UserError

class CrmTeam(models.Model):
    _inherit = "crm.team"

    def write(self, vals):
        res = super().write(vals)

        if "member_ids" in vals:
            kpis = self.env["kpi.kpi"].search([
                ("team_id", "in", self.ids)
            ])
            kpis._sync_employee_targets()
            kpis._redistribute_team_targets()

        return res