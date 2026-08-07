from odoo import fields, models, api


class AtencionClienteTipoSolicitud(models.Model):
    _name = 'atencion.cliente.tipo.solicitud'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre"
    )