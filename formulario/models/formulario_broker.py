from odoo import fields,models,api


class FormularioBroker(models.Model):
    _name = 'formulario.broker'
    _description = 'Formulario de Broker'

    nombre = fields.Char(
        string="Nombre completo quién refiere"
    )
    telefono = fields.Char(
        string="Número de teléfono"
    )
    correo = fields.Char(
        string="Correo electrónico",
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    municipio_id = fields.Many2one(
        comodel_name='municipio',
        string='Municipio',
    )
    num_empleado = fields.Selection(
        selection=[
            ('mas_de_100', '100-200 empleados'),
            ('200_300','200-300 empleados'),
            ('301_500','301-500 empleados'),
            ('500_1000','501-1000 empleados'),
            ('mas_de_1000','Más de 1000 empleados'),
        ],
        string='Número de trabajadores',
    )
    acepto_uso_datos = fields.Boolean(
        string='Acepto uso de datos personales',
    )
