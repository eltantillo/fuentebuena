from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FleetAdecuacionFleet(models.Model):
    _inherit = 'fleet.vehicle'

    adecuacion_ids = fields.One2many(
        comodel_name='fleet.adecuacion',
        inverse_name='vehiculo_id',
        string='Adecuaciones'
    )
    tiene_gps = fields.Boolean(
        string='Tiene GPS',
    )
    proveedor_gps = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor de GPS',
        compute='_compute_proveedor_gps',
        store=True,
    )
    proveedor_gnv = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor de GNV',
        compute='_compute_proveedor_gnv',
        store=True,
    )



    def _compute_proveedor_gnv(self):
        for record in self:
            adecuacion_gnv = self.env['fleet.adecuacion.catalogo'].search([('name','=', 'GNV')], limit=1)
            existe_gnv = self.env['fleet.adecuacion'].search([('adecuacion_id','=', adecuacion_gnv.id),
                                                              ('vehiculo_id','=', record.id)], limit=1, order='id desc')
            if existe_gnv:
                record.proveedor_gnv = existe_gnv.proveedor_id.id
            else:
                record.proveedor_gnv = False

    def _compute_proveedor_gps(self):
        for record in self:
            adecuacion_gps = self.env['fleet.adecuacion.catalogo'].search([('name','=', 'GPS')], limit=1)
            existe_gps = self.env['fleet.adecuacion'].search([('adecuacion_id','=', adecuacion_gps.id),
                                                              ('vehiculo_id','=', record.id)], limit=1, order='id desc')
            if existe_gps:
                record.proveedor_gps = existe_gps.proveedor_id.id
                record.tiene_gps = True
            else:
                record.proveedor_gps = False
                record.tiene_gps = False

    def write(self, vals):
        res = super().write(vals)
        if 'state_id' in vals:
            etapa_disponible = self.env['fleet.vehicle.state'].search([('es_estapa_disponible', '=', True)], limit=1)
            if vals['state_id'] == etapa_disponible.id:
                ade_gps = self.env['fleet.adecuacion.catalogo'].search([('name','=','GPS')], limit=1)
                ade_gnv = self.env['fleet.adecuacion.catalogo'].search([('name','=','GNV')], limit=1)
                adecuaciones = self.env['fleet.adecuacion'].search([
                    ('vehiculo_id', '=', self.id),
                    ('adecuacion_id', 'in', [ade_gps.id, ade_gnv.id])
                ])
                tipos = adecuaciones.mapped('adecuacion_id.id')
                if ade_gps.id not in tipos:
                    raise ValidationError(
                        "El vehículo debe contar con una adecuación de tipo 'GPS' para pasar a Disponible."
                    )
                if self.es_gnv:
                    if ade_gnv.id not in tipos:
                        raise ValidationError(
                            "El vehículo debe contar con una adecuación de tipo 'GNV' para pasar a Disponible."
                        )