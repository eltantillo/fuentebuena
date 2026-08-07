from odoo import models,fields


class MedioContacto(models.Model):
    _name = 'medio.contacto'
    _description = 'Medio Contacto'

    name = fields.Char(
        string='Nombre',
        required=True
    )