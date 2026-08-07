from odoo import fields, models, api


class ActualizarOdometroEtapa(models.Model):
    _name = 'actualizar.odometro.etapa'

    name = fields.Char(
        string = 'Nombre',
    )