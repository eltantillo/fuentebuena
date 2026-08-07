from odoo import models,api,fields


class ComplementoInheritTramite(models.Model):

    _inherit = "fleet.tramite"

    complemento_ids = fields.One2many(
        comodel_name='complemento.pago',
        inverse_name='tramite_id',
    )