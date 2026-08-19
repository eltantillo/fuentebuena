/** @odoo-module **/

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";

patch(Composer.prototype, {
    setup() {
        super.setup();
        this.sh_is_readonly = session.sh_is_readonly;
        if (this.sh_is_readonly) {
            this.state.active = false;
        }
    },

    get placeholder() {
        if (this.sh_is_readonly) {
            return _t("🚫 You have read-only access and are not permitted to modify any records.");
        }
        return super.placeholder;
    }
});
