from odoo import fields,models,api

class IntegracionBaseBloqueo(models.Model):

    _name = 'integracion.base.bloqueo'
    _rec_name = 'rec_name'

    estado_peticion = fields.Selection([
        ('registrado','Registrado'),
        ('aplicado', 'Aplicado'),
        ('error', 'Error')],
        default='registrado',
        string='Estado',
    )
    tipo = fields.Selection([
        ('bloqueo','Bloqueo'),
        ('desbloqueo','Desbloqueo')],
        string='Tipo',
    )
    vehiculo_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehiculo",
        tracking=True,
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos_vehiculo',
        store=True
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto',
        compute='_compute_datos_vehiculo',
        store=True
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute='_compute_datos_vehiculo',
        store=True
    )
    proveedor_gps = fields.Char(
        string='Proveedor GPS',
        compute='_compute_datos_vehiculo',
        store=True
    )
    id_gps = fields.Char(
        string='ID GPS',
        compute='_compute_datos_vehiculo',
        store=True
    )
    msg_error = fields.Text(
        string='Error',
    )
    rec_name = fields.Char(
        string='Record Name',
        compute='_compute_rec_name',
        store=True
    )

    @api.depends('vin_sn','tipo','proveedor_gps')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.tipo}-{record.vin_sn}-{record.proveedor_gps}"

    @api.depends('vehiculo_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            record.vin_sn = record.vehiculo_id.vin_sn
            record.producto_id = record.vehiculo_id.producto_id.id
            record.plaza_id = record.vehiculo_id.plaza_id.id
            record.proveedor_gps = record.vehiculo_id.external_gps_provider
            record.id_gps = record.vehiculo_id.external_gps_id

    def write(self, vals):
        res = super(IntegracionBaseBloqueo, self).write(vals)
        if 'estado_peticion' in vals:
            if vals['estado_peticion'] == 'aplicado':
                if self.tipo == 'bloqueo':
                    self.vehiculo_id.external_estado_bloqueo = 'bloqueado'
                elif self.tipo == 'desbloqueo':
                    self.vehiculo_id.external_estado_bloqueo = 'desbloqueado'