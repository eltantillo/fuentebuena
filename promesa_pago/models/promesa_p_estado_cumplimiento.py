from odoo import fields,models,api

class PromesaPEstadoCumplimiento(models.Model):
    _name = 'promesa.p.estado.cumplimiento'

    name = fields.Char(
        string='Nome'
    )