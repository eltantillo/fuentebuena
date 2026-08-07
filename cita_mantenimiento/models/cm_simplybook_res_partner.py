from odoo import fields,models,api


class CMSimplyBookRespartner(models.Model):
    _inherit = "res.partner"


    simplybook_cliente_id = fields.Integer(
        string='Cliente id simplybook',
    )
    simplybook_proveedor_id = fields.Integer(
        string='Proveedor id simplybook',
    )