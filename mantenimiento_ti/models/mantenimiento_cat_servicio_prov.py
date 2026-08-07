from odoo import models,fields,api


class MantenimientoCatServicioProv(models.Model):
    _name = 'mantenimiento.cat.servicio.prov'

    name = fields.Char(
        string="Nombre"
    )