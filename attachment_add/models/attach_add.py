from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class IrAttachmentMigration(models.Model):
    _inherit = 'ir.attachment'

    origin_id = fields.Integer(
        string='ID Origen Migración',
        index=True,
    )