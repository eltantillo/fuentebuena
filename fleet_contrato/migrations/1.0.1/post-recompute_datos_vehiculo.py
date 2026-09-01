from odoo import SUPERUSER_ID, api

VEHICLE_FIELDS = ('cliente_id', 'plaza_id', 'producto_id', 'vin_sn', 'numero_economico')


def migrate(cr, version):
    """Refresh the vehicle-derived fields on every stored contract.

    Until this version `_compute_datos_vehiculo` depended on `vehicle_id` alone
    while reading the vehicle's driver, plaza, product and VIN. Those are stored
    computes, so assigning a driver to a vehicle never refreshed the contracts
    already in the database: `cliente_id` was empty on all of them and the rest
    could be stale. Fixing the dependency does not recompute what is already
    stored, hence this pass.

    Archived contracts are included: they carry the same broken values and any
    report that unarchives one would read them.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    contracts = env['fleet.vehicle.log.contract'].with_context(active_test=False).search([])
    for name in VEHICLE_FIELDS:
        env.add_to_compute(contracts._fields[name], contracts)
    env.flush_all()
