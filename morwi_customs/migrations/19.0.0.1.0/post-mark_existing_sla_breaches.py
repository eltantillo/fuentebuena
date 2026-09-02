from odoo import SUPERUSER_ID, api, fields


def migrate(cr, version):
    """Stamp the tickets that had already run out of response time.

    The alert is new, so on its first run the cron would find every ticket
    whose deadline went by before the feature existed and drop that whole
    backlog on the team leaders at once. They are stamped as if the alert had
    already gone out, so only the breaches from here on raise an activity.

    Clearing `sla_breach_alert_date` on a ticket is enough to have it alerted
    anyway, should the backlog be worth reviewing one by one.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    overdue = env['helpdesk.ticket'].with_context(active_test=False).search([
        ('sla_deadline', '!=', False),
        ('sla_deadline', '<', fields.Datetime.now()),
    ])
    if overdue:
        overdue.write({'sla_breach_alert_date': fields.Datetime.now()})
