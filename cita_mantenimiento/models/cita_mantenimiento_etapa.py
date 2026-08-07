from odoo import fields,models,api


class CitaMantenimientoEtapa(models.Model):
    _name = 'cita.mantenimiento.etapa'

    name = fields.Char(
        string='Nombre',
    )