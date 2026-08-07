from email.policy import default

from  odoo import fields, api, models


class AltaVehiculo(models.TransientModel):
    _name = 'alta.vehiculo'

    vin_sn = fields.Char(
        string="VIN SN"
    )
    num_motor = fields.Char(
        string="Número de Motor"
    )
    model_id = fields.Many2one(
        comodel_name='fleet.vehicle.model',
        string='Modelo'
    )
    version_id = fields.Many2one(
        comodel_name='fleet.customer.version',
        string='Versión'
    )
    year = fields.Char(
        string='Año'
    )
    color = fields.Char(
        string='Color'
    )
    es_gnv = fields.Boolean(
        string='Es GNV'
    )
    flotilla_id = fields.Many2one(
        comodel_name='fleet.customer.flotilla',
        string='Flotilla'
    )
    producto_id = fields.Many2one(
        comodel_name='fleet.customer.producto',
        string='Producto'
    )
    plaza_id = fields.Many2one(
        comodel_name='fleet.customer.plaza',
        string='Plaza'
    )
    estado_id = fields.Many2one(
        comodel_name='fleet.vehicle.state',
        string='Estado',
        default=lambda self: self.env['fleet.vehicle.state'].search([('name', '=', 'En registro')],limit=1).id,
        domain = [('name', '=', 'Alta')]
    )
    transmission = fields.Selection(
        [('manual', 'Manual'),
         ('automatic', 'Automatica')],
        string='Transmission',
    )

    def alta(self):
        sub_state = self.env['fleet.customer.sub.etapa'].search([('name','=', 'Alta')], limit=1)
        for record in self:
            record.env['fleet.vehicle'].create({
                'vin_sn': record.vin_sn,
                'transmission': record.transmission,
                'numero_motor': record.num_motor,
                'model_id': record.model_id.id,
                'version': record.version_id.id,
                'model_year': record.year,
                'color': record.color,
                'es_gnv': record.es_gnv,
                'flotilla_id': record.flotilla_id.id,
                'producto_id': record.producto_id.id,
                'plaza_id': record.plaza_id.id,
                'state_id': record.estado_id.id,
                'orden_compra_id': self.env.context.get('active_id'),
                'sub_etapa_id': sub_state.id,
                'proveedor_id': self.env.context.get('default_proveedor_id'),
            })