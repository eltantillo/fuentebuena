from odoo import models, fields, api


class FleetContratoCancelacion(models.TransientModel):
    _name = 'fleet.contrato.cancelacion'
    _description = 'Cancelación de contrato'

    motivo_id = fields.Many2one(
        comodel_name='fleet.contrato.motivo.cancelacion',
        string='Motivo de cancelación'
    )

    def action_confirm(self):
        contrato_id = self._context.get('active_id')
        contrato = self.env['fleet.vehicle.log.contract'].browse(contrato_id)
        contrato.write({
            'motivo_cancelacion_id': self.motivo_id,
        })