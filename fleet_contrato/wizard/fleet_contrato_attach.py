from odoo import models, fields, api


class FleetContratoAttach(models.TransientModel):
    _name = 'fleet.contrato.attach'
    _description = 'Attach de contrato'

    archivo = fields.Binary(
        string='Archivo',
    )

    def action_confirm(self):
        contrato_id = self._context.get('active_id')
        contrato = self.env['fleet.vehicle.log.contract'].browse(contrato_id)
        contrato.sudo().write({
            'attach_contrato': self.archivo,
        })