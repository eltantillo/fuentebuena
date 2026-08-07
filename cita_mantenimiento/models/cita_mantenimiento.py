from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CitaMantenimiento(models.Model):
    _name = 'cita.mantenimiento'
    _description = 'Cita Mantenimiento'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'rec_name'
    _order = 'create_date desc'

    etapa_id = fields.Many2one(
        comodel_name='cita.mantenimiento.etapa',
        string='Etapa',
        tracking=True,
    )
    mantenimiento_id = fields.Many2one(
        comodel_name='fleet.mantenimiento',
        string='Mantenimiento',
        tracking=True,
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        tracking=True,
    )
    nombre_cliente = fields.Char(
        string='Nombre de cliente',
        compute='_compute_datos_cliente',
        store=True,
        tracking=True
    )
    correo_cliente = fields.Char(
        string='Correo de cliente',
        compute='_compute_datos_cliente',
        store=True,
        tracking=True
    )
    odometro = fields.Integer(
        string='Odometro',
    )
    telefono_cliente = fields.Char(
        string="Teléfono",
        compute="_compute_datos_cliente",
        store=True,
        tracking=True
    )
    "Datos del vehículo"
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehiculo',
        tracking=True,
    )
    numero_economico = fields.Char(
        string='N° economico',
        compute='_compute_datos_vehiculo',
        store=True
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
    matricula = fields.Char(
        string='Matricula',
        compute='_compute_datos_vehiculo',
        store=True
    )
    "Datos de cita"
    proveedor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Proveedor',
    )
    fecha_cita_inicio = fields.Datetime(
        string='Fecha cita inicio',
        tracking = True,
    )
    fecha_cita_fin = fields.Datetime(
        string='Fecha cita fin',
        tracking=True,
    )
    fecha_reagenda = fields.Datetime(
        string='Fecha reagenda',
        tracking=True,
    )
    contador_reagenda = fields.Integer(
        string='Contador reagenda',
        tracking=True,
    )
    contador_reagenda_au = fields.Integer(
        string='Contador reagenda automatica',
        tracking=True,
    )
    rec_name = fields.Char(
        string='Rec name',
        compute='_compute_rec_name',
        store=True,
    )
    color = fields.Integer(
        string='Color',
        compute='_compute_color',
    )
    reagenda_automatica = fields.Boolean(
        string='Reagenda automatica',
    )
    cita_creada_automaticamente = fields.Boolean(
        string="Cita creada automaticamente"
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.depends('vehiculo_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = self.env['fleet.vehicle'].browse(record.vehiculo_id.id)
            record.numero_economico = vehiculo.numero_economico
            record.vin_sn = vehiculo.vin_sn
            record.producto_id = vehiculo.producto_id.id
            record.plaza_id = vehiculo.plaza_id.id
            record.odometro = vehiculo.odometro_mod
            record.matricula = vehiculo.license_plate


    def _compute_color(self):
        etapa_programada = self.env['cita.mantenimiento.etapa'].search([('name','=','Programada')], limit=1)
        etapa_reagendada = self.env['cita.mantenimiento.etapa'].search([('name','=','Reagendada')], limit=1)
        etapa_cancelada = self.env['cita.mantenimiento.etapa'].search([('name','=','Cancelada')], limit=1)
        etapa_asistida = self.env['cita.mantenimiento.etapa'].search([('name','=', 'Asistida')], limit=1)
        for cita in self:
            if cita.etapa_id.id == etapa_programada.id:
                cita.color =  3
            if cita.etapa_id.id == etapa_reagendada.id:
                cita.color = 4
            if cita.etapa_id.id == etapa_cancelada.id:
                cita.color = 1
            if cita.etapa_id.id == etapa_asistida.id:
                cita.color = 10
            else:
                cita.color = 0


    @api.depends('cliente_id','vehiculo_id')
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.vehiculo_id.vin_sn}-{record.cliente_id.display_name}"

    @api.depends('cliente_id')
    def _compute_datos_cliente(self):
        for cita in self:
            cita.nombre_cliente = cita.cliente_id.display_name
            cita.correo_cliente = cita.cliente_id.email
            cita.telefono_cliente = cita.cliente_id.phone

    def asistir_cita(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'asistir.cita',
            'name': 'Asistir citas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('cita_mantenimiento.asistir_cita_view_form').id,
            'context': {'default_cita_ids': self.ids}
        }

    def inasistencia_cita(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inasistencia.cita',
            'name': 'Inasistencia citas',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('cita_mantenimiento.inasistencia_cita_view_form').id,
            'context': {'default_cita_ids': self.ids}
        }

