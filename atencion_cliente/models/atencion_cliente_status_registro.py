from odoo import fields, models, api


class AtencionClienteStatusRegistro(models.Model):
    _name = 'atencion.cliente.status.registro'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre'
    )