/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { FormController } from "@web/views/form/form_controller";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { CalendarController } from "@web/views/calendar/calendar_controller";
import { ExportAll, exportAllItem } from "@web/views/list/export_all/export_all";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { onWillStart, onMounted, onPatched, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { user } from "@web/core/user";

// ────────────────────────────────────────────────────────────────────────────
// Helper: hide / show DOM elements reliably
// ────────────────────────────────────────────────────────────────────────────
function applyDisplay(selector, show) {
    document.querySelectorAll(selector).forEach(el => {
        el.style.setProperty("display", show ? "" : "none", "important");
    });
}

// ════════════════════════════════════════════════════════════════════════════
// LIST CONTROLLER
// ════════════════════════════════════════════════════════════════════════════
patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = this.state || useState({});
        Object.assign(this.state, {
            rpc_result: null,
            group_show_create: true,
            group_show_action: true,
            group_show_print: true,
            group_show_export: true,
            group_show_delete: true,
            group_show_duplicate: true,
            group_show_archive: true,
        });

        onWillStart(async () => {
            const uid = user.userId;
            this.state.rpc_result = await this.orm.call(
                "sh.access.model", "check_crud_operation",
                [{ user_id: uid, company_id: user.activeCompany.id }], {}
            );
            this._shComputeListState();
        });
        onMounted(() => this._shApplyListDOM());
        onPatched(() => this._shApplyListDOM());
    },

    _shComputeListState() {
        const dic = this.state.rpc_result || {};
        const model = this.props.resModel;
        const v = dic[model] || {};
        const g = dic["__global__"] || {};
        const rules = v.sh_conditional_rules || [];

        // Reset
        this.state.group_show_create = true;
        this.state.group_show_action = true;
        this.state.group_show_print = true;
        this.state.group_show_export = true;
        this.state.group_show_delete = true;
        this.state.group_show_duplicate = true;
        this.state.group_show_archive = true;
        this.state.group_show_unarchive = true;

        // 1 – Global
        if (g.sh_global_hide_create || g.sh_readonly) this.state.group_show_create = false;
        if (g.sh_global_hide_action_button) this.state.group_show_action = false;
        if (g.sh_global_hide_print_button) this.state.group_show_print = false;
        if (g.hide_export || g.sh_readonly) this.state.group_show_export = false;
        if (g.sh_global_hide_delete || g.sh_readonly) this.state.group_show_delete = false;
        if (g.sh_global_hide_duplicate || g.sh_readonly) this.state.group_show_duplicate = false;
        if (g.sh_global_hide_archive || g.sh_readonly) this.state.group_show_archive = false;
        if (g.sh_global_hide_unarchive || g.sh_readonly) this.state.group_show_unarchive = false;

        // 2 – Model-wise
        if (v.hide_create || v.hide_edit) this.state.group_show_create = false;
        if (v.sh_hide_action) this.state.group_show_action = false;
        if (v.sh_hide_print) this.state.group_show_print = false;
        if (v.hide_export) this.state.group_show_export = false;
        if (v.hide_delete || v.hide_edit) this.state.group_show_delete = false;
        if (v.hide_duplicate || v.hide_edit) this.state.group_show_duplicate = false;
        if (v.hide_archieve || v.hide_edit) {
            this.state.group_show_archive = false;
            this.state.group_show_unarchive = false;
        }

        // 3 – Conditional
        if (rules.some(r => r.hide_create)) this.state.group_show_create = false;
        if (rules.some(r => r.hide_export)) this.state.group_show_export = false;
        if (rules.some(r => r.hide_action)) this.state.group_show_action = false;
        if (rules.some(r => r.hide_print)) this.state.group_show_print = false;
        if (rules.some(r => r.hide_delete)) this.state.group_show_delete = false;
    },


    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems ? super.getStaticActionMenuItems() : {};

        // Filter items based on our state flags
        if (items.export) {
            const originalIsAvailable = items.export.isAvailable || (() => true);
            items.export.isAvailable = () => originalIsAvailable() && this.state.group_show_export;
        }
        if (items.delete) {
            const originalIsAvailable = items.delete.isAvailable || (() => true);
            items.delete.isAvailable = () => originalIsAvailable() && this.state.group_show_delete;
        }
        if (items.duplicate) {
            const originalIsAvailable = items.duplicate.isAvailable || (() => true);
            items.duplicate.isAvailable = () => originalIsAvailable() && this.state.group_show_duplicate;
        }
        if (items.archive) {
            const originalIsAvailable = items.archive.isAvailable || (() => true);
            items.archive.isAvailable = () => originalIsAvailable() && this.state.group_show_archive;
        }
        if (items.unarchive) {
            const originalIsAvailable = items.unarchive.isAvailable || (() => true);
            items.unarchive.isAvailable = () => originalIsAvailable() && this.state.group_show_unarchive;
        }

        return items;
    },

    _shApplyListDOM() {
        applyDisplay(".o_list_button_add", this.state.group_show_create);
        // Cog button (visible when records selected)
        applyDisplay(".o_cog_menu", this.state.group_show_action);
        // Top-level Print button (visible when records selected)
        applyDisplay(".o_list_selection_box ~ .o_control_panel_actions .o_print_button, .o_action_buttons .o_print_button", this.state.group_show_print);
    },

    getActionMenuItems() {
        const items = super.getActionMenuItems ? super.getActionMenuItems() : {};
        if (!this.state.group_show_action) { items.other = []; items.print = []; }
        if (!this.state.group_show_print) items.print = [];
        return items;
    },
});

