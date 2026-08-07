from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FleetMantenimientServicioTipo(models.Model):
    _name = 'fleet.mantenimiento.servicio.tipo'
    _description = 'Configuración de mantenimiento'

    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    mantenimiento_tipo_id = fields.Many2one(
        comodel_name='fleet.mantenimiento.tipo',
        string='Mantenimientos'
    )
    serivicio_ids = fields.Many2many(
        comodel_name='fleet.mantenimiento.servicio',
        relation='mantenimiento_servicio_tipo_rel',
        string='Servicios'
    )
    valor = fields.Float(
        string='Valor'
    )
    unidad_medida_id = fields.Many2one(
        comodel_name='fleet.mantenimiento.unidad.medida',
        string='Unidad de medida'
    )
    es_primer_mantenimiento = fields.Boolean(
        string='Es primer mantenimiento'
    )
    categoria_id = fields.Many2one(
        string='Categoria',
        comodel_name='fleet.mantenimiento.categoria',
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.constrains('es_primer_mantenimiento')
    def _check_es_primer_mantenimiento(self):
        num_mant = self.search_count([('es_primer_mantenimiento', '=', True)])
        if num_mant > 1:
            raise ValidationError('Solo se puede tener un mantenimiento como primer mantenimiento')

    @api.depends('valor',)
    def _compute_name(self):
        for record in self:
            record.name = f"{str(int(record.valor))} {record.unidad_medida_id.name}"