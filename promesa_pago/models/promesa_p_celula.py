from odoo import fields,models,api

class PromesaPCelula(models.Model):
    _name='promesa.p.celula'
    _rec_name ='celula_id'

    celula_id = fields.Char(
        string='ID de celula',
    )
    name = fields.Char(
        string='Nombre de celula',
    )
    zona_id = fields.Many2one(
        comodel_name='promesa.p.zona',
        string='Zona',
    )
    zona_name = fields.Char(
        string='ID de zona',
    )