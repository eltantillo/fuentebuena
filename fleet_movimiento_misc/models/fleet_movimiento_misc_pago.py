from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetMovimientoMiscPagos(models.Model):
    _name = 'fleet.movimiento.misc.pago'
    _description = 'Fleet Movimiento Misc Pagos'
    _rec_name = 'rec_name'

    movimiento_id = fields.Many2one(
        comodel_name='fleet.movimiento.misc',
        string='Movimiento',
    )
    monto = fields.Float(
        string='Monto'
    )
    monto_pendiente = fields.Float(
        string='Monto Pendiente',
        related='movimiento_id.importe_pendiente'
    )
    rec_name = fields.Char(
        string='Nombre',
        compute='_compute_rec_name',
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.depends('movimiento_id', 'monto')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.movimiento_id.rec_name}-{record.monto}"

    @api.model
    def create(self, vals):
        if vals.get('movimiento_id') and vals.get('monto'):
            movimiento = self.env['fleet.movimiento.misc'].browse(vals['movimiento_id'])
            importe_pendiente = movimiento.importe_pendiente
            if importe_pendiente < vals['monto']:
                raise ValidationError('El monto a pagar no puede ser mayor al monto pendiente.')
            else:
                importe_pagado = movimiento.importe_pagado
                nuevo_importe_pagado = importe_pagado + vals['monto']
                movimiento.write({
                    'importe_pagado': nuevo_importe_pagado,
                    'fecha_ultimo_pago': fields.Date.today()
                })
        res = super(FleetMovimientoMiscPagos, self).create(vals)
        return res