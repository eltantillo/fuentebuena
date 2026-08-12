from odoo import fields,models,api


class GestionCaidoNotificacion(models.Model):

    _name = 'gestion.caido.notificacion'

    plaza_ids = fields.Many2many(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
    )
    correo = fields.Char(
        string='Correo'
    )