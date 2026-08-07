"""
@author: Jorge Eduardo Limon Munguia <jorge.limon@fuentebuena.com>
@date: 30/06/2025
"""


from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import logging
import json
import urllib.request
import urllib.error

_logger = logging.getLogger(__name__)

class ProveedorResPartner(models.Model):
    _inherit = 'res.partner'

    # ETAPA = [
    #     ('borrador', 'Borrador'),
    #     ('en_proceso', 'En Proceso'),
    #     ('confirmado', 'Confirmado'),
    # ]
    #
    # etapa = fields.Selection(
    #     string='Etapas',
    #     selection=ETAPA,
    #     default='borrador'
    # )
    # aprobacion_administracion = fields.Boolean(
    #     string='Aprobación Administración',
    #     default=False
    # )
    # aprobacion_contabilidad = fields.Boolean(
    #     string='Aprobación Contabilidad',
    #     default=False
    # )
    # aprobacion_tesoreria = fields.Boolean(
    #     string='Aprobación Tesorería',
    #     default=False
    # )
    # tipo_proveedor = fields.Many2one(
    #     comodel_name='proveedor.tipo',
    #     string='Tipo de Proveedor'
    # )
    id_proveedor = fields.Integer(
        string='ID Proveedor'
    )
    tipo_proveedor_ids = fields.Many2many(
        comodel_name='proveedor.tipo',
        string='Tipo de Proveedor'
    )
    es_proveedor = fields.Boolean(
        string='Es proveedor',
    )
    razones_sociales_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Razones Sociales Relacionadas",
        relation="res_partner_razones_sociales_rel",
        column1="partner_id",
        column2="razon_id",
    )
    id_res_partner_id = fields.Integer(
        comodel_name='res.partner',
    )

    def action_abrir_asignacion(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "proveedor.asignar.razon",
            "view_mode": "form",
            "target": "new",
            "view_id": self.env.ref("proveedor.provedoor_asignar_razon_view_form").id,
        }


    @api.model
    def create(self,vals):
        for proveedor in self:
            esproveedor = proveedor.env.context.get('default_es_proveedor')
            if esproveedor:
                for val in vals:
                    val['supplier_rank'] = 1
        res = super(ProveedorResPartner, self).create(vals)
        return res

    # def write(self, vals):
    #     usuario_log = self.env.user
    #     for record in self:
    #         if 'aprobacion_administracion' in vals and vals['aprobacion_administracion'] is True:
    #             if not usuario_log.has_group('proveedor.group_proveedor_administracion'):
    #                 vals['validacion_administracion'] = False
    #                 raise ValidationError("No puedes confirmar el status, solo usuarios de administración")
    #             else:
    #                 if record.aprobacion_contabilidad is True and record.aprobacion_tesoreria is True:
    #                     vals['etapa'] = 'confirmado'
    #                     record.send_data_to_epicor()
    #         if 'aprobacion_contabilidad' in vals and vals['aprobacion_contabilidad'] is True:
    #             if not usuario_log.has_group('proveedor.group_proveedor_contabilidad'):
    #                 raise ValidationError("No puedes confirmar el status, solo usuarios de contabilidad")
    #             else:
    #                 if record.aprobacion_administracion is True and record.aprobacion_tesoreria is True:
    #                     vals['etapa'] = 'confirmado'
    #                     record.send_data_to_epicor()
    #         if 'aprobacion_tesoreria' in vals and vals['aprobacion_tesoreria'] is True:
    #             if not usuario_log.has_group('proveedor.group_proveedor_tesoreria'):
    #                 raise ValidationError("No puedes confirmar el status, solo usuarios de tesoreria")
    #             else:
    #                 if record.aprobacion_administracion is True and record.aprobacion_contabilidad is True:
    #                     vals['etapa'] = 'confirmado'
    #                     record.send_data_to_epicor()
    #     return super().write(vals)

    @api.model
    def action_confirmar(self, id):
        proveedor = self.browse(id)
        proveedor.write({'etapa': 'en_proceso'})
        proveedor.notificar()

    # def validar_js(self):
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'validar_js',
    #     }

    # @api.model
    # def notificar(self):
    #     grupos_ids = [
    #         self.env.ref('proveedor.group_proveedor_administracion').id,
    #         self.env.ref('proveedor.group_proveedor_contabilidad').id,
    #         self.env.ref('proveedor.group_proveedor_tesoreria').id
    #     ]
    #     usuarios = self.env['res.users'].search([('group_ids', 'in', grupos_ids)])
    #
    #     if not usuarios:
    #         raise ValidationError("No se encontraron usuarios para notificar")
    #
    #     for usuario in usuarios:
    #         self.env['mail.activity'].create({
    #             'res_model_id': self.env['ir.model']._get_id('res.partner'),
    #             'res_id': self.id,
    #             'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
    #             'summary': _('Proveedor pendiente de aprobación'),
    #             'note': _('Esta factura está marcada como pendiente de aprobación.'),
    #             'user_id': usuario.id,
    #             'date_deadline': fields.Date.today(),
    #         })
    #     template = self.env.ref('proveedor.proveedor_notificar_mail_template')
    #     for usuario in usuarios:
    #         template.send_mail(self.id, force_send=True, email_values={
    #             'email_to': usuario.email,
    #         })
    #
    # def action_borrador(self):
    #     for provedor in self:
    #         provedor.write({'etapa': 'borrador'})
    #         provedor.write({'aprobacion_administracion': False})
    #         provedor.write({'aprobacion_contabilidad': False})
    #         provedor.write({'aprobacion_tesoreria': False})
    #
    # def json_epicor(self):
    #     banco = self.bank_ids[:1]
    #     return json.dumps({
    #         "id_envio_origen": 1,
    #         "proveedor": {
    #             "id_proveedor": "1",
    #             "razon_social": self.complete_name,
    #             "moneda": "Peso mexicano",
    #             "obligacion_fiscal": "Ninguna",
    #             "rfc": self.vat,
    #             "grupo": "Pruebas",
    #             "terminos": "Ninguno",
    #             "domicilio_fiscal_1": self.street,
    #             "domicilio_fiscal_2": "X calle num 4",
    #             "domicilio_fiscal_3": "x calle num 5",
    #             "ciudad": self.city,
    #             "estado": self.state_id.name,
    #             "cp": self.zip,
    #             "codigo_pais": self.country_code,
    #             "telefono": self.phone,
    #             "correo_electronico": self.email,
    #             "nombre_legal": self.complete_name,
    #             "nombre_banco_remitir_a": banco.bank_id.name,
    #             "codigo_babnco": banco.bank_id.bic,
    #             "codigo_metodo_pago": 1,
    #             "cuenta_bancaria": "Pruebas BBVA"
    #         }
    #     }).encode('utf-8')
    #
    # @api.model
    # def send_data_to_epicor(self):
    #     url = "https://mock-880e8581231942438f6a38775c594553.mock.insomnia.rest/CobranzaAPI/Proveedor/Alta"
    #     data = self.json_epicor()
    #     headers = {'Content-type': 'application/json'}
    #     request = urllib.request.Request(url, data=data, headers=headers)
    #     try:
    #         with urllib.request.urlopen(request) as response:
    #             _logger.info(response.read().decode('utf-8'))
    #     except urllib.error.HTTPError as e:
    #         _logger.error(e)
    #     except urllib.error.URLError as e:
    #         _logger.error(e)
    #     return True