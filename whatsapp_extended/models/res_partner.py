from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    otp_text = fields.Char(string="OTP Text")
    otp_time = fields.Datetime(string='OTP Time')