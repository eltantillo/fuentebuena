from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.http import request
import json
import urllib.request
import urllib.error
import logging

_logger = logging.getLogger(__name__)

msg_doble_autorizacion = "Se requiere doble autorización, envíela para su aprobación"
msg_aprobacion = "Se necesita la autorización de: "
msg_monto_rebazado = "Debido a que esta factura supera el monto autorizado, se requiere enviarla para su aprobación."
msg_sin_permiso = "No tienes permisos para validar esta factura"
msg_proveedor_no_confirmado = "Debido a que el proveedor no ha sido confirmado, la factura no puede ser confirmada."
msg_proveedo_no_confirmado_apb = "Debido a que el proveedor no ha sido confirmado, la factura no puede ser enviada a aprobación."


class FacturaContabilidad(models.Model):
    _inherit = 'account.move'
    _description = (
        'Herencia para modificar el comportamiento general de facturas, añadiendo la posibilidad de aprobación y adicionado a esto'
        'el envío de facturas a epicor'
    )

    etapa_aprobacion = fields.Selection(
        selection=[
            ('sin_solicitar', 'Sin solicitar'),
            ('pendiente', 'Pendiente de aprobación'),
            ('aprobada', 'Aprobada')
        ],
        string='Estado de aprobación',
        default='sin_solicitar',
        tracking=True
    )
    factura_epicor = fields.Boolean(
        string='¿Es factura con proveedor recurrente?',
        default=False
    )
    aprobacion_gerente = fields.Boolean(
        string='Aprobada por gerente',
    )
    aprobacion_director = fields.Boolean(
        string='Aprobada por director',
    )
    btn_disponible_usuario = fields.Boolean(
        string='Disponible',
        default=False
    )
    btn_disponible_gerente = fields.Boolean(
        string='Disponible',
        default=False
    )
    btn_disponible_director = fields.Boolean(
        string='Disponible',
        default=True
    )
    motivo_cancelacion = fields.Many2one(
        comodel_name='factura.motivo.cancelacion',
        string='Motivo de cancelación',
    )
    factura_para_aprobacion = fields.Boolean(
        string='Factura para aprobación',
        default=False
    )
    proveedor_sin_confirmar = fields.Boolean(
        string='Proveedor sin confirmar',
        default=False
    )
    factura_para_confirmar = fields.Boolean(
        string='Factura para confirmar',
        default=False
    )
    factura_para_aprobacion_gerente = fields.Boolean(
        string='Factura para aprobación gerente',
        default=False
    )


    def notificar_todas(self):
        for factura in self:
            if factura.factura_para_aprobacion == True:
                factura.action_notificar()

    def action_notificar(self):
        for factura in self:
            if factura.factura_epicor == True:
                rfc_factura = factura.partner_id.vat
                proveedor = self.env['res.partner'].search([('vat', '=', rfc_factura)])
                if proveedor.etapa == 'confirmado':
                    self.proveedor_sin_confirmar = False
                    factura.notificar()
                else:
                    self.proveedor_sin_confirmar = True
                    return self.mostrar_mensaje(msg_proveedo_no_confirmado_apb)
            else:
                factura.notificar()
                if factura.factura_para_aprobacion == True:
                    factura.write({'factura_para_aprobacion': False})
                if factura.factura_para_aprobacion_gerente == True:
                    factura.write({'factura_para_aprobacion_gerente': False})

    def notificar(self):
        self.write({'etapa_aprobacion': 'pendiente'})
        if self.create_uid.has_group('factura.group_accountant_director'):
            self.write({'btn_disponible_director': True})
            self.write({'btn_disponible_gerente': False})
            self.write({'btn_disponible_usuario': False})
        if self.create_uid.has_group('factura.group_accountant_gerente'):
            self.write({'btn_disponible_gerente': False})
            self.write({'btn_disponible_director': True})
            self.write({'btn_disponible_usuario': False})
        if self.create_uid.has_group('factura.group_accountant_usuario_factura'):
            self.write({'btn_disponible_usuario': False})
            self.write({'btn_disponible_gerente': True})
            self.write({'btn_disponible_director': True})
        empleado_creador = self.create_uid.employee_id
        if not empleado_creador:
            raise UserError(_("El creador de la factura no tiene un empleado asignado."))
        jefe = empleado_creador.parent_id
        if not jefe or not jefe.user_id:
            raise UserError(_("El jefe directo del creador no está asignado o no tiene usuario."))
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('account.move'),
            'res_id': self.id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': _('Factura pendiente de aprobación'),
            'note': _('Esta factura está marcada como pendiente de aprobación.'),
            'user_id': jefe.user_id.id,
            'date_deadline': fields.Date.today(),
        })
        empleado = self.create_uid.employee_id
        jefe = empleado.parent_id
        template = self.env.ref('account.notificar_factura')
        template.send_mail(self.id, force_send=True, email_values={
            'email_to': jefe.email,
        })

    def action_cancelar(self):
        for factura in self:
            factura.factura_para_confirmar = False
            factura.factura_para_aprobacion = False
            factura.factura_para_aprobacion_gerente = False
            factura.btn_disponible_gerente = False
            factura.btn_disponible_director = False
            factura.btn_disponible_usuario = False
            factura.button_cancel()

    def action_borrador(self):
        for factura in self:
            factura.factura_para_confirmar = False
            factura.factura_para_aprobacion = False
            factura.aprobacion_gerente = False
            factura.aprobacion_director = False
            factura.btn_disponible_director = False
            factura.btn_disponible_gerente = False
            factura.btn_disponible_usuario = False
            factura.button_draft()

    def obtener_monto(self, grupo):
        monto = self.env['factura.monto.autorizado'].search([('grupo', '=', grupo)])
        return monto

    def retornar_dominio(self,tipo,user):
        dominio = []
        if tipo == 'usuario':
            dominio = [
                ('create_uid', '=', user.id)
            ]
        elif tipo == 'gerente_director':
            dominio = ['|',
                       ('create_uid', '=', user.id),
                       ('create_uid.employee_id', 'child_of', user.employee_id.id)
            ]
        elif tipo == 'all':
            dominio = []
        return dominio

    def action_notificar_gerente(self):
        return self.action_notificar()


    @api.model
    def validar_aprobaciones_proveedor(self,tipo):
        usuario_logueado = self.env.user
        dominio = self.retornar_dominio(tipo,usuario_logueado)
        facturas = self.env['account.move'].search([('state', '=', 'draft'),('move_type', '=', 'in_invoice'),*dominio])
        for factura in facturas:
            if factura.factura_epicor == True:
                rfc_factura = factura.partner_id.vat
                proveedor = self.env['res.partner'].search([('vat', '=', rfc_factura)])
                if proveedor.etapa == 'confirmado':
                    factura.write({'proveedor_sin_confirmar': False})
                else:
                    factura.write({'proveedor_sin_confirmar': True})
                    factura.write({'factura_para_confirmar': False})
                    factura.write({'factura_para_aprobacion': False})
                    factura.write({'factura_para_aprobacion_gerente': False})
                    if usuario_logueado.has_group('factura.group_accountant_director'):
                        factura.write({'btn_disponible_director': False})
                    elif usuario_logueado.has_group('factura.group_accountant_gerente'):
                        factura.write({'btn_disponible_gerente': False})
                    elif usuario_logueado.has_group('factura.group_accountant_usuario_factura'):
                        factura.write({'btn_disponible_usuario': False})

    @api.model
    def validar_aprobaciones_por_solicitar(self,tipo):
        usuario_logueado = self.env.user
        dominio = self.retornar_dominio(tipo,usuario_logueado)
        facturas = self.env['account.move'].search([('state', '=', 'draft'), ('move_type', '=', 'in_invoice'),*dominio])

        monto_usuario = self.obtener_monto('usuario_factura')
        monto_gerente = self.obtener_monto('gerente')
        monto_director = self.obtener_monto('director')
        for factura in facturas:
            if usuario_logueado.has_group('factura.group_accountant_usuario_factura'):
                if factura.amount_total > monto_usuario.monto_autorizado:
                    if factura.etapa_aprobacion == 'sin_solicitar':
                        factura.write({'factura_para_aprobacion': True})
                        factura.write({'factura_para_confirmar': False})
                else:
                    factura.write({'factura_para_aprobacion': False})
                    factura.write({'btn_disponible_usuario': True})
                    factura.write({'factura_para_confirmar': True})
            elif usuario_logueado.has_group('factura.group_accountant_gerente'):
                if factura.amount_total > monto_gerente.monto_autorizado:
                    if factura.etapa_aprobacion == 'sin_solicitar':
                        factura.write({'factura_para_aprobacion_gerente': True})
                else:
                    if factura.create_uid.has_group('factura.group_accountant_usuario_factura'):
                        if factura.factura_para_confirmar == True:
                            factura.write({'btn_disponible_gerente': True})
                        else:
                            if factura.etapa_aprobacion == 'sin_solicitar':
                                factura.write({'btn_disponible_gerente': False})
                                factura.write({'factura_para_aprobacion_gerente': False})
                            elif factura.etapa_aprobacion == 'pendiente':
                                factura.write({'btn_disponible_gerente': True})
                    elif factura.create_uid.has_group('factura.group_accountant_gerente'):
                        factura.write({'factura_para_aprobacion_gerente': False})
                        factura.write({'factura_para_confirmar': True})
                        factura.write({'btn_disponible_gerente': True})
            elif usuario_logueado.has_group('factura.group_accountant_director'):
                if factura.amount_total > monto_director.monto_autorizado:
                    if factura.etapa_aprobacion == 'sin_solicitar':
                        factura.write({'factura_para_aprobacion': True})
                else:
                    if factura.create_uid.has_group('factura.group_accountant_usuario_factura'):
                        if factura.etapa_aprobacion == 'sin_solicitar':
                            factura.write({'btn_disponible_director': False})
                        else:
                            if factura.amount_total < monto_gerente.monto_autorizado:
                                factura.write({'btn_disponible_director': True})
                            else:
                                factura.write({'btn_disponible_director': True})
                    elif factura.create_uid.has_group('factura.group_accountant_gerente'):
                        if factura.etapa_aprobacion == 'sin_solicitar':
                            factura.write({'btn_disponible_director': False})
                        else:
                            if factura.etapa_aprobacion == 'pendiente':
                                factura.write({'btn_disponible_director': True})
                    elif factura.create_uid.has_group('factura.group_accountant_director'):
                        if factura.amount_total > monto_director.monto_autorizado:
                            factura.write({'btn_disponible_director': False})
                        else:
                            factura.write({'factura_para_aprobacion': False})
                            factura.write({'factura_para_confirmar': True})
                            factura.write({'btn_disponible_director': True})

    def action_confirmar(self):
        usuario_logueado = self.env.user
        monto_usuario = self.obtener_monto('usuario_factura')
        monto_gerente = self.obtener_monto('gerente')
        monto_director = self.obtener_monto('director')
        for factura in self:
            monto_factura = factura.amount_total
            if usuario_logueado.has_group('factura.group_accountant_usuario_factura'):
                if monto_factura > monto_usuario.monto_autorizado:
                    if monto_factura > monto_gerente.monto_autorizado:
                        if factura.etapa_aprobacion != 'pediente':
                            self.factura_para_aprobacion = True
                        return self.mostrar_mensaje(msg_doble_autorizacion)
                    else:
                        if factura.etapa_aprobacion != 'pediente':
                            self.factura_para_aprobacion = True
                        return self.mostrar_mensaje(msg_monto_rebazado)
                else:
                    self.btn_disponible_usuario = False
                    factura.send_data_to_epicor()
                    return factura.aprobar_notificar()
            elif usuario_logueado.has_group('factura.group_accountant_gerente'):
                if monto_factura > monto_gerente.monto_autorizado:
                    if factura.aprobacion_director == True:
                        factura.aprobacion_gerente = True
                        factura.doble_aprobacion()
                    else:
                        factura.aprobacion_gerente = True
                        if factura.etapa_aprobacion == 'sin_solicitar':
                            self.write({'factura_para_aprobacion': True})
                        return self.mostrar_mensaje(
                            f"{msg_aprobacion} {self.env.user.employee_id.parent_id.name}")
                else:
                    self.btn_disponible_gerente = False
                    return factura.aprobar_notificar()
            elif usuario_logueado.has_group('factura.group_accountant_director'):
                if monto_factura > monto_director.monto_autorizado:
                    if factura.etapa_aprobacion != 'pediente':
                        self.factura_para_aprobacion = True
                    return self.mostrar_mensaje(msg_monto_rebazado)
                else:
                    if factura.aprobacion_gerente == True:
                        factura.aprobacion_director = True
                        factura.doble_aprobacion()
                    else:
                        if factura.create_uid.has_group('factura.group_accountant_usuario_factura'):
                            if monto_factura > monto_gerente.monto_autorizado:
                                factura.aprobacion_director = True
                                return self.mostrar_mensaje(
                                    f"{msg_aprobacion} {self.create_uid.employee_id.parent_id.name}")
                            else:
                                self.btn_disponible_director = False
                                return factura.aprobar_notificar()
                        else:
                            self.btn_disponible_director = False
                            return factura.aprobar_notificar()
            else:
                return self.mostrar_mensaje(msg_sin_permiso)

    def doble_aprobacion(self):
        if self.aprobacion_gerente == True and self.aprobacion_director == True:
            self.btn_disponible_gerente = False
            self.btn_disponible_director = False
            return self.aprobar_notificar()
        else:
            raise ValidationError("Se necesita doble autorización")

    def validar_multiples(self):
        for factura in self:
            factura.action_confirmar()

    def aprobar_notificar(self):
        if self.factura_epicor == True:
            usuario_logueado = self.env.user
            rfc_factura = self.partner_id.vat
            proveedor = self.env['res.partner'].search([('vat', '=', rfc_factura)])
            if proveedor.etapa == 'confirmado':
                self.proveedor_sin_confirmar = False
                self.action_post()
                self.btn_disponible_usuario = False
                self.btn_disponible_gerente = False
                self.btn_disponible_director = False
                self.factura_para_confirmar = False
                # template = self.env.ref('account.notificacion_aprobacion')
                # template.send_mail(self.id, force_send=True, email_values={
                #     'email_to': self.create_uid.email,
                # })
                _logger.info('-------------------------------------------------------------------------')
                _logger.info('Se envían los datos a epicor ')
                self.send_data_to_epicor()
            else:
                if usuario_logueado.has_group('factura.group_accountant_usuario_factura'):
                    self.btn_disponible_usuario = True
                    self.proveedor_sin_confirmar = True
                    return self.mostrar_mensaje(msg_proveedor_no_confirmado)
                elif usuario_logueado.has_group('factura.group_accountant_gerente'):
                    self.proveedor_sin_confirmar = True
                    self.btn_disponible_gerente = True
                    return self.mostrar_mensaje(msg_proveedor_no_confirmado)
                elif usuario_logueado.has_group('factura.group_accountant_director'):
                    self.proveedor_sin_confirmar = True
                    self.btn_disponible_director = True
                    return self.mostrar_mensaje(msg_proveedor_no_confirmado)
        else:
            self.action_post()
            self.btn_disponible_usuario = False
            self.btn_disponible_gerente = False
            self.btn_disponible_director = False
            self.factura_para_confirmar = False
            # template = self.env.ref('account.notificacion_aprobacion')
            # template.send_mail(self.id, force_send=True, email_values={
            #     'email_to': self.create_uid.email,
            # })

    def json_epicor_factura(self):
        return json.dumps(
            {
                "id_envio_origen": 1,
                "factura": {
                    "id_grupo": "1",
                    "fecha_aplicacion": fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "id_proveedor": "2",
                    "centro_costos": "Prueba",
                    "factura": self.l10n_mx_edi_cfdi_uuid,
                    "fecha_factura": self.invoice_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    "me26onto_factura": self.amount_total,
                    "tipo_documento": "Factura prueba",
                    "descripcion": "Prueba",
                    "lineas": [
                        {
                            "codigo_parte": "P1",
                            "cantidad_parte": 10,
                            "costo_unitario": 1000
                        }
                    ]
                }
            }
        ).encode('utf-8')

    def send_data_to_epicor(self):
        _logger.info('++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        _logger.info('Entra a Send Data')
        # url = "https://mock-4e64f2866f294a50b33fd2ca15025865.mock.insomnia.rest/CobranzaAPI/FacturasCxP/Enviar"
        url = "https://mock-0d0766c979224881806f4ad217e83d0a.mock.insomnia.run/CobranzaAPI/FacturasCxP/Enviar"
        data = self.json_epicor_factura()
        headers = {'Content-type': 'application/json'}
        request = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(request) as response:
                _logger.info(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            _logger.error(e)
        except urllib.error.URLError as e:
            _logger.error(e)
        return True

    def mostrar_mensaje(self, mensaje):
        return {
            'name': 'Mensaje Informativo',
            'type': 'ir.actions.act_window',
            'res_model': 'factura.modal.informativo',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_mensaje': mensaje
            }
        }

    """def notificar_usuario(self, user,titulo,mensaje):
        channel=["res.users", user.id]
        message = {
            'type': 'simple_notification',
            'title': titulo,
            'message': mensaje,
        }
        self.env['bus.bus']._sendone(self.env.cr.dbname, channel, message)"""

    def write(self, vals):
        if vals.get('state') == 'posted':
            vals['etapa_aprobacion'] = 'aprobada'
        elif vals.get('state') == 'draft':
            vals['etapa_aprobacion'] = 'sin_solicitar'
        elif vals.get('factura_epicor') == False:
            vals['proveedor_sin_confirmar'] = False
        res = super().write(vals)
        return res
