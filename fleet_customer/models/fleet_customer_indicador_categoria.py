from odoo import models, fields, api

class FleetCustomerIndicadorCategoria(models.Model):
    _name = 'fleet.customer.indicador.categoria'
    _description = 'Módulo personalizado para registrar las categorias para los indicadores'

    name = fields.Char(
        string='Nombre de indicador categoria',
    )