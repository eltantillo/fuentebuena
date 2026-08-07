from odoo import fields, models, api


class AgendaEntregaEvento(models.Model):
    _name = "agenda.entrega.evento"
    _description = "Agenda Entrega Evento"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "rec_name"

    agenda_id = fields.Many2one(
        comodel_name="agenda.entrega",
        string="Agenda"
    )
    tipo_evento_id = fields.Many2one(
        comodel_name="agenda.entrega.tipo.evento",
    )
    descripcion = fields.Text(
        string="Descripción",
        tracking=True
    )
    status_id = fields.Many2one(
        comodel_name="agenda.entrega.estatus.evento",
        string="Estatus de evento",
        domain="[('id', 'in', [1,2,4])]",
        tracking=True
    )
    mostrar_status = fields.Boolean(
        string="Mostrar status",
        compute="_compute_mostrar_status",
    )
    estatus_id = fields.Many2one(
        comodel_name="agenda.entrega.estatus.evento",
        string="Estatus de evento",
        domain="[('id', '=', 3)]",
        tracking=True
    )
    mostrar_estatus = fields.Boolean(
        string="Mostrar estatus",
        compute="_compute_mostrar_status",
    )
    descripcion_solventacion = fields.Text(
        string="Descripción de Solventación",
        tracking=True
    )
    incidencia_id = fields.Many2one(
        comodel_name="agenda.entrega.evento",
        string="Incidencia",
    )

    rec_name = fields.Char(
        string="Nombre del evento",
        compute="_compute_rec_name",
    )

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.tipo_evento_id.name}-{record.status_id.name}"


    @api.depends("status_id")
    def _compute_mostrar_status(self):
        etapa_pendiente = self.retornar_etapa_id('Pendiente')
        etapa_solventado = self.retornar_etapa_id('Solventado')
        etapa_atendido = self.retornar_etapa_id('Atendido')
        etapa_reincidencia = self.retornar_etapa_id('Reincidencia')
        for evento in self:
            if evento.status_id.id in [etapa_pendiente,etapa_solventado,etapa_atendido]:
                evento.mostrar_status = True
                evento.mostrar_estatus = False
            else:
                if evento.status_id.id == etapa_reincidencia:
                    evento.mostrar_estatus = True
                    evento.mostrar_status = False
                else:
                    evento.mostrar_status = False
                    evento.mostrar_estatus = True

    def retornar_etapa_id(self, name):
        etapa = self.env['agenda.entrega.estatus.evento'].search([('name','=', name)])
        return etapa.id


    def action_solventar(self):
        for record in self:
            etapa = self.retornar_etapa_id('Solventado')
            record.status_id = etapa

    def action_atender(self):
        return  {
            'type': 'ir.actions.act_window',
            'name': 'Solventar',
            'res_model': 'evento.solventar.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_agenda_entrega.solventar_view_form').id
        }

    def action_reincidencia(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'agenda.entrega.evento.wizard',
            'name': 'Evento',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('fleet_agenda_entrega.evento_view_form').id,
            'context': {
                'id_incidencia': self.id,
                'agenda_id': self.agenda_id.id
            }
        }