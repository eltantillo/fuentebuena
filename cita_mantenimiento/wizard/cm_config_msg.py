from odoo import fields, models


class CMConfigMsg(models.TransientModel):
    _name = 'cm.config.msg'
    _description = 'Configuración Cita Mantenimiento'


    msg_rango_minimo = fields.Text(
        string='Mensaje rango mínimo',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_rango_minimo', ''
        )
    )
    msg_rango_maximo = fields.Text(
        string='Mensaje rango máximo',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_rango_maximo', ''
        )
    )
    msg_desfase_mantenimientos = fields.Text(
        string='Mensaje desfase mantenimiento',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_desfase_mantenimientos', ''
        )
    )
    msg_primer_mantenimiento = fields.Text(
        string='Mensaje primer mantenimiento',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_primer_mantenimiento', ''
        )
    )
    msg_max_reagendas = fields.Text(
        string='Mensaje max reagendas',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_max_reagendas', ''
        )
    )
    msg_max_reagendas_manual = fields.Text(
        string='Mensaje max reagendas manual',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_max_reagendas_manual', ''
        )
    )
    msg_placa_no_encontrada = fields.Text(
        string='Mensaje placa no encontrada',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_placa_no_encontrada', ''
        )
    )
    msg_placa_otra_plaza = fields.Text(
        string='Mensaje placa de diferente plaza',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.msg_placa_otra_plaza', ''
        )
    )

    def confirm_change(self):
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param(
            'cita_mantenimiento.msg_rango_minimo',
            self.msg_rango_minimo or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_rango_maximo',
            self.msg_rango_maximo or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_desfase_mantenimientos',
            self.msg_desfase_mantenimientos or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_primer_mantenimiento',
            self.msg_primer_mantenimiento or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_max_reagendas',
            self.msg_max_reagendas or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_max_reagendas_manual',
            self.msg_max_reagendas_manual or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_placa_no_encontrada',
            self.msg_placa_no_encontrada or ''
        )
        icp.set_param(
            'cita_mantenimiento.msg_placa_otra_plaza',
            self.msg_placa_otra_plaza or ''
        )
        return True