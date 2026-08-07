from odoo import  fields, models, api


class AtencionCLienteMedioContacto(models.Model):
    _name = 'atencion.cliente.medio.contacto'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre"
    )