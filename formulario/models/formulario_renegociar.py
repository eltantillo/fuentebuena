from odoo import fields,models,api

ESTADOS = [
    ('aguascalientes', 'Aguascalientes'),
    ('baja_california', 'Baja California'),
    ('baja_california_sur', 'Baja California Sur'),
    ('campeche', 'Campeche'),
    ('cdmx', 'Ciudad de México'),
    ('coahuila', 'Coahuila'),
    ('colima', 'Colima'),
    ('chiapas', 'Chiapas'),
    ('chihuahua', 'Chihuahua'),
    ('durango', 'Durango'),
    ('guanajuato', 'Guanajuato'),
    ('guerrero', 'Guerrero'),
    ('hidalgo', 'Hidalgo'),
    ('jalisco', 'Jalisco'),
    ('mexico', 'México'),
    ('michoacan', 'Michoacán'),
    ('morelos', 'Morelos'),
    ('nayarit', 'Nayarit'),
    ('nuevo_leon', 'Nuevo León'),
    ('oaxaca', 'Oaxaca'),
    ('puebla', 'Puebla'),
    ('queretaro', 'Querétaro'),
    ('quintana_roo', 'Quintana Roo'),
    ('san_luis_potosi', 'San Luis Potosí'),
    ('sinaloa', 'Sinaloa'),
    ('sonora', 'Sonora'),
    ('tabasco', 'Tabasco'),
    ('tamaulipas', 'Tamaulipas'),
    ('tlaxcala', 'Tlaxcala'),
    ('veracruz', 'Veracruz'),
    ('yucatan', 'Yucatán'),
    ('zacatecas', 'Zacatecas'),
]

class FormularioDeuda(models.Model):
    _name = 'formulario.renegociar'
    _description = 'Formulario para regnegociar las deudas'
    _rec_name = 'rec_name'
    _order = 'id desc'

    nombre = fields.Char(
        string='Nombre',
    )
    apellido = fields.Char(
        string='Apellido',
    )
    correo = fields.Char(
        string='Correo',
    )
    telefono = fields.Char(
        string='Teléfono',
    )
    estado = fields.Selection(
        selection=ESTADOS,
        string='Estado',
    )
    estado_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Estado',
        domain=[('country_id', '=', 'MX')],
    )
    puesto_ocupado_id = fields.Many2one(
        comodel_name='puesto.ocupado',
        string='Puesto que desempeña',
    )
    medio_contacto_id = fields.Many2one(
        comodel_name='medio.contacto',
        string='Medio de contacto',
    )
    rec_name = fields.Char(
        string='Nombre',
        compute='_compute_rec_name',
    )

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.nombre} - {record.telefono}"