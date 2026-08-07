from odoo import models,fields,api


class AgendaEntregaEstatusEvento(models.Model):
    _name = "agenda.entrega.estatus.evento"
    _order = 'sequence asc'
    _description = "Agenda Entrega Estatus Evento"

    name = fields.Char(
        string="Nombre",
    )
    sequence = fields.Integer(
        string="Sequence",
    )
