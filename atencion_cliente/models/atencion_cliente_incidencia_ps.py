from odoo import fields, models, api

class AtencionClienteIncidenciaPs(models.Model):
    _name = 'atencion.cliente.incidencia.ps'
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
    incidencia = fields.Text(
        string='Incidencia'
    )
    causa_id = fields.Many2one(
        comodel_name='atencion.cliente.causa.incidencia.ps',
        string='Causa'
    )
    vehiculo_ids = fields.Many2many(
        comodel_name="fleet.vehicle",
        string="Vehículos del cliente",
        compute="_compute_vehicles",
        store=True,
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )

    @api.depends('vehiculo_id')
    def _compute_datos(self):
        for record in self:
            if record.vehiculo_id:
                record.vin_sn = record.vehiculo_id.vin_sn
                record.plaza_id = record.vehiculo_id.plaza_id

    @api.depends('cliente_id')
    def _compute_vehicles(self):
        for record in self:
            if record.cliente_id:
                record.vehiculo_ids = self.env['fleet.vehicle'].search([('driver_id','=', record.cliente_id.id)])
            else: record.cliente_id = False

    @api.depends('cliente_id')
    def _compute_vehiculo_id(self):
        etapa_renta = self.env['atencion.cliente.interaccion'].return_etapa_renta()
        for record in self:
            if record.cliente_id:
                vehiculo = self.env['fleet.vehicle'].search([('driver_id', '=', record.cliente_id.id),('state_id','=', etapa_renta)], limit=1)
                record.vehiculo_id = vehiculo.id if vehiculo else False

    def _inverse_vehiculo_id(self):
        pass

    def _compute_name(self):
        for record in self:
            record.name = f"{record.id}-{record.cliente_id.name}"