from odoo import models, fields, api

class FleetCustomerSubEtapa(models.Model):
    _name = 'fleet.customer.sub.etapa'
    _description = 'Módulo personalizado para registrar las sub etapas para los vehículos'

    name = fields.Char(
        string='Nombre de sub etapa',
    )
    active = fields.Boolean(
        string='Activa',
        default=True
    )