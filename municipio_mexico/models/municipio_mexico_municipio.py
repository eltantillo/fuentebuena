from odoo import models, fields, api


class MunicipioMexicoMunicipio(models.Model):
    _name = 'municipio'
    _description = 'Municipio de Mexico'
    _rec_name = 'rec_name'

    cvegeo = fields.Char(
        string='CVEGEO'
    )
    nombre_entidad = fields.Char(
        string='Municipio'
    )
    nombre_municipio = fields.Char(
        string='Municipio'
    )
    code = fields.Char(
        string='Municipio'
    )
    rec_name = fields.Char(
        string='Municipio',
        compute='_compute_rec_name'
    )

    @api.depends('nombre_municipio')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.nombre_municipio} - {record.code}"