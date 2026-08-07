from odoo import models, fields, api


class FormularioEmpresaConfig(models.Model):
    _name = 'formulario.empresa.config'
    _description = 'Empresas Formularios'

    name = fields.Char(
        string='Empresa',
        required=True
    )
    slug = fields.Char(
        string='Slug URL',
        required=True
    )
    logo = fields.Image(
        string='Logo'
    )
    color_primario = fields.Char(
        string='Color Primario',
        default='#875A7B'
    )
    active = fields.Boolean(
        default=True
    )