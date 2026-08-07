from odoo import fields, models, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class RolesPiloteaInheritAgenda(models.Model):
    _inherit = "agenda.entrega"

    edicion_habilitada = fields.Boolean(
        string="Edicion Habilitada",
        compute="_compute_edicion_habilitada",
    )
    edicion_habilitada_credito = fields.Boolean(
        string="Edicion Habilitada Credito",
        compute="_compute_edicion_habilitada_credito",
    )
    edicion_habilitada_operacion = fields.Boolean(
        string="Edicion Habilitada Operacion",
        compute="_compute_edicion_habilitada_operacion",
    )
    edicion_etapa = fields.Boolean(
        string="Edicion Etapa",
        compute="_compute_edicion_habilitada_etapa",
    )
    motivo_cambio_hora_id = fields.Many2one(
        comodel_name='rp.motivo.cambio.agenda',
        string="Motivo cambio de hora",
    )

    def send_mail(self,res_id,email,name_template):
        template = self.env.ref(name_template)
        template.send_mail(
            res_id,
            force_send=True,
            email_values={
                'email_to': email
            }
        )

    def send_mail_users(self, plaza_id, flotilla_id, record, name_template):
        group_names = [
            'Gerente de operaciones',
            'Auxiliar/Analista operaciones',
            'Gerente comercial',
            'Director comercial'
        ]
        groups = self.env['res.groups'].search([('name', 'in', group_names)])
        users = self.env['res.users'].search([])
        if groups:
            users = users.filtered(lambda u: any(g.id in groups.ids for g in u.group_ids))
        if plaza_id:
            users = users.filtered(lambda u: plaza_id in u.plaza_ids.ids)
        if flotilla_id:
            users = users.filtered(lambda u: flotilla_id in u.flotilla_ids.ids)
        users = users.filtered(lambda u: u.email)
        emails = users.mapped('email')
        rol_tipo_agenda = self.env['roles.pilotea.exclusion.tipo'].search([('name','=','Agenda entrega')])
        if emails:
            datos = self.env['roles.pilotea.exclusion'].search_read([('tipo_exclusion_ids','in',[rol_tipo_agenda.id])], fields=['correo'])
            correos_excluir = []
            for registro in datos:
                correos_excluir.append(registro['correo'])
            emails = [e for e in emails if e not in correos_excluir]
            email_to = ','.join(emails)
            self.send_mail(record.id, email_to, name_template)


    def cambiar_hora(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Motivo de cambio',
            'res_model': 'cambiar.hora',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('roles_pilotea.cambiar_hora_view_form').id
        }

    def _compute_edicion_habilitada_etapa(self):
        for record in self:
            if record.etapa_id.id == 4 or record.etapa_id.id == 3:
                record.edicion_etapa = True
            else:
                record.edicion_etapa = False

    def _compute_edicion_habilitada(self):
        usuario_logueado = self.env.user
        for record in self:
            if record.etapa_id.id == 4 or record.etapa_id.id == 3:
                record.edicion_habilitada = True
            else:
                if usuario_logueado.has_group('roles_pilotea.group_gerente_comercial') or usuario_logueado.has_group('roles_pilotea.group_director_comercial'):
                    record.edicion_habilitada = False
                else:
                    record.edicion_habilitada = True

    def _compute_edicion_habilitada_credito(self):
        usuario_logueado = self.env.user
        for record in self:
            if record.etapa_id.id == 4 or record.etapa_id.id == 3:
                record.edicion_habilitada_credito = True
            else:
                if usuario_logueado.has_group('roles_pilotea.group_credito'):
                    record.edicion_habilitada_credito = False
                else:
                    record.edicion_habilitada_credito = True

    def _compute_edicion_habilitada_operacion(self):
        usuario_logueado = self.env.user
        for record in self:
            if record.etapa_id.id == 4 or record.etapa_id.id == 3:
                record.edicion_habilitada_operacion = True
            else:
                if usuario_logueado.has_group('roles_pilotea.group_gerente_operacion') or usuario_logueado.has_group('group_auxiliar_analista_operacion'):
                    record.edicion_habilitada_operacion = False
                else:
                    record.edicion_habilitada_operacion = True

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('skip_agenda_mail'):
            return super().create(vals_list)
        for vals in vals_list:
            vals['fecha_confirmada'] = vals.get('fecha_entrega')
        records = super().create(vals_list)
        for record in records:
            record.with_context(skip_agenda_mail=True).send_mail_users(
                record.plaza_id.id,
                record.producto_id.flotilla_id.id,
                record,
                'fleet_agenda_entrega.agenda_entrega_mail_template'
            )
            record.with_context(skip_agenda_mail=True).send_mail(
                record.id,
                'originacion.arrendamiento@fuentebuena.com',
                'fleet_agenda_entrega.agenda_entrega_mail_template'
            )
            record.with_context(skip_agenda_mail=True).send_mail(
                record.id,
                record.asesor_id.work_email,
                'fleet_agenda_entrega.agenda_entrega_mail_template'
            )
        return records

    def write(self, vals):
        if self.env.context.get('skip_agenda_mail'):
            return super().write(vals)
        fields_trigger = {
            'req_instrumentacion',
            'fecha_confirmada',
            'nota',
            'etapa_id'
        }
        etapa_value = vals.get('etapa_id')
        estatus_value = vals.get('estatus_comprobante_deposito')
        for rec in self:
            nuevo_req = vals.get('req_instrumentacion', rec.req_instrumentacion.id)
            nuevo_estatus = vals.get('estatus_comprobante_deposito', rec.estatus_comprobante_deposito.id)
            if etapa_value and etapa_value in [2, 3, 4]:
                if not (
                        self.env.user.has_group('roles_pilotea.group_gerente_operacion') or
                        self.env.user.has_group('roles_pilotea.group_auxiliar_analista_operacion')
                ):
                    if not (etapa_value == 4 and self.env.user.has_group('roles_pilotea.group_credito')):
                        raise ValidationError("Solo operaciones puede cambiar etapa")
                if etapa_value == 2 and nuevo_req != 1:
                    raise ValidationError("Req. instrumentación debe ser Correcto")
                if etapa_value == 3:
                    if not (nuevo_req == 1 and nuevo_estatus in [2, 4]):
                        raise ValidationError("Validaciones de entregado no cumplidas")
                if etapa_value == 4 and rec.etapa_id == 3:
                    raise ValidationError("No puedes cambiar de etapa 'Entregado a Cancelado'")
        res = super().write(vals)
        for rec in self:
            if etapa_value == 3:
                vehiculo = rec.vehiculo_id
                if vehiculo:
                    vehiculo.write({'state_id': 10})
                rec.fecha_confirmada = rec.fecha_entrega
                nombre = rec.dictamen_id.cliente
                cliente = self.env['res.partner'].search([('name', '=', nombre)], limit=1)
                if not cliente:
                    cliente = self.env['res.partner'].sudo().create({
                        'name': nombre,
                        'customer_rank': 1,
                        'es_cliente': True
                    })
                if vehiculo:
                    vehiculo.write({'driver_id': cliente.id})
            if estatus_value and estatus_value in [2, 4] and rec.req_instrumentacion.id == 1:
                rec.with_context(skip_agenda_mail=True).send_mail_users(
                    rec.plaza_id.id,
                    rec.producto_id.flotilla_id.id,
                    rec,
                    'fleet_agenda_entrega.agenda_entrega_deposito_valido_mail_template'
                )
                rec.with_context(skip_agenda_mail=True).send_mail(
                    rec.id,
                    'originacion.arrendamiento@fuentebuena.com',
                    'fleet_agenda_entrega.agenda_entrega_deposito_valido_mail_template'
                )
                rec.with_context(skip_agenda_mail=True).send_mail(
                    rec.id,
                    rec.asesor_id.work_email,
                    'fleet_agenda_entrega.agenda_entrega_deposito_valido_mail_template'
                )
            if fields_trigger.intersection(vals.keys()):
                rec.with_context(skip_agenda_mail=True).send_mail_users(
                    rec.plaza_id.id,
                    rec.producto_id.flotilla_id.id,
                    rec,
                    'fleet_agenda_entrega.agenda_entrega_actualizacion_mail_template'
                )
                rec.with_context(skip_agenda_mail=True).send_mail(
                    rec.id,
                    'originacion.arrendamiento@fuentebuena.com',
                    'fleet_agenda_entrega.agenda_entrega_actualizacion_mail_template'
                )
                rec.with_context(skip_agenda_mail=True).send_mail(
                    rec.id,
                    rec.asesor_id.work_email,
                    'fleet_agenda_entrega.agenda_entrega_actualizacion_mail_template'
                )
        return res