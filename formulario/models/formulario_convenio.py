from odoo import models, fields, api


class formulario_convenio(models.Model):
    _name = 'formulario.convenio'
    _description = 'formulario.convenio'

    name = fields.Char(
        string='Nombre'
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    celula_id = fields.Many2one(
        comodel_name='formulario.celula',
        string='Célula',
    )
    region_id = fields.Many2one(
        comodel_name='formulario.region',
        string='Region',
    )
    estatus = fields.Selection([
        ('activo','Activo'),
        ('suspendido', 'Suspendido'),
    ], string='Estatus',)
