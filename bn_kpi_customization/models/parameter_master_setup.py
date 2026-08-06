from odoo import models, fields, api


class ParameterMasterSetup(models.Model):
    _name = 'parameter.master.setup'
    _description = "Parameter Master Setup"


    name = fields.Char(string = 'Name')

    type = fields.Selection(
        [
            ("manual", "Manual"),
            ("auto", "Auto"),
        ],
        string="Type",
        required=True,
    )

    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        help="Select the Odoo model to fetch data from.",
    )

    calculation = fields.Selection([
        ("count", "Count"),
        ("sum", "Sum"),
    ])

    field_value = fields.Many2one(
        "ir.model.fields",
        string="Value Field",
        domain="[('model_id', '=', model_id)]"
    )

    domain = fields.Text(
        string="Domain",
        help="Write a complete Odoo domain. Example:\n"
             "[('create_uid','=',rec.employee_id.id),"
             "('create_date','>=',datetime.combine(rec.kpi_id.from_date,time.min)),"
             "('create_date','<=',datetime.combine(rec.kpi_id.to_date,time.max)),"
             "('state','=','sale')]"
    )