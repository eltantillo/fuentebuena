from odoo import models,api,fields


class ComplementoInheritAdecuacion(models.Model):

    _inherit = "fleet.adecuacion"

    complemento_ids = fields.One2many(
        comodel_name='complemento.pago',
        inverse_name='adecuacion_id',
    )