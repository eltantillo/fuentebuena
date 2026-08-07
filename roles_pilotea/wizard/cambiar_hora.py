from odoo import fields, models, api
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)


HORA = [
    ('00','00'),
    ('01', '01'),
    ('02', '02'),
    ('03', '03'),
    ('04', '04'),
    ('05', '05'),
    ('06', '06'),
    ('07', '07'),
    ('08', '08'),
    ('09', '09'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
]

MINUTO = [
    ('00','00'),
    ('15', '15'),
    ('30', '30'),
    ('45', '45'),
]

class CambiarHora(models.TransientModel):
    _name = 'cambiar.hora'

    hora = fields.Selection(
        selection=HORA,
        string='Hora',
    )

    minuto = fields.Selection(
        selection=MINUTO,
        string='Minuto',
    )

    motivo_id = fields.Many2one(
        comodel_name='rp.motivo.cambio.agenda',
        string='Motivo de cambio',
    )

    def action_confirm(self):
        agenda_id = self.env.context.get('active_id')
        agenda = self.env['agenda.entrega'].browse(agenda_id)
        fecha_original = agenda.fecha_confirmada
        fecha_local = fields.Datetime.context_timestamp(self, fecha_original)
        _logger.info(f"Hora de cambio: {self.hora}, minuto: {self.minuto}")
        nueva_fecha_local = fecha_local.replace(
            hour=int(self.hora),
            minute=int(self.minuto),
            second=0,
            microsecond=0,
        )
        user_tz = timezone(self.env.user.tz or 'UTC')
        nueva_fecha_utc = nueva_fecha_local.astimezone(timezone('UTC'))

        agenda.sudo().write({
            'fecha_confirmada': fields.Datetime.to_string(nueva_fecha_utc),
            'motivo_cambio_hora_id': self.motivo_id.id
        })