// ════════════════════════════════════════════════════════════════════════════
// FORM CONTROLLER
// ════════════════════════════════════════════════════════════════════════════
patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.state = this.state || useState({});
        Object.assign(this.state, {
            rpc_result: null,
            group_show_create: true,
            group_show_delete: true,
            group_show_action: true,
            group_show_print: true,
            group_show_export: true,
            group_show_duplicate: true,
            group_show_archive: true,
            group_show_unarchive: true,
            group_show_add_properties: true,
        });

        onWillStart(async () => {
            const uid = user.userId;
            this.state.rpc_result = await this.orm.call(
                "sh.access.model", "check_crud_operation",
                [{ user_id: uid, company_id: user.activeCompany.id }], {}
            );
        });
        onMounted(async () => { await this._shApplyFormRestrictions(); });
        onPatched(async () => { await this._shApplyFormRestrictions(); });
    },

    async _shApplyFormRestrictions() {
        const dic = this.state.rpc_result || {};
        const model = this.props.resModel;
        const res_id = this.model?.root?.resId;
        const v = dic[model] || {};
        const g = dic["__global__"] || {};
        const rules = v.sh_conditional_rules || [];

        this.state.group_show_create = true;
        this.state.group_show_delete = true;
        this.state.group_show_action = true;
        this.state.group_show_print = true;
        this.state.group_show_export = true;
        this.state.group_show_duplicate = true;
        this.state.group_show_archive = true;
        this.state.group_show_unarchive = true;
        this.state.group_show_add_properties = true;
        document.querySelector('.o_form_view')?.classList.remove('sh_conditional_no_edit');

        // 1 – Global
        if (g.sh_global_hide_create || g.sh_readonly) this.state.group_show_create = false;
        if (g.sh_global_hide_create || g.sh_readonly) this.state.group_show_create = false;
        if (g.sh_global_hide_action_button) this.state.group_show_action = false;
        if (g.sh_global_hide_print_button) this.state.group_show_print = false;
        if (g.hide_export || g.sh_readonly) this.state.group_show_export = false;
        if (g.sh_global_hide_delete || g.sh_readonly) this.state.group_show_delete = false;
        if (g.sh_global_hide_duplicate || g.sh_readonly) this.state.group_show_duplicate = false;
        if (g.sh_global_hide_archive || g.sh_readonly) this.state.group_show_archive = false;
        if (g.sh_global_hide_unarchive || g.sh_readonly) this.state.group_show_unarchive = false;
        if (g.hide_add_property) this.state.group_show_add_properties = false;

        // 2 – Model-wise
        if (v.hide_create || v.hide_edit) this.state.group_show_create = false;
        if (v.sh_hide_action) this.state.group_show_action = false;
        if (v.sh_hide_print) this.state.group_show_print = false;
        if (v.hide_export) this.state.group_show_export = false;
        if (v.hide_delete || v.hide_edit) this.state.group_show_delete = false;
        if (v.hide_duplicate || v.hide_edit) this.state.group_show_duplicate = false;
        if (v.hide_archieve || v.hide_edit) {
            this.state.group_show_archive = false;
            this.state.group_show_unarchive = false;
        }

        // 3 – Per-record Conditional
        if (rules.some(r => r.hide_create)) this.state.group_show_create = false;
        if (rules.some(r => r.hide_export)) this.state.group_show_export = false;
        if (rules.some(r => r.hide_action)) this.state.group_show_action = false;
        if (rules.some(r => r.hide_print)) this.state.group_show_print = false;
        if (rules.some(r => r.hide_delete)) this.state.group_show_delete = false;

        if (rules.length > 0 && res_id) {
            try {
                const matched = await this.orm.call(
                    "sh.conditional.domain", "sh_check_record_matches_rules", [],
                    { model_name: model, res_id: res_id, rules: rules }
                );
                if (matched) {
                    if (matched.hide_create) this.state.group_show_create = false;
                    if (matched.hide_delete) this.state.group_show_delete = false;
                    if (matched.hide_archive) this.state.group_show_archive = false;
                    if (matched.hide_unarchive) this.state.group_show_unarchive = false;
                    if (matched.hide_action) this.state.group_show_action = false;
                    if (matched.hide_print) this.state.group_show_print = false;
                    if (matched.hide_write) {
                        document.querySelector('.o_form_view')?.classList.add('sh_conditional_no_edit');
                    }
                }
            } catch (e) {
                // error handled
            }
        }

        // Apply DOM
        applyDisplay(".o_form_button_create, .o_list_button_add", this.state.group_show_create);
        applyDisplay(".o_cp_action_menus button.o_dropdown_toggler, .o_action_menu_toggle, .o_cog_menu", this.state.group_show_action);
        if (!this.state.group_show_print) {
            applyDisplay('.o_print_dropdown button, button[title*="Print"]', false);
        }
    },

    getActionMenuItems() {
        const items = super.getActionMenuItems ? super.getActionMenuItems() : {};
        if (!this.state.group_show_action) { items.other = []; items.print = []; }
        if (!this.state.group_show_print) items.print = [];
        return items;
    },

    getStaticActionMenuItems() {
        const items = super.getStaticActionMenuItems ? super.getStaticActionMenuItems() : {};
        if (items.delete) {
            const originalIsAvailable = items.delete.isAvailable || (() => true);
            items.delete.isAvailable = () => originalIsAvailable() && this.state.group_show_delete;
        }
        if (items.duplicate) {
            const originalIsAvailable = items.duplicate.isAvailable || (() => true);
            items.duplicate.isAvailable = () => originalIsAvailable() && this.state.group_show_duplicate;
        }
        if (items.archive) {
            const originalIsAvailable = items.archive.isAvailable || (() => true);
            items.archive.isAvailable = () => originalIsAvailable() && this.state.group_show_archive;
        }
        if (items.unarchive) {
            const originalIsAvailable = items.unarchive.isAvailable || (() => true);
            items.unarchive.isAvailable = () => originalIsAvailable() && this.state.group_show_unarchive;
        }
        if (items.addPropertyFieldValue) {
            const originalIsAvailable = items.addPropertyFieldValue.isAvailable || (() => true);
            items.addPropertyFieldValue.isAvailable = () => originalIsAvailable() && this.state.group_show_add_properties;
        }
        return items;
    },
});

