from odoo import fields,models,api


class AtencionClienteResponsabilidad(models.Model):
    _name = 'atencion.cliente.responsabilidad'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Responsabilidad'
    )
