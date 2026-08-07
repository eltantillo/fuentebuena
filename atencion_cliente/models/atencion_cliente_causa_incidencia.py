from odoo import fields, models, api


class AtencionClienteInteraccionStage(models.Model):
    _name = 'atencion.cliente.causa.incidencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre"
    )