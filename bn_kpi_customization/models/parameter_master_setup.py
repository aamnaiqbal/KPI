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