from odoo import fields,api,models


class FormularioProspectoColaborador(models.Model):
    _name = 'formulario.prospecto.colaborador'
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
    nombre_gerente = fields.Char(
        string="Nombre de gerente",
    )
    puesto_id = fields.Many2one(
        string="Puesto",
        comodel_name='formulario.puesto.trabajo',
    )
    convenio_id = fields.Many2one(
        comodel_name='formulario.convenio',
        string='Convenio',
    )
    celula_id = fields.Many2one(
        comodel_name='formulario.celula',
        string='Celula',
        compute='_compute_celula_id',
    )
    region_id = fields.Many2one(
        comodel_name='formulario.region',
        string='Región',
        compute='_compute_celula_id',
    )
    actividad_id = fields.Many2one(
        comodel_name='formulario.actividad',
        string='Actividad',
    )

    @api.depends('convenio_id')
    def _compute_celula_id(self):
        for record in self:
            record.celula_id = record.convenio_id.celula_id.id
            record.region_id = record.convenio_id.region_id.id