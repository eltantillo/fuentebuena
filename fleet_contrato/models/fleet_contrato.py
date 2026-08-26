from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class FleetContrato(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
    _description = 'Módulo personalizado para registrar los contratos para los vehículos'
    _rec_name = 'rec_name'
    _order = 'id desc'

    cie = fields.Char(
        string='CIE',
        tracking=True
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        compute='_compute_datos_vehiculo',
        store=True,
        tracking=True
    )
    nombre_cliente = fields.Char(
        string='Nombre del cliente',
    )
    num_plazos = fields.Integer(
        string='N° de plazos'
    )
    condicion_vehiculo_id = fields.Many2one(
        comodel_name='fleet.contrato.condicion.vehiculo',
        string='Condición del vehículo',
    )
    id_solicitud = fields.Char(
        string='ID de solicitud'
    )
    "Cancelación"
    fecha_cancelacion = fields.Date(
        string='Fecha de cancelación',
        tracking=True
    )
    motivo_cancelacion_id = fields.Many2one(
        comodel_name='fleet.contrato.motivo.cancelacion',
        string='Motivo de cancelación'
    )
    cancelado = fields.Boolean(
        string='Cancelado'
    )
    rec_name = fields.Char(
        string='rec_name',
        compute='_compute_rec_name',
    )
    "Importes"
    importe_garantia = fields.Float(
        string='Importe de garantia',
        tracking=True
    )
    "Información del vehiculo"
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
    "Documentos"
    attach_contrato = fields.Binary(
        string='Contrato',
        attachment=True,
    )
    attach_contrato_filename = fields.Char(
        string='Nombre del archivo',
    )
    user_landing_id = fields.Char(
        string='Id user landin',
    )
    nombre_relacional = fields.Char(
        string="Nombre relacional",
    )
    name = fields.Char(
        string="Name"
    )
    existe_attach_contrato = fields.Boolean(
        string='Existe archivo de contrato',
        compute='_compute_existe_contrato',
        store=True
    )
    estado_vigencia = fields.Selection(
        selection=[
            ('vigente', 'Vigente'),
            ('vencido', 'Vencido'),
            ('falta_subir', 'Falta subir'),
        ],
        string='Estado',
        compute='_compute_estado_vigencia',
        store=True,
    )

    @api.depends('existe_attach_contrato', 'state', 'expiration_date')
    def _compute_estado_vigencia(self):
        today = fields.Date.today()
        for record in self:
            if not record.existe_attach_contrato:
                record.estado_vigencia = 'falta_subir'
            elif record.state != 'open' or (record.expiration_date and record.expiration_date < today):
                record.estado_vigencia = 'vencido'
            else:
                record.estado_vigencia = 'vigente'

    @api.depends('attach_contrato')
    def _compute_existe_contrato(self):
        if not self.ids:
            for record in self:
                record.existe_attach_contrato = False
            return
        self.env.cr.execute("""
            SELECT res_id 
            FROM ir_attachment 
            WHERE res_model = %s AND res_field = 'attach_contrato' AND res_id IN %s
        """, (self._name, tuple(self.ids)))
        ids_con_archivo = {row[0] for row in self.env.cr.fetchall()}
        for record in self:
            record.existe_attach_contrato = record.id in ids_con_archivo

    @api.model
    def create(self, vals):
        contrato = self.search_count([('vehicle_id', '=', vals['vehicle_id'])])
        if contrato == 0:
            vals['condicion_vehiculo_id'] = 1
        else:
            vals['condicion_vehiculo_id'] = 2
        res = super(FleetContrato, self).create(vals)
        if 'attach_contrato' in vals and vals['attach_contrato']:
            res.message_post(body='✔️ Se subió un nuevo archivo al expediente.')
        return res

    @api.model
    def create_custom(self, vals):
        res = super(FleetContrato, self).create(vals)
        return res

    def cancelar_contrato(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancelación de contrato',
            'res_model': 'fleet.contrato.cancelacion',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_contrato.fleet_contrato_cancelacion_view_form').id
        }

    def attach_contrato_asignar(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attach de contrato',
            'res_model': 'fleet.contrato.attach',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_contrato.fleet_contrato_attach_view_form').id
        }

    @api.depends('vehicle_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = self.env['fleet.vehicle'].browse(record.vehicle_id.id)
            if vehiculo:
                record.vin_sn = vehiculo.vin_sn
                record.numero_economico = vehiculo.numero_economico
                record.producto_id = vehiculo.producto_id.id
                record.plaza_id = vehiculo.plaza_id.id
                record.cliente_id = vehiculo.driver_id.id
            else:
                record.vin_sn = False
                record.numero_economico = False
                record.producto_id = False
                record.plaza_id = False
                record.cliente_id = False

    @api.model
    def write(self, vals):
        if 'attach_contrato' in vals:
            if vals['attach_contrato']:
                self.message_post(body='📂 Se actualizó o subió un nuevo archivo al expediente.')
            else:
                self.message_post(body='🗑️ Se elimino el archivo del expediente.')
        res = super(FleetContrato, self).write(vals)
        return res


    def write_custom(self, vals):
        res = super(FleetContrato, self).write(vals)
        return res

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.vin_sn}-{record.ins_ref}"