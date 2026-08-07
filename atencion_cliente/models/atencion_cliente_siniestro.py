from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class AtencionClienteSiniestro(models.Model):
    _name = 'atencion.cliente.siniestro'
    _inherit = ['mail.thread','mail.activity.mixin']
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
    estado_id = fields.Many2one(
        comodel_name='fleet.vehicle.state',
        string='Estado de vehículo',
        compute='_compute_datos',
        store=True
    )
    telefono = fields.Char(
        string='Teléfono',
        compute='_compute_telefono',
        inverse='_inverse_telefono',
        tracking=True,
    )
    medio_contacto_id = fields.Many2one(
        comodel_name='atencion.cliente.medio.contacto',
        string='Medio de contacto',
        tracking=True,
    )
    estatus_registro_id = fields.Many2one(
        comodel_name='atencion.cliente.status.registro',
        string="Estatus de registro",
        tracking=True,
    )
    seguimiento = fields.Text(
        string='Seguimiento',
        tracking=True,
    )
    #---------------------------------------------INFORME DEL SINIESTRO ------------------------------------------------
    ubicacion = fields.Char(
        string='Ubicacion',
        tracking=True,
    )
    conductor = fields.Char(
        string='Conductor'
    )
    telefono_conductor = fields.Char(
        string="Telefono conductor",
    )
    fecha_ocurrido = fields.Datetime(
        string='Fecha de Ocurrido'
    )
    fecha_reporte = fields.Datetime(
        string='Fecha de Reporte'
    )
    responsabilidad = fields.Many2one(
        comodel_name = 'atencion.cliente.responsabilidad',
        string='Responsabilidad',
        tracking=True,
    )
    num_reporte = fields.Char(
        string='Num Reporte',
        tracking=True,
    )
    num_siniestro = fields.Char(
        string='Num Siniestro'
    )
    tipo_siniestro_id = fields.Many2one(
        comodel_name="fleet.siniestro.tipo",
        string="Tipo de siniestro",
        tracking=True,
    )
    volante_en_reparacion = fields.Boolean(
        string="¿Volante en reparación?",
        tracking=True,
    )
    con_deducible = fields.Boolean(
        string="¿Con deducible?",
        tracking=True,
    )
    caracteristica_id = fields.Many2one(
        comodel_name="atencion.cliente.caracteristica",
        string="Caracteristica",
        tracking=True,
    )
    detalle = fields.Text(
        string='Detalles',
        tracking=True,
    )
    #Evidencia fotografica
    evidencia_1 = fields.Binary(
        string="Evidencia 1",
        attachment=True
    )
    evidencia_2 = fields.Binary(
        string="Evidencia 2",
        attachment=True,
    )
    evidencia_3 = fields.Binary(
        string="Evidencia 3",
        attachment=True,
    )
    evidencia_4 = fields.Binary(
        string="Evidencia 4",
        attachment=True,
    )
    vehiculo_ids = fields.Many2many(
        comodel_name="fleet.vehicle",
        compute='_compute_vehiculos',
        store=True
    )
    name = fields.Char(
        string="Nombre",
        compute="_compute_name"
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    siniestro_robo = fields.Many2one(
        comodel_name="fleet.siniestro.tipo",
        string="Siniestro robo",
        compute='_compute_robo'
    )

    def _compute_robo(self):
        for record in self:
            siniestro_robo = self.env['fleet.siniestro.tipo'].search([('name','=','Robo')], limit=1)
            record.siniestro_robo = siniestro_robo.id

    @api.depends('cliente_id')
    def _compute_vehiculos(self):
        for record in self:
            if record.cliente_id:
                record.vehiculo_ids = self.env['fleet.vehicle'].sudo().search([('driver_id', '=', record.cliente_id.id)])

    @api.depends('cliente_id')
    def _compute_telefono(self):
        for record in  self:
            record.telefono = record.cliente_id.phone if record.cliente_id.phone else False

    def _inverse_telefono(self):
        pass


    def _compute_name(self):
        for record in self:
            record.name = f'{record.id}-{record.cliente_id.name}'

    @api.depends('vehiculo_id')
    def _compute_datos(self):
        for record in self:
            if record.vehiculo_id:
                record.vin_sn = record.vehiculo_id.vin_sn
                record.plaza_id = record.vehiculo_id.plaza_id
                record.estado_id = record.vehiculo_id.state_id

    @api.depends('cliente_id')
    def _compute_vehiculo_id(self):
        etapa_renta = self.env['atencion.cliente.interaccion'].return_etapa_renta()
        for record in self:
            if record.cliente_id:
                vehiculo = self.env['fleet.vehicle'].sudo().search([('driver_id', '=', record.cliente_id.id),('state_id','=', etapa_renta)], limit=1)
                record.vehiculo_id = vehiculo.id if vehiculo else False

    def _inverse_vehiculo_id(self):
        pass

    def write_custom(self, vals):
        res = super(AtencionClienteSiniestro, self).write(vals)
        return res