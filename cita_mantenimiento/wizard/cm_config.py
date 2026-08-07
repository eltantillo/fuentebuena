from odoo import fields,models,api


class CMConfig(models.TransientModel):
    _name = 'cm.config'

    max_reagendas = fields.Integer(
        string='Max. reagendas',
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.max_reagendas', 0
        ))
    )

    max_reagendas_au = fields.Integer(
        string='Max. reagendas automáticas',
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.max_reagendas_au', 0
        ))
    )

    km_promedio = fields.Integer(
        string='Promedio de km',
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.km_promedio', 0
        ))
    )

    limite_inferior = fields.Integer(
        string='Límite inferior',
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.limite_inferior', 0
        ))
    )

    limite_superior = fields.Integer(
        string='Límite superior',
        default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.limite_superior', 0
        ))
    )

    llave_creacion = fields.Char(
        string='Creación',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'cita_mantenimiento.llave_creacion', ''
        )
    )


    def confirm_change(self):
        self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.max_reagendas', self.max_reagendas)
        self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.max_reagendas_au', self.max_reagendas_au)
        self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.km_promedio', self.km_promedio)
        self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.limite_inferior', self.limite_inferior)
        self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.limite_superior', self.limite_superior)
        self.env['ir.config_parameter'].sudo().set_param('cita_mantenimiento.llave_creacion', self.llave_creacion)