// ════════════════════════════════════════════════════════════════════════════
// KANBAN CONTROLLER
// ════════════════════════════════════════════════════════════════════════════
patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = this.state || useState({});
        Object.assign(this.state, { group_show_create: true, rpc_result: null });

        onWillStart(async () => {
            const uid = user.userId;
            this.state.rpc_result = await this.orm.call(
                "sh.access.model", "check_crud_operation",
                [{ user_id: uid, company_id: user.activeCompany.id }], {}
            );
            this._shComputeKanbanState();
        });
        onMounted(() => applyDisplay(".o-kanban-button-new", this.state.group_show_create));
        onPatched(() => applyDisplay(".o-kanban-button-new", this.state.group_show_create));
    },

    _shComputeKanbanState() {
        const dic = this.state.rpc_result || {};
        const model = this.props.resModel;
        const v = dic[model] || {};
        const g = dic["__global__"] || {};
        const rules = v.sh_conditional_rules || [];

        this.state.group_show_create = true;
        if (g.sh_global_hide_create || g.sh_readonly) this.state.group_show_create = false;
        if (v.hide_create || v.hide_edit) this.state.group_show_create = false;
        if (rules.some(r => r.hide_create)) this.state.group_show_create = false;
    }
});

// ════════════════════════════════════════════════════════════════════════════
// CALENDAR CONTROLLER
// ════════════════════════════════════════════════════════════════════════════
patch(CalendarController.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = this.state || useState({});
        Object.assign(this.state, { group_show_create: true, rpc_result: null });

        onWillStart(async () => {
            const uid = user.userId;
            this.state.rpc_result = await this.orm.call(
                "sh.access.model", "check_crud_operation",
                [{ user_id: uid, company_id: user.activeCompany.id }], {}
            );
            this._shComputeCalendarState();
        });
        onMounted(() => this._shApplyCalendarDOM());
        onPatched(() => this._shApplyCalendarDOM());
    },

    _shComputeCalendarState() {
        const dic = this.state.rpc_result || {};
        const model = this.props.resModel;
        const v = dic[model] || {};
        const g = dic["__global__"] || {};
        const rules = v.sh_conditional_rules || [];

        this.state.group_show_create = true;
        if (g.sh_global_hide_create || g.sh_readonly) this.state.group_show_create = false;
        if (v.hide_create || v.hide_edit) this.state.group_show_create = false;
        if (rules.some(r => r.hide_create)) this.state.group_show_create = false;
    },

    _shApplyCalendarDOM() {
        // DOM fallback to catch various "New" button implementations in Calendar
        const rootEl = this.el || document;
        const allButtons = rootEl.querySelectorAll("button");
        allButtons.forEach((btn) => {
            const text = (btn.textContent || "").trim();
            const classes = btn.className;
            const hotkey = btn.dataset ? btn.dataset.hotkey : undefined;

            if (!this.state.group_show_create) {
                const looksLikeNew =
                    hotkey === "c" ||
                    classes.includes("o_calendar_button_new") ||
                    classes.includes("o_button_new") ||
                    (text && text.toLowerCase() === "new");

                if (looksLikeNew) {
                    btn.style.setProperty("display", "none", "important");
                }
            }
        });
    }
});

