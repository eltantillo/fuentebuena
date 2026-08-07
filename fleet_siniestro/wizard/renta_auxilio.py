

from odoo import fields,models,api
import logging
_logger = logging.getLogger(__name__)

class RentaAuxilio(models.TransientModel):
    _name = 'renta.auxilio'


    aplica_renta_auxilio = fields.Selection(
        string='¿Aplica beneficio Renta Auxilio?',
        selection = [
            ('si','Si'),
            ('no','No')
        ]
    )
    motivo = fields.Text(
        string='Motivo',
    )
    motivo_id = fields.Many2one(
        comodel_name='fleet.siniestro.motivo.renta',
        string='Motivo',
    )
    detalles_motivo = fields.Text(
        string='Detalles de motivo',
    )
    etapa_id = fields.Many2one(
        string='Etapa',
        comodel_name='fleet.vehicle.state',
        compute='_compute_etapa_id',
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto',
        compute='_compute_producto_id',
    )
    vehiculo_id = fields.Many2one(
        string='Vehículo',
        comodel_name='fleet.vehicle',
    )
    vehiculos_renta_ids = fields.Many2many(
        comodel_name='fleet.vehicle',
        compute='_compute_vehiculos_renta_ids',
    )
    tipo_rent_aux = fields.Many2one(
        string='Tipo de renta auxilio',
        comodel_name='renta.auxilio.tipo',
    )
    motrar_tipo = fields.Boolean(
        string='Motrar Tipo',
        compute="_compute_mostrar_tipo"
    )
    siniestro_id = fields.Many2one(
        comodel_name='fleet.siniestro',
        string='Siniestro',
    )
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
    )
    mostrar_aplica_renta = fields.Boolean(
        string="Mostrar Aplica Renta Auxilio",
        compute='_compute_mostrar_aplica_renta'
    )
    vehiculo_original_id = fields.Many2one(
        string='Vehículo original',
        comodel_name='fleet.vehicle',
        default=False
    )
    siniestros_aplicables_ids = fields.Many2many(
        string='Siniestros a los que aplica',
        comodel_name='fleet.siniestro',
    )
    mostrar_seleccionar_siniestro = fields.Boolean(
        string='Mostrar Siniestro',
        compute='_compute_mostrar_seleccionar_siniestro'
    )

    @api.onchange('cliente_id')
    def _onchange_vehiculo_id(self):
        if self.cliente_id:
            vehiculos = self.env['fleet.vehicle'].search([('driver_id', '=', self.cliente_id.id)])
            if len(vehiculos) > 1:
                self.vehiculo_original_id = False
            else:
                self.vehiculo_original_id = vehiculos
        else:
            self.vehiculo_original_id = False


    @api.onchange('vehiculo_original_id','tipo_rent_aux')
    def _onchange_vehiculo_original_id(self):
        siniestro_robo = self.env['fleet.siniestro.tipo'].search([('name','=', 'Robo')], limit=1)
        siniestros = self.env['fleet.siniestro.tipo'].search([('name','in', ['Colisión','Fenómenos naturales'])])
        _logger.info("===========On changes ===============")
        _logger.info(f"Valor de tipo:  {self.tipo_rent_aux.name}")
        if self.vehiculo_original_id:
            if self.tipo_rent_aux.name == 'Siniestro':
                _logger.info(f"Entra a SIniestro")
                siniestros_ap = self.env['fleet.siniestro'].search([('vehiculo_id','=', self.vehiculo_original_id.id),('siniestro_tipo_id','in', siniestros.ids)])
                if siniestros_ap:
                    self.siniestros_aplicables_ids = siniestros_ap.ids
                else:
                    self.siniestros_aplicables_ids = False
            elif self.tipo_rent_aux.name == 'Robo':
                _logger.info(f"Entra a Robo")
                siniestros_ap = self.env['fleet.siniestro'].search([('vehiculo_id','=', self.vehiculo_original_id.id),('siniestro_tipo_id','=', siniestro_robo.id)])
                if siniestros_ap:
                    self.siniestros_aplicables_ids = siniestros_ap.ids
                else:
                    self.siniestros_aplicables_ids = False
            else:
                _logger.info("Entra al false que engloba falla mecanica")
                self.siniestros_aplicables_ids = False
        else:
            self.siniestros_aplicables_ids = False

    @api.depends('tipo_rent_aux')
    def _compute_mostrar_seleccionar_siniestro(self):
        _logger.info("Compute _compute_mostrar_seleccionar_siniestro")
        if self.tipo_rent_aux:
            _logger.info(f"Entra mostrar seleccionar: {self.tipo_rent_aux.name}")
            if self.tipo_rent_aux.name in ['Siniestro', 'Robo']:
                _logger.info(f"Entra a SIniestro o Robo")
                self.mostrar_seleccionar_siniestro = False
            else:
                _logger.info(f"No Entra a SIniestro o Robo")
                self.mostrar_seleccionar_siniestro = True
        else:
            _logger.info("NO hay tipo de renta")
            self.mostrar_seleccionar_siniestro = True



    def _compute_mostrar_aplica_renta(self):
        siniestro_id = self.env.context.get('default_siniestro_id')
        if siniestro_id:
            self.mostrar_aplica_renta = False
        else:
            self.mostrar_aplica_renta = True

    def _compute_mostrar_tipo(self):
        siniestro_id = self.env.context.get('default_siniestro_id')
        if siniestro_id:
            self.motrar_tipo = True
        else:
            self.motrar_tipo = False

    def _compute_vehiculos_renta_ids(self):
        etapa_disponible = self.env['fleet.vehicle.state'].search([('name','=', 'Disponible')])
        producto_renta_aux = self.env['fleet.customer.producto'].search([('name', '=', 'Renta Auxilio')])
        vehiculos = self.env['fleet.vehicle'].search([('state_id', '=', etapa_disponible.id),
             ('producto_id', '=', producto_renta_aux.id),
             ('plaza_id', '=', self.env.context.get('default_plaza_id'))]
        )
        for record in self:
            record.vehiculos_renta_ids = vehiculos.ids


    def _compute_etapa_id(self):
        etapa_renta_auxilio = self.env['fleet.vehicle.state'].search([('name', '=', 'En préstamo')])
        for record in self:
            if etapa_renta_auxilio:
                record.etapa_id = etapa_renta_auxilio.id
            else:
                record.etapa_id = False

    def _compute_producto_id(self):
        producto_renta_auxilio = self.env['fleet.customer.producto'].search([('name', '=', 'Renta Auxilio')])
        for record in self:
            if producto_renta_auxilio:
                record.producto_id = producto_renta_auxilio.id
            else:
                record.producto_id = False

    def create_renta_aux(self,diccionario):
        new = self.env['fleet.siniestro.renta.auxilio.track'].create(diccionario)
        return new

    def action_renta_auxilio(self):
        siniestro = self.env['fleet.siniestro'].browse(self.env.context.get('default_siniestro_id'))
        if siniestro:
            if siniestro.siniestro_tipo_id.name in ['Colisión','Fenómenos naturales']:
                tipo_siniestro = self.env['renta.auxilio.tipo'].search([('name','=','Siniestro')])
                self.tipo_rent_aux = tipo_siniestro.id
            elif siniestro.siniestro_tipo_id.name == 'Robo':
                tipo_siniestro = self.env['renta.auxilio.tipo'].search([('name', '=', 'Robo')])
                self.tipo_rent_aux = tipo_siniestro.id
            if self.aplica_renta_auxilio == 'si':
                siniestro.motivo_id = False
                siniestro.detalles_motivo = False
                registro = self.env['fleet.siniestro.renta.auxilio.track'].search([('vehiculo_renta_id','=',self.vehiculo_id.id),('estado','=', 'active')])
                if not registro:
                    dict = {
                        'vehiculo_siniestro_id': self.env.context.get('default_vehiculo_siniestro_id'),
                        'vehiculo_renta_id': self.vehiculo_id.id,
                        'fecha_inicio': fields.Datetime.now(),
                        'estado': 'active',
                        'conductor_id': self.env.context.get('default_cliente_siniestro_id'),
                        'fleet_siniestro_id': siniestro.id,
                        'tipo_id': self.tipo_rent_aux.id,
                    }
                    renta = self.create_renta_aux(dict)
                    self.vehiculo_id.state_id = self.etapa_id.id
                    self.vehiculo_id.driver_id = self.env.context.get('default_cliente_siniestro_id')
                    siniestro.renta_auxilio_id = renta.id
                    siniestro.aplica_renta_auxilio = self.aplica_renta_auxilio
            elif self.aplica_renta_auxilio == 'no':
                siniestro.aplica_renta_auxilio = self.aplica_renta_auxilio
                siniestro.motivo_id = self.motivo_id.id
                siniestro.detalles_motivo = self.detalles_motivo