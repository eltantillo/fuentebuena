# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import api, fields, models


class WhatsAppChatbot(models.Model):
    _name = "whatsapp.chatbot"
    _description = "Odoo Whatsapp Chatbot Automation"
    _rec_name = "title"
    _order = "title"

    title = fields.Char("Title", required=True, translate=True)
    active = fields.Boolean(default=True)
    image_1920 = fields.Image(readonly=False)
    step_type = fields.Selection(
        [
            ("message", "Message"),
            ("template", "Template"),
            ("interactive", "Interactive"),
        ],
        string="Step Type",
    )
    step_type_ids = fields.One2many(
        comodel_name="whatsapp.chatbot.script",
        inverse_name="whatsapp_chatbot_id",
        string="Message",
    )
    template_id = fields.Many2one(
        comodel_name="whatsapp.template", string="WhatsApp Template"
    )
    action_ids = fields.One2many(
        comodel_name="whatsapp.ir.actions", inverse_name="chatbot_id", string="Actions"
    )
    channel_ids = fields.One2many(
        comodel_name="discuss.channel", inverse_name="wa_chatbot_id", string="Channels"
    )
    wa_conversation_count = fields.Integer(
        "Number of conversation",
        compute="_compute_wa_conversation",
        store=False,
        readonly=True,
    )
    sequence = fields.Integer(string="Sequence")
    create_record = fields.Boolean("Create Lead/Ticket")
    record_model_selection = fields.Selection([("crm_lead", "CRM Lead"), ("helpdesk_ticket", "Helpdesk Ticket")], string="Record Selection")
    user_ids = fields.Many2many("res.users", string="Operators")


    @api.depends("channel_ids")
    def _compute_wa_conversation(self):
        channel_count = len(self.env['discuss.channel'].search([(("wa_chatbot_id", "in", self._ids))]))
        for record in self:
            record.wa_conversation_count = channel_count or 0
