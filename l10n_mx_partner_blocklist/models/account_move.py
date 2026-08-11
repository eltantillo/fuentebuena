from odoo import models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        vat_list = self.commercial_partner_id.mapped("vat")
        if vat_list and self.env["res.partner.blacklist"].search([("vat", "in", vat_list)], limit=1):
            raise ValidationError(
                self.env._(
                    "Some partner is on the block list provided by the SAT. To avoid this error you "
                    "can go to the partner block list and remove that partner."
                )
            )
        return super().action_post()
