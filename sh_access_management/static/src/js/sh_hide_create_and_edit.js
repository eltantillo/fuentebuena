

/** @odoo-module **/
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";

patch(Many2XAutocomplete.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.sh_global_hide_field_credit_edit = false;
        onWillStart(async () => {
            try {
                const result = await this.orm.call(
                    "sh.access.manager",
                    "get_access_restrictions",
                    [{ user_id: user.userId, company_id: user.activeCompany.id }]
                );
                if (result && result.model_restrictions) {
                    this.sh_global_hide_field_credit_edit = result.model_restrictions.sh_global_hide_field_credit_edit;
                }
            } catch (error) {
                console.error("Error fetching access restrictions:", error);
            }
        });
    },

    addCreateSuggestion({ request }) {
        if (this.sh_global_hide_field_credit_edit) {
            return false;
        }
        return super.addCreateSuggestion({ request });
    },

    addCreateEditSuggestion({ records, request }) {
        if (this.sh_global_hide_field_credit_edit) {
            return false;
        }
        return super.addCreateEditSuggestion({ records, request });
    },

    addNoRecordsSuggestion({ request, records }) {
        if (this.sh_global_hide_field_credit_edit) {
            return true;
        }
        return super.addNoRecordsSuggestion({ request, records });
    },

    suggest(request, lock) {
        const suggestions = super.suggest(request, lock);
        return suggestions;
    }
});
