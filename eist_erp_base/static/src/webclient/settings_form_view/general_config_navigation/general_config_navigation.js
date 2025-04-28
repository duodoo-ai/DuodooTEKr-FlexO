/** @odoo-module */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";


export class ResConfigGeneralNavigation extends Component {
	static template = "eist_erp_base.res_config_general_navigation";
	static props = ["*"];  // could contain view_widget props

	setup() {
		super.setup(...arguments);
	}

	onClickJumpAnchor() {}
}

export const resConfigGeneralNavigation = {
	component: ResConfigGeneralNavigation,
};


registry
	.category("view_widgets")
	.add("res_config_general_navigation", resConfigGeneralNavigation);
