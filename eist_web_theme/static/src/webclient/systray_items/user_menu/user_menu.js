/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { markup } from "@odoo/owl";
import { isMacOS } from "@web/core/browser/feature_detection";
import { _t } from "@web/core/l10n/translation";
import { escape } from "@web/core/utils/strings";
import { session } from "@web/session";

patch(UserMenu.prototype, {
    setup() {
        super.setup();
        this.user_menu_items = session["user_menu_items"];
    },

    getElements() {
        let sortedItems = super.getElements(...arguments);
        sortedItems = this.re_init_user_menu_items(sortedItems);
        // console.log("sortedItems", sortedItems);

        // 重新排序
        sortedItems.sort((x, y) => {
            const xSeq = x.sequence ? x.sequence : 100;
            const ySeq = y.sequence ? y.sequence : 100;
            return xSeq - ySeq;
        })
        return sortedItems;
    },

    re_init_user_menu_items(items) {
        // 原生有7个菜单项，附加icon图标
        items.forEach((item) => {
            if (item.id === "documentation") {
                item.sequence = 10;
                item.href = this.user_menu_items.documentation.documentation_url;
                item.hide = !this.user_menu_items.documentation.show;
                item.icon = "fa fa-book";
            }

            if (item.id === "support") {
                item.sequence = 20;
                item.href = this.user_menu_items.support.support_url;
                item.hide = !this.user_menu_items.support.show;
                item.icon = "fa fa-life-ring";
            }

            if (item.id === "shortcuts") {
                const translatedText = _t("Shortcuts: ");
                item.sequence = 30;
                item.description = markup(
                    `${escape(translatedText)}${isMacOS() ? "CMD" : "CTRL"} + K`
                );
                item.icon = "fa fa-keyboard-o";
            }

            if (item.id === "install_pwa") {
                item.sequence = 34;
                item.description =_t("Install App");
                item.icon = "oi oi-apps";
            }

            if (item.id === "color_scheme.switch_theme") {
                item.sequence = 40;
                item.description =_t("Dark Mode");
                item.icon = "fa fa-moon-o";
            }

            if (item.id === "web_tour.tour_enabled") {
                item.sequence = 40;
                item.description =_t("Onboarding");
                item.icon = "fa fa-smile-o";
            }

            if (item.id === "settings") {
                item.sequence = 50;
                item.icon = "fa fa-cog";
            }

            if (item.id === "account") {
                item.sequence = 60;
                item.icon = "fa fa-user";
                item.hide = !this.user_menu_items.enable_odoo_account;
            }

            if (item.id === "logout") {
                item.sequence = 140;
                item.icon = "fa fa-power-off";
            }
        });
        return items;
    },

})