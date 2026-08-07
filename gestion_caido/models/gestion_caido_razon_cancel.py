from odoo import fields,models,api


class GestionCaidoRazonCancel(models.Model):

    _name = 'gestion.caido.razon.cancel'

    name = fields.Char(
        string="Nombre",
    )