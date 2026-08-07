from odoo import fields, models, api


class AgendaEntregaCanalizacion(models.Model):
    _name = "agenda.entrega.canalizacion"
    _description = "Canalizacion de la agenda de entrega"

    name = fields.Char(
        string="Nombre",
    )