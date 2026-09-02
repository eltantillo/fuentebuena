import re
from odoo import models, fields, api, _, exceptions
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date


class Asset(models.Model):
    _name = 'asset.management'
    _description = 'Asset Management'

    # Basic Asset Information
    name = fields.Char(string="Asset Reference", required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    serial_number = fields.Char(string="Serial Number", copy=False,
                                help="Manufacturer serial number for unique identification")
    barcode = fields.Char(string="Barcode", copy=False, help="Barcode for asset identification and scanning")
    product_id = fields.Many2one('product.product', string="Associated Product", help="Select the product used in this asset from available options")
    asset_type_id = fields.Many2one('asset.type', string="Asset Type", help="Classification of the asset (e.g., Equipment, Vehicle, Building)")
    condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ], string="Condition", default='new', help="Current physical condition of the asset")
    department_id = fields.Many2one('hr.department', string="Department",
                                    help="Department responsible for this asset")
    responsible_user_id = fields.Many2one('res.users', string="Responsible Person",
                                          help="Person accountable for this asset")
    notes = fields.Text(string="Internal Notes", help="Internal remarks about this asset")
    # Model Type and Stock Management
    model_type = fields.Selection([
        ('single', 'Single Asset'),
        ('multiple', 'Multiple Assets')
    ], string="Model Type", default='single', required=True, 
       help="Single: Unique asset with specific tracking. Multiple: Assets with stock management")
    
    initial_stock = fields.Integer(string="Initial Stock", default=1,
                                  help="Initial quantity of this asset")
    current_stock = fields.Integer(string="Current Stock", compute='_compute_current_stock', store=True,
                                  help="Current available quantity of this asset")
    active_transfers = fields.Integer(string="Active Transfers", compute='_compute_active_transfers', store=True,
                                     help="Number of assets currently assigned to users")
    
    # Depreciation Settings
    depreciation_apply = fields.Boolean(string="Enable Depreciation", help="Check to apply depreciation calculations for this asset")
    
    # Vendor and Purchase Information
    expired_warranty_date = fields.Date(string="Expired Warranty Date")
    vendor_id = fields.Many2one('asset.vendor', string="Associated Vendor", help="Select the vendor or supplier of this asset")
    invoice_date = fields.Date(string="Invoice Date", help="Date when the asset was purchased or acquired")
    amount = fields.Float(string="Purchase Price", help="Initial cost of acquiring the asset")
    
    # Computed Financial Fields
    current_amount = fields.Float(string="Current Book Value", compute="_compute_current_amount", help="Current value of the asset after depreciation (Read-only)")
    total_depreciation_amount = fields.Float(string="Accumulated Depreciation",
                                             compute='_compute_total_depreciation_amount', store=True, help="Total depreciation applied to the asset to date (Read-only)")
    total_maintenance_amount = fields.Float(string="Total Maintenance Cost",
                                            compute='_compute_total_maintenance_amount', store=True, help="Sum of all maintenance expenses for this asset (Read-only)")
    # Asset Status 
    status = fields.Selection([
        ('assign', 'Assign'),
        ('return', 'Return'),
        ('on_hold', 'On Hold'),
        ('in_warehouse', 'In Warehouse'),
        ('repair', 'Repair'),
        ('destroyed', 'Destroyed')
    ], string="Status", default="assign")

    # Related Documents and Entries
    document_ids = fields.Many2many('ir.attachment', string="Asset Documentation", help="Upload multiple documents related to the asset (e.g., Warranty,Invoice)")
    current_location = fields.Char(string="Current Location", compute="_compute_current_location",
                                   inverse="_inverse_current_location", store=True)
    manual_location = fields.Char(string="Manual Location",
                                  help="Fallback location when no active transfer is assigned")
    tag_ids = fields.Many2many('asset.tag', string='Tags', help="Categorize assets with tags for easier filtering and organization")
    transfer_ids = fields.One2many('asset.transfer.entry', 'asset_id', string="Transfer Entries")
    maintenance_ids = fields.One2many('asset.maintenance.entry', 'asset_id', string="Maintenance Entries")
    depreciation_ids = fields.One2many('asset.depreciation.entry', 'asset_id', string="Depreciation Entries")
    
    # Additional Information
    last_depreciation_date = fields.Date(string="Last Depreciation Date", help="Last Depreciation Entry Date", readonly=True)
    transfer_count = fields.Integer(string='Asset Transfer History',
                                    compute='_compute_all_count', store=True)
    maintenance_count = fields.Integer(string='Maintenance Records',
                                       compute='_compute_all_count', store=True)
    depreciation_count = fields.Integer(string='Depreciation Count',
                                        compute='_compute_all_count', store=True)
    invoice_id = fields.Many2one('account.move', string="Associated Invoice")
    months_left = fields.Integer(string='Months Left',)
    assigned_user = fields.Char(string="Assigned User", compute='_compute_assigned_user',
                                store=True)
    assign_by = fields.Char(string="Assigned By", compute='_compute_assigned_user',
                                store=True)
    remaining_warranty = fields.Char(string="Remaining Warranty",
                                     compute="_compute_months_left", store=True)
    warranty_status = fields.Char(string='Warranty Status')
    next_maintenance_date = fields.Date(string="Next Maintenance Date",
                                         compute='_compute_next_maintenance_date', store=True,
                                         help="Estimated next maintenance date based on history")

    _barcode_unique = models.Constraint(
        'unique(barcode)',
        'Barcode must be unique! Another asset already uses this barcode.',
    )
    _serial_number_unique = models.Constraint(
        'unique(serial_number)',
        'Serial number must be unique! Another asset already has this serial number.',
    )
    _amount_positive = models.Constraint(
        'CHECK(amount >= 0)',
        'Purchase price cannot be negative.',
    )

    @api.depends('maintenance_ids', 'maintenance_ids.return_date', 'maintenance_ids.maintenance_status')
    def _compute_next_maintenance_date(self):
        for record in self:
            completed = record.maintenance_ids.filtered(
                lambda m: m.maintenance_status == 'completed' and m.return_date
            )
            if len(completed) >= 2:
                dates = sorted(completed.mapped('return_date'))
                intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
                avg_interval = sum(intervals) / len(intervals)
                record.next_maintenance_date = dates[-1] + timedelta(days=int(avg_interval))
            elif completed:
                last_date = max(completed.mapped('return_date'))
                record.next_maintenance_date = last_date + relativedelta(months=6)
            else:
                record.next_maintenance_date = False

    @api.depends('transfer_ids', 'transfer_ids.status', 'transfer_ids.stock_qty')
    def _compute_active_transfers(self):
        for record in self:
            # Count transfers that are in 'assigned' status and sum their quantities
            assigned_transfers = record.transfer_ids.filtered(lambda t: t.status == 'assigned')
            record.active_transfers = sum(assigned_transfers.mapped('stock_qty'))

    @api.depends('initial_stock', 'active_transfers')
    def _compute_current_stock(self):
        for record in self:
            record.current_stock = record.initial_stock - record.active_transfers

    # Compute methods
    @api.depends('expired_warranty_date')
    def _compute_months_left(self):
        today = fields.Date.today()
        for record in self:
            if record.expired_warranty_date:
                if record.expired_warranty_date < today:
                    record.remaining_warranty = 'Expired'
                    record.warranty_status = 'expired'

                elif record.expired_warranty_date == today:
                    record.remaining_warranty = 'Today'
                    record.warranty_status = 'danger'

                else:
                    rd = relativedelta(record.expired_warranty_date, today)
                    total_months = rd.years * 12 + rd.months + (
                                rd.days / 30)  # Approximate

                    if total_months > 6:
                        record.warranty_status = 'success'
                    elif 3 <= total_months <= 6:
                        record.warranty_status = 'warning'
                    else:
                        record.warranty_status = 'danger'
                    years = rd.years
                    months = rd.months
                    days = rd.days

                    parts = []
                    if years > 0:
                        parts = [f"{years} year{'s' if years > 1 else ''}"]
                    elif months > 0:
                        parts = [f"{months} month{'s' if months > 1 else ''}"]
                    elif days > 0:
                        parts = [f"{days} day{'s' if days > 1 else ''}"]
                    
                       
                    print("parts : ", parts)
                    record.remaining_warranty = ', '.join(parts)

            else:
                record.remaining_warranty = 'No warranty'
                record.warranty_status = 'expired'

    @api.depends('transfer_ids')
    def _compute_assigned_user(self):
        for record in self:
            # Check if there are any transfer entries
            if record.transfer_ids:
                # Retrieve the most recent transfer entry based on 'assign_date'
                last_transfer = record.transfer_ids[-1]
                if last_transfer:
                    # Get the user who assigned the asset in the last transfer
                    record.assigned_user = last_transfer.transfer_employee_id.name
                    record.assign_by = last_transfer.assign_by.id
                else:
                    record.assigned_user = ''
                    record.assign_by = ''
            else:
                # Handle the case where there are no transfer entries
                record.assigned_user = ''
                record.assign_by = ''

    @api.depends('transfer_ids.status', 'transfer_ids.assign_date', 'transfer_ids.to_location', 'transfer_ids.to_location_id', 'transfer_ids.location', 'manual_location')
    def _compute_current_location(self):
        for record in self:
            assigned = record.transfer_ids.filtered(lambda t: t.status == 'assigned')
            if assigned:
                last_transfer = assigned.sorted(key=lambda t: (t.assign_date or date.min, t.id))[-1]
                location_value = (last_transfer.to_location_id.complete_name
                                  or self._match_location_name(last_transfer.to_location)
                                  or self._match_location_name(last_transfer.location)
                                  or last_transfer.to_location
                                  or last_transfer.location
                                  or '').strip()
                record.current_location = location_value
                record.manual_location = location_value
            else:
                record.current_location = (self._match_location_name(record.manual_location) or record.manual_location or '').strip()

    def _inverse_current_location(self):
        for record in self:
            record.manual_location = (record.current_location or '').strip()

    def _match_location_name(self, name_value):
        """Resolve a location by name/complete_name and return its complete_name for display."""
        if not name_value:
            return False
        loc = self.env['asset.location'].search([
            '|',
            ('complete_name', '=ilike', name_value),
            ('name', '=ilike', name_value)
        ], limit=1)
        return loc.complete_name if loc else False

    @api.depends('transfer_ids', 'maintenance_ids', 'depreciation_ids')
    def _compute_all_count(self):
        for record in self:
            record.transfer_count = len(record.transfer_ids)
            record.maintenance_count = len(record.maintenance_ids)
            record.depreciation_count = len(record.depreciation_ids)

    @api.depends('amount',)
    def _compute_current_amount(self):
        for record in self:
            record.current_amount = record.amount - record.total_depreciation_amount

    @api.depends('depreciation_ids.depreciation_amount')
    def _compute_total_depreciation_amount(self):
        for record in self:
            record.total_depreciation_amount = sum(record.depreciation_ids.mapped('depreciation_amount'))

    @api.depends('maintenance_ids.maintenance_amount')
    def _compute_total_maintenance_amount(self):
        for record in self:
            record.total_maintenance_amount = sum(record.maintenance_ids.mapped('maintenance_amount'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('asset.management') or 'New'
        return super(Asset, self).create(vals_list)


    def generate_depreciation_entries(self):
        """Generate depreciation entries with value subtraction."""
        assets = self.search(
            [('status', '!=', 'destroyed'), ('depreciation_apply', '=', True)])

        for asset in assets:
            # Check if the maximum number of depreciation entries has been reached
            existing_entries_count = self.env['asset.depreciation.entry'].search_count(
                [('asset_id', '=', asset.id),('create_uid', '=', 1)])
            max_entries = asset.asset_type_id.maximum_depreciation_entries

            if max_entries and existing_entries_count >= max_entries:
                continue  # Skip this asset if the maximum number of entries has been reached

            # Determine the starting date for depreciation
            start_date = asset.last_depreciation_date if asset.last_depreciation_date else asset.invoice_date
            if not start_date:
                continue  # Skip if no valid starting date

            # Calculate next depreciation date
            if asset.asset_type_id.depreciation_frequency == 'yearly':
                next_depreciation_date = start_date + relativedelta(
                    years=asset.asset_type_id.depreciation_start_delay)
            elif asset.asset_type_id.depreciation_frequency == 'monthly':
                next_depreciation_date = start_date + relativedelta(
                    months=asset.asset_type_id.depreciation_start_delay)
            elif asset.asset_type_id.depreciation_frequency == 'days':
                next_depreciation_date = start_date + timedelta(
                    days=asset.asset_type_id.depreciation_start_delay)
            else:
                continue  # Invalid depreciation type

            # Check if depreciation needs to be applied today
            if next_depreciation_date > datetime.today().date():
                continue  # Skip if next depreciation date is in the future

            # Determine the depreciation amount and subtract it from the value
            if asset.asset_type_id.depreciation_method == 'fix':
                depreciation_amount = asset.asset_type_id.depreciation_rate
            elif asset.asset_type_id.depreciation_method == 'percentage':
                base_amount = asset.amount if asset.asset_type_id.depreciation_basis == 'real_value' else asset.current_amount
                depreciation_amount = (
                                                  base_amount * asset.asset_type_id.depreciation_rate) / 100
            else:
                continue  # Invalid depreciation value type

            # Subtract the depreciation amount from the asset's value
            if asset.asset_type_id.depreciation_basis == 'real_value':
                asset.amount -= depreciation_amount
            else:
                asset.total_depreciation_amount -= depreciation_amount

            # Update the last depreciation date and create an entry in the depreciation model
            asset.last_depreciation_date = next_depreciation_date

            # Create a depreciation entry in the 'asset.depreciation' model
            self.env['asset.depreciation.entry'].create({
                'asset_id': asset.id,
                'created_by': self.env.uid,
                'depreciation_amount': depreciation_amount,
                'entry_date': datetime.today().date(),
            })

            print(
                f"Depreciation Entry Created for {asset.name}: {depreciation_amount} deducted on {next_depreciation_date}"
            )

    def action_open_label_layout(self):
        """Open the label layout wizard for printing asset labels"""
        action = self.env['ir.actions.act_window']._for_xml_id('sdlc_asset_management.action_open_label_layout')
        action['context'] = {'default_asset_ids': self.ids}
        return action


class AssetTag(models.Model):
    _name = 'asset.tag'
    _description = 'Asset Tag'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    
    _name_uniq = models.Constraint(
        'unique (name)',
        "Tag name already exists!",
    )


class AssetTransferEntry(models.Model):
    _name = 'asset.transfer.entry'
    _description = 'Asset Transfer Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Fields for tracking asset transfers
    from_location_id = fields.Many2one('asset.location', string="From Location", help="Select the location asset is moving from")
    to_location_id = fields.Many2one('asset.location', string="To Location", help="Select the destination location")
    asset_id = fields.Many2one('asset.management', string="Asset Reference", help="Choose the asset for which the transfer is being recorded", tracking=True)
    transfer_employee_id = fields.Many2one('hr.employee', string="Assigned To", help="Employee who is receiving or has received the asset", tracking=True)
    assign_date = fields.Date(string="Assign Date", help="Date when the asset was assigned to the employee", tracking=True)
    assign_by = fields.Many2one('res.users', string="Assign By", default=lambda self: self.env.user, help="Person responsible for assigning the asset", tracking=True)
    from_location = fields.Char(string="From Location (Text)", help="Location the asset is moving from", tracking=True)
    to_location = fields.Char(string="To Location (Text)", help="Location the asset is being assigned to", tracking=True)
    location = fields.Char(string="Location", help="Physical location or department where the asset is assigned (kept for compatibility)", tracking=True)
    return_date = fields.Date(string="Return Date", help="Date when the asset was returned by the employee", tracking=True)
    status = fields.Selection([
        ('assigned', 'Assigned'),
        ('returned', 'Returned'),
        ('under_maintenance', 'Under Maintenance')
    ], string="Status", help="Current status of the asset transfer", tracking=True)
    transfer_code = fields.Char(string="Transfer Code", copy=False, readonly=True, 
                               default=lambda self: _('New'), help="Unique identifier for this transfer", tracking=True)
    stock_qty = fields.Integer(string="Quantity", default=1, 
                              help="Quantity of assets being transferred (for multiple assets)", tracking=True)
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        default_location = res.get('from_location') or self.env.context.get('default_from_location')
        if default_location and 'from_location_id' in fields_list:
            location = self.env['asset.location'].search(['|', ('complete_name', '=', default_location), ('name', '=', default_location)], limit=1)
            if location:
                res['from_location_id'] = location.id
        # If default to_location provided via context, map it to Many2one
        default_to = res.get('to_location') or self.env.context.get('default_to_location')
        if default_to and 'to_location_id' in fields_list:
            location = self.env['asset.location'].search(['|', ('complete_name', '=', default_to), ('name', '=', default_to)], limit=1)
            if location:
                res['to_location_id'] = location.id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate transfer code and check stock availability"""
        records = self.browse()
        for vals in vals_list:
            if vals.get('transfer_code', 'New') == 'New':
                vals['transfer_code'] = self.env['ir.sequence'].next_by_code('asset.transfer.entry') or 'New'

            # Keep from/to location synchronized with drop-down choice
            vals = self._sync_location_vals(vals)
            
            if vals.get('asset_id') and vals.get('status') == 'assigned':
                asset = self.env['asset.management'].browse(vals['asset_id'])
                # Check if stock quantity is valid
                if vals.get('stock_qty', 1) <= 0:
                    raise exceptions.ValidationError(_("Transfer quantity must be greater than zero."))
                    
                if asset.model_type == 'multiple':
                    if asset.current_stock < vals.get('stock_qty', 1):
                        raise exceptions.ValidationError(_("Cannot assign this asset: Insufficient stock available."))
                if not vals.get('from_location'):
                    vals['from_location'] = self._get_last_location(asset)
            # Keep legacy "location" field in sync so existing views and metrics work
            if vals.get('to_location') and not vals.get('location'):
                vals['location'] = vals['to_location']
        records = super(AssetTransferEntry, self).create(vals_list)
        # Post creation message
        for rec in records:
            rec._post_creation_message()
        return records

    def write(self, vals):
        vals = self._sync_location_vals(vals)
        tracked_fields = self._get_tracked_fields()
        old_values = {rec.id: {f: rec[f] for f in tracked_fields} for rec in self}
        res = super().write(vals)
        # Post update message
        for rec in self:
            rec._post_update_message(old_values.get(rec.id, {}))
        return res

    def _get_tracked_fields(self):
        return [
            'transfer_employee_id', 'assign_date', 'assign_by', 'from_location_id', 'from_location',
            'to_location_id', 'to_location', 'return_date', 'status', 'stock_qty'
        ]

    def _format_value(self, field, value):
        if not value:
            return ''
        return value.display_name if hasattr(value, 'display_name') else value

    def _post_creation_message(self):
        body = _("<b>Transfer created</b>")
        self.message_post(body=body, subtype_xmlid="mail.mt_note")

    def _post_update_message(self, old_values):
        changes = []
        for field in self._get_tracked_fields():
            old = old_values.get(field)
            new = self[field]
            if old != new:
                changes.append(f"<li><b>{field}</b>: {self._format_value(field, old)} → {self._format_value(field, new)}</li>")
        if changes:
            body = "<b>Transfer updated</b><ul>%s</ul>" % "".join(changes)
            self.message_post(body=body, subtype_xmlid="mail.mt_note")

    @api.onchange('from_location_id')
    def _onchange_from_location_id(self):
        self.from_location = self.from_location_id.name if self.from_location_id else False

    @api.onchange('to_location_id')
    def _onchange_to_location_id(self):
        self.to_location = self.to_location_id.name if self.to_location_id else False
        self.location = self.to_location

    def _sync_location_vals(self, vals):
        """Ensure from/to char fields stay aligned with selected location records"""
        # From location sync
        if vals.get('from_location_id') and not vals.get('from_location'):
            location = self.env['asset.location'].browse(vals['from_location_id'])
            vals['from_location'] = location.complete_name or location.name
        elif vals.get('from_location') and not vals.get('from_location_id'):
            location = self.env['asset.location'].search(['|', ('complete_name', '=', vals['from_location']), ('name', '=', vals['from_location'])], limit=1)
            if location:
                vals['from_location_id'] = location.id
        # To location sync
        if vals.get('to_location_id') and not vals.get('to_location'):
            location = self.env['asset.location'].browse(vals['to_location_id'])
            vals['to_location'] = location.complete_name or location.name
        elif vals.get('to_location') and not vals.get('to_location_id'):
            location = self.env['asset.location'].search(['|', ('complete_name', '=', vals['to_location']), ('name', '=', vals['to_location'])], limit=1)
            if location:
                vals['to_location_id'] = location.id
        # Keep legacy location field aligned to destination
        if vals.get('to_location') and not vals.get('location'):
            vals['location'] = vals['to_location']
        return vals

    def _match_location_name(self, name_value):
        """Return complete_name if we can resolve a location by provided name text"""
        if not name_value:
            return False
        loc = self.env['asset.location'].search([
            '|',
            ('complete_name', '=ilike', name_value),
            ('name', '=ilike', name_value)
        ], limit=1)
        return loc.complete_name if loc else False

    def _get_last_location(self, asset):
        """Fetch the most recent known location for an asset to prefill from_location"""
        last_transfer = self.search([('asset_id', '=', asset.id)], order='assign_date desc, id desc', limit=1)
        if last_transfer:
            location_value = last_transfer.to_location or last_transfer.to_location_id.name or last_transfer.location
            if location_value:
                return location_value
        return asset.current_location or asset.manual_location or ''

    @api.constrains('assign_date', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.assign_date and record.return_date and record.return_date < record.assign_date:
                raise exceptions.ValidationError(
                    _("Return date cannot be earlier than the assign date."))

    @api.constrains('status', 'asset_id', 'stock_qty')
    def _check_stock_availability(self):
        """Ensure stock is available when assigning assets"""
        for record in self:
            if record.status == 'assigned' and record.asset_id.model_type == 'multiple':
                # Get current stock after excluding this record (important for updates)
                other_transfers = self.search([
                    ('asset_id', '=', record.asset_id.id),
                    ('status', '=', 'assigned'),
                    ('id', '!=', record.id)
                ])
                total_assigned = sum(other_transfers.mapped('stock_qty'))
                available = record.asset_id.initial_stock - total_assigned
                if available < record.stock_qty:
                    raise exceptions.ValidationError(_("Cannot assign this asset: Insufficient stock available."))

class AssetMaintenanceEntry(models.Model):
    _name = 'asset.maintenance.entry'
    _description = 'Asset Maintenance Entry'

    # Fields for tracking asset maintenance
    asset_id = fields.Many2one('asset.management', string="Asset Reference", help="Choose the asset for undergoing maintenance or repair is being recorded")
    maintenance_vendor_id = fields.Many2one('asset.vendor', string="Select Vendor", help="Vendor or technician performing the maintenance or repair")
    assign_date = fields.Date(string="Service Start Date", help="Date when the asset was sent for maintenance or repair")
    assign_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user, help="Person who initiated the maintenance or repair request")
    return_date = fields.Date(string="Completion Date", help="Date when the maintenance or repair was completed")
    maintenance_status = fields.Selection([
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], string="Status", default='pending', help="Current status of the maintenance or repair process")
    maintenance_amount = fields.Float(string="Amount")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    file_name = fields.Char(string='File Name')
    document = fields.Binary(string='Documents')
    description = fields.Text(string="Description", help="Detailed description of the maintenance work required or performed")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string="Priority", default='1', help="Priority level of this maintenance request")
    maintenance_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive'),
        ('predictive', 'Predictive'),
    ], string="Type", default='corrective', help="Type of maintenance being performed")
    duration_days = fields.Integer(string="Duration (Days)", compute='_compute_duration', store=True,
                                   help="Number of days the maintenance took")

    _amount_positive = models.Constraint(
        'CHECK(maintenance_amount >= 0)',
        'Maintenance amount cannot be negative.',
    )

    @api.depends('assign_date', 'return_date')
    def _compute_duration(self):
        for record in self:
            if record.assign_date and record.return_date:
                record.duration_days = (record.return_date - record.assign_date).days
            else:
                record.duration_days = 0

    @api.constrains('assign_date', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.assign_date and record.return_date and record.return_date < record.assign_date:
                raise exceptions.ValidationError(
                    _("Completion date cannot be earlier than the service start date."))


class AssetDepreciationEntry(models.Model):
    _name = 'asset.depreciation.entry'
    _description = 'Asset Depreciation Entry'

    # Fields for tracking asset depreciation
    asset_id = fields.Many2one('asset.management', string="Asset Reference", help="Choose the asset for which depreciation is being recorded")
    depreciation_amount = fields.Float(string="Amount", help="The monetary value of depreciation applied in this entry")
    entry_date = fields.Date(string="Depreciation Date", help="Date when this depreciation entry was recorded")
    notes = fields.Text(string="Comments", help="Additional information or remarks about this depreciation entry")
    created_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user, help="Person who created this depreciation entry")
    asset_type_name = fields.Char(string="Asset Type", related='asset_id.asset_type_id.name', store=True, readonly=True)

    _amount_positive = models.Constraint(
        'CHECK(depreciation_amount >= 0)',
        'Depreciation amount cannot be negative.',
    )

class AssetLocation(models.Model):
    _name = 'asset.location'
    _description = 'Asset Location'
    _rec_name = 'complete_name'

    name = fields.Char(string='Name', required=True)
    parent_id = fields.Many2one('asset.location', string='Parent Location', help="Hierarchical parent location")
    stock_location_id = fields.Many2one('stock.location', string='Stock Location',
                                        help="Link to a real inventory location for reporting")
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)
    complete_name = fields.Char(string='Full Location', compute='_compute_complete_name', store=True, recursive=True)

    _name_unique = models.Constraint(
        'unique(name)',
        'Location name must be unique.',
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_stock_location_link()
        return records

    def write(self, vals):
        res = super().write(vals)
        # If stock_location_id not set, auto-create
        missing = self.filtered(lambda l: not l.stock_location_id)
        missing._ensure_stock_location_link()
        return res

    def _ensure_stock_location_link(self):
        """Create and link a stock.location for any asset location missing one."""
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        parent = warehouse.view_location_id if warehouse else self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        StockLocation = self.env['stock.location']
        for loc in self:
            if loc.stock_location_id:
                continue
            stock_location = StockLocation.create({
                'name': loc.complete_name or loc.name,
                'usage': 'internal',
                'location_id': parent.id if parent else False,
                'active': loc.active,
            })
            loc.stock_location_id = stock_location.id

    @api.depends('name', 'parent_id', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = f"{location.parent_id.complete_name} / {location.name}"
            else:
                location.complete_name = location.name

    @api.depends('complete_name')
    def _compute_display_name(self):
        """Display hierarchical location as Parent/Child"""
        for location in self:
            location.display_name = location.complete_name or location.name or _("Unnamed Location")


class AssetType(models.Model):
    _name = 'asset.type'
    _description = 'Asset Type'

    # Fields for defining asset types and their depreciation rules
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index', help="Color index for this asset type")
    depreciation_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('days', 'Days')
    ], string='Depreciation Frequency', required=True, help="How often depreciation is calculated (Yearly, Monthly, or Daily)")

    depreciation_method = fields.Selection([
        ('fix', 'Fix'),
        ('percentage', 'Percentage')
    ], string='Depreciation Value Type', required=True, help="Whether depreciation is calculated as a percentage or fixed amount")

    depreciation_rate = fields.Float(string='Depreciation Rate', help="The percentage or fixed amount used to calculate depreciation")
    depreciation_start_delay = fields.Integer(string='Depreciation Start Delay', help="Time duration before depreciation begins after asset acquisition")
    depreciation_basis = fields.Selection([
        ('real_value', 'Purchase Price'),
        ('depreciation_value', 'Book Price')
    ], string='Depreciation Basis', required=True, help="Whether depreciation is applied to the adjusted value (after previous depreciation) or the original value")
    maximum_depreciation_entries = fields.Integer(string="Maximum Depreciation Entries", help="The maximum number of depreciation entries allowed for this asset type")


class AssetDashboard(models.Model):
    _name = 'asset.dashboard'
    _description = 'Asset Dashboard'

    # Financial KPIs
    total_asset_value = fields.Monetary(string="Total Asset Value", compute='_compute_metrics', currency_field='currency_id')
    total_purchase_cost = fields.Monetary(string="Purchase Cost", compute='_compute_metrics', currency_field='currency_id')
    depreciation_total = fields.Monetary(string="Depreciation", compute='_compute_metrics', currency_field='currency_id')
    depreciation_this_month = fields.Monetary(string="Depreciation This Month", compute='_compute_metrics', currency_field='currency_id')
    avg_asset_value = fields.Monetary(string="Avg Asset Value", compute='_compute_metrics', currency_field='currency_id')
    total_maintenance_cost = fields.Monetary(string="Total Maintenance Cost", compute='_compute_metrics', currency_field='currency_id')
    net_book_value = fields.Monetary(string="Net Book Value", compute='_compute_metrics', currency_field='currency_id')

    # Asset counts by status
    total_assets = fields.Integer(string="Total Assets", compute='_compute_metrics')
    assigned_count = fields.Integer(string="Assigned", compute='_compute_metrics')
    in_warehouse_count = fields.Integer(string="In Warehouse", compute='_compute_metrics')
    on_hold_count = fields.Integer(string="On Hold", compute='_compute_metrics')
    repair_count = fields.Integer(string="In Repair", compute='_compute_metrics')
    return_count = fields.Integer(string="Returned", compute='_compute_metrics')
    disposed_count = fields.Integer(string="Disposed", compute='_compute_metrics')

    # Percentage fields for progress bars
    assigned_pct = fields.Integer(string="Assigned %", compute='_compute_metrics')
    warehouse_pct = fields.Integer(string="Warehouse %", compute='_compute_metrics')
    on_hold_pct = fields.Integer(string="On Hold %", compute='_compute_metrics')
    repair_pct = fields.Integer(string="Repair %", compute='_compute_metrics')
    return_pct = fields.Integer(string="Return %", compute='_compute_metrics')
    disposed_pct = fields.Integer(string="Disposed %", compute='_compute_metrics')

    # Maintenance
    maintenance_open = fields.Integer(string="Maintenance Open", compute='_compute_metrics')
    maintenance_done = fields.Integer(string="Maintenance Done", compute='_compute_metrics')
    maintenance_pending = fields.Integer(string="Maintenance Pending", compute='_compute_metrics')

    # Operations
    transfers_count = fields.Integer(string="Transfers", compute='_compute_metrics')
    transfers_this_month = fields.Integer(string="Transfers This Month", compute='_compute_metrics')
    alert_count = fields.Integer(string="Alerts", compute='_compute_metrics')
    vendor_count = fields.Integer(string="Vendors", compute='_compute_metrics')
    non_moving_count = fields.Integer(string="Non-Moving", compute='_compute_metrics')
    warranty_expiring_count = fields.Integer(string="Warranty Expiring", compute='_compute_metrics')

    # Utilization
    utilization_rate = fields.Integer(string="Utilization Rate", compute='_compute_metrics')

    # Text fields
    locations_text = fields.Text(string="Locations", compute='_compute_metrics')
    recent_transfers_text = fields.Text(string="Recent Transfers", compute='_compute_metrics')
    top_categories_text = fields.Text(string="Top Categories", compute='_compute_metrics')
    warranty_alerts_text = fields.Text(string="Warranty Alerts", compute='_compute_metrics')

    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id.id)

    def _compute_display_name(self):
        for record in self:
            record.display_name = _("Asset Dashboard")

    def _compute_metrics(self):
        Asset = self.env['asset.management']
        Transfer = self.env['asset.transfer.entry']
        Maintenance = self.env['asset.maintenance.entry']
        Depreciation = self.env['asset.depreciation.entry']
        Vendor = self.env['asset.vendor']

        today = fields.Date.today()
        cutoff = today - relativedelta(days=30)
        month_start = today.replace(day=1)

        assets = Asset.search([])
        transfers = Transfer.search([])
        maintenance_entries = Maintenance.search([])
        depreciation_entries = Depreciation.search([])

        total_count = len(assets)
        total_purchase_cost = sum(assets.mapped('amount'))
        total_asset_value = sum(assets.mapped('current_amount'))

        # Status counts
        assigned_count = len(assets.filtered(lambda a: a.status == 'assign'))
        in_warehouse_count = len(assets.filtered(lambda a: a.status == 'in_warehouse'))
        on_hold_count = len(assets.filtered(lambda a: a.status == 'on_hold'))
        repair_count = len(assets.filtered(lambda a: a.status == 'repair'))
        return_count = len(assets.filtered(lambda a: a.status == 'return'))
        disposed_count = len(assets.filtered(lambda a: a.status == 'destroyed'))

        # Percentages for progress bars
        def pct(count):
            return int(round(count * 100 / total_count)) if total_count else 0

        # Maintenance
        maintenance_open_entries = maintenance_entries.filtered(lambda m: m.maintenance_status == 'in_progress')
        maintenance_pending_entries = maintenance_entries.filtered(lambda m: m.maintenance_status == 'pending')
        maintenance_done_entries = maintenance_entries.filtered(lambda m: m.maintenance_status == 'completed')

        # Financial
        depreciation_total = sum(depreciation_entries.mapped('depreciation_amount'))
        depreciation_this_month = sum(
            depreciation_entries.filtered(
                lambda d: d.entry_date and d.entry_date >= month_start
            ).mapped('depreciation_amount')
        )
        total_maintenance_cost = sum(maintenance_entries.mapped('maintenance_amount'))
        avg_asset_value = total_asset_value / total_count if total_count else 0
        net_book_value = total_purchase_cost - depreciation_total

        # Alerts - warranties expiring in 30 days
        warranty_expiring = assets.filtered(
            lambda a: a.expired_warranty_date and today <= a.expired_warranty_date <= today + relativedelta(days=30)
        )
        alerts = assets.filtered(
            lambda a: (a.expired_warranty_date and a.expired_warranty_date <= today + relativedelta(days=30))
            or (a.model_type == 'multiple' and a.current_stock <= 0)
        )

        # Warranty alerts text
        warranty_lines = []
        for a in warranty_expiring[:5]:
            days_left = (a.expired_warranty_date - today).days
            warranty_lines.append(f"{a.name}|{days_left} days left")
        warranty_alerts_text = "\n".join(warranty_lines)

        # Non-moving assets
        recent_transfer_assets = set(
            transfers.filtered(lambda t: t.assign_date and t.assign_date >= cutoff).mapped('asset_id').ids
        )
        non_moving_assets = assets.filtered(lambda a: a.id not in recent_transfer_assets)

        # Transfers this month
        transfers_this_month = transfers.filtered(
            lambda t: t.assign_date and t.assign_date >= month_start
        )

        # Vendor count
        vendor_count = Vendor.search_count([])

        # Utilization rate: assigned assets / total active assets (not destroyed)
        active_assets = total_count - disposed_count
        utilization_rate = int(round(assigned_count * 100 / active_assets)) if active_assets else 0

        # Top categories
        type_counts = {}
        for asset in assets:
            type_name = asset.asset_type_id.name if asset.asset_type_id else 'Uncategorized'
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories_text = "\n".join(f"{name}|{count}" for name, count in sorted_types)

        # Recent transfers (last 5)
        recent_transfers = transfers.sorted(key=lambda t: (t.assign_date or date.min, t.id), reverse=True)[:5]
        recent_lines = []
        for t in recent_transfers:
            asset_name = t.asset_id.name if t.asset_id else 'Unknown'
            to_loc = ''
            if t.to_location_id:
                to_loc = t.to_location_id.name
            elif hasattr(t, 'to_location') and t.to_location:
                to_loc = t.to_location
            emp = t.transfer_employee_id.name if t.transfer_employee_id else ''
            dt = str(t.assign_date) if t.assign_date else ''
            recent_lines.append(f"{asset_name}|{to_loc}|{emp}|{dt}|{t.status or ''}")
        recent_transfers_text = "\n".join(recent_lines)

        # Locations
        location_map = {}
        for asset in assets:
            assigned_transfers = asset.transfer_ids.filtered(lambda t: t.status == 'assigned')
            if not assigned_transfers:
                continue
            last = assigned_transfers.sorted(key=lambda t: (t.assign_date or date.min, t.id))[-1]
            to_location_name = (last.to_location_id.complete_name if last.to_location_id else '').strip() or (asset.current_location or '').strip()
            if not to_location_name:
                continue
            from_loc_record = last.from_location_id
            from_location = (from_loc_record.complete_name if from_loc_record else getattr(last, 'from_location', '') or 'Unknown').strip() or 'Unknown'
            key = (from_location, to_location_name)
            location_map[key] = location_map.get(key, 0) + 1
        locations_text = "\n".join(
            f"{frm} -> {to}: {count}"
            for (frm, to), count in sorted(location_map.items(), key=lambda kv: (kv[0][0].lower(), kv[0][1].lower()))
        )

        for record in self:
            record.total_asset_value = total_asset_value
            record.total_purchase_cost = total_purchase_cost
            record.depreciation_total = depreciation_total
            record.depreciation_this_month = depreciation_this_month
            record.avg_asset_value = avg_asset_value
            record.total_maintenance_cost = total_maintenance_cost
            record.net_book_value = net_book_value
            record.total_assets = total_count
            record.assigned_count = assigned_count
            record.in_warehouse_count = in_warehouse_count
            record.on_hold_count = on_hold_count
            record.repair_count = repair_count
            record.return_count = return_count
            record.disposed_count = disposed_count
            record.assigned_pct = pct(assigned_count)
            record.warehouse_pct = pct(in_warehouse_count)
            record.on_hold_pct = pct(on_hold_count)
            record.repair_pct = pct(repair_count)
            record.return_pct = pct(return_count)
            record.disposed_pct = pct(disposed_count)
            record.maintenance_open = len(maintenance_open_entries)
            record.maintenance_done = len(maintenance_done_entries)
            record.maintenance_pending = len(maintenance_pending_entries)
            record.transfers_count = len(transfers)
            record.transfers_this_month = len(transfers_this_month)
            record.alert_count = len(alerts)
            record.vendor_count = vendor_count
            record.non_moving_count = len(non_moving_assets)
            record.warranty_expiring_count = len(warranty_expiring)
            record.utilization_rate = utilization_rate
            record.locations_text = locations_text
            record.recent_transfers_text = recent_transfers_text
            record.top_categories_text = top_categories_text
            record.warranty_alerts_text = warranty_alerts_text
