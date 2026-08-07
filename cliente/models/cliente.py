from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class cliente(models.Model):
    _inherit = 'res.partner'
    _description = 'Clientes'

    es_cliente = fields.Boolean(
        string='Es cliente'
    )
    fecha_nacimiento = fields.Date(
        string='Fecha de nacimiento'
    )
    genero = fields.Selection(
        string='Genero',
        selection=[
            ('M', 'Masculino'),
            ('F', 'Femenino')
        ]
    )
    curp = fields.Char(
        string='CURP'
    )
    user_landing_id = fields.Char(
        string='User Landing'
    )
    primer_nombre = fields.Char(
        string='Primer nombre'
    )
    segundo_nombre = fields.Char(
        string='Segundo nombre'
    )
    apellido_paterno = fields.Char(
        string='Apellido paterno'
    )
    apellido_materno = fields.Char(
        string='Apelido materno'
    )
    id_cliente = fields.Integer(
        string='ID anterior'
    )
    # constancia_filename = fields.Char(
    #     string='Constancia filename'
    # )
    # constancia_valida = fields.Binary(
    #     string='Constancia valida'
    # )

    @api.model
    def create(self,vals):
        escliente = self.env.context.get('default_es_cliente')
        if escliente:
            for val in vals:
                val['customer_rank'] = 1
        res = super(cliente, self).create(vals)
        return res