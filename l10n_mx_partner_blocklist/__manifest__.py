{
    "name": "Partner blocklist for Mexican Localization",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com",
    "summary": "Manage the partner blocklist provided by the SAT and avoid to buy and sell to blocked partners.",
    "license": "OPL-1",
    "category": "Accounting/Accounting",
    "version": "19.0.1.0.0",
    "depends": [
        "l10n_mx_edi",
        "contacts",
    ],
    "data": [
        "security/blocklist_groups.xml",
        "security/ir.model.access.csv",
        "data/cron_partner_blacklist.xml",
        "data/partner_blocklist_status.xml",
        "data/ir_config_parameter.xml",
        "views/res_partner_view.xml",
        "views/res_partner_blacklist.xml",
    ],
    "demo": [
        "demo/settings.xml",
        "demo/ir_config_parameter_demo.xml",
        "demo/res_users_demo.xml",
    ],
    "images": [
        "static/description/main_screen.jpeg",
    ],
    "live_test_url": "https://vauxoo.com/r/lmpb_190",
    "price": 100,
    "currency": "USD",
    "pre_init_hook": "pre_init_hook",
}
