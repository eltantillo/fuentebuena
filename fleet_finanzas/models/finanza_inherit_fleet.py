from odoo import fields,api,models

class FinanzaInheritFleet(models.Model):
    _inherit = 'fleet.vehicle'

    fuente_fondeo_id = fields.Many2one(
        comodel_name="fleet.finanza.fuente.fondeo",
        string="Fuente de fondeo",
        tracking=True,
    )
    linea_credito_id = fields.Many2one(
        comodel_name="fleet.finanza.linea.credito",
        string="Linead de credito",
    )
    sesionario_id = fields.Many2one(
        comodel_name="fleet.finanza.sesionario",
        string="Sesionario",
        tracking=True,
    )