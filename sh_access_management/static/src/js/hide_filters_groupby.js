/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";
import { SearchModel } from "@web/search/search_model"; // Import SearchModel

patch(SearchBar.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.sh_hide_search_panel_entire = false; // Initialize on the component instance

        onWillStart(async () => {
            const resModel = this.env.searchModel ? this.env.searchModel.resModel : false;
            if (!resModel) {
                return;
            }

            // Fetch model-specific restrictions
            const modelResult = await this.orm.call("sh.access.model", "check_crud_operation", [], {
                kwargs: {
                    user_id: user.userId,
                    company_id: user.activeCompany.id,
                },
            });

            // Fetch global restrictions
            const globalResult = await this.orm.call(
                "sh.access.manager",
                "get_access_restrictions",
                [{ user_id: user.userId, company_id: user.activeCompany.id }]
            );
            const globalRestrictions = globalResult.model_restrictions || {};

            // Determine final state for hiding search panel, filter, and group by
            const model_restr = modelResult && modelResult[resModel] || {};
            const hasModelLine = modelResult && resModel in modelResult;
            const conditional_rules = model_restr.sh_conditional_rules || [];

            // If global hide is true but model-line has sh_hide_filter=false, filter should be visible
            const sh_hide_search_panel_final = hasModelLine
                ? (model_restr.sh_hide_search_panel || conditional_rules.some(r => r.hide_search_panel) || false)
                : (globalRestrictions.global_hide_search_panel || model_restr.sh_hide_search_panel || conditional_rules.some(r => r.hide_search_panel));
            const sh_hide_filter_final = hasModelLine
                ? (model_restr.sh_hide_filter || conditional_rules.some(r => r.hide_filter) || false)
                : (globalRestrictions.global_hide_filter || conditional_rules.some(r => r.hide_filter) || false);
            const sh_hide_group_by_final = hasModelLine
                ? (model_restr.sh_hide_group_by || conditional_rules.some(r => r.hide_group_by) || false)
                : (globalRestrictions.global_hide_group_by || conditional_rules.some(r => r.hide_group_by) || false);

            // Apply global hide custom filter/group by options to searchModel
            const searchModel = this.env.searchModel;
            if (searchModel) {
                searchModel.sh_hide_custom_filter = !!globalRestrictions.global_hide_custom_filter;
                searchModel.sh_hide_custom_group_by = !!globalRestrictions.global_hide_custom_group_by;
                searchModel.sh_global_hide_favorite_edit = !!globalRestrictions.sh_global_hide_favorite_edit;

                // Update existing filter/group by flags
                searchModel.sh_hide_filter_tab = sh_hide_filter_final;
                searchModel.sh_hide_group_by_tab = sh_hide_group_by_final;
                const sh_hide_favourite_final = hasModelLine
                    ? (model_restr.sh_hide_favourite || conditional_rules.some(r => r.hide_favourite) || false)
                    : (globalRestrictions.sh_global_hide_favourite || conditional_rules.some(r => r.hide_favourite) || false);
                searchModel.sh_hide_favourite_tab = sh_hide_favourite_final;

                // Store globalRestrictions on searchModel for later use in SearchModel.load
                searchModel.globalRestrictions = globalRestrictions;
            }
            this.sh_hide_search_panel_entire = sh_hide_search_panel_final; // Set on component instance
        });
    },

    get shouldHideSearchBar() {
        return this.sh_hide_search_panel_entire;
    },
});

patch(SearchModel.prototype, {
    async load(config) {
        const resModel = config.resModel;
        if (!resModel) {
            return super.load(config);
        }

        // Fetch model-specific and global restrictions directly
        const modelResult = await this.orm.call("sh.access.model", "check_crud_operation", [], {
            kwargs: {
                user_id: user.userId,
                company_id: user.activeCompany.id,
            },
        });

        const globalResult = await this.orm.call(
            "sh.access.manager",
            "get_access_restrictions",
            [{ user_id: user.userId, company_id: user.activeCompany.id }]
        );
        const globalRestrictions = globalResult.model_restrictions || {};
        const model_restr = (modelResult && modelResult[resModel]) || {};
        const hasModelLine = modelResult && resModel in modelResult;
        const conditional_rules = model_restr.sh_conditional_rules || [];

        // If model has explicit model-line entry, use model-level setting (overrides global)
        const sh_hide_filter_model = hasModelLine
            ? (model_restr.sh_hide_filter || conditional_rules.some(r => r.hide_filter) || false)
            : (globalRestrictions.global_hide_filter || conditional_rules.some(r => r.hide_filter) || false);
        const sh_hide_group_by_model = hasModelLine
            ? (model_restr.sh_hide_group_by || conditional_rules.some(r => r.hide_group_by) || false)
            : (globalRestrictions.global_hide_group_by || conditional_rules.some(r => r.hide_group_by) || false);

        const hiddenFilterData = await this.orm.call("base", "get_hidden_filter_data", [resModel]);
        const hiddenFilterNames = hiddenFilterData.sh_hidden_filter_names || [];
        const hiddenGroupbyNames = hiddenFilterData.sh_hidden_groupby_names || [];

        const hideAllFilters = hiddenFilterNames.includes("__all__");
        const hideAllGroupbys = hiddenGroupbyNames.includes("__all__");

        // Combine model-wise restrictions with specific hidden names
        const shouldHideAllFilters = hideAllFilters || sh_hide_filter_model;
        const shouldHideAllGroupbys = hideAllGroupbys || sh_hide_group_by_model;

        // Filter out hidden search_default_ entries from config.context
        if (config.context && (shouldHideAllFilters || shouldHideAllGroupbys || hiddenFilterNames.length > 0 || hiddenGroupbyNames.length > 0)) {
            const newContext = { ...config.context };
            for (const key in newContext) {
                if (key.startsWith("search_default_")) {
                    const filterName = key.substring("search_default_".length);
                    const isGroupby = filterName.startsWith("groupby_");

                    if (isGroupby) {
                        const groupbyName = filterName.substring("groupby_".length);
                        // It's a groupby
                        if (shouldHideAllGroupbys || hiddenGroupbyNames.includes(groupbyName)) {
                            delete newContext[key];
                        }
                    } else {
                        // It's a filter
                        if (shouldHideAllFilters || hiddenFilterNames.includes(filterName)) {
                            delete newContext[key];
                        }
                    }
                }
            }
            config.context = newContext;
        }

        // Call the original load method
        const res = await super.load(config);
        const sh_hide_favourite_model = hasModelLine
            ? (model_restr.sh_hide_favourite || conditional_rules.some(r => r.hide_favourite) || false)
            : (globalRestrictions.sh_global_hide_favourite || conditional_rules.some(r => r.hide_favourite) || false);

        this.sh_hide_filter_tab = sh_hide_filter_model;
        this.sh_hide_group_by_tab = sh_hide_group_by_model;
        this.sh_hide_favourite_tab = sh_hide_favourite_model;

        if (sh_hide_favourite_model && this.searchMenuTypes.has('favorite')) {
            this.searchMenuTypes.delete('favorite');
        }
        return res;
    },

    get facets() {
        const facets = super.facets;
        return facets.filter(facet => {
            if (facet.type === "filter" && this.sh_hide_filter_tab) {
                return false;
            }
            if (facet.type === "favorite" && this.sh_hide_favourite_tab) {
                return false;
            }
            return true;
        });
    },
});
