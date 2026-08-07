from odoo import models, fields, api


class AgendaEntregaEtapa(models.Model):
    _name="agenda.entrega.etapa"
    _description="Estado de la agenda de entrega"

    name = fields.Char(
        string="Nombre",
    )
