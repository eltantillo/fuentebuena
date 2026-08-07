from odoo import models, fields, api


class FleetMovimientoPago(models.TransientModel):
    _name = 'fleet.movimiento.pago'
    _description = 'Fleet Movimiento Pago'

    movimiento_id = fields.Many2one(
        comodel_name='fleet.movimiento.misc',
        string='Movimiento',
    )
    monto = fields.Float(
        string='Monto a pagar'
    )
    monto_pendiente = fields.Float(
        string='Monto Pendiente',
        related='movimiento_id.importe_pendiente'
    )


    def action_confirm(self):
        self.env['fleet.movimiento.misc.pago'].create({
            'movimiento_id': self.movimiento_id.id,
            'monto': self.monto
        })