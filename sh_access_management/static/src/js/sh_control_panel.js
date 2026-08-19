/** @odoo-module **/

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, onMounted, useState, onWillUpdateProps } from "@odoo/owl";
import { user } from "@web/core/user";
import { session } from "@web/session";

patch(ControlPanel.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = this.state || useState({});
        Object.assign(this.state, { hide_filter: false, hide_group_by: false, hide_favourite: false, hide_search_panel: false, hide_search_bar: false });
        onWillStart(async () => { await this._shCheckFullSearchRestrictions(); });
        onMounted(() => this._shApplyFullSearchRestrictions());
        onWillUpdateProps(async () => {
            await this._shCheckFullSearchRestrictions();
            this._shApplyFullSearchRestrictions();
        });
    },
    async _shCheckFullSearchRestrictions() {
        const model = this.env.searchModel ? this.env.searchModel.resModel : false;
        if (!model) return;
        const dic = await this.orm.call("sh.access.model", "check_crud_operation", [{ user_id: session.uid, company_id: user.activeCompany.id }], {});
        const v = dic[model] || {};
        const global = dic["__global__"] || {};
        const rd_rules = v.sh_conditional_rules || [];

        this.state.hide_filter = false;
        this.state.hide_group_by = false;
        this.state.hide_favourite = false;
        this.state.hide_search_panel = false;
        this.state.hide_search_bar = false;

        // 1. Global
        if (global.sh_global_hide_filter) this.state.hide_filter = true;
        if (global.sh_global_hide_group) this.state.hide_group_by = true;
        if (global.sh_global_hide_favourite) this.state.hide_favourite = true;
        if (global.sh_global_hide_search_panel) this.state.hide_search_panel = true;
        if (global.sh_global_hide_search_bar) this.state.hide_search_bar = true;

        // 2. Model (Additive)
        if (v.sh_hide_filter) this.state.hide_filter = true;
        if (v.sh_hide_group_by) this.state.hide_group_by = true;
        if (v.sh_hide_favourite) this.state.hide_favourite = true;
        if (v.sh_hide_search_panel) this.state.hide_search_panel = true;

        // 3. Conditional (Additive)
        if (rd_rules.some(r => r.hide_filter)) this.state.hide_filter = true;
        if (rd_rules.some(r => r.hide_group_by)) this.state.hide_group_by = true;
        if (rd_rules.some(r => r.hide_favourite)) this.state.hide_favourite = true;
        if (rd_rules.some(r => r.hide_search_panel)) this.state.hide_search_panel = true;
        if (rd_rules.some(r => r.hide_search_bar)) this.state.hide_search_bar = true;

        // 4. View Switcher Hiding
        if (this.env.config && this.env.config.viewSwitcherEntries) {
            const hiddenViews = await this.orm.call("sh.access.manager", "get_hidden_views", [], {
                model: model,
                user_id: user.userId
            });
            if (hiddenViews && hiddenViews.length > 0) {
                this.env.config.viewSwitcherEntries = this.env.config.viewSwitcherEntries.filter(
                    entry => !hiddenViews.includes(entry.type)
                );
            }
        }
    },
    _shApplyFullSearchRestrictions() {
        setTimeout(() => {
            if (this.state.hide_filter) document.querySelector(".o_filters_menu_button")?.style.setProperty("display", "none", "important");
            if (this.state.hide_group_by) document.querySelector(".o_group_by_menu_button")?.style.setProperty("display", "none", "important");
            if (this.state.hide_favourite) document.querySelector(".o_favorite_menu_button")?.style.setProperty("display", "none", "important");
            if (this.state.hide_search_panel) document.querySelector(".o_search_panel")?.style.setProperty("display", "none", "important");
            if (this.state.hide_search_bar) document.querySelector(".o_control_panel_main_buttons .o_searchview")?.style.setProperty("display", "none", "important");
        }, 0);
    }
});
