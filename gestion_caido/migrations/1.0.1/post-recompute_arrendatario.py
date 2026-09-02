from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Refresh the contract-derived fields on every gestion.

    `arrendatario_id` used to copy the contract's `cliente_id` while that field
    mirrored the vehicle's driver, and the free-text `nombre_arrendatario` next
    to it carried the real lessee. The text field is gone and the contract now
    holds the lessee itself, so the stored copies have to be refreshed: they
    depend on `contato_id` alone, which did not change.

    Refreshing `arrendatario_id` runs `_compute_datos_contrato`, so the CIE,
    the contract number and the status are rewritten in the same pass.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    gestiones = env['gestion.caido'].with_context(active_test=False).search([])
    env.add_to_compute(gestiones._fields['arrendatario_id'], gestiones)
    env.flush_all()
