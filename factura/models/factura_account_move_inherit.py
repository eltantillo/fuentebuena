from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    folio = fields.Char(
        string='Folio',
    )
    exportacion = fields.Char(
        string='Exportación',
    )
    lugar_expedicion = fields.Char(
        string='Lugar de expedición',
    )
    no_certificado_sat = fields.Char(
        string='No. Certificado SAT',
    )
    total_imp_trasladados = fields.Float(
        string='Total impuestos trasladados',
    )
    fecha_timbrado = fields.Char(
        string='Fecha timbrado',
    )