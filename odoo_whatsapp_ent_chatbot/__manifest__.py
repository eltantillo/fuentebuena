{
    "name": "WhatsApp Chatbot for Odoo V19 Enterprise | WhatsApp Cloud API",
    "version": "1.0",
    "author": "TechUltra Solutions Private Limited",
    "category": "Discuss",
    "live_test_url": "https://www.youtube.com/playlist?list=PL8o8i9mlxsWg0R0lgWBXrDz6bGFJ64lOJ",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com/",
    "summary": "Odoo Whatsapp Chatbot Integration, Interactive Templates, Buttons send through odoo on WhatsApp and Message Automation",
    "description": """
        Odoo Whatsapp Chatbot Integration,
        Interactive Templates,
        Buttons send through odoo on WhatsApp and Message Automation
        Odoo Chatbot
        Chatbot
        Odoo
        ERP
        Odoo ERP
        WhatsApp
        Whats-App
        Discuss
        App
        Enterprise
        Odoo Whatsapp Chatbot
        Whatsapp Chatbot
        Odoo V19 Enterprise Edition
    """,
    "depends": ["whatsapp_extended"],
    "data": [
        "security/ir.model.access.csv",
        "data/wa_template.xml",
        "data/whatsapp_chatbot.xml",
        "views/whatsapp_chatbot_script_views.xml",
        "views/discuss_channel_views.xml",
        "views/whatsapp_chatbot_views.xml",
        "views/whatsapp_ir_action_views.xml",
        "views/whatsapp_account_inherit_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/odoo_whatsapp_ent_chatbot/static/src/scss/kanban_view.scss"
        ],
    },
    "images": ["static/description/main_screen.gif"],
    "price": 99,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
}
