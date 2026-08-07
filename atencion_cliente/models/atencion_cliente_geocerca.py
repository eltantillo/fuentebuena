from odoo import  fields, models, api

class AtencionClienteGeocerca(models.Model):
    _name = 'atencion.cliente.geocerca'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente'
    )
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehiculo',
        store=True,
        compute='_compute_vehiculo_id',
        inverse='_inverse_vehiculo_id',
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos',
        store=True
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute='_compute_datos',
        store=True
    )
    fecha_solicitud = fields.Datetime(
        string='Fecha de Solicitud'
    )
    motivo = fields.Text(
        string = 'Motivo'
    )
    solucion = fields.Text(
        string = 'Solución'
    )
    name = fields.Char(
        string="name",
        compute = '_compute_name',
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.depends('vehiculo_id')
    def _compute_datos(self):
        for record in self:
            if record.vehiculo_id:
                record.vin_sn = record.vehiculo_id.vin_sn
                record.plaza_id = record.vehiculo_id.plaza_id

    def _compute_name(self):
        for record in self:
            if record.cliente_id:
                record.name = f'{record.id}-{record.cliente_id.name}'
            else:
                record.name = f'{record.id}'

    @api.depends('cliente_id')
    def _compute_vehiculo_id(self):
        etapa_renta = self.env['atencion.cliente.interaccion'].return_etapa_renta()
        for record in self:
            if record.cliente_id:
                vehiculo = self.env['fleet.vehicle'].search([('driver_id', '=', record.cliente_id.id),('state_id','=', etapa_renta)], limit=1)
                record.vehiculo_id = vehiculo.id if vehiculo else False

    def _inverse_vehiculo_id(self):
        pass