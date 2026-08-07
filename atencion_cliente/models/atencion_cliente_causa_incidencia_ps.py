from odoo import fields, models, api


class AtencionClienteInteraccionStagePs(models.Model):
    _name = 'atencion.cliente.causa.incidencia.ps'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre"
    )