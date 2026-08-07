from odoo import http
from odoo.http import request
import logging
import json
_logger = logging.getLogger(__name__)

class CitaMantenimientoController(http.Controller):

    def _handle_create(self, id_booking):
        _logger.info(f"📥 INfor de booking id: {id_booking}")
        self.env['cita.mantenimiento'].sudo().process_cita_save(id_booking)
        pass

    def _handle_cancel(self, id_booking):
        self.env['cita.mantenimiento'].sudo().cancel_cita(id_booking)
        pass

    def _handle_change(self, id_booking):
        self.env['cita.mantenimiento'].sudo().update_cita_save(id_booking)
        pass

    @http.route('/citaWebhook', type='http', auth='public', methods=['POST'], csrf=False)
    def simplybook_webhook(self, **post):
        try:
            raw = request.httprequest.data
            data = json.loads(raw or "{}")
            if not data:
                return json.dumps({"error": "no data"})
            type_event = data.get('notification_type')
            booking_id = data.get('booking_id')
            if type_event == 'create':
                self._handle_create(booking_id)
            elif type_event == 'change':
                self._handle_change(booking_id)
            elif type_event == 'cancel':
                self._handle_cancel(booking_id)
            return json.dumps({"success": True})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


    @http.route('/validacionsb', type='http', auth='public', methods=['POST'], csrf=False)
    def validacionsb(self, **post):
        raw = request.httprequest.data
        data = json.loads(raw or "{}")
        _logger.info("=============Cae a validacion sb==================")
        _logger.info(data)
        datos = request.env['cita.mantenimiento'].sudo().validar_cita(data)
        return json.dumps(datos)
