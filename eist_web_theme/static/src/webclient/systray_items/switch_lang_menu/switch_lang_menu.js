/** @odoo-module **//** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownGroup } from "@web/core/dropdown/dropdown_group";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { user } from "@web/core/user";
import { rpc } from "@web/core/network/rpc";
import { Component, useState } from "@odoo/owl";

export class SwitchLangMenu extends Component {
    static template = "web.SwitchLangMenu";
    static components = { DropdownGroup, Dropdown, DropdownItem };
    static props = {};
    static toggleDelay = 1000;

    
    setup() {
        this.langService = useService("language");
        this.user = user;
        this.rpc = rpc;
        this.state = useState({ languagesToToggle: [] });
        this.allLanguages = this.langService.allLanguages;
        this.currentLanguage = this.langService.currentLanguage;
    }

    async toggleLanguage(lang) {
        if (lang.id == this.currentLanguage.id) {
            return;
        } else {
            const result = await this.rpc("/web/lang/toggle", {
                context: this.user.context,
                lang: lang,
            });
            if (result) {
                browser.location.reload();
            }
        }
    }
}


export const systrayItem = {
    Component: SwitchLangMenu,
    isDisplayed(env) {
        const { availableLanguages } = env.services.language;
        if (availableLanguages.length > 1 && !env.isSmall) {
            return true;
        } else {
            return false;
        }
    },
};

registry.category("systray").add("SwitchLangMenu", systrayItem, {
    sequence: 1,
});
