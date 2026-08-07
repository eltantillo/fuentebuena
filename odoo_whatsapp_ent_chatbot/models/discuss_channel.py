# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import random
from markupsafe import Markup
from odoo.tools import html2plaintext
from odoo import api, fields, models, tools


class ChatbotDiscussChannel(models.Model):
    _inherit = "discuss.channel"

    wa_chatbot_id = fields.Many2one(
        comodel_name="whatsapp.chatbot", string="Whatsapp Chatbot"
    )
    message_ids = fields.One2many(
        "mail.message",
        "res_id",
        domain=lambda self: [
            ("wa_chatbot_id", "!=", False),
            ("wa_chatbot_id", "=", self.wa_chatbot_id.id),
        ],
        string="Messages",
    )
    script_sequence = fields.Integer(string="Sequence", default=1)
    is_chatbot_ended = fields.Boolean(string="Inactivate Chatbot")

    def chatbot_activate(self):
        channels = self.search([])
        for rec in channels:
            if rec.is_chatbot_ended:
                rec.is_chatbot_ended = False
                rec.wa_chatbot_id = rec.wa_account_id.wa_chatbot_id.id

    def _get_wa_channel_history(self):
        """
        Converting message body back to plaintext for correct data formatting in HTML field.
        """
        return Markup('').join(
            Markup('%s: %s<br/>') % (message.author_id.name or self.anonymous_name, html2plaintext(message.body))
            for message in self.message_ids.sorted('id')
        )

class ChatbotMailMessage(models.Model):
    _inherit = "mail.message"

    wa_chatbot_id = fields.Many2one(
        comodel_name="whatsapp.chatbot", string="Whatsapp Chatbot"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self.env.context.get("wa_chatbot_id"):
                whatsapp_chatbot = self.env["whatsapp.chatbot"].search(
                    [("id", "=", self.env.context.get("wa_chatbot_id"))]
                )
                if whatsapp_chatbot:
                    vals.update(
                        {
                            "wa_chatbot_id": whatsapp_chatbot.id,
                        }
                    )
        return super(ChatbotMailMessage, self).create(vals_list)
