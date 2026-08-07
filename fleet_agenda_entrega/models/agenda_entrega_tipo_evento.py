from odoo import fields, models, api


class AgendaEntregaTipoEvento(models.Model):
    _name = "agenda.entrega.tipo.evento"
    _description = "Tipo de evento de la agenda de entrega"

    name = fields.Char(
        string="Nombre",
    )