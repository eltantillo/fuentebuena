from odoo import models, fields, api

CALIFICACION1 = [
    ('Bueno', 'Bueno'),
    ('Malo', 'Malo'),
]
CALIFICACION2 = [
    ('Optimo', 'Optimo'),
    ('Medio', 'Medio'),
    ('Bajo', 'Bajo'),
]

class FleetRecepcion(models.Model):
    _name = 'fleet.recepcion'
    _description = 'Fleet Recepcion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'

    condicion_vehiculo_id = fields.Many2one(
        comodel_name='fleet.customer.condicion.vehiculo',
        string='Condición del vehículo',
    )
    fecha_recepcion = fields.Datetime(
        string='Fecha de recepcion',
        default=fields.Datetime.now,
        tracking=True
    )
    lugar_recepcion_id = fields.Many2one(
        comodel_name='fleet.recepcion.lugar',
        string='Lugar de recepcion',
        tracking=True
    )
    permiso_provicional = fields.Boolean(
        string='Permiso provicional de circulacion',
    )
    "Vehiculo"
    vehiculo_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo',
        tracking=True
    )
    vin_sn = fields.Char(
        string='VIN',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    numero_economico = fields.Char(
        string='Número economico',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    modelo_id = fields.Many2one(
        comodel_name='fleet.vehicle.model',
        string='Modelo',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    ultimo_odometro = fields.Float(
        string='Ultimo odometro',
        compute='_compute_datos_vehiculo',
        store=True,
    )
    "Exterior frontal"
    exterior_frontal_faro = fields.Selection(
        selection=CALIFICACION1,
        string='Faros',
        tracking=True
    )
    exterior_frontal_faro_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_cofre = fields.Selection(
        selection=CALIFICACION1,
        string='Cofre',
        tracking=True
    )
    exterior_frontal_cofre_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_portaplaca = fields.Selection(
        selection=CALIFICACION1,
        string='Porta placa',
        tracking=True
    )
    exterior_frontal_portaplaca_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_tapon_liquido = fields.Selection(
        selection=CALIFICACION1,
        string='Tapones y nivel de liquido',
        tracking=True
    )
    exterior_frontal_tapon_liquido_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_varillaaceite = fields.Selection(
        selection=CALIFICACION1,
        string='Varilla de aceite',
        tracking=True
    )
    exterior_frontal_varillaaceite_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_nivelaceite = fields.Selection(
        selection=CALIFICACION2,
        string='Nivel de aceite',
        tracking=True
    )
    exterior_frontal_nivelaceite_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_anticongelante = fields.Selection(
        selection=CALIFICACION2,
        string='Anticongelante',
        tracking=True
    )
    exterior_frontal_anticongelante_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_liquidofrenos = fields.Selection(
        selection=CALIFICACION2,
        string='Líquido de frenos',
        tracking=True
    )
    exterior_frontal_liquidofrenos_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_facia = fields.Selection(
        selection=CALIFICACION1,
        string='Facia',
        tracking=True
    )
    exterior_frontal_facia_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_limpiador = fields.Selection(
        selection=CALIFICACION1,
        string='Limpiadores',
        tracking=True
    )
    exterior_frontal_limpiador_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_frontal_antena = fields.Selection(
        selection=CALIFICACION1,
        string='Antena',
        tracking=True
    )
    exterior_frontal_antena_observacion = fields.Char(
        string='Observaciones',
    )
    "Exterior trasero"
    exterior_trasero_cajuela = fields.Selection(
        selection=CALIFICACION1,
        string='Cajuela',
        tracking=True
    )
    exterior_trasero_cajuela_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_trasero_calavera = fields.Selection(
        selection=CALIFICACION1,
        string='Calaveras',
        tracking=True
    )
    exterior_trasero_calavera_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_trasero_defensa = fields.Selection(
        selection=CALIFICACION1,
        string='Defensa',
        tracking=True
    )
    exterior_trasero_defensa_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_trasero_llantaref_gato = fields.Selection(
        selection=CALIFICACION1,
        string='Llanta refacción y gato',
        tracking=True
    )
    exterior_trasero_llantaref_gato_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_trasero_refherramienta = fields.Selection(
        selection=CALIFICACION1,
        string='Reflejante y herramienta',
        tracking=True
    )
    exterior_trasero_refherramienta_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_trasero_portaplaca = fields.Selection(
        selection=CALIFICACION1,
        string='Porta placa',
        tracking=True
    )
    exterior_trasero_portaplaca_observacion = fields.Char(
        string='Observaciones',
    )
    "exterior lateral derecho"
    exterior_lat_derecho_espejo = fields.Selection(
        selection=CALIFICACION1,
        string='Espejo',
        tracking=True
    )
    exterior_lat_derecho_espejo_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_lat_derecho_costado = fields.Selection(
        selection=CALIFICACION1,
        string='Costado',
        tracking=True
    )
    exterior_lat_derecho_costado_observacion = fields.Char(
        string='Observaciones',
    )
    "exterior lateral izquierdo"
    exterior_lat_izquierdo_espejo = fields.Selection(
        selection=CALIFICACION1,
        string='Espejo',
        tracking=True
    )
    exterior_lat_izquierdo_espejo_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_lat_izquierdo_costado = fields.Selection(
        selection=CALIFICACION1,
        string='Costado',
        tracking=True
    )
    exterior_lat_izquierdo_costado_observacion = fields.Char(
        string='Observaciones',
    )
    exterior_lat_izquierdo_tapon = fields.Selection(
        selection=CALIFICACION1,
        string='Tapón de gasolina',
        tracking=True
    )
    exterior_lat_izquierdo_tapon_observacion = fields.Char(
        string='Observaciones',
    )
    "Interior frontal"
    interior_frontal_tablero = fields.Selection(
        selection=CALIFICACION1,
        string='Tablero de instrumentos',
        tracking=True
    )
    interior_frontal_tablero_observacion = fields.Char(
        string='Observaciones',
    )
    interior_frontal_estereo = fields.Selection(
        selection=CALIFICACION1,
        string='Estéreo',
        tracking=True
    )
    interior_frontal_estereo_observacion = fields.Char(
        string='Observaciones',
    )
    interior_frontal_clima = fields.Selection(
        selection=CALIFICACION1,
        string='Clima',
        tracking=True
    )
    interior_frontal_clima_observacion = fields.Char(
        string='Observaciones',
    )
    interior_frontal_espejo_retrovisor = fields.Selection(
        selection=CALIFICACION1,
        string='Espejo retrovisor',
        tracking=True
    )
    interior_frontal_espejo_retrovisor_observacion = fields.Char(
        string='Observaciones',
    )
    "Interiores"
    interiores = fields.Selection(
        selection=CALIFICACION1,
        string='Interiores',
        tracking=True
    )
    interiores_observacion = fields.Char(
        string='Observaciones',
    )
    tapetes = fields.Selection(
        selection=CALIFICACION1,
        string='Tapetes',
        tracking=True
    )
    tapetes_observacion = fields.Char(
        string='Observaciones',
    )
    vidrios = fields.Selection(
        selection=CALIFICACION1,
        string='Vidrios',
        tracking=True
    )
    vidrios_observacion = fields.Char(
        string='Observaciones',
    )
    birlos_seguridad = fields.Selection(
        selection=CALIFICACION1,
        string='Birlos de seguridad',
        tracking=True
    )
    birlos_seguridad_observacion = fields.Char(
        string='Observaciones',
    )
    "Entrega"
    persona_entrega = fields.Char(
        string='Persona que entrega',
        tracking=True
    )
    persona_entrega_firma = fields.Binary(
        string='Firma persona que entrega',
    )
    persona_recibe = fields.Many2one(
        comodel_name='hr.employee',
        string='Persona que recibe',
        tracking=True
    )
    persona_recibe_firma = fields.Binary(
        string='Firma persona que recibe',
    )
    "Cronos de fotos"
    foto_vin = fields.Binary(
        string='VIN',
        attachment=True
    )
    foto_toldo = fields.Binary(
        string='Toldo',
        attachment=True
    )
    foto_frente = fields.Binary(
        string='Frontal',
        attachment=True
    )
    foto_trasero = fields.Binary(
        string='Posterior',
        attachment=True
    )
    foto_lateral_derecho = fields.Binary(
        string='Lateral derecho',
        attachment=True
    )
    foto_lateral_izquierdo = fields.Binary(
        string='Lateral izquierdo',
        attachment=True
    )
    rec_name = fields.Char(
        string='rec_name',
        compute='_compute_rec_name'
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.model
    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.vin_sn}-{record.lugar_recepcion_id.name}"

    @api.depends('vehiculo_id')
    def _compute_datos_vehiculo(self):
        for record in self:
            vehiculo = self.env['fleet.vehicle'].browse(record.vehiculo_id.id)
            record.vin_sn = vehiculo.vin_sn
            record.numero_economico = vehiculo.numero_economico
            record.producto_id = vehiculo.producto_id.id
            record.plaza_id = vehiculo.plaza_id.id
            record.modelo_id = vehiculo.model_id.id
            record.ultimo_odometro = vehiculo.odometer

    def action_open_recepcion(self):
        return {
            'type': 'ir.actions.client',
            'name': 'Recepcion de vehículos',
            'tag': 'factura_recepcion_invoice_action',
            'target': 'main'
        }