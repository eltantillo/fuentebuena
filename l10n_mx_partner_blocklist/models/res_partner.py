from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_mx_in_blocklist = fields.Selection(
        [
            ("normal", "No information"),
            ("done", "Ok"),
            ("blocked", "Blocked"),
        ],
        string="Partner SAT State",
        help="This field is set as 'Blocked' if the partner is in the "
        "Definitive list published buy the SAT, 'Ok' if the partner is not in "
        "the list or 'No information' if the partner has not being consulted "
        "yet.",
        default="normal",
        copy=False,
        compute="_compute_l10n_mx_in_blocklist",
        store=True,
    )

    @api.onchange("l10n_mx_in_blocklist")
    def _onchange_l10n_mx_in_blocklist(self):
        if self.l10n_mx_in_blocklist == "blocked":
            return {
                "warning": {
                    "title": self.env._("Warning: VAT value"),
                    "message": self.env._(
                        "This partner appears in the SAT block list. It is recommended to avoid commercial "
                        "transactions with this customer."
                    ),
                }
            }

    @api.depends("vat")
    def _compute_l10n_mx_in_blocklist(self):
        for partner in self:
            partner_blacklist = self.env["res.partner.blacklist"].search([("vat", "=", partner.vat)], limit=1)
            if partner_blacklist:
                partner.l10n_mx_in_blocklist = "blocked"
            else:
                partner.l10n_mx_in_blocklist = "done"
