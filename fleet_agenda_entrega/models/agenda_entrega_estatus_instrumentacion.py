from odoo import fields, models, api

class AgendaEntregaEstatusInstrumentacion(models.Model):
    _name = "agenda.entrega.estatus.instru"
    _description = "Estatus de la agenda de entrega"

    name = fields.Char(
        string="Nombre",
    )