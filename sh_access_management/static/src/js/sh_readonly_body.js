/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { onMounted } from "@odoo/owl";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        onMounted(() => {
            if (session.sh_is_readonly) {
                document.body.classList.add("sh_readonly_user");
            }
        });
    },
});
