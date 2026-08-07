from odoo import fields,models,api

class FormularioProspectoAnimador(models.Model):
    _name = 'formulario.prospecto.animador'
    _order = 'id desc'


    nombre = fields.Char(
        string="Nombre",
    )
    apellido = fields.Char(
        string="Apellido",
    )
    rfc = fields.Char(
        string="RFC",
    )
    celular = fields.Char(
        string="Celular",
    )
    confirmacion_celular = fields.Char(
        string="Confirmacion celular",
    )
    convenio_id = fields.Many2one(
        comodel_name='formulario.convenio',
        string='Convenio',
    )
    uso_datos = fields.Boolean(
        string='Acepto terminos y condiciones',
    )
    celula_id = fields.Many2one(
        comodel_name='formulario.celula',
        string='Celula',
        compute='_compute_celula_id',
        store=True,
    )
    region_id = fields.Many2one(
        comodel_name='formulario.region',
        string='Región',
        compute='_compute_celula_id',
        store=True,
    )

    @api.depends('convenio_id')
    def _compute_celula_id(self):
        for record in self:
            record.celula_id = record.convenio_id.celula_id.id
            record.region_id = record.convenio_id.region_id.id