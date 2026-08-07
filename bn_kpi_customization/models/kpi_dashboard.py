from odoo import models


class KPIDashboard(models.AbstractModel):
    _name = "kpi.dashboard"
    _description = "KPI Dashboard"

    def get_dashboard_data(self):
        return {
            "message": "Dashboard Connected",
            "cards": {
                "kpis": 10,
                "teams": 5,
            },
        }