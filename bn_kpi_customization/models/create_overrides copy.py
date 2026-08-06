from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)

        EmployeeTarget = self.env["employee.target"]

        for order in orders:
            EmployeeTarget._refresh_auto_targets(order)

        return orders

    class ResPartner(models.Model):
        _inherit = "res.partner"

        @api.model_create_multi
        def create(self, vals_list):
            partners = super().create(vals_list)

            EmployeeTarget = self.env["employee.target"]

            for partner in partners:
                EmployeeTarget._refresh_auto_targets(partner)

            return partners

    

    class CrmLead(models.Model):
        _inherit = "crm.lead"

        @api.model_create_multi
        def create(self, vals_list):
            leads = super().create(vals_list)

            EmployeeTarget = self.env["employee.target"]

            for lead in leads:
                EmployeeTarget._refresh_auto_targets(lead)

            return leads


    class AccountPayment(models.Model):
        _inherit = "account.payment"

        @api.model_create_multi
        def create(self, vals_list):
            payments = super().create(vals_list)

            EmployeeTarget = self.env["employee.target"]

            for payment in payments:
                EmployeeTarget._refresh_auto_targets(payment)

            return payments


    
    class HrAttendance(models.Model):
        _inherit = "hr.attendance"

        @api.model_create_multi
        def create(self, vals_list):
            attendances = super().create(vals_list)

            EmployeeTarget = self.env["employee.target"]

            for attendance in attendances:
                EmployeeTarget._refresh_auto_targets(attendance)

            return attendances

        def write(self, vals):
            res = super().write(vals)

            EmployeeTarget = self.env["employee.target"]

            for attendance in self:
                EmployeeTarget._refresh_auto_targets(attendance)

            return res