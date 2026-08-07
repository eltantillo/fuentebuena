from odoo import fields,models,api

class GCLiberarRetencion(models.TransientModel):

    _name = 'gc.liberar.retencion'

    etapa_destino_id = fields.Many2one(
        comodel_name='fleet.vehicle.state',
        string='Estado del vehiculo',
        domain=[('name','in', ['Reacondicionamiento','Rentado'])],
    )
    motivo_cancelacion_id = fields.Many2one(
        comodel_name='gestion.caido.razon.cancel',
        string='Motivo de cancelación'
    )
    mostrar_cancelacion = fields.Boolean(
        string='Mostrar cancelación',
        default=True,
    )

    @api.onchange('etapa_destino_id')
    def _onchange_mostrar_cancelacion(self):
        for record in self:
            if record.etapa_destino_id.name == 'Reacondicionamiento':
                record.mostrar_cancelacion = False
            else:
                record.mostrar_cancelacion = True
                record.motivo_cancelacion_id = False


    def confirmar(self):
        gestion = self.env['gestion.caido'].browse(self.env.context.get('default_gestion_id'))
        etapa_recuperado = self.env['gestion.caido.estado'].search([('name','=', 'Recuperado')], limit=1)
        etapa_recuperado_v = self.env['fleet.vehicle.state'].search([('name','=', 'Recuperado')], limit=1)
        if gestion:
            vals = {
                'estado_id': etapa_recuperado.id ,
                'etapa_destino_vehiculo_id': self.etapa_destino_id.id,
                'fecha_finalizacion_retencion': fields.Datetime.now(),
                'mostrar_btn_lib_retencion': True,
                'mostrar_btn_retencion': True,
                'mostrar_btn_cambio_etapa': True,
                'motivo_cancelacion_id': self.motivo_cancelacion_id.id,
            }
            if (self.env.context.get('default_type') == 'no_retencio'):
                vals['fecha_finalizacion_retencion'] = False
                gestion.write(vals)
            else:
                gestion.registrar_evento("Vehículo liberado de retención")
                gestion.write(vals)
            gestion.vehiculo_id.with_context(from_wizard=True).write({
                'btn_confirmar_recepcion': False,
                'state_id': etapa_recuperado_v.id
            })
            gestion.registrar_evento("Vehículo recuperado por el gestor")
            gestion.registrar_evento("Envió de notificación a Operaciones")
            gestion.registrar_evento("Esperando confirmación automática o manual")