/** @odoo-module **/

import { exportAllItem } from "@web/views/list/export_all/export_all";
import { registry } from "@web/core/registry";
import { exprToBoolean } from "@web/core/utils/strings";
import { user } from "@web/core/user";

const cogMenuRegistry = registry.category("cogMenu");

export const shExportAllItem = {
    ...exportAllItem,
    isDisplayed: async (env) => {
        // Standard base conditions from Odoo
        if (
            env.config.viewType !== "list" ||
            env.model.root.selection.length > 0 ||
            !(await user.hasGroup("base.group_allow_export")) ||
            !exprToBoolean(env.config.viewArch.getAttribute("export_xlsx"), true)
        ) {
            return false;
        }

        try {
            const modelDic = await env.services.orm.call(
                "sh.access.model",
                "check_crud_operation",
                [{ user_id: user.userId, company_id: user.activeCompany.id }],
                {}
            );

            const modelName = env.model.config.resModel;
            const global = modelDic["__global__"] || {};
            const v = modelDic[modelName] || {};
            const rules = v.sh_conditional_rules || [];

            // 1 – Global
            if (global.hide_export || global.hide_action || global.sh_readonly) {
                return false;
            }

            // 2 – Model-wise
            if (v.hide_export) {
                return false;
            }

            // 3 – Conditional
            if (rules.some(r => r.hide_export)) {
                return false;
            }

        } catch (e) {
            return true;
        }

        return true;
    },
};

cogMenuRegistry.add("export-all-menu", shExportAllItem, { sequence: 10, force: true });
