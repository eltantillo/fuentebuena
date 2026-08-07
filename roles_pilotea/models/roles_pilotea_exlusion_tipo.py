from odoo import fields,models,api


class RolesPiloteaExclusionTiPO(models.Model):
    _name = 'roles.pilotea.exclusion.tipo'

    name = fields.Char(
        string='Nombre'
    )