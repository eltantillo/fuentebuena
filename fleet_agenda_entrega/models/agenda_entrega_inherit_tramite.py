from odoo import fields,models,api


class AgendaEntregaInheritTramite(models.Model):
    _inherit = 'fleet.tramite'

    @api.model
    def create(self, vals):
        res = super(AgendaEntregaInheritTramite, self).create(vals)
        estado_solicitado = self.env['agenda.entrega.etapa'].search([('name','=','Solicitado')])
        estado_confirmado = self.env['agenda.entrega.etapa'].search(['name','=','Confirmado'])
        if 'vehiculo_id' in vals and vals['vehiculo_id']:
            vehiculo = self.env['fleet.vehicle'].browse(vals['vehiculo_id'])
            if vehiculo:
                agenda = self.env['fleet.agenda'].search([('vehiculo_id','=',vehiculo.id),('etapa_id','in', [estado_solicitado.id,estado_confirmado.id])])
        # if 'expediente' in vals and vals['expediente']:
        #     res.message_post(body='✔️ Se subió un nuevo archivo al expediente.')
        # if 'folio' in vals and vals['folio']:
        return res