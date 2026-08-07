from odoo import fields,models,api


class FormularioEMpresa(models.Model):
    _name = 'formulario.empresa'
    _order = 'id desc'


    nombre_completo = fields.Char(
        string='Nombre completo',
    )
    numero_telefono = fields.Char(
        string='Numero telefono',
    )
    correo  = fields.Char(
        string='Correo',
    )
    empresa_id = fields.Many2one(
        string='Empresa',
        comodel_name='formulario.empresa.config',
    )
    rfc = fields.Char(
        string='RFC',
    )
    autorizacion_datos = fields.Boolean(
        string='Autorizacion Datos',
    )