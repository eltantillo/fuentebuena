from odoo import fields, models, api
from .formulario_renegociar import ESTADOS

import logging
_logger = logging.getLogger(__name__)

class FormularioPrestamoSinBuro(models.Model):
    _name = 'formulario.prestamo.sin.buro'
    _description = 'Formulario para almacenar prestamos sin buro de crédito '
    _rec_name = 'rec_name'
    _order = 'id desc'

    nombre = fields.Char(
        string='Nombre',
    )
    apellido = fields.Char(
        string='Apellido',
    )
    correo = fields.Char(
        string='Correo',
    )
    telefono = fields.Char(
        string='Teléfono',
    )
    estado = fields.Selection(
        selection=ESTADOS,
        string='Estado',
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    convenio_id = fields.Many2one(
        comodel_name='formulario.ayuntamiento',
        string='Convenio',
    )
    puesto_ocupado_id = fields.Many2one(
        comodel_name='puesto.ocupado',
        string='Puesto que desempeña',
    )
    rec_name = fields.Char(
        string='Nombre',
        compute='_compute_rec_name',
    )
    ver_convenio = fields.Boolean(
        string='Ver convenio',
        compute='_compute_mostrar_convenios',
        default=False
    )
    es_trabajador_ayuntamiento = fields.Selection(
        string='¿Eres trabajador del Ayuntamiento',
        selection = [
            ('si','Si'),
            ('no','No')
        ]
    )
    producto_id = fields.Many2one(
        comodel_name='formulario.producto',
        string='Producto',
    )
    uso_datos_personales = fields.Boolean(
        string='Uso de datos personales',
    )

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f'{record.nombre} - {record.telefono}'

    @api.depends('estado_id')
    def _compute_mostrar_convenios(self):
        for record in self:
            if record.estado_id:
                convenios = self.env['formulario.convenio'].search([('estado_id', '=', record.estado_id.id)])
                if convenios:
                    record.ver_convenio = True
                else:
                    record.ver_convenio = False