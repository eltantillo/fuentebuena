from odoo import  fields,models,api


class FleetSiniestroTipoAseguradora(models.Model):
    _name = 'fleet.siniestro.tipo.aseguradora'

    name = fields.Char(
        string='Nombre',
    )