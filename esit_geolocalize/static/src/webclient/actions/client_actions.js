/** @odoo-module */


import { browser } from "@web/core/browser/browser";
import { router } from "@web/core/browser/router";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { escape, sprintf } from "@web/core/utils/strings";

import { markup } from "@odoo/owl";

import { DisplayTencentMapDialog } from "@esit_geolocalize/webclient/actions/display_tencent_map_dialog";

export function displayTencentMapDialogAction(env, action) {
    const params = action.params || {};
    // const options = {
    //     className: params.className || "",
    //     sticky: params.sticky || false,
    //     title: params.title,
    //     type: params.type || "info",
    // };
    // const links = (params.links || []).map((link) => {
    //     return `<a href="${escape(link.url)}" target="_blank">${escape(link.label)}</a>`;
    // });
    // const message = markup(sprintf(escape(params.message), ...links));
    // env.services.notification.add(message, options);
    // return params.next;
    env.services.dialog.add(DisplayTencentMapDialog, params, {});
}

registry.category("actions").add("display_tencent_map_dialog", displayTencentMapDialogAction);