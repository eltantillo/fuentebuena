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
                if tramite and tramite.fecha_vencimiento_renovacion:
                    fecha_venc = tramite.fecha_vencimiento_renovacion
                    if isinstance(fecha_venc, fields.Datetime):
                        fecha_venc = fecha_venc.date()
                    if hoy <= fecha_venc <= limite:
                        tramites_proximos |= tramite
        if not tramites_proximos:
            return False
        if not emails_set:
            return False
        email_to_str = ','.join(emails_set)
        try:
            excel = self.create_excel(tramites_proximos)
        except Exception as e:
            return False
        try:
            mail = self.env['mail.mail'].sudo().create({
                'subject': 'Estado de tramites renovación',
                'body_html': """
                    <p>Buen día,</p>
                    <p>Se adjunta el reporte correspondiente a los trámites próximos a renovar.</p>
                    <p>El archivo contiene el estado de los trámites y los días restantes para su renovación.</p>
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
            return False
        return True

    def create_excel(self, tramites):
        if not xlsxwriter:
            _logger.error("Módulo xlsxwriter no disponible en el servidor.")
            raise ImportError("xlsxwriter no disponible")
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(
            buffer,
            {'in_memory': True}
        )
        sheet = workbook.add_worksheet('Próximos a vencer')
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
        days_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
        wrap_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
        })
        headers = [
            'VIN',
            'Plaza',
            'Tipo de trámite',
            'Fecha de vencimiento',
            'Días restantes',
        ]
        for columna, header in enumerate(headers):
            sheet.write(0, columna, header, header_format)
        sheet.set_column(0, 0, 22)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 22)
        sheet.set_column(4, 4, 18)
        sheet.freeze_panes(1, 0)
        sheet.autofilter(0, 0, len(tramites), len(headers) - 1)
        ahora = fields.Datetime.now()
        for fila, tramite in enumerate(tramites, start=1):
            vehiculo = tramite.vehiculo_id
            fecha_vencimiento = tramite.fecha_vencimiento_renovacion
            if isinstance(fecha_vencimiento, fields.Datetime):
                fecha_vencimiento = fecha_vencimiento.date()
            dias_restantes = (fecha_vencimiento - ahora.date()).days
            sheet.write(fila, 0, vehiculo.vin_sn or 'SIN VIN', wrap_format)
            sheet.write(fila, 1, vehiculo.plaza_id.name or 'SIN PLAZA', wrap_format)
            sheet.write(fila, 2, tramite.tipo_tramite_id.name or 'SIN TIPO', wrap_format)
            dt_vencimiento = datetime.combine(fecha_vencimiento, datetime.min.time())
            sheet.write_datetime(fila, 3, dt_vencimiento, date_format)
            sheet.write(fila, 4, dias_restantes, days_format)
        workbook.close()
        buffer.seek(0)
        return {
            'name': 'tramites_proximos_a_vencer.xlsx',
            'data': base64.b64encode(
                buffer.read()
            ).decode('utf-8'),
            'mimetype': (
                'application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet'
            ),
        }