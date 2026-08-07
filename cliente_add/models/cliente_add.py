from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class clienteAdd(models.Model):
    _inherit = 'res.partner'
    _description = 'Clientes'

    constancia_filename = fields.Char(
        string='Constancia filename'
    )
    constancia_valida = fields.Boolean(
        string='Constancia valida'
    )
    constancia = fields.Binary(
        string='Constancia'
    )
