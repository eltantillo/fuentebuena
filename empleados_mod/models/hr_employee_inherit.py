from odoo import  fields, models


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    numero_empleado = fields.Char(
        string='Número de empleado',
        private=False
    )
    fecha_ingreso = fields.Date(
        string='Fecha de ingreso',
        private=False
    )
    id_empleado = fields.Integer(
        string='ID de empleado',
    )
    # plaza_id = fields.Many2one(
    #     string='Plaza',
    #     comodel_name='fleet.customer.plaza',
    #     private=False
    # )
    # flotilla_ids = fields.Many2many(
    #     string='Flotilla',
    #     comodel_name='fleet.customer.flotilla',
    #     private=False
    # )
    #
    #
    #
    # def recalcular(self):
    #     emps = self.env['hr.employee'].search([])
    #     emps.write({'active': False})
    #     emps.write({'active': True})
