from odoo import fields,models,api


class PromesaPPeriodoNomConvenio(models.Model):
    _name = 'promesa.p.periodo.nom.convenio'
    _rec_name = 'rec_name'
    _inherit = ["mail.thread","mail.activity.mixin"]
    _order = "id desc"

    year_periodo_nomina = fields.Char(
        string="Año periodo nómina",
    )
    frecuencia_nomina_id = fields.Many2one(
        string="Frecuencia",
        comodel_name='promesa.p.frecuencia.nomina'
    )
    tipo_frecuencia = fields.Char(
        string="Tipo de frecuencia",
    )
    num_periodo = fields.Integer(
        string="Numero de periodo",
    )
    periodo = fields.Char(
        string="Periodo",
    )
    clientes_descontado = fields.Char(
        string="Clientes descontados",
    )
    monto_enviado_descuento = fields.Float(
        string="Monto enviado a descuento",
    )
    fecha_envio_lista = fields.Date(
        string="Fecha de envio lista",
    )
    periodo_gestion = fields.Char(
        string="Periodo gestion",
    )
    num_clientes_retenidos = fields.Integer(
        string="Numero de clientes retenidos",
    )
    monto_retenido = fields.Float(
        string="Monto retenido",
    )
    monto_recibido = fields.Float(
        string="Monto recibido",
    )
    descuento_vs_retenido = fields.Float(
        string="Descuento vs retenido",
    )
    retenido_vs_recibido = fields.Float(
        string="Retenido vs recibido",
    )
    por_cobrar = fields.Float(
        string="Por cobrar",
    )
    id_proceso_convenio = fields.Char(
        string="ID proceso convenio",
    )
    convenio_id = fields.Many2one(
        string="Convenio",
        comodel_name='promesa.p.convenio',
    )
    periodos_con_atraso = fields.Integer(
        string="Periodos con atraso",
    )
    celula = fields.Char(
        string="Celula",
    )
    zona = fields.Char(
        string="Zona",
    )
    responsable_id = fields.Many2one(
        string="Responsable",
        comodel_name='hr.employee',
    )
    gestor_id = fields.Many2one(
        string="Gestor",
        comodel_name='hr.employee',
    )
    fecha_inicio_gestion = fields.Date(
        string="Fecha de inicio gestión",
    )
    fecha_fin_gestion = fields.Date(
        string="Fecha de fin gestión",
    )
    monto_pendiente = fields.Float(
        string="Monto pendiente",
    )
    estatus_convenio = fields.Char(
        string="Estatus convenio",
    )
    estatus_colocacion = fields.Char(
        string="Estatus colocación"
    )
    estatus_cumplimiento = fields.Char(
        string="Estatus cumplimiento"
    )
    estatus_lista = fields.Char(
        string="Estatus listas",
    )
    gestores = fields.Many2many(
        comodel_name='hr.employee',
        relation='promesa_periodo_nom_convenio_gestor_rel',
        column1='periodo_id',
        column2='employee_id',
        string="Gestores",
        compute="_compute_gestores"
    )
    responsables = fields.Many2many(
        comodel_name='hr.employee',
        relation='promesa_periodo_nom_convenio_responsable_rel',
        column1='periodo_id',
        column2='employee_id',
        string="Responsables",
        compute="_compute_responsables"
    )
    promesa_ids = fields.One2many(
        comodel_name='promesa.p.promesa',
        string='Promesas',
        inverse_name='periodo_nomina_id'
    )
    rec_name = fields.Char(
        string="Name",
        compute="_compute_rec_name"
    )
    active = fields.Boolean('Active', default=True, tracking=True)

    def _compute_rec_name(self):
        for record in self:
            record.rec_name = f"{record.id}-{record.convenio_id.name}-{record.tipo_frecuencia}-{record.num_periodo}"

    def _compute_gestores(self):
        for record in self:
            rol = self.env['promesa.p.rol'].search([('name', '=', 'Gestores')], limit=1)
            if rol:
                record.gestores = [(6, 0, rol.employee_ids.ids)]
            else:
                record.gestores = [(5, 0, 0)]

    def _compute_responsables(self):
        for record in self:
            rol = self.env['promesa.p.rol'].search([('name', '=', 'Responsables')], limit=1)
            if rol:
                record.responsables = [(6, 0, rol.employee_ids.ids)]
            else:
                record.responsables = [(5, 0, 0)]