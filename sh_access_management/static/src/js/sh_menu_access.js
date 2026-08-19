/** @odoo-module **/

import { menuService } from "@web/webclient/menus/menu_service";
import { patch } from "@web/core/utils/patch";

function getCompanyIdsFromCookie() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('cids='))
        ?.split('=')[1];
    if (!cookieValue) {
        return [];
    }
    return cookieValue.split(',').map(Number).filter(id => !isNaN(id));
}

patch(menuService, {
    async start(env, services) {
        const menuAPI = await super.start(...arguments);
        const { orm } = env.services;

        const companyIds = getCompanyIdsFromCookie();
        const hiddenMenuIds = await orm.call(
            "ir.ui.menu",
            "get_menus_to_hide",
            [companyIds]
        );

        if (!hiddenMenuIds || hiddenMenuIds.length === 0) {
            return menuAPI;
        }

        const hiddenMenuIdsSet = new Set(hiddenMenuIds);

        const originalGetMenu = menuAPI.getMenu.bind(menuAPI);
        menuAPI.getMenu = (menuId) => {
            if (hiddenMenuIdsSet.has(menuId)) {
                return undefined;
            }
            const menu = originalGetMenu(menuId);
            if (menu && menu.children) {
                const newChildren = menu.children.filter(childId => !hiddenMenuIdsSet.has(childId));
                return { ...menu, children: newChildren };
            }
            return menu;
        };

        const originalGetAll = menuAPI.getAll.bind(menuAPI);
        menuAPI.getAll = () => {
            return originalGetAll().filter(m => !hiddenMenuIdsSet.has(m.id));
        };

        return menuAPI;
    }
});