from odoo import fields,models,api


class PromesaPEcvPromesaPago(models.Model):
    _name = 'promesa.p.ecv.promesa.pago'

    name = fields.Char(
        string='Nombre',
    )