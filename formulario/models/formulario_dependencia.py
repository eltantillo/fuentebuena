from odoo import fields, models, api


class FormularioDependencia(models.Model):
    _name = 'formulario.dependencia'
    _description = 'Formulario Dependencia'

    nombre_completo = fields.Char(
        string="Nombre completo",
    )
    numero_telefono = fields.Char(
        string="Número de teléfono",
    )
    correo_electronico = fields.Char(
        string="Correo electrónico",
    )
    dependencia_ayuntamiento = fields.Char(
        string="Dependencia o Ayuntamiento",
    )
    puesto = fields.Char(
        string="Puesto",
    )
    categoria_empleado_id = fields.Many2one(
        comodel_name="puesto.ocupado",
        string="Categoría de empleado",
    )
    pertenece_sindicato = fields.Char(
        string="¿Perteneces a un sindicato?",
    )
    medio_contacto_institucional = fields.Char(
        string="Medio de contacto institucional con tu dependencia",
    )
    nombre_contacto = fields.Char(
        string="Nombre del contacto",
    )
    puesto_contacto = fields.Char(
        string="Puesto del contacto",
    )
    nombre_presidente_municipal = fields.Char(
        string="Nombre del presidente municipal",
    )