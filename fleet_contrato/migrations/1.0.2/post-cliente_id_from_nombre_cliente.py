import logging
import unicodedata

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _normalize(name):
    """Fold a captured name so that it can be compared with a partner's.

    The legacy text was typed by hand, so it differs from the contact in case,
    accents and padding. Everything else is left alone: a name that only looks
    similar is not a match.
    """
    if not name:
        return ''
    decomposed = unicodedata.normalize('NFKD', name)
    unaccented = ''.join(c for c in decomposed if not unicodedata.combining(c))
    return ' '.join(unaccented.lower().split())


def _partners_by_name(cr):
    """Map every unambiguous partner name to its id, active contacts first.

    A name shared by several contacts resolves to nothing: guessing which of
    two homonyms signed the contract would be worse than falling back to the
    driver.
    """
    cr.execute("""
        SELECT id, name, active
        FROM res_partner
        WHERE name IS NOT NULL AND btrim(name) != ''
    """)
    buckets = {True: {}, False: {}}
    for partner_id, name, is_active in cr.fetchall():
        key = _normalize(name)
        if not key:
            continue
        bucket = buckets[bool(is_active)]
        bucket[key] = None if key in bucket else partner_id

    resolved, ambiguous = {}, set()
    for key in set(buckets[True]) | set(buckets[False]):
        bucket = buckets[True] if key in buckets[True] else buckets[False]
        if bucket[key]:
            resolved[key] = bucket[key]
        else:
            ambiguous.add(key)
    return resolved, ambiguous


def migrate(cr, version):
    """Turn the free-text lessee name into the `cliente_id` relation.

    `nombre_cliente` held the lessee as typed by the legacy system while
    `cliente_id` was a stored compute mirroring the vehicle's driver, and the
    contracts one2many on `res.partner` hangs off the latter. Both fields are
    now a single editable `cliente_id`, so the text has to be resolved into a
    contact before it is dropped.

    Contracts whose text matches no single contact keep the driver: that is
    what the customer's contract list already showed, and blanking them would
    empty the 360 sheet for those customers. The `nombre_cliente` column is
    left in the database as the record of what was captured.
    """
    cr.execute("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'fleet_vehicle_log_contract' AND column_name = 'nombre_cliente'
    """)
    if not cr.fetchone():
        _logger.info("fleet_contrato: no nombre_cliente column, nothing to migrate")
        return

    partners, ambiguous_names = _partners_by_name(cr)
    cr.execute("""
        SELECT c.id, c.nombre_cliente, c.cliente_id, v.driver_id
        FROM fleet_vehicle_log_contract c
        LEFT JOIN fleet_vehicle v ON v.id = c.vehicle_id
    """)
    rows = cr.fetchall()

    updates = {}
    counts = {'matched': 0, 'driver': 0, 'ambiguous': 0, 'no_text': 0, 'empty': 0}
    unmatched = set()
    for contract_id, nombre, cliente_id, driver_id in rows:
        key = _normalize(nombre)
        if not key:
            counts['no_text'] += 1
            continue
        partner_id = partners.get(key)
        if partner_id:
            counts['matched'] += 1
        else:
            if key in ambiguous_names:
                counts['ambiguous'] += 1
            else:
                unmatched.add(nombre.strip())
            partner_id = driver_id
            counts['driver' if driver_id else 'empty'] += 1
        if partner_id and partner_id != cliente_id:
            updates.setdefault(partner_id, []).append(contract_id)

    for partner_id, contract_ids in updates.items():
        cr.execute(
            "UPDATE fleet_vehicle_log_contract SET cliente_id = %s WHERE id IN %s",
            (partner_id, tuple(contract_ids)),
        )

    _logger.info(
        "fleet_contrato: %s contracts, %s matched by name, %s fell back to the driver "
        "(%s of them because the name has homonym contacts), %s had no driver to fall "
        "back to, %s had no name; %s contracts rewritten",
        len(rows), counts['matched'], counts['driver'], counts['ambiguous'],
        counts['empty'], counts['no_text'],
        sum(len(ids) for ids in updates.values()),
    )
    if unmatched:
        _logger.info(
            "fleet_contrato: names with no contact (%s): %s",
            len(unmatched), '; '.join(sorted(unmatched)),
        )

    api.Environment(cr, SUPERUSER_ID, {}).invalidate_all()
