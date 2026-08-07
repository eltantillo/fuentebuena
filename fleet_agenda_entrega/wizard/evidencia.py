from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class EvidenciaWizard(models.TransientModel):
    _name = 'evidencia.wizard'

    foto_entrega = fields.Binary(
        string='Foto entrega',
        required=True,
    )
    autorizacion_uso_datos = fields.Boolean(
        string='Autorizacion Uso Datos'
    )
    eviencia_uso_datos = fields.Binary(
        string='Eviencia Uso Datos'
    )

    def insert_evidencia(self):
        active_id = self.env.context.get('active_id')
        agenda = self.env['agenda.entrega'].search([('id', '=', active_id)])
        agenda.write({
            'autorizacion_uso': self.autorizacion_uso_datos,
            'evidencia_autorizacion': self.eviencia_uso_datos,
            'foto_entrega': self.foto_entrega,
        })
        agenda.message_post(
            body="📂 Se actualizó o subió un nuevo archivo a la agenda",
        )

    @api.onchange('autorizacion_uso_datos')
    def _onchange_autorizacion_uso_datos(self):
        for record in self:
            if not record.autorizacion_uso_datos:
                record.eviencia_uso_datos = False