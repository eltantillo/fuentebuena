from odoo import fields,models,api


class GCRetencion(models.TransientModel):

    _name = 'gc.retencion'

    fecha_estimada_retencion = fields.Datetime(
        string='Fecha de Estimada',
    )
    motivo_retencion = fields.Text(
        string='Motivo de retención'
    )

    def confirmar(self):
        gestion = self.env['gestion.caido'].browse(self.env.context.get('default_gestion_id'))
        etapa_retenido = self.env['gestion.caido.estado'].search([('name','=', 'Retenido')])
        if gestion:
            gestion.registrar_evento("Vehículo retenido por el gestor")
            gestion.write({
                'estado_id': etapa_retenido.id ,
                'fecha_incio_retencion': fields.Datetime.now(),
                'fecha_estimada_retencion': self.fecha_estimada_retencion,
                'motivo_retencion': self.motivo_retencion,
                'mostrar_btn_lib_retencion': False,
                'mostrar_page_retencion': False,
            })