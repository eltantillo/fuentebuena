from odoo import fields,models,api

class PromesaPConvenio(models.Model):
    _name = 'promesa.p.convenio'

    name = fields.Char(
        string='Nombre',
    )
    pk_cat_convenio = fields.Char(
        string='pk_cat_Convenio',
    )
    celula_id = fields.Many2one(
        comodel_name='promesa.p.celula',
        string='Celula',
    )
    celula_name = fields.Char(
        string='Nombre',
    )