/* ==================== ExportAll Patch ==================== */
patch(ExportAll.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.state = this.state || useState({});
        Object.assign(this.state, {
            rpc_result: null,
            group_show_export: true,
        });

        onWillStart(async () => {
            const uid = user.userId;
            this.state.rpc_result = await this.orm.call(
                "sh.access.model", "check_crud_operation",
                [{ user_id: uid, company_id: user.activeCompany.id }], {}
            );
            this._shComputeExportState();
        });
    },

    _shComputeExportState() {
        const dic = this.state.rpc_result || {};
        const global = dic["__global__"] || {};
        const model = this.env.model?.config?.resModel;
        const v = dic[model] || {};
        const rules = v.sh_conditional_rules || [];

        this.state.group_show_export = true;

        // 1 – Global
        if (global.hide_export || global.hide_action || global.sh_readonly) {
            this.state.group_show_export = false;
        }

        // 2 – Model-wise
        if (v.hide_export) this.state.group_show_export = false;

        // 3 – Conditional
        if (rules.some(r => r.hide_export)) this.state.group_show_export = false;
    }
});

/* ==================== Cog Menu Registry Override ==================== */
const cogMenuRegistry = registry.category("cogMenu");
export const shExportAllItem = {
    ...exportAllItem,
    isDisplayed: async (env) => {
        if (env.config.viewType !== "list" || env.model.root.selection.length > 0) {
            return false;
        }
        try {
            const modelDic = await env.services.orm.call(
                "sh.access.model", "check_crud_operation",
                [{ user_id: user.userId, company_id: user.activeCompany.id }], {}
            );
            const modelName = env.model.config.resModel;
            const global = modelDic["__global__"] || {};
            const v = modelDic[modelName] || {};
            const rules = v.sh_conditional_rules || [];

            if (global.hide_export || global.hide_action || global.sh_readonly) return false;
            if (v.hide_export) return false;
            if (rules.some(r => r.hide_export)) return false;
        } catch (e) {
            return true;
        }
        return true;
    },
};
cogMenuRegistry.add("export-all-menu", shExportAllItem, { sequence: 10, force: true });

