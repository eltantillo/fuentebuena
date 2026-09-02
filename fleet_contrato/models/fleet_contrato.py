from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
    clabe_pago = fields.Char(
        string='CLABE de pago',
        size=18,
        tracking=True
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Arrendatario',
        compute='_compute_cliente_id',
        store=True,
        readonly=False,
        tracking=True
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

    @api.constrains('clabe_pago')
    def _check_clabe_pago(self):
        for record in self:
            if record.clabe_pago and (len(record.clabe_pago) != 18 or not record.clabe_pago.isdigit()):
                raise ValidationError('La CLABE de pago debe tener exactamente 18 dígitos numéricos.')

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
    def _compute_cliente_id(self):
        """Propose the vehicle's driver, without overwriting a captured lessee.

        The lessee is the person who signed the contract and is not always the
        person driving, so the field is only filled in while it is empty: what
        the user captured wins over the vehicle.
        """
        for record in self:
            if not record.cliente_id:
                record.cliente_id = record.vehicle_id.driver_id

    @api.depends('vehicle_id.vin_sn',
                 'vehicle_id.numero_economico',
                 'vehicle_id.producto_id',
                 'vehicle_id.plaza_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = record.vehicle_id
            if vehiculo:
                record.vin_sn = vehiculo.vin_sn
                record.numero_economico = vehiculo.numero_economico
                record.producto_id = vehiculo.producto_id.id
                record.plaza_id = vehiculo.plaza_id.id
            else:
                record.vin_sn = False
                record.numero_economico = False
                record.producto_id = False
                record.plaza_id = False

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