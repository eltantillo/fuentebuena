from odoo import models, fields, api

from datetime import datetime


class FleetCustomerModelo(models.Model):
    _inherit = 'fleet.vehicle.model'

    prefijo = fields.Char(
        string='Prefijo'
    )

    def _get_year_selection(self):
        current_year = datetime.now().year
        return [(str(i), i) for i in range(1970, current_year + 2)]
