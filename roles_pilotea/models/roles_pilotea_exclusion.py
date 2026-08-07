from odoo import fields,models,api


class RolesPiloteaExclusion(models.Model):
    _name = 'roles.pilotea.exclusion'

    correo = fields.Char(
        string='Correo'
    )
    tipo_exclusion_ids = fields.Many2many(
        comodel_name="roles.pilotea.exclusion.tipo",
        string="Tipo de exclusiones",
    )