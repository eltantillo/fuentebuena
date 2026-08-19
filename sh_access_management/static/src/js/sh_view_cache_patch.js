/** @odoo-module **/

import { viewService } from "@web/views/view_service";
import { patch } from "@web/core/utils/patch";

patch(viewService, {
    start(env, { orm }) {
        const api = super.start(...arguments);
        const originalLoadViews = api.loadViews;

        api.loadViews = async (params, options = {}) => {
            const { context, resModel, views } = params;

            // Re-implementing the logic of loadViews but without Disk Cache.
            // This ensures that access management rules applied by the server-side get_views method
            // are always respected on page loads/refreshes in Odoo 19, bypassing 
            // the persistent stale-while-revalidate disk cache of the view service.

            const loadViewsOptions = {
                action_id: options.actionId || false,
                embedded_action_id: options.embeddedActionId || false,
                embedded_parent_res_id: options.embeddedParentResId || false,
                load_filters: options.loadIrFilters || false,
                toolbar: (!context?.disable_toolbar && options.loadActionMenus) || false,
            };
            for (const key in options) {
                if (!["actionId", "embeddedActionId", "embeddedParentResId", "loadIrFilters", "loadActionMenus"].includes(key)) {
                    loadViewsOptions[key] = options[key];
                }
            }
            if (env.isSmall) {
                loadViewsOptions.mobile = true;
            }
            if (env.debug) {
                loadViewsOptions.debug = true;
            }

            const filteredContext = Object.fromEntries(
                Object.entries(context || {}).filter(
                    ([k, v]) => k == "lang" || k.endsWith("_view_ref")
                )
            );


            // DIRECT ORM CALL - No .cache({ type: "disk" })
            const result = await orm.call(resModel, "get_views", [], {
                context: filteredContext,
                views: views,
                options: loadViewsOptions,
            });


            const viewDescriptions = {
                fields: result.models[resModel].fields,
                relatedModels: result.models,
                views: {},
            };
            for (const viewType in result.views) {
                const { arch, toolbar, id, filters, custom_view_id } = result.views[viewType];


                const viewDescription = { arch, id, custom_view_id };
                if (toolbar) {
                    viewDescription.actionMenus = toolbar;
                }
                if (filters) {
                    viewDescription.irFilters = filters;
                }
                viewDescriptions.views[viewType] = viewDescription;
            }
            return viewDescriptions;
        };
        return api;
    }
});
