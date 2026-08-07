from odoo import models,api,fields


class ComplementoInheritPoliza(models.Model):

    _inherit = "fleet.poliza"

    complemento_ids = fields.One2many(
        comodel_name='complemento.pago',
        inverse_name='poliza_id',
    )