from odoo import fields, models, api,_
import logging

_logger = logging.getLogger(__name__)

class RolesPiloteaInheritEvento(models.Model):
    _inherit = 'agenda.entrega.evento'

    edicion_habilitada = fields.Boolean(
        string="Edicion Habilitada Credito",
        compute="_compute_edicion_habilitada",
    )

    def _compute_edicion_habilitada(self):
        usuario_logueado = self.env.user
        for record in self:
            if not usuario_logueado.has_group('roles_pilotea.group_gerente_operacion') or not usuario_logueado.has_group('roles_pilotea.group_auxiliar_analista_operacion'):
                record.edicion_habilitada = False
            else:
                record.edicion_habilitada = True

    @api.model
    def create(self, vals):
        record = super(RolesPiloteaInheritEvento, self).create(vals)
        titulo = "Se ha creado un evento"
        mensaje = f"Evento nuevo en: {record.agenda_id}"
        record.notificar_usuario(titulo, mensaje, 'roles_pilotea.group_gerente_operacion')
        return record

    def notificar_usuario(self,titulo,mensaje,grupo_notificacion):
        plaza_registro = self.agenda_id.plaza_id.id
        group_names = [
            'Gerente de operaciones',
            'Auxiliar/Analista operaciones',
        ]
        groups = self.env['res.groups'].search([('name', 'in', group_names)])
        users = self.env['res.users'].search([])
        if groups:
            users = users.filtered(lambda u: any(g.id in groups.ids for g in u.group_ids))
        if plaza_registro:
            users = users.filtered(lambda u: plaza_registro in u.plaza_ids.ids)
        users = users.filtered(lambda u: 1 in u.flotilla_ids.ids)
        rol_tipo_agenda = self.env['roles.pilotea.exclusion.tipo'].search([('name','=','Agenda entrega')])
        datos = self.env['roles.pilotea.exclusion'].search_read([('tipo_exclusion_ids','in',[rol_tipo_agenda.id])], fields=['correo'])
        correos_excluir = []
        for registro in datos:
            correos_excluir.append(registro['correo'])
        users = [u for u in users if u.login not in correos_excluir]
        for user in users:
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get_id(self._name),
                'res_id': self.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _(titulo),
                'note': _(mensaje),
                'user_id': user.id,
                'date_deadline': fields.Date.today(),
            })

    def action_solventar(self):
        res = super().action_solventar()
        for record in self:
            record.notificar_usuario("Evento solventado","El evento ha sido solventado con exito",'roles_pilotea.group_gerente_operacion')
        return res

    def action_atender(self):
        res = super().action_atender()
        for record in self:
            record.notificar_usuario("Evento atendido","El evento ha sido atendido con exito",'roles_pilotea.group_credito')
        return res