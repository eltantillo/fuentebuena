from odoo import models, fields, api

class FleetCustomerCategoriaEtapa(models.Model):
    _name = 'fleet.customer.categoria.etapa'
    _description = 'Módulo personalizado para registrar las categorias de etapas para los vehículos'

    name = fields.Char(
        string='Nombre de categoria',
    )