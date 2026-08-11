import re
from odoo import models, fields, api, _, exceptions


class AssetVendor(models.Model):
    _name = 'asset.vendor'
    _description = 'Asset Vendor'

    # Basic Information
    name = fields.Char(string="Name", required=True, help="Official registered name of the vendor company")
    address = fields.Text(string="Primary Address", help="Main business address of the vendor")
    location = fields.Char(string="Service Area", help="Geographic regions where the vendor operates or provides services")
    website = fields.Char(string="Website", help="Vendor's website URL")
    tax_id = fields.Char(string="Tax ID / VAT", help="Tax identification or VAT number")

    # Contact Information
    seller = fields.Char(string="Primary Contact", help="Name and position of the main point of contact")
    contact_phone = fields.Char(string="Contact Phone", help="Primary phone number for vendor communication")
    contact_email = fields.Char(string="Contact Email", help="Primary email address for vendor communication")

    # Service Offerings
    additional_services = fields.Boolean(string="Additional Services", help="Other relevant services offered by the vendor")
    repair_service = fields.Boolean(string="Repair Services", help="Indicates if the vendor offers repair services (Yes/No)")
    maintenance_service = fields.Boolean(string="Maintenance Services", help="Indicates if the vendor provides maintenance services (Yes/No)")

    # Rating & Notes
    rating = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Below Average'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent'),
    ], string="Rating", default='3', help="Overall vendor performance rating")
    notes = fields.Text(string="Internal Notes", help="Internal remarks about this vendor")
    active = fields.Boolean(string="Active", default=True, help="Uncheck to archive this vendor")

    # Computed
    asset_count = fields.Integer(string="Assets", compute='_compute_asset_count')
    asset_ids = fields.One2many('asset.management', 'vendor_id', string="Assets")
    maintenance_count = fields.Integer(string="Maintenance Jobs", compute='_compute_maintenance_count')

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for record in self:
            record.asset_count = len(record.asset_ids)

    def _compute_maintenance_count(self):
        Maintenance = self.env['asset.maintenance.entry']
        for record in self:
            record.maintenance_count = Maintenance.search_count([
                ('maintenance_vendor_id', '=', record.id)
            ])

    @api.constrains('contact_email')
    def _check_email(self):
        for record in self:
            if record.contact_email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', record.contact_email):
                raise exceptions.ValidationError(
                    _("Please enter a valid email address for '%s'.") % record.name)

    def action_view_assets(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assets'),
            'res_model': 'asset.management',
            'view_mode': 'list,form',
            'domain': [('vendor_id', '=', self.id)],
        }

    def action_view_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Maintenance Jobs'),
            'res_model': 'asset.maintenance.entry',
            'view_mode': 'list,form',
            'domain': [('maintenance_vendor_id', '=', self.id)],
        }
    