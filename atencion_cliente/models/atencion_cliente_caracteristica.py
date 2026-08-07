from odoo import fields,models,api

class AtencionClienteCaracteristica(models.Model):
    _name = "atencion.cliente.caracteristica"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nombre'
    )
