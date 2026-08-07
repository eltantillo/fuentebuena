from odoo import models,fields,api


class MantenimientoPreventivoEtapa(models.Model):
    _name = 'mantenimiento.preventivo.etapa'


    name = fields.Char(
        string="Nombre"
    )