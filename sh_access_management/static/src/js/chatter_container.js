/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(Chatter.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.globalRestrictions = {};
        this.currentRestrictions = {};

        onWillStart(async () => {
            try {
                const { model_restrictions } = await this.orm.call(
                    "sh.hide.chatter",
                    "sh_checkhide_chatter",
                    [{ user_id: user.userId, company_id: user.activeCompany.id }]
                );
                this.globalRestrictions = model_restrictions["global"] || {};
                this.currentRestrictions = model_restrictions[this.props.threadModel] || {};
            } catch (error) {
            }
        });
    },

    // Global has priority; model-level applies when global is not set.

    isSHChatterHidden() {
        if (this.globalRestrictions.sh_global_hide_full_chatter) return true;
        return this.currentRestrictions.hide_full_chatter || false;
    },

    isSHSendMessageHidden() {
        if (this.globalRestrictions.sh_global_hide_send_message) return true;
        return this.currentRestrictions.hide_send_msg || false;
    },

    isSHLogNoteHidden() {
        if (this.globalRestrictions.sh_global_hide_log_note) return true;
        return this.currentRestrictions.hide_log_notes || false;
    },

    isSHActivityHidden() {
        if (this.globalRestrictions.sh_global_hide_activity) return true;
        return this.currentRestrictions.hide_activity || false;
    },

    isSHSearchMessageIconHidden() {
        if (this.globalRestrictions.sh_global_hide_search_message_icon) return true;
        return this.currentRestrictions.hide_search_message_icon || false;
    },

    isSHAttachmentIconHidden() {
        if (this.globalRestrictions.sh_global_hide_attachment_icon) return true;
        return this.currentRestrictions.hide_attachments || false;
    },

    isSHFollowersIconHidden() {
        if (this.globalRestrictions.sh_global_hide_followers_icon) return true;
        return this.currentRestrictions.hide_followers || false;
    },
});
