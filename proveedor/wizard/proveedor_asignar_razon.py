from odoo import fields, api, models


class ProveedorAsignarRazon(models.TransientModel):
    _name = 'proveedor.asignar.razon'

    razon_social_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Razones sociales',
    )

    def action_confirm(self):
        for record in self:
            partner = record.env['res.partner'].browse(self.env.context.get('active_id'))
            partner.write({
                'razones_sociales_ids': record.razon_social_ids,
            })