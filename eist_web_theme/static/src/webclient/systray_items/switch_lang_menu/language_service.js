/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";

export const langService = {
    // dependencies: ["user", "router"],
    // start(env, { user, router }) {
    start(env, { }) {
        const availableLanguages = session.user_langs.langs;
        const currentLanguage = session.user_langs.current_lang;

        return {
            availableLanguages,
            get allLanguages() {
                return availableLanguages;
            },
            get currentLanguage() {
                return currentLanguage;
            },
        };
    },
};

registry.category("services").add("language", langService);
