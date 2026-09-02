# -*- coding: utf-8 -*-
# Copyright 2026 Morwi Encoders Consulting SA de CV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Mark Pilotea so the CRM knows when to show its origination fields.

    The fields are meant for one company, and pointing at it by database id
    would break on any instance where Pilotea is not company 2, so the rule
    lives in a flag on the company. This only seeds it: the flag can be moved
    by hand from the company form afterwards.
    """
    company = env['res.company'].search([('name', 'ilike', 'Pilotea')], limit=1)
    if not company:
        company = env['res.company'].browse(2).exists()
    if company:
        company.es_pilotea = True
        _logger.info("crm_pilotea: origination fields tied to company %s (id %s)",
                     company.name, company.id)
    else:
        _logger.warning(
            "crm_pilotea: no Pilotea company found, the origination fields stay "
            "hidden until 'Es Pilotea' is ticked on a company.")
