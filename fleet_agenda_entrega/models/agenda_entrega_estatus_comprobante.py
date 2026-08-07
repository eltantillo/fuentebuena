from odoo import fields, models, api


class AgendaEntregaEstatusComprobante(models.Model):
    _name = 'agenda.entrega.estatus.comprobante'
    _description = 'Estatus de comprobante'

    name = fields.Char(
        string='Nombre'
    )