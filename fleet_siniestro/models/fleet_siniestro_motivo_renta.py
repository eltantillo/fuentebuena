from odoo import fields,models, api

class FleetSiniestroMotivoRenta(models.Model):
    _name = 'fleet.siniestro.motivo.renta'

    name = fields.Char(
        string='Nombre'
    )