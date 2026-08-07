from odoo import fields, models, api


class AtencionClienteInteraccionStage(models.Model):
    _name = 'atencion.cliente.interaccion.stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre"
    )