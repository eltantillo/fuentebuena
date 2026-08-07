from odoo import fields, models, api


class FleetSiniestroEtapa(models.Model):
    _name = "fleet.siniestro.etapa"
    _description = "Etapa de siniestro"
    _order = 'sequence asc'

    name = fields.Char(
        string="Nombre"
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    sequence = fields.Integer(
        string="Sequence",
    )