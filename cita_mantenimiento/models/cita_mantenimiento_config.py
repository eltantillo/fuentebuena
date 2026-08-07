from odoo import models,api,fields
from odoo.exceptions import ValidationError


class CitaMantenimientoConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    max_reagendas = fields.Integer(
        string='Max. reagendas',
        config_parameter='cita_mantenimiento.max_reagendas',
    )
    max_reagendas_au = fields.Integer(
        string='Max. reagendas automáticas',
        config_parameter='cita_mantenimiento.max_reagendas_au',
    )
    km_promedio = fields.Integer(
        string='Promedio de km',
        config_parameter='cita_mantenimiento.km_promedio',
    )
    limite_inferior = fields.Integer(
        string='Límite inferior',
        config_parameter='cita_mantenimiento.limite_inferior',
    )
    limite_superior = fields.Integer(
        string='Límite superior',
        config_parameter='cita_mantenimiento.limite_superior',
    )
    llave_creacion = fields.Char(
        string='Creacion',
        config_parameter='cita_mantenimiento.llave_creacion',
    )
    msg_rango_minimo = fields.Char(
        string='Mensaje rango mínimo',
        config_parameter='cita_mantenimiento.msg_rango_minimo',
    )
    msg_rango_maximo = fields.Char(
        string='Mensaje rango máximo',
        config_parameter='cita_mantenimiento.msg_rango_maximo',
    )
    msg_desfase_mantenimientos = fields.Char(
        string='Mensaje desfase mantenimiento',
        config_parameter='cita_mantenimiento.msg_desfase_mantenimientos',
    )
    msg_primer_mantenimiento = fields.Char(
        string='Mensaje primer mantenimiento',
        config_parameter='cita_mantenimiento.msg_primer_mantenimiento',
    )
    msg_max_reagendas = fields.Char(
        string='Mensaje max reagendas',
        config_parameter='cita_mantenimiento.msg_max_reagendas',
    )
    msg_max_reagendas_manual = fields.Char(
        string='Mensaje max reagendas manual',
        config_parameter='cita_mantenimiento.msg_max_reagendas_manual',
    )
    msg_placa_no_encontrada = fields.Char(
        string='Mensaje placa no encontrada',
        config_parameter='cita_mantenimiento.msg_placa_no_encontrada',
    )
    msg_placa_otra_plaza = fields.Char(
        string='Mensaje placa de diferente plaza',
        config_parameter='cita_mantenimiento.msg_placa_otra_plaza',
    )