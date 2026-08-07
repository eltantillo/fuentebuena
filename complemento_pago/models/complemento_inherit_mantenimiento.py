from odoo import fields,models,api


class ComplementoInheritMantenimiento(models.Model):
    _inherit = "fleet.mantenimiento"

    complemento_ids = fields.One2many(
        comodel_name='complemento.pago',
        inverse_name='mantenimiento_id',
    )