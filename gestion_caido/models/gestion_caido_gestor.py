from odoo import fields,models,api


class GestionCaidoGestor(models.Model):

    _name = 'gestion.caido.gestor'

    plaza_id = fields.Many2one(
        string="Plaza",
        comodel_name='fleet.customer.plaza',
    )
    hr_employee_id = fields.Many2one(
        string="Empleado",
        comodel_name='hr.employee',
    )
    token_acces = fields.Char(
        string="Token Access",
    )