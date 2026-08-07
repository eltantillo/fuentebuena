from odoo import fields, api, models

class FleetTecnoNoGps(models.Model):
    _name = 'fleet.tecno.no.gps'
    _inherit = ['mail.thread','mail.activity.mixin']

    id_gps = fields.Char(
        string='ID GPS'
    )
    vin_sn = fields.Char(
        string='VIN',
        tracking=True,
    )