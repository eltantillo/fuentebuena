from odoo import models, fields, api


class FleetOdometro(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    _rec_name = 'rec_name'

    vin_sn = fields.Char(
        string='VIN SN',
        compute='_compute_vin_sn',
        store=True,
    )
    rec_name = fields.Char(
        string='Rec Name',
        compute='_compute_rec_name',
    )

    @api.depends('vehicle_id','date')
    def _compute_rec_name(self):
        for odometro in self:
            odometro.rec_name = f"{odometro.vehicle_id.model_id.name}/{odometro.vehicle_id.vin_sn}/{odometro.date}"

    @api.model
    def create(self, vals):
        for val in vals:
            if val.get('vehicle_id'):
                vehiculo = self.env['fleet.vehicle'].browse(val['vehicle_id'])
                val['vin_sn'] = vehiculo.vin_sn
                vehiculo.write({
                    'odometro_mod': val['value']
                })
        res = super(FleetOdometro, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        if vals.get('vehicle_id'):
            vehiculo = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
            vals['vin_sn'] = vehiculo.vin_sn
        res = super(FleetOdometro, self).write(vals)
        return res

    @api.depends('vehicle_id')
    def _compute_vin_sn(self):
        for record in self:
            record.vin_sn = record.vehicle_id.vin_sn