from odoo import fields,models,api

class FormularioServicioCliente(models.Model):
    _name = 'formulario.servicio.cliente'
    _description = 'Formulario para resolver dudas del cliente'
    _rec_name = 'rec_name'
    _order = 'id desc'

    nombre = fields.Char(
        string='Nombre'
    )
    apellido = fields.Char(
        string='Apellido'
    )
    correo = fields.Char(
        string='Correo'
    )
    telefono = fields.Char(
        string='Télefono'
    )
    mensaje = fields.Char(
        string='Mensaje'
    )
    rec_name = fields.Char(
        string='Nombre',
        compute='_compute_rec_name',
    )

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.nombre} - {record.telefono}"