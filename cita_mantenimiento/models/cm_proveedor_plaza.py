from odoo import fields,models,api


class CMProveedorPlaza(models.Model):

    _name = 'cm.proveedor.plaza'


    plaza_id = fields.Many2one(
        string='Plaza',
        comodel_name='fleet.customer.plaza',
    )
    provedoor_ids = fields.Many2many(
        comodel_name='res.partner',
        domain=[('es_proveedor','=',True)],
        string='Provedores',
    )


