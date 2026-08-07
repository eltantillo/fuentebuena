from odoo import fields,api,models
from .formulario_renegociar import ESTADOS


class FormularioSolicita(models.Model):
    _name = 'formulario.solicita'
    _description = 'Formulario solicita'
    _rec_name = 'rec_name'
    _order = 'id desc'


    nombre = fields.Char(
        string='Nombre'
    )
    rfc = fields.Char(
        string='RFC',
    )
    telefono = fields.Char(
        string='Número de telefono'
    )
    correo = fields.Char(
        string='Correo'
    )
    estado = fields.Selection(
        selection=ESTADOS,
        string='Estado o región'
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    rec_name = fields.Char(
        string='Nombre',
        compute='_compute_rec_name',
    )

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.nombre} - {record.telefono}"