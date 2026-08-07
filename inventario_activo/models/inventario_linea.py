from odoo import  fields,models,api

class InventarioLinea(models.Model):

    _name = 'inventario.linea'

    name = fields.Char(
        string='Nombre',
    )
    etapa_id = fields.Many2one(
        comodel_name='inventario.linea.etapa',
        string='Etapa',
    )
    telefono = fields.Char(
        string='Telefono',
    )
    region_id = fields.Many2one(
        comodel_name='inventario.region',
        string='Region',
    )
    cuenta_padre = fields.Char(
        string='Cuenta padre',
    )
    plan_id = fields.Many2one(
        comodel_name='inventario.plan',
    )
    razon_social_selection = fields.Selection(
        string='Razon Social',
        selection=[
            ('CORPORATIVO OLIVO 2017 SA DE CV', 'CORPORATIVO OLIVO 2017 SA DE CV'),
            ('FOMEPADE', 'FOMEPADE')
        ]
    )
    estatus_adendum = fields.Selection(
        string='Estatus Adendum',
        selection=[
            ('Con Adendum', 'Con Adendum'),
            ('Sin Adendum', 'Sin Adendum'),
        ]
    )
    num_plazos = fields.Selection(
        string='Num Plazos',
        selection=[
            ('12', '12'),
            ('24', '24'),
            ('25', '25'),
            ('26', '26'),
            ('27', '27'),
            ('36', '36'),
            ('48', '48'),
        ]
    )
    fecha_inicio = fields.Date(
        string='Fecha Inicio',
    )
    fecha_termino = fields.Date(
        string='Fecha Termino',
    )
    incluye_celular = fields.Boolean(
        string='Incluye Celular',
    )
    empleado_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado',
    )
    fecha_asignacion = fields.Date(
        string='Fecha Asignacion',
    )
    subtotal = fields.Float(
        string='Subtotal',
    )
    iva = fields.Float(
        string='IVA',
    )
    total = fields.Float(
        string='Total',
    )
    mb_aginados = fields.Integer(
        string='MB aginados',
    )
    dia_corte = fields.Integer(
        string='Dia Corte',
    )


