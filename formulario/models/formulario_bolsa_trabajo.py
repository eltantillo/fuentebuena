from odoo import fields,models

class FormularioBolsaTrabajo(models.Model):
    _name = 'formulario.bolsa.trabajo'
    _description = 'Formulario para bolsa de trabajo'
    _rec_name = 'rec_name'
    _order = 'id desc'

    nombre = fields.Char(
        string='Nombre'
    )
    correo = fields.Char(
        string='Correo'
    )
    telefono = fields.Char(
        string=' Número de teléfono'
    )
    asunto = fields.Char(
        string='Asunto'
    )
    area_id = fields.Many2one(
        comodel_name='bolsa.trabajo.area',
        string='Area',
    )
    cv = fields.Binary(
        string='CV',
        attachment=True,
    )
    cv_filename = fields.Char(
        string='Nombre del cv',
    )
    rec_name = fields.Char(
        string='Nombre completo',
        compute='_compute_rec_name'
    )

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.nombre} - {record.telefono}"