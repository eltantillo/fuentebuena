from odoo import fields,models,api
from odoo.exceptions import ValidationError

class CMTallerAutorizado(models.Model):
    _name='cm.taller.autorizado'

    brand_id = fields.Many2one(
        string='Marca autorizada',
        comodel_name='fleet.vehicle.model.brand',
    )
    plaza_id = fields.Many2one(
        string='Plaza',
        comodel_name='fleet.customer.plaza',
    )
    taller_autorizado_ids = fields.Many2many(
        string='Talleres Autorizados',
        comodel_name='res.partner',
        domain=[('es_proveedor', '=',True)]
    )
    km_permitido = fields.Integer(
        string='KM Pemitido'
    )


    @api.constrains('plaza_id','brand_id')
    def _check_plaza_id(self):
        num_registros = self.search_count([('plaza_id', '=',self.plaza_id.id),('brand_id', '=', self.brand_id.id)])
        if num_registros > 1:
            raise ValidationError('No se puede utilizar la misma plaza y marca en dos registros')
