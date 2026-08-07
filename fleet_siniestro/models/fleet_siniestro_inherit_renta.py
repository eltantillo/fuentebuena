from odoo import fields,models,api

class FleetSiniestroInheritRenta(models.Model):
    _inherit = 'fleet.siniestro'

    aplica_renta_auxilio = fields.Selection(
        string='¿Aplica beneficio Renta Auxilio?',
        selection = [
            ('si','Si'),
            ('no','No')
        ]
    )

    #No existe renta auxilio
    motivo_id = fields.Many2one(
        comodel_name='fleet.siniestro.motivo.renta',
        string='Motivo',
    )
    detalles_motivo = fields.Text(
        string='Detalles de motivo',
    )

    #Existe renta auxilio
    renta_auxilio_id = fields.Many2one(
        comodel_name='fleet.siniestro.renta.auxilio.track',
        string='Renta Auxilio',
    )
    vehiculo_renta_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string="Vehículo renta",
        related = 'renta_auxilio_id.vehiculo_renta_id',
        store=True,
    )
    fecha_inicio = fields.Datetime(
        string="Fecha inicio",
        related='renta_auxilio_id.fecha_inicio',
        store=True,
    )
    fecha_final = fields.Datetime(
        string="Fecha final",
        related='renta_auxilio_id.fecha_final',
        store=True,
    )
    dias_renta = fields.Integer(
        string="Dias renta",
        related = 'renta_auxilio_id.dias_renta',
        store=True,
    )
    estado = fields.Selection(
        selection=[
            ('active','Activo'),
            ('finalizado','Finalizado'),
        ],
        related='renta_auxilio_id.estado',
        store=True,
    )
    mostrar_terminar_renta = fields.Boolean(
        string='Mostrar terminar renta',
        compute='_compute_terminar_renta_auxilio',
    )


    def return_terminar_renta_auxilio(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'terminar.renta.auxilio',
            'name': 'Terminar Renta Auxilio',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_siniestro.fleet_siniestro_terminar_renta_auxilio_form').id,
            'context': {'default_vehiculo_id': self.vehiculo_renta_id.id }
        }

    def _compute_terminar_renta_auxilio(self):
        etapa_prestado = self.env['fleet.vehicle.state'].search([('name','=','En préstamo')], limit=1)
        producto_renta = self.env['fleet.customer.producto'].search([('name','=','Renta Auxilio')], limit=1)
        for record in self:
            if record.vehiculo_renta_id.producto_id.id == producto_renta.id and record.vehiculo_renta_id.state_id.id == etapa_prestado.id:
                record.mostrar_terminar_renta = False
            else:
                record.mostrar_terminar_renta = True