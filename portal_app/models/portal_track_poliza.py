from odoo import fields,models,api


class PortalTrackPoliza(models.Model):
    _name = 'portal.track.poliza'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    etapa = fields.Selection(
        selection=[
            ('pendiente', 'Pendiente de descarga'),
            ('descargado', 'Descargado'),
        ],
        string="Estado",
        tracking=True,
        default='pendiente'
    )
    #Datos de vehículo
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo',
    )
    vin_sn = fields.Char(
        string='VIN',
        store=True,
        compute='_compute_datos',
    )
    matricula = fields.Char(
        string='Matricula',
        compute='_compute_datos',
        store=True,
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute='_compute_datos',
        store=True,
    )
    #Datos de cliente
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        compute='_compute_datos',
        store=True,
    )
    #Datos de descarga
    fecha_hora_descarga = fields.Datetime(
        string='Fecha y hora de descarga',
    )
    fecha_hora_ult_desc = fields.Datetime(
        string='Fecha y hora de última descarga',
        tracking=True,
    )
    num_descargas = fields.Integer(
        string='Numero de descargas',
        tracking=True,
    )

    @api.depends('vehiculo_id')
    def _compute_datos(self):
        for record in self:
            record.vin_sn = record.vehiculo_id.vin_sn
            record.cliente_id = record.vehiculo_id.driver_id.id
            record.matricula = record.vehiculo_id.license_plate
            record.plaza_id = record.vehiculo_id.plaza_id.id