from odoo import models,fields,api


class MantenimientoGastoTiEtapa(models.Model):
    _name = 'mantenimiento.gasto.ti.etapa'

    name = fields.Char(
        string="Nombre"
    )