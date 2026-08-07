from odoo import models,api,fields


class RentaAuxilioTipo(models.Model):
    _name = 'renta.auxilio.tipo'

    name = fields.Char(
        string='Nombre'
    )