from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Fill in the lessee on every movement.

    `cliente_id` was a plain field that nothing ever wrote — it is readonly in
    the form — so the lessee was shown through `arrendatario_name`, a mirror of
    the contract's free text. That text is gone: `cliente_id` now derives from
    the contract, and every stored movement needs the first pass.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    movimientos = env['fleet.movimiento.misc'].with_context(active_test=False).search([])
    env.add_to_compute(movimientos._fields['cliente_id'], movimientos)
    env.flush_all()
