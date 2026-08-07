from odoo import models,fields,api


class MantenimientoCatActividad(models.Model):
    _name = 'mantenimiento.cat.actividad'

    name = fields.Char(
        string="Nombre"
    )