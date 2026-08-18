from odoo import fields,models,api


class GestionCaidoNotificacion(models.Model):

    _name = 'gestion.caido.notificacion'

    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
    )
    empleado_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Empleados',
    )