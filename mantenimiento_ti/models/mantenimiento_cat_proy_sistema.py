from odoo import models,fields,api


class MantenimientoCatProySistema(models.Model):
    _name = 'mantenimiento.cat.proy.sistema'

    name = fields.Char(
        string="Nombre"
    )
    proveedor_id = fields.Many2one(
        string="Proveedor",
        comodel_name='mantenimiento.ti.proveedor'
    )