from odoo import tools


def pre_init_hook(env):
    _create_column_l10n_mx_in_blocklist(env)


def _create_column_l10n_mx_in_blocklist(env):
    """Create the `l10n_mx_in_blocklist` column in the `res_partner` table if it does not exist.
    This avoids setting a default value on all records, which could be computationally expensive.
    """
    if not tools.sql.column_exists(env.cr, "res_partner", "l10n_mx_in_blocklist"):
        tools.sql.create_column(env.cr, "res_partner", "l10n_mx_in_blocklist", "varchar")
