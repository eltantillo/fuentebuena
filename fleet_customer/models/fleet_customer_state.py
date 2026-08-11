from  odoo import fields, models, api
from odoo.exceptions import ValidationError


class FleetCustomerState(models.Model):
    _inherit = 'fleet.vehicle.state'

    es_estapa_alta = fields.Boolean(
        string='Es estapa alta'
    )
    es_etapa_rentado = fields.Boolean(
        string='Es etapa rentado'
    )
    es_etapa_reacondicionamiento = fields.Boolean(
        string='Es etapa reacondicionamiento'
    )
    es_etapa_recibido = fields.Boolean(
        string='Es etapa recibido'
    )
    es_estapa_disponible = fields.Boolean(
        string='Es etapa disponible'
    )
    es_etapa_baja = fields.Boolean(
        string='Es etapa baja'
    )
    es_etapa_adaptacion = fields.Boolean(
        string='Es etapa adaptación'
    )
    categoria_agrupacion = fields.Many2one(
        comodel_name='fleet.customer.categoria.agrupacion',
        string='Categoria de agrupación'
    )
    sub_etapa_ids = fields.Many2many(
        comodel_name='fleet.customer.sub.etapa',
        string='Sub etapa'
    )
    ubicacion_ids = fields.Many2many(
        comodel_name='fleet.customer.ubicacion',
        string='Ubicaciones'
    )
    categoria = fields.Many2one(
        comodel_name='fleet.customer.categoria.etapa',
        string='Categoria'
    )
    indicador = fields.Many2one(
        comodel_name='fleet.customer.indicador.categoria',
        string='Indicador'
    )
    active = fields.Boolean(
        string='Activa',
        default=True
    )

    @api.constrains('es_estapa_disponible')
    def _chack_es_etapa_disponible(self):
        self._check_etapa('es_estapa_disponible','disponible')

    @api.constrains('es_etapa_recibido')
    def _chack_es_etapa_recibido(self):
        self._check_etapa('es_etapa_recibido','recibido')

    @api.constrains('es_etapa_reacondicionamiento')
    def _check_es_etapa_reacondicionado(self):
        self._check_etapa('es_etapa_reacondicionamiento', 'reacondicionamiento')

    @api.constrains('es_estapa_alta')
    def _check_es_etapa_alta(self):
        self._check_etapa('es_estapa_alta', 'alta')

    @api.constrains('es_etapa_rentado')
    def _check_es_etapa_rentado(self):
        self._check_etapa('es_etapa_rentado', 'rentado')

    @api.constrains('es_etapa_rentado')
    def _check_es_etapa_baja(self):
        self._check_etapa('es_etapa_baja', 'baja')

    @api.constrains('es_etapa_adaptacion')
    def _check_es_etapa_adaptacion(self):
        self._check_etapa('es_etapa_adaptacion', 'adaptacion')

    def _check_etapa(self,etapa,nombre):
        num_etapa = self.search_count([(etapa, '=', True)])
        if num_etapa > 1:
            raise ValidationError(f'Solo se puede tener un estado como etapa {nombre}')