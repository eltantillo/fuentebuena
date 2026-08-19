/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";

const originalSetup = WebClient.prototype.setup;

patch(WebClient.prototype, {
    __patch_name__: "sh_access_management.HideSpreadsheet",
    setup() {
        originalSetup.apply(this, arguments);
        const cogMenuRegistry = registry.category("cogMenu");

        if (cogMenuRegistry.contains("spreadsheet-cog-menu")) {
            const spreadsheetCogMenu = cogMenuRegistry.get("spreadsheet-cog-menu");

            cogMenuRegistry.add(
                "spreadsheet-cog-menu",
                {
                    ...spreadsheetCogMenu,
                    isDisplayed: async (env) => {
                        const originalIsDisplayed = await spreadsheetCogMenu.isDisplayed(env);

                        if (!originalIsDisplayed) {
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
                            const hasModelLine = modelName && Object.prototype.hasOwnProperty.call(modelDic, modelName);

                            // If model has a model-line entry, use model-level setting (overrides global)
                            if (hasModelLine) {
                                if (modelDic[modelName]?.hide_spreadsheet === true) {
                                    return false;
                                }
                            } else {
                                // No model-line entry: apply global restriction
                                if (modelDic["__global__"]?.hide_spreadsheet === true) {
                                    return false;
                                }
                            }
                        } catch (e) {
                            return true;
                        }

                        return true;
                    },
                },
                { force: true }
            );
        }
    },
});
