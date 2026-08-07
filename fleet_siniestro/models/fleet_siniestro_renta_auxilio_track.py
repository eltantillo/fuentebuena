from odoo import fields,models,api


class FleetSiniestroRentaAuxilioTrack(models.Model):
    _name = 'fleet.siniestro.renta.auxilio.track'
    _description = 'Fleet Siniestro Auxilio Tracking'
    _order = 'fecha_inicio desc'

    tipo_id = fields.Many2one(
        comodel_name='renta.auxilio.tipo',
        string="Tipo",
    )
    vehiculo_siniestro_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehículo siniestro'
    )
    vehiculo_renta_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string="Vehículo renta"
    )
    conductor_id  = fields.Many2one(
        comodel_name='res.partner',
        string="Conductor"
    )
    fecha_inicio = fields.Datetime(
        string="Fecha inicio"
    )
    fecha_final = fields.Datetime(
        string="Fecha final"
    )
    dias_renta = fields.Integer(
        string="Dias renta",
        compute='_compute_dias_renta',
        store=True,
    )
    estado = fields.Selection(
        selection=[
            ('active','Activo'),
            ('finalizado','Finalizado'),
        ]
    )
    fleet_siniestro_id = fields.Many2one(
        comodel_name='fleet.siniestro',
        string='Fleet Siniestro',
    )



    @api.depends('fecha_inicio','fecha_final')
    def _compute_dias_renta(self):
        for record in self:
            record.dias_renta = 0
            if record.fecha_inicio and record.fecha_final:
                resul = record.fecha_final - record.fecha_inicio
                record.dias_renta = resul.days