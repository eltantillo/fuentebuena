from odoo import models,fields,api

class FacturaModeloVin(models.Model):
    _name = 'factura.modelo.vin'
    _description = 'Modelo de coches relacionados por los digitos del VIN'

    modelo_auto = fields.Many2one(
        comodel_name='fleet.vehicle.model',
        string='Modelo',
    )
    prefijo_vin = fields.Char(
        string='Prefijo VIN',
    )


    def return_prefijos(self):
        return self.env['factura.modelo.vin'].search(['prefijo_vin'])