from odoo import fields,models,api


class PromesaPRol(models.Model):
    _name = 'promesa.p.rol'

    name = fields.Char(
        string='Rol',
    )
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Empleados',
    )

