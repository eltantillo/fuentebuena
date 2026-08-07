from odoo import fields,models,api


class FleetFinanzaAsignar(models.TransientModel):
    _name = 'fleet.finanza.asignar'


    vehicle_ids = fields.Many2many(
        comodel_name='fleet.vehicle',
        string='Vehiculos',
    )
    sesionario_id = fields.Many2one(
        comodel_name='fleet.finanza.sesionario',
        string='Sesionario',
    )
    fuente_fodeo_id = fields.Many2one(
        comodel_name='fleet.finanza.fuente.fondeo',
        string='Fuente de fodeo',
    )

    def action_confirm(self):
        self.vehicle_ids.write({
            'sesionario_id': self.sesionario_id.id,
            'fuente_fondeo_id': self.fuente_fodeo_id
        })
