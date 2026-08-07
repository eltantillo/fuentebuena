from odoo import fields,models,api


class PromesaPZona(models.Model):
    _name = 'promesa.p.zona'
    _rec_name = 'zona_id'

    name = fields.Char(
        string='Nombre de zona',
    )
    zona_id = fields.Char(
        string='ID zona',
    )