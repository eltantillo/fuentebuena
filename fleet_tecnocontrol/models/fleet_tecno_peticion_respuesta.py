from odoo import fields, api, models

class FleetTecnoPeticionRespuesta(models.Model):
    _name = 'fleet.tecno.peticion.respuesta'

    name = fields.Char(
        string="Nombre",
    )