/** @odoo-module **/

import { importRecordsItem } from "@base_import/import_records/import_records";
import { registry } from "@web/core/registry";
import { exprToBoolean } from "@web/core/utils/strings";
import { user } from "@web/core/user";

const cogMenuRegistry = registry.category("cogMenu");

export const shImportRecordsItem = {
    ...importRecordsItem,
    isDisplayed: async (env) => {
        const { config, isSmall, services } = env;
        // Standard base conditions
        if (
            isSmall ||
            config.actionType !== "ir.actions.act_window" ||
            !["kanban", "list"].includes(config.viewType) ||
            !exprToBoolean(config.viewArch.getAttribute("import"), true) ||
            !exprToBoolean(config.viewArch.getAttribute("create"), true)
        ) {
            return false;
        }

        try {
            const modelDic = await services.orm.call(
                "sh.access.model",
                "check_crud_operation",
                [{ user_id: user.userId, company_id: user.activeCompany.id }],
                {}
            );
            const modelName = env.searchModel?.resModel || env.model?.config?.resModel || config?.resModel || config?.action?.res_model;
            const global = modelDic["__global__"] || {};
            const v = modelDic[modelName] || {};
            const rules = v.sh_conditional_rules || [];

            // 1 - Global
            if (global.hide_import || global.sh_readonly) {
                return false;
            }

            // 2 - Model-wise
            if (v.hide_import) {
                return false;
            }

            // 3 - Conditional
            if (rules.some(r => r.hide_import)) {
                return false;
            }

        } catch (e) {
            return true;
        }

        return true;
    },
};

cogMenuRegistry.add("import-menu", shImportRecordsItem, { sequence: 1, force: true });
