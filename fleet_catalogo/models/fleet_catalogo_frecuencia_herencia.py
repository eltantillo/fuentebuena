from odoo import models, fields, api
from setuptools._distutils.command import config


class FleetCatalogoFrecuenciaTramiteConfig(models.Model):
    _inherit = 'fleet.tramite.config'
    _description = 'Frecuencia de pago del tramite config'

    frecuencia_pago_id = fields.Many2one(
        comodel_name='fleet.catalogo.frecuencia.pago',
        string='Frecuencia de pago',
    )

class FleetCatalogoFrecuenciaPolizaConfig(models.Model):
    _inherit = 'fleet.poliza.config'

    frecuencia_pago_id = fields.Many2one(
        comodel_name='fleet.catalogo.frecuencia.pago',
        string='Frecuencia de pago',
    )

class FleetCatalogoFrecuenciaHerenciaTramite(models.Model):
    _inherit = 'fleet.tramite'
    _description = 'Frecuencia de pago del tramite'

    frecuencia_pago_id = fields.Many2one(
        comodel_name='fleet.catalogo.frecuencia.pago',
        string='Frecuencia de pago',
    )

    @api.onchange('tipo_tramite_id')
    def onchange_tipo_tramite_id(self):
        config = self.env['fleet.tramite.config'].search([
            ('plaza_id', '=', self.plaza_id.id),
            ('tipo_tramite_id', '=', self.tipo_tramite_id.id)],
            limit=1)
        if config:
            self.dependencia = config.dependencia
            self.estado = config.estado.id
            self.motivo_pago_id = config.motivo_pago_id.id
            self.importe = config.importe
            self.frecuencia_pago_id = config.frecuencia_pago_id.id
        else:
            self.dependencia = False
            self.estado = False
            self.motivo_pago_id = False
            self.importe = 0.0
            self.frecuencia_pago_id = False

class FleetCatalogoFrecuenciaHerenciaPoliza(models.Model):
    _inherit = 'fleet.poliza'
    _description = 'Frecuencia de pago de la póliza'

    frecuencia_pago_id = fields.Many2one(
        comodel_name='fleet.catalogo.frecuencia.pago',
        string='Frecuencia de pago',
    )

    @api.onchange('tipo_poliza_id')
    def onchange_tipo_tramite_id(self):
        config = self.env['fleet.poliza.config'].search([('plaza_id','=', self.plaza_id.id),('tipo_poliza_id','=', self.tipo_poliza_id.id)], limit=1)
        if config:
            self.proveedor_id = config.proveedor_id.id
            self.tipo_cobertura_id = config.tipo_cobertura_id.id
            self.tipo_valor_id = config.tipo_valor_id.id
            self.frecuencia_pago_id = config.frecuencia_pago_id.id
            self.prima_neta = config.prima_neta
            self.gasto_expedicion = config.gasto_expedicion
        else:
            self.proveedor_id = False
            self.tipo_cobertura_id = False
            self.tipo_valor_id = False
            self.frecuencia_pago_id = False
            self.prima_neta = False
            self.gasto_expedicion = False