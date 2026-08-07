from odoo import models, fields, api, tools
import random


class WhatsappMessage(models.Model):
    _inherit = 'whatsapp.message'

    def _get_chatbot_script_line(self, wa_account_id, message, channel):
        message_script = wa_account_id.wa_chatbot_id.step_type_ids.mapped(
            'multi_script_chatbot_ids').filtered(
            lambda script_message: script_message.message_for_multi_script == tools.html2plaintext(
                message.mail_message_id.body)).wa_chatbot_script_id

        current__chat_seq_script = (
            wa_account_id.wa_chatbot_id.step_type_ids
            .filtered(lambda l: l.sequence == channel.script_sequence)
        )
        if message_script:
            chatbot_script_lines = message_script
        elif current__chat_seq_script and current__chat_seq_script.step_call_type == 'interactive':
            chatbot_script_lines = current__chat_seq_script
        else:
            chatbot_script_lines = wa_account_id.wa_chatbot_id.step_type_ids[0]
        return chatbot_script_lines

    def _update_channel_script_sequence(self, wa_account_id, chat, channel):
        channel.write(
            {
                "wa_chatbot_id": chat.whatsapp_chatbot_id.id
                if wa_account_id.wa_chatbot_id
                   == chat.whatsapp_chatbot_id
                else False,
                "script_sequence": chat.sequence,
            }
        )

    def _create_chatbot_lead(self, partner_id, user_id, channel):
        crm_lead = self.env["crm.lead"].with_user(user_id.id).sudo().create({
            "name": partner_id.name + " WA ChatBot Lead ",
            "partner_id": partner_id.id,
            "email_from": partner_id.email if partner_id.email else False,
            "phone": partner_id.phone if partner_id.phone else False,
            "user_id": user_id.id,
            "type": "lead",
            "description": channel._get_wa_channel_history(),
        })
        return crm_lead

    def _create_chatbot_ticket(self, partner_id, user_id, channel):
        helpdesk_ticket = self.env["helpdesk.ticket"].with_user(user_id.id).sudo().create({
            "name": partner_id.name + " WA ChatBot Ticket ",
            "partner_id": partner_id.id,
            "partner_phone": partner_id.phone if partner_id.phone else False,
            "user_id": user_id.id,
            "description": channel._get_wa_channel_history(),
        })
        return helpdesk_ticket

    def _find_active_operator(self, wa_account_id, channel):
        available_operator = False
        active_operator = wa_account_id.wa_chatbot_id.mapped("user_ids").filtered(
            lambda user: user.im_status == "online")
        if active_operator:
            wa_chatbot_channels = wa_account_id.wa_chatbot_id.mapped("channel_ids")
            for wa_channel in wa_chatbot_channels:
                operator = active_operator.filtered(
                    lambda av_user: av_user.partner_id not in wa_channel.channel_member_ids.partner_id)
                if operator:
                    operator = random.choice(operator)
                    available_operator = operator.partner_id
                else:
                    available_operator = random.choice(active_operator).partner_id
            if available_operator:
                added_operator = channel.channel_partner_ids.filtered(lambda x: x.id == available_operator.id)
                if added_operator:
                    channel.write({
                        "is_chatbot_ended": True,
                        "wa_chatbot_id": False,
                    })
                else:
                    channel.write({
                        "channel_partner_ids": [(4, available_operator.id)],
                        "is_chatbot_ended": True,
                        "wa_chatbot_id": False,
                    })
                mail_channel_partner = self.env["discuss.channel.member"].sudo().search(
                    [("channel_id", "=", self.id), ("partner_id", "=", available_operator.id)])
                mail_channel_partner.write({"is_pinned": True})
        return available_operator

    def _send_action_whatsapp_message(self, record, chat, message, channel):
        res_user = channel.wa_account_id.notify_user_ids.sorted(lambda user: user.id) and channel.wa_account_id.notify_user_ids.sorted(lambda user: user.id)[0]
        if chat.action_id.last_message_conf == 'message':
            record.with_user(
                res_user.id).message_post(
                body=chat.action_id.no_operator_message if self.env.context.get(
                    "is_no_operator_message") else chat.action_id.message,
                message_type="whatsapp_message",
            )
        elif chat.action_id.last_message_conf == 'template':
            wa_template = chat.action_id.no_operator_template if self.env.context.get(
                "is_no_operator_message") else chat.action_id.wa_template_id
            mobile_number = record._find_value_from_field_path(wa_template.phone_field)
            whatsapp_composer = self.env["whatsapp.composer"].with_user(
                res_user.id).with_context({
                "active_id": record.id,
                "is_chatbot": True,
                "wa_chatbot_id": chat.whatsapp_chatbot_id.id,
            }).create({
                "phone": mobile_number,
                "wa_template_id": wa_template.id,
                "res_model": wa_template.model_id.model,
            })
            whatsapp_composer._send_whatsapp_template()
        else:
            channel.with_user(
                res_user.id).message_post(
                body=message,
                message_type="whatsapp_message",
            )

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        for message in messages:
            wa_account_id = message.wa_account_id
            channel = message.mail_message_id.channel_id if message.mail_message_id and message.mail_message_id.channel_id else False
            user_partner = wa_account_id.notify_user_ids.sorted(lambda user: user.id) and wa_account_id.notify_user_ids.sorted(lambda user: user.id)[0]
            partner_id = channel.whatsapp_partner_id if channel and channel.whatsapp_partner_id else False
            # If a message comes from user chatbot should stop working for a 1 hour here is the code for it:
            if channel and not channel.is_chatbot_ended and self.env.context.get(
                    'temporary_id') and channel.script_sequence != 1 and wa_account_id.is_chatbot_ended:
                channel.is_chatbot_ended = True
            if wa_account_id and user_partner and wa_account_id.wa_chatbot_id and message.state == 'received' and message.mail_message_id.message_type == 'whatsapp_message' and channel and not channel.is_chatbot_ended:
                message.mail_message_id.update({"wa_chatbot_id": wa_account_id.wa_chatbot_id.id})
                chatbot_script_lines = self._get_chatbot_script_line(wa_account_id, message, channel)
                for chat in chatbot_script_lines:
                    self._update_channel_script_sequence(wa_account_id, chat, channel)
                    if chat.step_call_type in ["template", "interactive"]:
                        mobile_number = partner_id._find_value_from_field_path(chat.template_id.phone_field)
                        whatsapp_composer = self.env["whatsapp.composer"].with_user(user_partner.id).with_context({
                            "active_id": partner_id.id,
                            "is_chatbot": True,
                            "wa_chatbot_id": channel.wa_chatbot_id.id,
                        }).create({
                            "phone": mobile_number,
                            "wa_template_id": chat.template_id.id,
                            "res_model": chat.template_id.model_id.model,
                        })
                        whatsapp_composer._send_whatsapp_template()
                    elif chat.step_call_type == "message":
                        channel.with_user(user_partner.id).message_post(
                            body=chat.answer,
                            message_type="whatsapp_message",
                        )
                    elif chat.step_call_type == "action":
                        if chat.action_id.binding_model_id.model == "crm.lead":
                            crm_lead = self._create_chatbot_lead(partner_id, user_partner, channel)
                            if crm_lead:
                                lead_message = f"Dear {partner_id.name}, We are pleased to inform you that your lead {crm_lead.name} has been successfully generated. Our team will be in touch with you shortly."
                                self._send_action_whatsapp_message(crm_lead, chat, lead_message, channel)
                                channel.write({
                                    "is_chatbot_ended": True,
                                    "wa_chatbot_id": False,
                                })
                        if chat.action_id.binding_model_id.model == "helpdesk.ticket":
                            helpdesk_ticket = self._create_chatbot_ticket(partner_id, user_partner, channel)
                            if helpdesk_ticket:
                                helpdesk_message = f"Dear {partner_id.name}, We are pleased to inform you that your Ticket {helpdesk_ticket.name} has been raised. Our team will be in touch with you shortly."
                                self._send_action_whatsapp_message(helpdesk_ticket, chat, helpdesk_message, channel)
                                channel.write({
                                    "is_chatbot_ended": True,
                                    "wa_chatbot_id": False,
                                })
                        if chat.action_id.binding_model_id.model == "discuss.channel":
                            active_operator = self._find_active_operator(wa_account_id, channel)
                            if active_operator:
                                operator_message = f"We are connecting you with one of our experts. Please wait a moment. You are now chatting with {active_operator.name}"
                                self._send_action_whatsapp_message(channel, chat, operator_message, channel)
                            else:
                                if wa_account_id.wa_chatbot_id.create_record:
                                    if wa_account_id.wa_chatbot_id.record_model_selection == 'crm_lead':
                                        crm_lead = self._create_chatbot_lead(partner_id, user_partner, channel)
                                        if crm_lead:
                                            operator_message = f"Apologies, but there are currently no active operators available. A lead has been created Ref: {crm_lead.name}, Our team will contact you shortly."
                                            self._send_action_whatsapp_message(crm_lead, chat, operator_message, channel)
                                            channel.write({
                                                "is_chatbot_ended": True,
                                                "wa_chatbot_id": False,
                                            })
                                    elif wa_account_id.wa_chatbot_id.record_model_selection == 'helpdesk_ticket':
                                        helpdesk_ticket = self._create_chatbot_ticket(partner_id, user_partner, channel)
                                        if helpdesk_ticket:
                                            operator_message = f"Apologies, but there are currently no active operators available. A helpdesk ticket has been created Ref: {helpdesk_ticket.name}, Our team will contact you shortly."
                                            self._send_action_whatsapp_message(helpdesk_ticket, chat,
                                                                               operator_message, channel)
                                            channel.write({
                                                "is_chatbot_ended": True,
                                                "wa_chatbot_id": False,
                                            })
                                else:
                                    operator_message = f"Apologies, but there are currently no active operators available. We will connect you with one shortly."
                                    self.with_context({'is_no_operator_message': True})._send_action_whatsapp_message(
                                        channel, chat, operator_message, channel)

        return messages
