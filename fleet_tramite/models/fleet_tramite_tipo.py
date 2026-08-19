import base64
import io
import logging
from datetime import datetime, timedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class FleetTramiteTipo(models.Model):
    _name = 'fleet.tramite.tipo'
    _description = 'Tipo de tramite'

    name = fields.Char(string='Tipo')
    notificar_renovacion = fields.Boolean(
        string='Notificar vencimiento',
    )
    dias_notificacion = fields.Integer(
        string='Dias notificacion',
    )
    usuarios_notificar_ids = fields.Many2many(
        string='Usuarios notificar',
        comodel_name='hr.employee'
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    def _verificar_notificar_cron(self):
        tramites_tipo = self.search([('notificar_renovacion', '=', True)])
        if not tramites_tipo:
            return False
        vehiculos = self.env['fleet.vehicle'].search([('flotilla_id', '=', 1)])
        if not vehiculos:
            return False
        tramites_proximos = self.env['fleet.tramite']
        hoy = fields.Date.today()
        emails_set = set()
        for tipo in tramites_tipo:
            for emp in tipo.usuarios_notificar_ids:
                if emp.work_email and emp.work_email.strip():
                    emails_set.add(emp.work_email.strip())
            limite = hoy + timedelta(days=tipo.dias_notificacion)
            for vehiculo in vehiculos:
                tramite = self.env['fleet.tramite'].search([
                    ('tipo_tramite_id', '=', tipo.id),
                    ('vehiculo_id', '=', vehiculo.id),
                ], limit=1, order='id desc')
                if tramite:
                    fecha_venc = tramite.fecha_vencimiento_renovacion
                    if not fecha_venc:
                        tramites_proximos |= tramite
                    else:
                        if isinstance(fecha_venc, fields.Datetime):
                            fecha_venc = fecha_venc.date()
                        if fecha_venc <= limite:
                            tramites_proximos |= tramite
        if not tramites_proximos:
            return False
        if not emails_set:
            return False
        email_to_str = ','.join(emails_set)
        try:
            excel = self.create_excel(tramites_proximos)
        except Exception as e:
            _logger.error("Error generando Excel de trámites: %s", str(e))
            return False
        try:
            mail = self.env['mail.mail'].sudo().create({
                'subject': 'Estado de trámites y renovaciones',
                'body_html': """
                    <p>Buen día,</p>
                    <p>Se adjunta el reporte correspondiente al estado de trámites (vencidos, por vencer y no renovados).</p>
                    <p>Por favor revise el archivo adjunto para tomar las acciones pertinentes.</p>
                    <p>Saludos.</p>
                """,
                'email_to': email_to_str,
            })
            attachment = self.env['ir.attachment'].sudo().create({
                'name': excel['name'],
                'type': 'binary',
                'datas': excel['data'],
                'mimetype': excel['mimetype'],
                'res_model': 'mail.mail',
                'res_id': mail.id,
            })
            mail.write({'attachment_ids': [(4, attachment.id)]})
            mail.send(raise_exception=True)
        except Exception as e:
            _logger.error("Error enviando correo de trámites: %s", str(e))
            return False
        return True

    def create_excel(self, tramites):
        if not xlsxwriter:
            _logger.error("Módulo xlsxwriter no disponible en el servidor.")
            raise ImportError("xlsxwriter no disponible")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        sheet = workbook.add_worksheet('Estado de Trámites')
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#283A3E',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'align': 'center',
            'valign': 'vcenter',
        })
        wrap_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
        })
        days_normal_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#E2EFDA',
            'font_color': '#375623',
        })
        days_warning_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
            'bold': True,
        })
        days_expired_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#7A0000',  # Rojo vino / borgoña intenso
            'font_color': '#FFFFFF',  # Blanco para alto contraste
            'bold': True,
        })
        headers = [
            'VIN',
            'Plaza',
            'Tipo de trámite',
            'Fecha de vencimiento',
            'Días restantes / Estatus',
        ]
        for columna, header in enumerate(headers):
            sheet.write(0, columna, header, header_format)
        sheet.set_column(0, 0, 22)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 22)
        sheet.set_column(4, 4, 25)
        sheet.freeze_panes(1, 0)
        sheet.autofilter(0, 0, len(tramites), len(headers) - 1)
        ahora_date = fields.Date.today()
        for fila, tramite in enumerate(tramites, start=1):
            vehiculo = tramite.vehiculo_id
            fecha_vencimiento = tramite.fecha_vencimiento_renovacion
            sheet.write(fila, 0, vehiculo.vin_sn or 'SIN VIN', wrap_format)
            sheet.write(fila, 1, vehiculo.plaza_id.name or 'SIN PLAZA', wrap_format)
            sheet.write(fila, 2, tramite.tipo_tramite_id.name or 'SIN TIPO', wrap_format)
            if not fecha_vencimiento:
                sheet.write(fila, 3, 'SIN FECHA', wrap_format)
                sheet.write(fila, 4, 'SIN RENOVACIÓN', days_expired_format)
                continue
            if isinstance(fecha_vencimiento, datetime):
                fecha_vencimiento = fecha_vencimiento.date()
            dt_vencimiento = datetime.combine(fecha_vencimiento, datetime.min.time())
            sheet.write_datetime(fila, 3, dt_vencimiento, date_format)
            dias_restantes = (fecha_vencimiento - ahora_date).days
            if dias_restantes < 0:
                dias_pasados = abs(dias_restantes)
                sheet.write(
                    fila,
                    4,
                    f"VENCIDO HACE {dias_pasados} DÍAS",
                    days_expired_format
                )
            elif dias_restantes == 0:
                sheet.write(fila, 4, "VENCE HOY", days_expired_format)
            elif dias_restantes <= 30:
                sheet.write(
                    fila,
                    4,
                    f"FALTAN {dias_restantes} DÍAS",
                    days_warning_format
                )
            else:
                sheet.write(
                    fila,
                    4,
                    f"FALTAN {dias_restantes} DÍAS",
                    days_normal_format
                )
        workbook.close()
        buffer.seek(0)
        return {
            'name': 'reporte_estatus_tramites.xlsx',
            'data': base64.b64encode(buffer.read()).decode('utf-8'),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }