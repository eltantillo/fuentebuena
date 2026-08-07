from odoo import fields,api,models

class TecnoPeticionBloqueoTipo(models.Model):
    _name = 'agenda.peticion.bloqueo.tipo'

    name = fields.Char(
        string='Nombre',
    )