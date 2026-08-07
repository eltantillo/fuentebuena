from odoo import fields,models,api


class GestionCaidoTrack(models.Model):

    _name = 'gestion.caido.track'


    gestion_id = fields.Many2one(
        string="Gestion",
        comodel_name='gestion.caido',
        ondelete='cascade',
    )
    fecha_inicio = fields.Datetime(
        string="Fecha de inicio"
    )
    fecha_finalizacion = fields.Datetime(
        string="Fecha de finalizacion"
    )
    evento = fields.Char(
        string="Evento"
    )