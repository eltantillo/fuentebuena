from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FleetMantenimiento(models.Model):
    _name = "fleet.mantenimiento.etapa"
    _description = "Mantenimiento de vehiculos"
    _order = 'sequence asc'

    name = fields.Char(
        string="Mantenimiento"
    )
    es_etapa_realizado = fields.Boolean(
        string="Etapa de realizado"
    )

    es_etapa_programado = fields.Boolean(
        string="Etapa de programado"
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    sequence = fields.Integer(
        string="Sequence",
    )


    @api.constrains('es_etapa_realizado')
    def _chack_es_etapa_realizado(self):
        self._check_etapa('es_etapa_realizado','Realizado')

    @api.constrains('es_etapa_programado')
    def _check_es_etapa_programado(self):
        self._check_etapa('es_etapa_programado', 'Programado')

    def _check_etapa(self,etapa,nombre):
        num_etapa = self.search_count([(etapa, '=', True)])
        if num_etapa > 1:
            raise ValidationError(f'Solo se puede tener un estado como etapa {nombre}')