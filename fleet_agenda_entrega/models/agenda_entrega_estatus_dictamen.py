from odoo import fields, models, api


class AgendaEntregaEstatusDictamen(models.Model):
    _name = "agenda.entrega.estatus.dictamen"
    _description = "Estatus Dictamen"

    name = fields.Char(
        string="Nombre"
    )