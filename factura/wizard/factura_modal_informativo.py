from odoo import fields,models


class FacturaModalInformativo(models.TransientModel):
    _name = 'factura.modal.informativo'
    _description = 'Ventana para mostrar información al usuario'

    mensaje = fields.Char(
        string='Mensaje',
    )

    def action_close(self):
        return {'type': 'ir.actions.act_window_close',}