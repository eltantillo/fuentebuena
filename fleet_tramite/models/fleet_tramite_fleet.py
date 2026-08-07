from odoo import fields, models, api
from odoo.exceptions import ValidationError

class FleetTramiteFleet(models.Model):
    _inherit = "fleet.vehicle"

    tramite_ids = fields.One2many(
        comodel_name='fleet.tramite',
        inverse_name='vehiculo_id',
        string='Tramites'
    )

    def write(self, vals):
        res = super().write(vals)
        if 'state_id' in vals:
            etapa_disponible = self.env['fleet.vehicle.state'].search([('es_estapa_disponible', '=', True)], limit=1)
            if vals['state_id'] == etapa_disponible.id:
                tarjeta = self.env['fleet.tramite.tipo'].search([('name', '=', 'Tarjeta de circulación')], limit=1)
                emplacamiento = self.env['fleet.tramite.tipo'].search([('name', '=', 'Emplacamiento')], limit=1)
                tramites = self.env['fleet.tramite'].search([
                    ('vehiculo_id', '=', self.id),
                    ('tipo_tramite_id', 'in', [tarjeta.id, emplacamiento.id])
                ])
                tipos = tramites.mapped('tipo_tramite_id.id')
                if tarjeta.id not in tipos or emplacamiento.id not in tipos:
                    raise ValidationError(
                        "El vehículo debe contar con un trámite de 'Tarjeta de circulación' y uno de 'Emplacamiento' para pasar a Disponible."
                    )
        return res